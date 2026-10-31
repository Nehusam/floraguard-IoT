@echo off
setlocal enabledelayedexpansion
title FloraGuard IoT - Plant Disease Early Warning System
cls

echo =========================================================================
echo    FloraGuard IoT - Plant Disease Detection & Early Warning System
echo =========================================================================
echo.

REM 1. Verify Python Installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not detected in your system PATH!
    echo Please install Python 3.10+ from https://www.python.org and check
    echo 'Add python.exe to PATH' during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
echo [System] Found %PYTHON_VER%

REM 2. Check and Activate Virtual Environment (if present)
if exist "venv\Scripts\activate.bat" (
    echo [Environment] Activating local virtual environment (venv)...
    call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    echo [Environment] Activating local virtual environment (.venv)...
    call ".venv\Scripts\activate.bat"
)

REM 3. Verify Required Python Dependencies
echo [Dependencies] Checking installed packages...
python -c "import fastapi, uvicorn, pydantic, PIL, numpy, multipart" >nul 2>&1
if %errorlevel% neq 0 (
    echo [Dependencies] Installing missing Python requirements from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install Python dependencies. Please run 'pip install -r requirements.txt' manually.
        pause
        exit /b 1
    )
) else (
    echo [Dependencies] All core libraries (FastAPI, Pillow, NumPy, Multipart) verified!
)

REM 4. Check if Backend is Already Running on Port 8000
netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% equ 0 (
    echo [Notice] A backend service is already actively running on port 8000.
    echo Skipping duplicate server launch.
) else (
    echo [Backend] Starting FastAPI Microclimate & AI Engine on http://0.0.0.0:8000...
    start "FloraGuard FastAPI Backend" /min python -m uvicorn backend:app --host 0.0.0.0 --port 8000
    timeout /t 3 /nobreak >nul
)

REM 5. Open Web Dashboard in Default Browser
echo [Dashboard] Opening integrated FloraGuard IoT Dashboard in your browser...
start http://127.0.0.1:8000

echo.
echo =========================================================================
echo   FloraGuard IoT System is Live!
echo   - Web Dashboard : http://127.0.0.1:8000
echo   - Interactive API Docs : http://127.0.0.1:8000/docs
echo   - Telemetry Stream : ws://127.0.0.1:8000/ws/telemetry
echo =========================================================================
echo Press any key to close this launcher window (backend continues running).
pause >nul
