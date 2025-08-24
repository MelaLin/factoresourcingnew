#!/bin/bash

# FactorESourcing Development Script
# Runs both frontend and backend services

echo "🚀 Starting FactorESourcing Development Environment"

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if required tools are installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command -v node &> /dev/null && ! command -v bun &> /dev/null; then
    echo "❌ Node.js or Bun is required but not installed"
    exit 1
fi

# Start backend
echo "🔧 Starting backend..."
cd backend
./start.sh &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
./start.sh &
FRONTEND_PID=$!
cd ..

echo "✅ Services started!"
echo "📊 Backend: http://localhost:8000"
echo "🎨 Frontend: http://localhost:5173"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for background processes
wait 