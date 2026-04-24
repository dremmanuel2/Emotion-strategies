@echo off
chcp 65001 >nul
echo ========================================
echo Emotion Company Agent - Startup
echo ========================================
echo.

REM Activate virtual environment
echo Activating virtual environment...
call D:\anaconda3\envs\py313\activate.bat

REM Enter project directory
cd /d "%~dp0"

REM Create logs directory
if not exist "logs" mkdir logs

echo.
echo Starting services...
echo.
echo [1] Starting Backend API...
start cmd /k "call D:\anaconda3\envs\py313\activate.bat && cd /d '%~dp0' && python -m uvicorn main:app --host 0.0.0.0 --port 8501"
timeout /t 5 /nobreak >nul
echo [2] Starting Web UI...
start cmd /k "call D:\anaconda3\envs\py313\activate.bat && cd /d '%~dp0' && python -m streamlit run web_app.py --server.address=0.0.0.0 --server.port=8502"
echo.
echo ========================================
echo Services Started!
echo ========================================
echo - Backend API: http://100.100.30.150/docs
echo - Web UI: http://100.100.30.150:8502
echo.
echo Press any key to close this window...
pause >nul