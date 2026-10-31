@echo off
title FloraGuard IoT - Plant Disease Early Detection Dashboard
echo ========================================================
echo Starting FloraGuard IoT Backend and Opening Dashboard...
echo ========================================================

REM Launch FastAPI backend in a separate minimized window
start "FloraGuard FastAPI Backend" /min python -m uvicorn backend:app --host 0.0.0.0 --port 8000

REM Wait 2 seconds for server startup
timeout /t 2 /nobreak >nul

REM Open dashboard in default browser
start http://127.0.0.1:8000

echo Backend is running on http://127.0.0.1:8000
echo Dashboard opened in your default web browser.
pause
