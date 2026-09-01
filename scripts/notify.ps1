<#
.SYNOPSIS
  Post today's hook as a Windows toast, with buttons into the local college.

.DESCRIPTION
  The toast is best-effort; the page is the contract. Everything here can fail
  without costing a study day, because scripts/daily.py has already written
  state/sessions/<date>.md, state/today.json and dashboard/today.html by the
  time this runs. So every failure path exits 0 quietly rather than turning a
  cosmetic problem into a scheduled-task error.

  Buttons use activationType="protocol", which hands a URL to the default
  browser. That is the whole reason this needs no COM activator registration
  and no BurntToast module: protocol activation can only issue a GET, and the
  local server's /open route is built to be reachable that way (the token
  rides in the query string; see scripts/serve.py).

  If the server is not up, the toast falls back to a single button opening
  dashboard/today.html directly off disk. A button that quietly does nothing
  is worse than a button that admits what it can reach.

  Nothing is posted on a rest day. Nothing is owed on a rest day.

.PARAMETER AppId
  The AppUserModelID the toast is posted under; it names the app in the banner
  and in the Action Center. scripts/register_daily_task.ps1 registers it, both
  as an HKCU key and as a System.AppUserModel.ID property on a Start Menu
  shortcut. Which of those two is strictly required was never isolated, so
  both stay.

  Note for anyone debugging a missing notification: this AUMID does NOT appear
  in Get-StartApps or in Settings > Notifications, and the Start Menu cannot
  find the shortcut by name -- and none of that stops the banner. Toasts under
  it display correctly with the title "Nexus College". A previous version of
  this script inferred from Get-StartApps that the id was unusable and fell
  back to Windows PowerShell's AUMID; that inference was wrong, the label was
  worse for it, and the fallback is gone. The actual cause of the missing
  banners was Do Not Disturb being on.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\notify.ps1
#>
[CmdletBinding()]
param(
    [string]$RepoRoot,
    [string]$AppId = 'NexusCollege.Daily',
    [switch]$WhatIfXml   # print the toast XML instead of showing it
)

# $PSScriptRoot is empty inside a param() default under Windows PowerShell 5.1,
# so the repo root is resolved here instead of in the signature.
if (-not $RepoRoot) { $RepoRoot = Split-Path -Parent $PSScriptRoot }

function Read-JsonFile($Path) {
    if (-not (Test-Path $Path)) { return $null }
    try { return (Get-Content -Raw -Encoding UTF8 $Path | ConvertFrom-Json) }
    catch { return $null }
}

function Esc($Text) { [System.Security.SecurityElement]::Escape([string]$Text) }

$plan = Read-JsonFile (Join-Path $RepoRoot 'state\today.json')
if ($null -eq $plan) {
    Write-Verbose 'no state/today.json - daily.py has not run; nothing to announce'
    exit 0
}
if ($plan.rest_day) {
    Write-Verbose 'rest day - nothing is owed, so nothing is posted'
    exit 0
}
if (-not $plan.lectures -or $plan.lectures.Count -eq 0) {
    Write-Verbose 'no lectures planned; nothing to hook with'
    exit 0
}

# The task's two actions run independently: if the builder fails, this one still
# fires, and yesterday's state/today.json is still on disk. Announcing it would
# put a plausible-looking toast over a failed build -- a notification that lies
# about the state of the system is worse than no notification at all, which is
# the whole reason this loop was rebuilt.
$todayIso = (Get-Date).ToString('yyyy-MM-dd')
if ($plan.date -ne $todayIso) {
    Write-Error ("state/today.json is dated $($plan.date), not $todayIso; the " +
                 "build did not run. Not announcing a stale plan.") -ErrorAction Continue
    exit 0
}
$beat = Read-JsonFile (Join-Path $RepoRoot 'state\last-daily-run.json')
if ($null -eq $beat -or $beat.date -ne $todayIso -or
        $beat.outcome -notin @('built', 'already-built', 'rest')) {
    Write-Error ("heartbeat is not healthy for $todayIso (outcome: " +
                 "$($beat.outcome)); not announcing.") -ErrorAction Continue
    exit 0
}

$first = $plan.lectures[0]
$due = [int]$plan.review_target

# Is the local server actually answering? Its own health route decides, not the
# presence of state/server.json -- a stale file from a dead process would
# otherwise produce buttons that lead nowhere.
$srv = Read-JsonFile (Join-Path $RepoRoot 'state\server.json')
$live = $false
if ($null -ne $srv) {
    try {
        $probe = Invoke-WebRequest -Uri "http://127.0.0.1:$($srv.port)/healthz" `
            -TimeoutSec 2 -UseBasicParsing
        $live = ($probe.StatusCode -eq 200)
    } catch { $live = $false }
}

$actions = New-Object System.Text.StringBuilder
if ($live) {
    $base = "http://127.0.0.1:$($srv.port)"
    $launch = "$base/"
    [void]$actions.Append(('<action content="{0}" activationType="protocol" arguments="{1}"/>' -f
        (Esc ("Start " + $first.id)), (Esc "$base/open/$($first.id)?t=$($srv.token)")))
    if ($due -gt 0) {
        [void]$actions.Append(('<action content="{0}" activationType="protocol" arguments="{1}"/>' -f
            (Esc ("Review $due")), (Esc "$base/review")))
    }
} else {
    # No server: the static page still has today on it, and says which parts
    # need the server rather than pretending they work.
    $launch = ([uri](Join-Path $RepoRoot 'dashboard\today.html')).AbsoluteUri
    [void]$actions.Append(('<action content="Open today" activationType="protocol" arguments="{0}"/>' -f
        (Esc $launch)))
}

$attribution = if ($due -gt 0) { "$due cards waiting" } else { 'no cards due' }

$toastXml = @"
<toast activationType="protocol" launch="$(Esc $launch)">
  <visual>
    <binding template="ToastGeneric">
      <text>$(Esc ("Lecture 1: " + $first.title))</text>
      <text>$(Esc $first.hook)</text>
      <text placement="attribution">$(Esc $attribution)</text>
    </binding>
  </visual>
  <actions>$($actions.ToString())</actions>
</toast>
"@

if ($WhatIfXml) { $toastXml; exit 0 }

try {
    [void][Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
    [void][Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]
    $doc = New-Object Windows.Data.Xml.Dom.XmlDocument
    $doc.LoadXml($toastXml)
    $toast = New-Object Windows.UI.Notifications.ToastNotification $doc
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($AppId).Show($toast)
    Write-Verbose "toast posted for $($first.id)"
} catch {
    # Cosmetic layer. Say so on stderr for anyone reading the task log, and
    # still exit 0: the day was built, and that is what mattered.
    Write-Error "toast failed (the day is still built): $_" -ErrorAction Continue
}
exit 0
