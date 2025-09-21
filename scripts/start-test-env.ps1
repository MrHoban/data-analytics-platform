# Data Analytics Platform - Test Environment Startup Script
# This script starts all services for local development and testing

Write-Host "🚀 Starting Data Analytics Platform Test Environment" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Function to start a service in a new window
function Start-ServiceWindow {
    param(
        [string]$Title,
        [string]$Command,
        [string]$WorkingDirectory
    )
    
    Write-Host "Starting $Title..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WorkingDirectory'; $Command" -WindowStyle Normal
    Start-Sleep -Seconds 2
}

# Check prerequisites
Write-Host "`n📋 Checking Prerequisites..." -ForegroundColor Cyan

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js" -ForegroundColor Red
    exit 1
}

# Check if .NET is installed
try {
    $dotnetVersion = dotnet --version
    Write-Host "✅ .NET: $dotnetVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ .NET not found. Please install .NET 8.0" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

Write-Host "`n🔧 Starting Services..." -ForegroundColor Cyan

# Get the project root directory
$projectRoot = Split-Path -Parent $PSScriptRoot

# Start C# Backend API (Port 5000)
if (Test-Port 5000) {
    Write-Host "⚠️  Port 5000 is already in use" -ForegroundColor Yellow
} else {
    Start-ServiceWindow "C# Backend API" "dotnet run --project DataAnalytics.API" "$projectRoot\backend"
}

# Start Python Analytics Engine (Port 8000)
if (Test-Port 8000) {
    Write-Host "⚠️  Port 8000 is already in use" -ForegroundColor Yellow
} else {
    Start-ServiceWindow "Python Analytics Engine" "python main.py" "$projectRoot\analytics-engine"
}

# Start React Frontend (Port 3001 or next available)
$frontendPort = 3001
while (Test-Port $frontendPort) {
    $frontendPort++
}

Start-ServiceWindow "React Frontend" "npm start" "$projectRoot\frontend"

Write-Host "`n🌐 Service URLs:" -ForegroundColor Cyan
Write-Host "Frontend:          http://localhost:$frontendPort" -ForegroundColor White
Write-Host "C# Backend API:    http://localhost:5000" -ForegroundColor White
Write-Host "Python Analytics:  http://localhost:8000" -ForegroundColor White
Write-Host "API Documentation: http://localhost:5000/swagger" -ForegroundColor White
Write-Host "Python API Docs:   http://localhost:8000/docs" -ForegroundColor White

Write-Host "`n💡 Tips:" -ForegroundColor Cyan
Write-Host "- The frontend includes light/dark mode toggle in the top navigation" -ForegroundColor White
Write-Host "- Use Ctrl+C in each window to stop services" -ForegroundColor White
Write-Host "- Check the browser console for any errors" -ForegroundColor White
Write-Host "- Services may take a few moments to fully start" -ForegroundColor White

Write-Host "`n✨ Test Environment Ready!" -ForegroundColor Green
Write-Host "Press any key to exit this script (services will continue running)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
