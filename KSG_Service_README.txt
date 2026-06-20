KSG Scheduler Service

Files:
- create_service.bat : Create and start the Windows service (run as Administrator).
- remove_service.bat : Stop and delete the service (run as Administrator).
- run_scheduler.bat  : Runs pythonw ksg_scheduler.py (no console window).
- ksg_scheduler.py   : Scheduler script (uses `schedule` library).

Installation (Administrator):
1. Ensure Python and dependencies are installed: `pip install schedule`.
2. Optionally test scheduler in console: `python ksg_scheduler.py`.
3. Run `create_service.bat` as Administrator to install and start the service.

Notes:
- The service runs under the LocalSystem account and invokes `pythonw` with the path to `ksg_scheduler.py`.
- If you prefer the service to run under a specific user account, edit `create_service.bat` and change the `obj=` parameter in the `sc create` command, then provide credentials.
- To uninstall: run `remove_service.bat` as Administrator.

Troubleshooting:
- Check Windows Event Viewer > Windows Logs > Application/System for service errors.
- If the service fails to start, run `pythonw` command manually to ensure `ksg_scheduler.py` runs without errors.
