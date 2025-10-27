#!/usr/bin/env python3
"""
Simple HTTP server to serve the test frontend
"""
import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("\n" + "="*60)
        print("🌐 Frontend Server Started!")
        print("="*60)
        print(f"📍 Local URL: http://localhost:{PORT}")
        print(f"📁 Serving: {DIRECTORY}")
        print("="*60)
        print("✨ Press Ctrl+C to stop\n")
        httpd.serve_forever()


