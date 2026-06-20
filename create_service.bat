@echo off
REM create_service.bat — creates a Windows service that runs ksg_scheduler.py via pythonw
REM Run this file as Administrator.

nSET PY=C:\Users\biost\AppData\Local\Programs\Python\Python312\pythonw.exe
SET SCRIPT=D:\Claude_VSCode_20260618\KCG\KoreaStrategyGroup\ksg_scheduler.py
SET SERVICENAME=KSG_Scheduler

necho Creating service %SERVICENAME%...

nsc create %SERVICENAME% binPath= "\"%PY%\" \"%SCRIPT%\"" start= auto DisplayName= "KSG Scheduler" obj= "LocalSystem"
nsc description %SERVICENAME% "Runs KSG scheduler (ksg_scheduler.py) via pythonw"
necho Starting service...
nsc start %SERVICENAME%
necho Done.
pause
