@echo off
REM schedule_setup_admin.bat — creates three daily tasks to run ksg_bot.py (run as Administrator)

nSET SCRIPT_DIR=%~dp0
SET PY=C:\Users\biost\AppData\Local\Programs\Python\Python312\python.exe

necho Creating scheduled tasks (will overwrite if exists)...

nschtasks /Create /SC DAILY /TN "KSG_Morning" /TR "\"%PY%\" \"%SCRIPT_DIR%ksg_bot.py\" morning" /ST 09:00 /F
schtasks /Create /SC DAILY /TN "KSG_Afternoon" /TR "\"%PY%\" \"%SCRIPT_DIR%ksg_bot.py\" afternoon" /ST 13:00 /F
schtasks /Create /SC DAILY /TN "KSG_Evening" /TR "\"%PY%\" \"%SCRIPT_DIR%ksg_bot.py\" evening" /ST 18:00 /F

necho Done. Use Task Scheduler to review tasks.
pause
