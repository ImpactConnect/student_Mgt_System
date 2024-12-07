@echo off
echo Building IMPACTTECH CODING ACADEMY Student Management System

REM Check Python installation
python --version
if errorlevel 1 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create virtual environment
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)

call venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

REM Build executable with detailed logging
pyinstaller --clean --onefile --windowed --add-data "database;database" --add-data "pages;pages" --name "ImpactTech_StudentMgt" main.py
if errorlevel 1 (
    echo Build failed
    pause
    exit /b 1
)

echo Build complete. Executable is in the 'dist' folder.
dir dist
pause 