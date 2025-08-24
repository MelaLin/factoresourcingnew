#!/bin/bash

# FactorESourcing Setup Script

echo "🔧 Setting up FactorESourcing..."

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check Node.js or Bun installation
if ! command -v node &> /dev/null && ! command -v bun &> /dev/null; then
    echo "❌ Node.js or Bun is required but not installed"
    echo "Please install Node.js 16+ from https://nodejs.org or Bun from https://bun.sh"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup backend
echo "🔧 Setting up backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Setup frontend
echo "🎨 Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    if command -v bun &> /dev/null; then
        bun install
    else
        npm install
    fi
fi
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start development:"
echo "  ./dev.sh                    # Run both services"
echo ""
echo "Or run services separately:"
echo "  cd backend && ./start.sh    # Backend only"
echo "  cd frontend && ./start.sh   # Frontend only"
echo ""
echo "Don't forget to set your OpenAI API key:"
echo "  export OPENAI_API_KEY='your-api-key'" 