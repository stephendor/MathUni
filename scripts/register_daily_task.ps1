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

$DailyTask  = 'NexusCollege Daily'
$ServerTask = 'NexusCollege Server'
$OldTask    = 'NexusCollege Morning'
$AumidKey   = "HKCU:\Software\Classes\AppUserModelId\$AppId"

$python  = (Get-Command python).Source
$pythonw = (Get-Command pythonw -ErrorAction SilentlyContinue)
if ($pythonw) { $pythonw = $pythonw.Source } else { $pythonw = $python }

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
    Write-Output 'uninstalled. scripts/daily.py still works when run by hand.'
    exit 0
}

# --- 1. AUMID -------------------------------------------------------------
if ($PSCmdlet.ShouldProcess($AumidKey, 'register AppUserModelID for toasts')) {
    New-Item -Path $AumidKey -Force | Out-Null
    New-ItemProperty -Path $AumidKey -Name 'DisplayName' -Value 'Nexus College' `
        -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $AumidKey -Name 'ShowInSettings' -Value 0 `
        -PropertyType DWord -Force | Out-Null
    Write-Output "registered AUMID: $AppId"
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
    <URI>\$DailyTask</URI>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT2M</Delay>
      <UserId>$env:USERNAME</UserId>
    </LogonTrigger>
    <CalendarTrigger>
      <StartBoundary>2026-01-01T${DailyTime}:00</StartBoundary>
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
      <Command>$pythonw</Command>
      <Arguments>scripts\daily.py</Arguments>
      <WorkingDirectory>$RepoRoot</WorkingDirectory>
    </Exec>
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "$RepoRoot\scripts\notify.ps1" -AppId "$AppId"</Arguments>
      <WorkingDirectory>$RepoRoot</WorkingDirectory>
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
    <URI>\$ServerTask</URI>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT1M</Delay>
      <UserId>$env:USERNAME</UserId>
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
      <Command>$pythonw</Command>
      <Arguments>scripts\serve.py</Arguments>
      <WorkingDirectory>$RepoRoot</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

function Register-FromXml($Name, $Xml) {
    if (-not $PSCmdlet.ShouldProcess($Name, 'register scheduled task')) { return }
    $tmp = Join-Path $env:TEMP ("nexus-" + [guid]::NewGuid().ToString('N') + ".xml")
    # schtasks /XML requires UTF-16 (the declaration above says so, and it must
    # be true of the bytes, not only of the text).
    [System.IO.File]::WriteAllText($tmp, $Xml, [System.Text.Encoding]::Unicode)
    try {
        schtasks /Create /TN $Name /XML $tmp /F | Out-Null
        if ($LASTEXITCODE -eq 0) { Write-Output "registered task: $Name" }
        else { Write-Error "schtasks failed for $Name (exit $LASTEXITCODE)" }
    } finally { Remove-Item $tmp -Force -ErrorAction SilentlyContinue }
}

Register-FromXml $DailyTask  $dailyXml
Register-FromXml $ServerTask $serverXml

# --- 4. retire the task this replaces -------------------------------------
Remove-TaskIfPresent $OldTask

Write-Output ''
Write-Output 'Installed. Verify with:'
Write-Output '  schtasks /Query /TN "NexusCollege Daily" /V /FO LIST'
Write-Output '  python scripts\check_daily_liveness.py'
Write-Output 'Remove with: -Uninstall'
