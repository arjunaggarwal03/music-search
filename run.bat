@echo off
echo Starting Music Similarity Search Application...

REM Check if Docker is running
docker info > nul 2>&1
if errorlevel 1 (
    echo Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Check and create .env file
if not exist "backend/.env" (
    echo No .env file found in backend directory. Creating from .env.example...
    if exist "backend/.env.example" (
        copy "backend\.env.example" "backend\.env"
        echo Please update backend/.env file with your Pinecone API key and other settings
        exit /b 1
    ) else (
        echo .env.example not found in backend directory
        exit /b 1
    )
)

REM Build and start the containers
echo Building and starting containers...
docker-compose -f docker/docker-compose.yml up --build

REM Wait for user input before closing
pause 