#!/bin/bash

# FactorESourcing Frontend Build Script

echo "Building FactorESourcing Frontend for production..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    if command -v bun &> /dev/null; then
        bun install
    else
        npm install
    fi
fi

# Build the production version
echo "Building production version..."
if command -v bun &> /dev/null; then
    bun run build
else
    npm run build
fi

echo "Frontend build completed! Check the 'dist' folder."
