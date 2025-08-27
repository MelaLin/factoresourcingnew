#!/bin/bash

echo "🛑 Stopping FactorESourcing Application..."
echo "========================================="

# Kill backend processes
echo "🔧 Stopping backend server..."
pkill -f "python3 main.py" 2>/dev/null

# Kill frontend processes
echo "🎨 Stopping frontend server..."
pkill -f "npm run dev" 2>/dev/null
pkill -f "vite" 2>/dev/null

# Kill any remaining processes on our ports
echo "🧹 Cleaning up ports..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

echo "✅ All servers stopped!"
echo "🌐 Ports 8000 and 5173 are now free"
