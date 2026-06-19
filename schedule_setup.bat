@echo off
REM schedule_setup.bat — creates three daily tasks to run ksg_bot.py
REM Run this file as Administrator to register scheduled tasks.

SET SCRIPT_DIR=%~dp0
SET PY=python

echo Creating scheduled tasks (will overwrite if exists)...

schtasks /Create /SC DAILY /TN "KSG_Morning" /TR "%PY% \"%SCRIPT_DIR%ksg_bot.py\" morning" /ST 09:00 /F
schtasks /Create /SC DAILY /TN "KSG_Afternoon" /TR "%PY% \"%SCRIPT_DIR%ksg_bot.py\" afternoon" /ST 13:00 /F
schtasks /Create /SC DAILY /TN "KSG_Evening" /TR "%PY% \"%SCRIPT_DIR%ksg_bot.py\" evening" /ST 18:00 /F

echo Done. Use Task Scheduler to review tasks.
pause
