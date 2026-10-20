@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
 echo Please follow the first-time setup steps in README.md.
 pause
 exit /b 1
)
.venv\Scripts\python.exe -m flask --app app:create_app run
pause
