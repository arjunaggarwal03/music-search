@echo off
echo Starting Music Similarity Search Setup...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Check if virtualenv is installed
pip show virtualenv >nul 2>&1
if errorlevel 1 (
    echo Installing virtualenv...
    pip install virtualenv
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Check if .env file exists
if not exist .env (
    echo No .env file found. Creating from .env.example...
    copy .env.example .env
    echo Please update the .env file with your Pinecone API key and other settings
    exit /b 1
)

REM Create media directory if it doesn't exist
if not exist media (
    echo Creating media directory...
    mkdir media
)

REM Initialize Django
echo Initializing Django...
python manage.py migrate

REM Initialize Pinecone
echo Initializing Pinecone...
python manage.py init_pinecone

REM Run server
echo Starting Django server...
python manage.py runserver 0.0.0.0:8000 