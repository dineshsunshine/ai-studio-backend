#!/usr/bin/env python3
"""
Script to start the FastAPI server with ngrok tunnel for public access.
This allows your local backend to be accessible via a public URL for Google AI Studio integration.
"""

import os
import sys
import time
import subprocess
from pyngrok import ngrok, conf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Get ngrok auth token from environment
    ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
    ngrok_domain = os.getenv("NGROK_DOMAIN", "")
    
    if not ngrok_token:
        print("❌ Error: NGROK_AUTH_TOKEN not found in .env file")
        print("Please sign up at https://ngrok.com and add your auth token to .env")
        sys.exit(1)
    
    # Set ngrok auth token
    conf.get_default().auth_token = ngrok_token
    
    print("🚀 Starting AI Studio Backend with ngrok...")
    print("=" * 60)
    
    # Start uvicorn server in background
    print("📦 Starting FastAPI server...")
    server_process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    # Start ngrok tunnel
    try:
        print("🌐 Creating ngrok tunnel...")
        
        # Create tunnel with custom domain if provided
        if ngrok_domain:
            public_url = ngrok.connect(8000, domain=ngrok_domain)
        else:
            public_url = ngrok.connect(8000)
        
        print("=" * 60)
        print(f"✅ Backend is running!")
        print(f"📍 Local URL:  http://localhost:8000")
        print(f"🌍 Public URL: {public_url}")
        print(f"📚 API Docs:   {public_url}/api/v1/docs")
        print("=" * 60)
        print("\n💡 Copy the Public URL above and use it in your Google AI Studio frontend")
        print("⚠️  Press Ctrl+C to stop the server and close the tunnel\n")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down...")
            
    except Exception as e:
        print(f"❌ Error creating ngrok tunnel: {e}")
        print("Make sure your NGROK_AUTH_TOKEN is valid")
    finally:
        # Clean up
        ngrok.kill()
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped successfully")


if __name__ == "__main__":
    main()

