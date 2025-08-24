#!/bin/bash

echo "🔧 Setting up FactorESourcing development environment..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "📦 Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Backend setup complete"

# Setup frontend
echo "⚛️  Setting up React frontend..."
cd ../frontend

# Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete"

# Return to root
cd ..

echo ""
echo "🎉 Setup complete! You can now run:"
echo "  ./dev.sh          # Start development environment"
echo "  npm run dev       # Start frontend only"
echo "  npm run dev:backend # Start backend only"
echo ""
echo "📱 Frontend will be available at: http://localhost:5173"
echo "🔧 Backend will be available at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
