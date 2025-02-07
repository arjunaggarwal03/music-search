#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Docker is not running. Please start Docker and try again.${NC}"
        exit 1
    fi
}

# Function to check and create .env file
check_env() {
    if [ ! -f "backend/.env" ]; then
        echo -e "${RED}No .env file found in backend directory. Creating from .env.example...${NC}"
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example backend/.env
            echo -e "${RED}Please update backend/.env file with your Pinecone API key and other settings${NC}"
            exit 1
        else
            echo -e "${RED}.env.example not found in backend directory${NC}"
            exit 1
        fi
    fi
}

# Function to stop all containers
cleanup() {
    echo -e "${GREEN}Stopping containers...${NC}"
    docker-compose -f docker/docker-compose.yml down
}

# Main script
echo -e "${GREEN}Starting Music Similarity Search Application...${NC}"

# Check if Docker is installed and running
check_docker

# Check and create .env files
check_env

# Set up trap for cleanup on script exit
trap cleanup EXIT

# Build and start the containers
echo -e "${GREEN}Building and starting containers...${NC}"
docker-compose -f docker/docker-compose.yml up --build

# Keep the script running until Ctrl+C
wait $! 