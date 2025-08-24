#!/bin/bash

# FactorESourcing Backend Startup Script

echo "Starting FactorESourcing Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY environment variable is not set"
    echo "Please set it with: export OPENAI_API_KEY='your-api-key'"
fi

# Start the server
echo "Starting FastAPI server..."

# Set default port if not provided by Render
PORT=${PORT:-8000}
echo "Using port: $PORT"

# Start uvicorn
uvicorn main:app --host 0.0.0.0 --port $PORT 