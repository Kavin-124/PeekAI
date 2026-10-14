Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "D:\Antigravity\Project\PeekAI"
WshShell.Run """.venv\Scripts\pythonw.exe"" main.py", 0, False
