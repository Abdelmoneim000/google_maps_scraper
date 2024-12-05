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

REM Start the Flask app and open the browser
echo Starting the Flask application...
start "" cmd /c "python app.py"
timeout /t 5 >nul
start http://localhost:5000

pause
