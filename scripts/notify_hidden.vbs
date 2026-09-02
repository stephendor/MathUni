' notify_hidden.vbs - launch notify.ps1 with no console window, ever.
'
' The scheduled task used to run powershell.exe directly with
' -WindowStyle Hidden. That flag is applied by PowerShell itself, AFTER the
' console host has already been created, so a window flashes on screen for a
' fraction of a second every time the task fires. Stephen saw exactly that at
' the 2026-09-01 logon and reasonably assumed it was unrelated noise.
'
' wscript.exe is a windowless host, so nothing is ever created to hide. Run
' with 0 (hidden) and False (do not wait): the toast is best-effort and the
' task should not sit blocked on it.
'
' Usage (from the repo root, which the task sets as its working directory):
'   wscript.exe scripts\notify_hidden.vbs [AppId]

Option Explicit

Dim shell, fso, here, ps1, appId, cmd
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

here = fso.GetParentFolderName(WScript.ScriptFullName)
ps1 = fso.BuildPath(here, "notify.ps1")

If Not fso.FileExists(ps1) Then
    ' Nothing to launch. The day is already built and the page already written,
    ' so this is not worth failing the task over.
    WScript.Quit 0
End If

cmd = "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File """ & ps1 & """"

If WScript.Arguments.Count > 0 Then
    appId = WScript.Arguments(0)
    If Len(appId) > 0 Then
        cmd = cmd & " -AppId """ & appId & """"
    End If
End If

shell.Run cmd, 0, False
WScript.Quit 0
