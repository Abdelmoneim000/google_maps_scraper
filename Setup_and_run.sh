#!/bin/bash

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "Python is not installed. Please install Python before running this script."
    exit 1
fi

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install required packages globally
echo "Installing necessary Python packages..."
pip3 install flask flask-socketio selenium undetected-chromedriver pandas

# Start the Flask app in the background
echo "Starting the Flask application..."
python3 app.py &
sleep 5

# Open the default browser at the app port
xdg-open http://localhost:5000 || open http://localhost:5000
