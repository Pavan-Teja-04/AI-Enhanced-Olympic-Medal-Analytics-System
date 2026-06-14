@echo off
cd /d "%~dp0"
echo Checking backend health...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/api/analytics/overview; Write-Host 'Backend OK:' $r.StatusCode; Write-Host $r.Content } catch { Write-Host 'Backend NOT running or not reachable.'; Write-Host $_.Exception.Message }"
pause
