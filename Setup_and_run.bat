@echo off
REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python before running this script.
    exit /b
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install required packages globally
echo Installing necessary Python packages...
pip install flask flask-socketio selenium undetected-chromedriver pandas

REM Start the Flask app in a separate terminal and capture the port
echo Starting the Flask application...
start "" cmd /c "python app.py > output.log 2>&1"

REM Wait for the app to start
echo Waiting for the Flask app to start...
timeout /t 5 >nul

REM Search the output log for the active port
set "port="
for /f "tokens=*" %%L in ('findstr /R /C:"Running on http://[^ ]*" output.log') do (
    for /f "tokens=3 delims=:" %%P in ("%%L") do set port=%%P
)

REM Remove any trailing slashes or characters from port
for /f "delims=/" %%P in ("%port%") do set port=%%P

IF "%port%"=="" (
    echo Failed to detect the app port. Opening the default port 5000...
    set port=5000
)

REM Open the Flask app in the default browser
echo Opening the Flask application on port %port%...
start http://localhost:%port%

REM Pause to keep the window open
pause
