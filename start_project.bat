@echo off
echo ===============================
echo   OS AI PROJECT STARTING...
echo ===============================

echo.
echo Activating Virtual Environment...
call .venv\Scripts\activate

echo.
echo Starting API Server...
start cmd /k python api_server.py

timeout /t 3

echo.
echo Starting Ngrok Tunnel...
start cmd /k ngrok http 5000

timeout /t 5

echo.
echo Starting Agent...
start cmd /k python agent.py

timeout /t 3

echo.
echo Starting Dashboard...
start cmd /k streamlit run dashboard.py

echo.
echo ===============================
echo   ALL SERVICES STARTED
echo ===============================

pause
