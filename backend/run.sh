#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Music Similarity Search Setup...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate || source venv/Scripts/activate

# Install requirements
echo -e "${GREEN}Installing requirements...${NC}"
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}Please update the .env file with your Pinecone API key and other settings${NC}"
    exit 1
fi

# Create media directory if it doesn't exist
if [ ! -d "media" ]; then
    echo -e "${GREEN}Creating media directory...${NC}"
    mkdir media
fi

# Initialize Django
echo -e "${GREEN}Initializing Django...${NC}"
python manage.py migrate

# Initialize Pinecone
echo -e "${GREEN}Initializing Pinecone...${NC}"
python manage.py init_pinecone

# Run server
echo -e "${GREEN}Starting Django server...${NC}"
python manage.py runserver 0.0.0.0:8000 