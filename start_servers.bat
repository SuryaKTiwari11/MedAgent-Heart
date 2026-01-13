@echo off
REM MedAgent-Heart Startup Script for Windows
REM This script starts both the backend and frontend servers

echo ===============================================
echo    MedAgent-Heart - Server Startup
echo ===============================================
echo.

REM Check if conda environment exists
echo Checking conda environment...
conda info --envs | findstr "medagent" >nul
if %errorlevel% neq 0 (
    echo ERROR: 'medagent' conda environment not found!
    echo Please run: conda create -n medagent python=3.11 -y
    pause
    exit /b 1
)

echo Environment found!
echo.

REM Check if .env file exists
if not exist "backend\.env" (
    echo WARNING: backend\.env file not found!
    echo Please create backend\.env with your API keys
    echo See QUICKSTART.md for details
    pause
    exit /b 1
)

echo Starting servers...
echo.

REM Start backend in new window
echo [1/2] Starting Backend Server (port 8000)...
start "MedAgent-Heart Backend" cmd /k "conda activate medagent && cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in new window  
echo [2/2] Starting Frontend Server (port 8501)...
start "MedAgent-Heart Frontend" cmd /k "conda activate medagent && streamlit run frontend\app.py"

echo.
echo ===============================================
echo    Servers Starting!
echo ===============================================
echo.
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:8501
echo API Docs will be available at: http://localhost:8000/docs
echo.
echo Check the new windows for server status.
echo Press any key to exit this window...
pause >nul
