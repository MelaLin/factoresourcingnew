#!/bin/bash

echo "🚀 Starting FactorESourcing Application..."
echo "=========================================="

# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend server
echo "🔧 Starting backend server on port 8000..."
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/api/history > /dev/null 2>&1; then
    echo "✅ Backend server started successfully!"
else
    echo "❌ Backend server failed to start"
    exit 1
fi

# Start frontend server
echo "🎨 Starting frontend server on port 5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

# Check if frontend is running
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend server started successfully!"
else
    echo "❌ Frontend server failed to start"
    exit 1
fi

echo ""
echo "🎉 Both servers are now running!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user to stop
wait
