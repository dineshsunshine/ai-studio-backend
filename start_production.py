"""
Production startup script
Removes ngrok dependencies and uses environment-provided PORT
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the FastAPI app
from api_with_db_and_ngrok import app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (Render, Railway, etc. set this)
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting AI Studio Backend on port {port}")
    print(f"📊 Database: {os.getenv('DATABASE_URL', 'SQLite (development)')[:50]}...")
    print(f"🔐 Environment: {'Production' if 'DATABASE_URL' in os.environ else 'Development'}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )


