REM install.bat
@echo off
echo Installing WhatsApp Sender Pro...

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Create necessary directories
mkdir config
mkdir logs
mkdir database\migrations

echo Installation completed!
echo.
echo To run the application:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run: python main.py
pause