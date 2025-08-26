#!/usr/bin/env python3
"""
Startup script for Render deployment
Handles environment variables and proper initialization
"""

import os
import sys
from pathlib import Path

def main():
    """Main startup function for Render"""
    print("🚀 Starting FactorESourcing API for Render deployment...")
    
    # Log environment information
    print(f"🌐 Environment variables:")
    print(f"   PORT: {os.environ.get('PORT', 'Not set')}")
    print(f"   PYTHON_VERSION: {os.environ.get('PYTHON_VERSION', 'Not set')}")
    print(f"   RENDER: {os.environ.get('RENDER', 'Not set')}")
    print(f"   Working directory: {os.getcwd()}")
    
    # Check if frontend assets exist
    frontend_path = Path("frontend")
    if frontend_path.exists():
        print(f"✅ Frontend directory found: {frontend_path}")
        if (frontend_path / "index.html").exists():
            print(f"✅ Frontend index.html found")
        else:
            print(f"⚠️  Frontend index.html not found")
            print(f"   Frontend contents: {list(frontend_path.iterdir())}")
    else:
        print(f"❌ Frontend directory not found")
        print(f"   Available files: {list(Path('.').iterdir())}")
    
    # Check if data directory exists
    data_path = Path("data")
    if data_path.exists():
        print(f"✅ Data directory found: {data_path}")
        print(f"   Data contents: {list(data_path.iterdir())}")
    else:
        print(f"📁 Creating data directory...")
        data_path.mkdir(exist_ok=True)
        print(f"✅ Data directory created")
    
    # Import and start the app
    try:
        from main import app
        print("✅ Main application imported successfully")
        
        import uvicorn
        
        # Get port from environment or use default
        port = int(os.environ.get("PORT", 8000))
        print(f"🌐 Starting server on port {port}")
        
        # Start the server
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
