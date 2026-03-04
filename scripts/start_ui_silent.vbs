Set oShell = CreateObject("WScript.Shell")
oShell.Run "cmd /c cd /d D:\Projects\jarvis && venv\Scripts\activate.bat && python -u -m jarvis.ui.interface >> D:\Projects\jarvis\data\logs\jarvis.log 2>&1", 0, False
