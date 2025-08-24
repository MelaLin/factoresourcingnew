#!/bin/bash

echo "🔧 Setting up Python environment for Render deployment..."

# Upgrade pip, setuptools, and wheel first
python -m pip install --upgrade pip setuptools wheel

# Install build dependencies first
pip install setuptools==69.5.1 wheel==0.42.0

# Now install the main requirements
pip install -r requirements.txt

echo "✅ Build completed successfully!"
