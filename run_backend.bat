@echo off
cd /d "%~dp0"
title Olympic Medal Analytics Backend
echo Starting Olympic Medal Analytics backend...
echo API URL: http://127.0.0.1:5000
echo Dashboard URL: http://127.0.0.1:5000
echo.
echo Using Python:
"%~dp0venv\Scripts\python.exe" --version
echo.
"%~dp0venv\Scripts\python.exe" -u "%~dp0backend\app.py"
echo.
echo Backend stopped. Read the error above, then press any key to close.
pause
