<#
.SYNOPSIS
  Install (or remove) the deterministic daily loop's Windows integration.

.DESCRIPTION
  Replaces the `NexusCollege Morning` task, which ran headless Claude Code at
  06:30 and failed silently every study morning from roughly 2026-07-11 to
  2026-08-31. Nothing here invokes a model, so nothing here can be broken by a
  retired model id or a usage limit.

  Three things are installed:

  1. An AppUserModelID under HKCU\Software\Classes\AppUserModelId. Windows
     silently drops toasts from an unregistered AUMID, so without this the
     notification layer fails in the one way that leaves no trace. The key is
     per-user, holds only a display name, and -Uninstall removes it.

  2. Scheduled task "NexusCollege Daily" — builds the day, then posts the
     toast. Registered from XML rather than schtasks.exe arguments because the
     CLI form can express only ONE trigger, and one trigger is a large part of
     why the old task missed so much. This carries two:

       * at logon, delayed 2 minutes  (covers "the machine was off at 06:30")
       * daily at 06:30               (covers "already logged in since Tuesday")

     with StartWhenAvailable=true so a missed window is caught up rather than
     skipped, and DisallowStartIfOnBatteries=false. The old task had
     `Stop On Battery Mode, No Start On Batteries` and `Logon Mode: Interactive
     only`, which between them meant a laptop on battery never ran it at all.

     The builder is idempotent, so both triggers firing on one day is a no-op.

  3. Scheduled task "NexusCollege Server" — the persistent local surface, at
     logon, via pythonw.exe so there is no console window. serve.py refuses to
     start a second college on a port that already answers, so a double fire
     is harmless.

.PARAMETER Uninstall
  Remove both tasks and the AUMID key. Does not touch the repo.

.PARAMETER WhatIf
  Print what would be done and change nothing. Run this first.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\register_daily_task.ps1 -WhatIf
  powershell -ExecutionPolicy Bypass -File scripts\register_daily_task.ps1
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$RepoRoot,
    [string]$AppId = 'NexusCollege.Daily',
    [string]$DailyTime = '06:30',
    [switch]$Uninstall
)

if (-not $RepoRoot) { $RepoRoot = Split-Path -Parent $PSScriptRoot }

# Every value interpolated into the task XML below is escaped. A repo path as
# ordinary as C:\Work\Math&Stats produces invalid XML otherwise, schtasks /Create
# rejects it, and the automation simply is not installed.
function XmlEsc($Text) { [System.Security.SecurityElement]::Escape([string]$Text) }

if ($DailyTime -notmatch '^([01][0-9]|2[0-3]):[0-5][0-9]$') {
    Write-Error "DailyTime must be HH:mm (24-hour); got '$DailyTime'."
    exit 1
}

$DailyTask  = 'NexusCollege Daily'
$ServerTask = 'NexusCollege Server'
$OldTask    = 'NexusCollege Morning'
$AumidKey   = "HKCU:\Software\Classes\AppUserModelId\$AppId"

function Remove-TaskIfPresent($Name) {
    $exists = schtasks /Query /TN $Name 2>$null
    if ($LASTEXITCODE -eq 0) {
        if ($PSCmdlet.ShouldProcess($Name, 'delete scheduled task')) {
            schtasks /Delete /TN $Name /F | Out-Null
            Write-Output "removed task: $Name"
        }
    } else {
        Write-Output "task not present (nothing to remove): $Name"
    }
}

# Uninstall runs BEFORE the interpreter is resolved. Removing the tasks does
# not need Python, and the moment you most want to uninstall is when the
# environment is broken -- a preflight that exits first would leave both
# tasks, the AUMID and the shortcut installed with no way to remove them.
if ($Uninstall) {
    Remove-TaskIfPresent $DailyTask
    Remove-TaskIfPresent $ServerTask
    if (Test-Path $AumidKey) {
        if ($PSCmdlet.ShouldProcess($AumidKey, 'remove AUMID registration')) {
            Remove-Item $AumidKey -Recurse -Force
            Write-Output "removed AUMID: $AppId"
        }
    } else {
        Write-Output "AUMID not present: $AppId"
    }
    $lnk = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Nexus College.lnk'
    if (Test-Path $lnk) {
        if ($PSCmdlet.ShouldProcess($lnk, 'remove Start Menu shortcut')) {
            Remove-Item $lnk -Force
            Write-Output 'removed Start Menu shortcut'
        }
    }
    Write-Output 'uninstalled. scripts/daily.py still works when run by hand.'
    exit 0
}

# Choosing the interpreter by name is not safe here, and this was not
# hypothetical: the first install of this task registered miniconda's
# pythonw.exe, because the installer ran in a shell whose profile had put
# conda ahead of the Python that actually has pyyaml. daily.py then died on
# `import yaml` at module-import time -- before its own crash handler could
# run, so it wrote no failure heartbeat -- and because notify.ps1 exits 0 by
# design, the task reported Last Result: 0. A task that reports success while
# doing nothing is the exact failure this loop was rebuilt to remove, so the
# interpreter is now PROVEN before it is registered.
function Resolve-Python {
    param([string]$Root)
    $seen = New-Object System.Collections.Generic.List[string]
    foreach ($name in 'python', 'python3') {
        Get-Command $name -All -ErrorAction SilentlyContinue |
            ForEach-Object { if ($_.Source) { $seen.Add($_.Source) } }
    }
    # The py launcher knows about installs that are not on PATH at all.
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $viaPy = & py -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $viaPy) { $seen.Add($viaPy.Trim()) }
    }
    foreach ($cand in ($seen | Select-Object -Unique)) {
        # RepoRoot travels through the environment, not interpolated into the
        # Python source: a path containing an apostrophe, or ending in a
        # backslash that escapes the closing quote, would make this snippet a
        # syntax error and every candidate interpreter would be rejected.
        $env:NEXUS_REPO_ROOT = $Root
        try {
            & $cand -c "import os, sys; sys.path.insert(0, os.environ['NEXUS_REPO_ROOT']); import scripts.daily" 2>$null
        } finally {
            Remove-Item Env:\NEXUS_REPO_ROOT -ErrorAction SilentlyContinue
        }
        if ($LASTEXITCODE -eq 0) { return $cand }
        Write-Verbose "rejected (cannot import scripts.daily): $cand"
    }
    return $null
}

$python = Resolve-Python -Root $RepoRoot
if (-not $python) {
    Write-Error ("No Python on this machine can import scripts.daily. Tried every " +
                 "python/python3 on PATH plus the py launcher. Install pyyaml " +
                 "(pip install -r requirements-dev.txt) and re-run.")
    exit 1
}
# pythonw from the SAME installation, never resolved separately by name.
$pythonw = Join-Path (Split-Path -Parent $python) 'pythonw.exe'
if (-not (Test-Path $pythonw)) { $pythonw = $python }
Write-Output "interpreter: $pythonw"

# --- 1. AUMID -------------------------------------------------------------
if ($PSCmdlet.ShouldProcess($AumidKey, 'register AppUserModelID for toasts')) {
    New-Item -Path $AumidKey -Force | Out-Null
    New-ItemProperty -Path $AumidKey -Name 'DisplayName' -Value 'Nexus College' `
        -PropertyType String -Force | Out-Null
    # Deliberately NOT setting ShowInSettings=0: hiding the app from the
    # notifications UI was a tidiness choice made unasked, and it takes away
    # the one place the toast behaviour can be inspected or turned off.
    Write-Output "registered AUMID: $AppId"
}

# --- 1b. the Start Menu shortcut carrying the AUMID -----------------------
# Microsoft's documented requirement for a desktop app to raise toasts is a
# Start Menu shortcut carrying System.AppUserModel.ID, so both that and the
# registry key above are installed.
#
# An earlier version of this comment claimed to have MEASURED that the registry
# key alone produced no notifications. That measurement was taken while Do Not
# Disturb was on, which suppressed every banner regardless of AUMID, so it
# proved nothing. Which of the two registrations is strictly required has not
# been isolated; both are cheap and both stay.
#
# What is known: with both in place, toasts display correctly titled "Nexus
# College" -- even though this AUMID never appears in Get-StartApps or in
# Settings > Notifications, and the Start Menu cannot find the shortcut by
# name. Absence from those surfaces is not evidence the AUMID is unusable.
if (-not ('NexusToast.Aumid' -as [type])) {
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

namespace NexusToast {
  [ComImport, Guid("00021401-0000-0000-C000-000000000046")]
  public class ShellLink { }

  [ComImport, Guid("0000010b-0000-0000-C000-000000000046"),
   InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  public interface IPersistFile {
    void GetClassID(out Guid pClassID);
    [PreserveSig] int IsDirty();
    void Load([MarshalAs(UnmanagedType.LPWStr)] string pszFileName, int dwMode);
    void Save([MarshalAs(UnmanagedType.LPWStr)] string pszFileName,
              [MarshalAs(UnmanagedType.Bool)] bool fRemember);
    void SaveCompleted([MarshalAs(UnmanagedType.LPWStr)] string pszFileName);
    void GetCurFile([MarshalAs(UnmanagedType.LPWStr)] out string ppszFileName);
  }

  [StructLayout(LayoutKind.Sequential, Pack = 4)]
  public struct PropertyKey {
    public Guid fmtid;
    public uint pid;
    public PropertyKey(Guid g, uint p) { fmtid = g; pid = p; }
  }

  // Size=24 is load-bearing, not decoration. PROPVARIANT on x64 is vt plus
  // three reserved WORDs (8 bytes) then a 16-byte union. Declared without an
  // explicit size this struct marshals as 16 bytes, SetValue reads past the
  // end of it, and the property is silently not written -- the shortcut saves
  // fine, the call returns success, and the AUMID reads back VT_EMPTY. That
  // was observed here before it was fixed.
  [StructLayout(LayoutKind.Explicit, Size = 24)]
  public struct PropVariant {
    [FieldOffset(0)] public ushort vt;
    [FieldOffset(8)] public IntPtr pointerValue;
    public void SetString(string v) {
      vt = 31; // VT_LPWSTR
      pointerValue = Marshal.StringToCoTaskMemUni(v);
    }
    public void Clear() {
      if (pointerValue != IntPtr.Zero) { Marshal.FreeCoTaskMem(pointerValue); }
      pointerValue = IntPtr.Zero; vt = 0;
    }
  }

  [ComImport, Guid("886d8eeb-8cf2-4446-8d02-cdba1dbdcf99"),
   InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  public interface IPropertyStore {
    void GetCount(out uint cProps);
    void GetAt(uint iProp, out PropertyKey pkey);
    void GetValue(ref PropertyKey key, out PropVariant pv);
    void SetValue(ref PropertyKey key, ref PropVariant pv);
    void Commit();
  }

  public static class Aumid {
    // PKEY_AppUserModel_ID
    static readonly Guid AppUserModel =
      new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3");
    public static void Set(string lnkPath, string appId) {
      IPersistFile link = (IPersistFile)new ShellLink();
      link.Load(lnkPath, 2); // STGM_READWRITE
      IPropertyStore store = (IPropertyStore)link;
      PropertyKey key = new PropertyKey(AppUserModel, 5);
      PropVariant pv = new PropVariant();
      pv.SetString(appId);
      store.SetValue(ref key, ref pv);
      store.Commit();
      pv.Clear();
      link.Save(lnkPath, true);
    }
    public static string Get(string lnkPath) {
      IPersistFile link = (IPersistFile)new ShellLink();
      link.Load(lnkPath, 0);
      IPropertyStore store = (IPropertyStore)link;
      PropertyKey key = new PropertyKey(AppUserModel, 5);
      PropVariant pv;
      store.GetValue(ref key, out pv);
      if (pv.vt == 31 && pv.pointerValue != IntPtr.Zero) {
        return Marshal.PtrToStringUni(pv.pointerValue);
      }
      return "(not set, vt=" + pv.vt + ")";
    }
  }
}
'@
}

$startMenu = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'
$shortcut  = Join-Path $startMenu 'Nexus College.lnk'
if ($PSCmdlet.ShouldProcess($shortcut, 'create Start Menu shortcut carrying the AUMID')) {
    $wsh = New-Object -ComObject WScript.Shell
    $lnk = $wsh.CreateShortcut($shortcut)
    # The target must be an EXECUTABLE. This pointed at dashboard/today.html
    # first, and a shortcut to a DOCUMENT is not indexed as an app -- so the
    # AUMID never resolved, and Windows files toasts from an unresolvable
    # AUMID into the Action Center WITHOUT showing a banner. Delivered,
    # recorded, and invisible: the notification arrived and nobody saw it.
    # explorer.exe is an executable and forwards its argument to the default
    # browser, so the shortcut both indexes and does something worth clicking.
    # The target must be an ORDINARY executable. Two earlier attempts failed
    # for the same underlying reason -- Windows would not index the shortcut,
    # so the AUMID never resolved, so toasts were filed into the Action Center
    # with no banner: delivered, recorded, invisible.
    #   * dashboard/today.html -- a document is not an app.
    #   * explorer.exe         -- Windows excludes its own shell binaries.
    # pythonw.exe running open_today.py is a real executable AND does the
    # right thing when clicked, so the shortcut is honest rather than a decoy.
    $lnk.TargetPath       = $pythonw
    $lnk.Arguments        = 'scripts\open_today.py'
    $lnk.WorkingDirectory = $RepoRoot
    $lnk.IconLocation     = "$pythonw,0"
    $lnk.Description      = "Open today's study day"
    $lnk.Save()
    [NexusToast.Aumid]::Set($shortcut, $AppId)
    $readback = [NexusToast.Aumid]::Get($shortcut)
    if ($readback -ne $AppId) {
        Write-Error ("Set the AUMID on $shortcut but it reads back as '$readback'. " +
                     "Toasts will be dropped silently. Not continuing quietly.")
        exit 1
    }
    Write-Output "created Start Menu shortcut: $shortcut (AUMID verified: $readback)"
}


# --- 2. the daily task ----------------------------------------------------
# One <Exec> cannot both build the day and post the toast, and a .cmd wrapper
# would put a console window on screen every morning. Two actions in one task
# run in sequence, which is exactly the ordering wanted: build, then announce.
$dailyXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Nexus College: build today's study day (no model in the path), then post the hook.</Description>
    <URI>\$(XmlEsc $DailyTask)</URI>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT2M</Delay>
      <UserId>$(XmlEsc $env:USERNAME)</UserId>
    </LogonTrigger>
    <CalendarTrigger>
      <StartBoundary>2026-01-01T$(XmlEsc $DailyTime):00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings><StopOnIdleEnd>false</StopOnIdleEnd><RestartOnIdle>false</RestartOnIdle></IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT10M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>$(XmlEsc $pythonw)</Command>
      <Arguments>scripts\daily.py</Arguments>
      <WorkingDirectory>$(XmlEsc $RepoRoot)</WorkingDirectory>
    </Exec>
    <!-- wscript.exe, not powershell.exe: -WindowStyle Hidden is applied by
         PowerShell after the console host already exists, so a window
         flashes on screen every time the task fires. wscript is a
         windowless host, so there is nothing to hide. -->
    <Exec>
      <Command>wscript.exe</Command>
      <Arguments>"$RepoRoot\scripts\notify_hidden.vbs" "$AppId"</Arguments>
      <WorkingDirectory>$(XmlEsc $RepoRoot)</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

# --- 3. the server task ---------------------------------------------------
$serverXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Nexus College: the persistent local surface on 127.0.0.1.</Description>
    <URI>\$(XmlEsc $ServerTask)</URI>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT1M</Delay>
      <UserId>$(XmlEsc $env:USERNAME)</UserId>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings><StopOnIdleEnd>false</StopOnIdleEnd><RestartOnIdle>false</RestartOnIdle></IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <!-- The server is meant to stay up for days; no execution time limit. -->
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <RestartOnFailure><Interval>PT5M</Interval><Count>3</Count></RestartOnFailure>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>$(XmlEsc $pythonw)</Command>
      <Arguments>scripts\serve.py</Arguments>
      <WorkingDirectory>$(XmlEsc $RepoRoot)</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

function Register-FromXml($Name, $Xml) {
    if (-not $PSCmdlet.ShouldProcess($Name, 'register scheduled task')) { return $true }
    $tmp = Join-Path $env:TEMP ("nexus-" + [guid]::NewGuid().ToString('N') + ".xml")
    # schtasks /XML requires UTF-16 (the declaration above says so, and it must
    # be true of the bytes, not only of the text).
    [System.IO.File]::WriteAllText($tmp, $Xml, [System.Text.Encoding]::Unicode)
    try {
        schtasks /Create /TN $Name /XML $tmp /F | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Output "registered task: $Name"
            return $true
        }
        # Write-Error is NON-TERMINATING under the default error policy, so a
        # bare Write-Error here let the script carry on and delete the task this
        # one was meant to replace -- installing nothing and removing the old
        # automation, which is the precise silent outage this work exists to
        # prevent. The caller must see the failure.
        Write-Error "schtasks failed for $Name (exit $LASTEXITCODE)"
        return $false
    } finally { Remove-Item $tmp -Force -ErrorAction SilentlyContinue }
}

$dailyOk  = Register-FromXml $DailyTask  $dailyXml
$serverOk = Register-FromXml $ServerTask $serverXml

# --- 4. retire the task this replaces -------------------------------------
# Only once the replacements are actually registered. Removing the old task
# after a failed registration would leave the machine with no daily automation
# at all, reported as a successful install.
if ($dailyOk -and $serverOk) {
    Remove-TaskIfPresent $OldTask
} else {
    Write-Error ("Registration failed, so '$OldTask' has been LEFT IN PLACE. " +
                 "Fix the error above and re-run; nothing has been removed.")
    exit 1
}

Write-Output ''
Write-Output 'Installed. Verify with:'
Write-Output '  schtasks /Query /TN "NexusCollege Daily" /V /FO LIST'
Write-Output '  python scripts\check_daily_liveness.py'
Write-Output ''
Write-Output 'Note: the daily task has two actions, so its Last Result reflects the'
Write-Output 'TOAST, not the build - notify.ps1 exits 0 on purpose. The heartbeat and'
Write-Output 'check_daily_liveness.py are the verdict that matters.'
Write-Output 'Remove with: -Uninstall'
