#!/usr/bin/env python3
"""
Reverse Proxy Server
Routes different URL paths to different local ports

Usage:
    python reverse_proxy.py

Then run ONE ngrok tunnel:
    ngrok http 8888

Access your services:
    https://your-ngrok-url.ngrok.io/backend  → localhost:8000 (AI Studio Backend)
    https://your-ngrok-url.ngrok.io/app      → localhost:8080 (Your other app)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import sys
import requests

PROXY_PORT = 8888

# Route configuration: path prefix → target port
ROUTES = {
    '/AIStudio': 8000,      # AI Studio Backend
    '/SampleAppGpt': 8080,  # Your SampleAppGpt application
}

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve frontend at /AIStudio root
        if self.path == '/AIStudio' or self.path == '/AIStudio/':
            self.serve_frontend()
            return
        # Show help page at root and /help
        if self.path == '/' or self.path == '/help':
            self.send_help_page()
            return
        self.proxy_request(add_ngrok_bypass=True)
    
    def do_POST(self):
        self.proxy_request(add_ngrok_bypass=True)
    
    def do_PUT(self):
        self.proxy_request(add_ngrok_bypass=True)
    
    def do_DELETE(self):
        self.proxy_request(add_ngrok_bypass=True)
    
    def do_PATCH(self):
        self.proxy_request(add_ngrok_bypass=True)
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Max-Age', '3600')
        self.send_header('Content-Length', '0')
        self.end_headers()
        print(f"✅ OPTIONS {self.path} → CORS preflight handled")
    
    def do_HEAD(self):
        # Handle HEAD requests (used by browsers to check if images exist)
        self.proxy_request(add_ngrok_bypass=True)
    
    def serve_frontend(self):
        """Serve the frontend HTML file"""
        try:
            frontend_path = '/Users/dgolani/Documents/AI_Studio/backend/frontend/index.html'
            with open(frontend_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
            print(f"✅ Served frontend to {self.client_address[0]}")
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_msg = f'<h1>Error Loading Frontend</h1><p>{str(e)}</p>'.encode()
            self.wfile.write(error_msg)
            print(f"❌ Error serving frontend: {e}")
    
    def proxy_request(self, add_ngrok_bypass=False):
        # Find matching route
        target_port = None
        path_prefix = None
        
        for prefix, port in ROUTES.items():
            if self.path.startswith(prefix):
                target_port = port
                path_prefix = prefix
                break
        
        if not target_port:
            # No matching route - show 404
            self.send_error(404, f"Route not found: {self.path}")
            return
        
        # Remove prefix from path (but preserve query string)
        path_with_query = self.path[len(path_prefix):]
        if not path_with_query or path_with_query[0] != '/':
            path_with_query = '/' + path_with_query if path_with_query else '/'
        
        new_path = path_with_query
        
        # Build target URL
        target_url = f"http://localhost:{target_port}{new_path}"
        
        try:
            # Read request body if present (with progress logging for large bodies)
            content_length = self.headers.get('Content-Length')
            body = None
            if content_length:
                content_length_int = int(content_length)
                print(f"📥 Reading request body: {content_length_int / 1024 / 1024:.2f} MB for {self.command} {self.path}")
                
                # Read entire body at once (requests library will handle it properly)
                body = self.rfile.read(content_length_int)
                print(f"✅ Finished reading {len(body) / 1024 / 1024:.2f} MB")
            
            # Prepare headers (excluding problematic ones)
            headers = {}
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection', 'content-length']:
                    headers[header] = value
            
            # Add ngrok bypass header if requested
            if add_ngrok_bypass:
                headers['ngrok-skip-browser-warning'] = 'true'
            
            # Make request using requests library (handles large bodies better than urllib)
            # Set a long timeout for large uploads (10 minutes)
            print(f"🔄 Proxying to {target_url}")
            response = requests.request(
                method=self.command,
                url=target_url,
                headers=headers,
                data=body,
                timeout=600,  # 10 minute timeout
                stream=True,   # Stream the response
                allow_redirects=False
            )
            
            # Send response status
            self.send_response(response.status_code)
            
            # Copy response headers
            for header, value in response.headers.items():
                if header.lower() not in ['connection', 'transfer-encoding', 'content-encoding']:
                    self.send_header(header, value)
            
            # Add CORS headers
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            
            self.end_headers()
            
            # Stream response body
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    self.wfile.write(chunk)
            
            print(f"✅ Successfully proxied {self.command} {self.path} -> {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Requests error for {self.command} {self.path}: {type(e).__name__}: {str(e)}")
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_msg = f'{{"error": "Proxy error: {str(e)}"}}'.encode()
            self.wfile.write(error_msg)
        
        except Exception as e:
            print(f"❌ Proxy error for {self.command} {self.path}: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_msg = f'{{"error": "Proxy error: {str(e)}"}}'.encode()
            self.wfile.write(error_msg)
    
    def send_help_page(self):
        """Send help page showing available routes"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reverse Proxy - Route Map</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .container {{
                    background: white;
                    color: #333;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }}
                h1 {{
                    color: #667eea;
                }}
                .route {{
                    background: #f5f5f5;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                    border-left: 4px solid #667eea;
                }}
                .route strong {{
                    color: #667eea;
                }}
                code {{
                    background: #f0f0f0;
                    padding: 2px 6px;
                    border-radius: 3px;
                    color: #c7254e;
                }}
                .status {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 15px;
                    font-size: 0.9em;
                    margin-left: 10px;
                }}
                .status.ok {{
                    background: #4caf50;
                    color: white;
                }}
                .status.error {{
                    background: #f44336;
                    color: white;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Reverse Proxy - Route Map</h1>
                <p>Welcome! This reverse proxy routes requests to different backend services.</p>
                
                <h2>Available Routes:</h2>
                
                <div class="route">
                    <strong>/AIStudio</strong> → AI Studio Frontend & Backend (Port 8000)
                    <br>
                    <small>Frontend: <code>/AIStudio/</code></small>
                    <br>
                    <small>API: <code>/AIStudio/health</code>, <code>/AIStudio/tasks</code></small>
                </div>
                
                <div class="route">
                    <strong>/SampleAppGpt</strong> → Port 8080 (Your SampleAppGpt Application)
                    <br>
                    <small>Example: <code>/SampleAppGpt/</code>, <code>/SampleAppGpt/api/...</code></small>
                </div>
                
                <h2>Quick Test Links:</h2>
                <ul>
                    <li><a href="/AIStudio/">🎨 AI Studio Frontend</a></li>
                    <li><a href="/AIStudio/health">AI Studio Health Check</a></li>
                    <li><a href="/AIStudio/docs">AI Studio API Docs</a></li>
                    <li><a href="/AIStudio/tasks">AI Studio Tasks</a></li>
                    <li><a href="/SampleAppGpt/">SampleAppGpt Application</a></li>
                </ul>
                
                <h2>Usage with Ngrok:</h2>
                <ol>
                    <li>Start this proxy: <code>python reverse_proxy.py</code></li>
                    <li>Start your services on ports 8000 and 8080</li>
                    <li>Run ONE ngrok: <code>ngrok http {PROXY_PORT}</code></li>
                    <li>Access via ngrok URL with path prefixes!</li>
                </ol>
                
                <hr>
                <p><small>Proxy running on port {PROXY_PORT}</small></p>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[PROXY] {self.address_string()} - {format % args}")


def main():
    print("\n" + "="*60)
    print("🔀 Reverse Proxy Server")
    print("="*60)
    print(f"\n📍 Proxy running on: http://localhost:{PROXY_PORT}")
    print("\n📋 Route Configuration:")
    for path, port in ROUTES.items():
        print(f"   {path:20} → localhost:{port}")
    
    print("\n" + "="*60)
    print("🚀 Setup Instructions:")
    print("="*60)
    print("\n1. Make sure your services are running:")
    print(f"   - Port 8000: AI Studio Backend")
    print(f"   - Port 8080: Your other application")
    print("\n2. From YOUR terminal, run:")
    print(f"   ngrok http {PROXY_PORT}")
    print("\n3. Access your services via ngrok URL:")
    print(f"   https://your-url.ngrok.io/AIStudio      → AI Studio Backend")
    print(f"   https://your-url.ngrok.io/SampleAppGpt  → SampleAppGpt")
    print("\n" + "="*60)
    print("✨ Press Ctrl+C to stop\n")
    
    server = HTTPServer(('', PROXY_PORT), ProxyHandler)
    
    # Set socket timeout to 10 minutes for large uploads (like video generation)
    # This prevents "Broken pipe" errors when reading large request bodies
    server.socket.settimeout(600)
    print(f"⏱️  Socket timeout set to: 600 seconds (10 minutes)")
    print(f"📦 Max request size: Unlimited (chunked reading for >1MB)\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down proxy server...")
        server.shutdown()


if __name__ == '__main__':
    main()

