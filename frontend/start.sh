#!/bin/bash

# FactorESourcing Frontend Startup Script

echo "Starting FactorESourcing Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    if command -v bun &> /dev/null; then
        bun install
    else
        npm install
    fi
fi

# Start the development server
echo "Starting development server..."
if command -v bun &> /dev/null; then
    bun dev
else
    npm run dev
fi 