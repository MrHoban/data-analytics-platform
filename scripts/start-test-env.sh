#!/bin/bash

# Data Analytics Platform - Test Environment Startup Script
# This script starts all services for local development and testing

echo "🚀 Starting Data Analytics Platform Test Environment"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "\n📋 ${CYAN}Checking Prerequisites...${NC}"

# Check if Node.js is installed
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "✅ ${GREEN}Node.js: $NODE_VERSION${NC}"
else
    echo -e "❌ ${RED}Node.js not found. Please install Node.js${NC}"
    exit 1
fi

# Check if .NET is installed
if command_exists dotnet; then
    DOTNET_VERSION=$(dotnet --version)
    echo -e "✅ ${GREEN}.NET: $DOTNET_VERSION${NC}"
else
    echo -e "❌ ${RED}.NET not found. Please install .NET 8.0${NC}"
    exit 1
fi

# Check if Python is installed
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "✅ ${GREEN}Python: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_VERSION=$(python --version)
    echo -e "✅ ${GREEN}Python: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python"
else
    echo -e "❌ ${RED}Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

echo -e "\n🔧 ${CYAN}Starting Services...${NC}"

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Start C# Backend API (Port 5000)
if check_port 5000; then
    echo -e "⚠️  ${YELLOW}Port 5000 is already in use${NC}"
else
    echo -e "${YELLOW}Starting C# Backend API...${NC}"
    cd "$PROJECT_ROOT/backend"
    gnome-terminal --title="C# Backend API" -- bash -c "dotnet run --project DataAnalytics.API; exec bash" 2>/dev/null || \
    xterm -title "C# Backend API" -e "cd '$PROJECT_ROOT/backend' && dotnet run --project DataAnalytics.API; bash" 2>/dev/null || \
    echo -e "${YELLOW}Please manually start: cd backend && dotnet run --project DataAnalytics.API${NC}"
fi

# Start Python Analytics Engine (Port 8000)
if check_port 8000; then
    echo -e "⚠️  ${YELLOW}Port 8000 is already in use${NC}"
else
    echo -e "${YELLOW}Starting Python Analytics Engine...${NC}"
    cd "$PROJECT_ROOT/analytics-engine"
    gnome-terminal --title="Python Analytics Engine" -- bash -c "$PYTHON_CMD main.py; exec bash" 2>/dev/null || \
    xterm -title "Python Analytics Engine" -e "cd '$PROJECT_ROOT/analytics-engine' && $PYTHON_CMD main.py; bash" 2>/dev/null || \
    echo -e "${YELLOW}Please manually start: cd analytics-engine && $PYTHON_CMD main.py${NC}"
fi

# Start React Frontend
echo -e "${YELLOW}Starting React Frontend...${NC}"
cd "$PROJECT_ROOT/frontend"
gnome-terminal --title="React Frontend" -- bash -c "npm start; exec bash" 2>/dev/null || \
xterm -title "React Frontend" -e "cd '$PROJECT_ROOT/frontend' && npm start; bash" 2>/dev/null || \
echo -e "${YELLOW}Please manually start: cd frontend && npm start${NC}"

sleep 3

echo -e "\n🌐 ${CYAN}Service URLs:${NC}"
echo -e "${WHITE}Frontend:          http://localhost:3000 (or next available port)${NC}"
echo -e "${WHITE}C# Backend API:    http://localhost:5000${NC}"
echo -e "${WHITE}Python Analytics:  http://localhost:8000${NC}"
echo -e "${WHITE}API Documentation: http://localhost:5000/swagger${NC}"
echo -e "${WHITE}Python API Docs:   http://localhost:8000/docs${NC}"

echo -e "\n💡 ${CYAN}Tips:${NC}"
echo -e "${WHITE}- The frontend includes light/dark mode toggle in the top navigation${NC}"
echo -e "${WHITE}- Use Ctrl+C in each terminal to stop services${NC}"
echo -e "${WHITE}- Check the browser console for any errors${NC}"
echo -e "${WHITE}- Services may take a few moments to fully start${NC}"

echo -e "\n✨ ${GREEN}Test Environment Setup Complete!${NC}"
echo -e "${WHITE}Services are starting in separate terminals...${NC}"
