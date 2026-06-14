@echo off
cd /d "%~dp0"
start "Olympic Backend API" cmd /k ""%~dp0run_backend.bat""
timeout /t 5 >nul
start "Olympic Frontend" "http://127.0.0.1:5000"
