@echo off
REM remove_service.bat — stops and deletes the KSG_Scheduler service (run as Administrator)
SET SERVICENAME=KSG_Scheduler
echo Stopping service %SERVICENAME%...
sc stop %SERVICENAME%
echo Deleting service %SERVICENAME%...
sc delete %SERVICENAME%
echo Done.
pause
