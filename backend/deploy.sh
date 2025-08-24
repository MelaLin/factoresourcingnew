#!/bin/bash

# FactorESourcing Unified Deployment Script
# This script builds the frontend and prepares the backend for Render deployment

echo "🚀 Starting FactorESourcing deployment preparation..."

# Check if we're in the project root
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Build the frontend
echo "📦 Building frontend..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    if command -v bun &> /dev/null; then
        bun install
    else
        npm install
    fi
fi

# Build production version
echo "Building production version..."
if command -v bun &> /dev/null; then
    bun run build
else
    npm run build
fi

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Error: Frontend build failed. No 'dist' folder found."
    exit 1
fi

echo "✅ Frontend built successfully!"

# Go back to project root
cd ..

# Copy frontend build to backend directory for unified deployment
echo "📁 Preparing unified deployment structure..."
if [ -d "backend/frontend" ]; then
    rm -rf backend/frontend
fi

# Create the structure Render expects
mkdir -p backend/frontend
cp -r frontend/dist/* backend/frontend/

echo "✅ Deployment structure prepared!"
echo ""
echo "🎯 Next steps for Render deployment:"
echo "1. Set Root Directory to: backend"
echo "2. Set Build Command to: pip install -r requirements.txt"
echo "3. Set Start Command to: uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo ""
echo "📁 Your backend directory now contains:"
echo "   - main.py (updated with frontend serving)"
echo "   - frontend/ (copied from frontend/dist)"
echo "   - All other backend files"
echo ""
echo "🚀 Ready for Render deployment!"
