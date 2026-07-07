# Registers the Nexus College morning routine with Windows Task Scheduler.
# Runs headless Claude Code in the repo on study-day mornings; the /morning
# skill itself checks state/schedule.json and exits silently on rest days,
# so the schtasks day list below can stay broad if you change study days.
# Re-run this script any time (/F overwrites). Remove with:
#   schtasks /Delete /TN "NexusCollege Morning" /F
$action = 'cmd /c cd /d C:\Users\steph\MathUni && claude -p "/morning" --permission-mode acceptEdits >> state\morning.log 2>&1'
schtasks /Create /F /TN "NexusCollege Morning" /SC WEEKLY /D MON,TUE,THU,FRI /ST 06:30 /TR $action
if ($LASTEXITCODE -eq 0) { Write-Output "Registered: NexusCollege Morning (Mon/Tue/Thu/Fri 06:30). Log: state\morning.log" }
else { Write-Output "schtasks failed with exit code $LASTEXITCODE" }
