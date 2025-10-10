"""
AI Studio Backend with Database + Ngrok Public URL
- SQLite database for persistence
- Full CRUD operations
- Ngrok tunnel for public access
"""

import os
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
from pyngrok import ngrok, conf

# ==================== Database Setup ====================

# Import database setup and models from app
from app.core.database import engine, Base, get_db as app_get_db
from app.models import user, access_request, user_settings, default_settings_model, model, look, product

# Create all tables
def create_db_tables():
    """Create all database tables"""
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Verify tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"✅ Database tables: {existing_tables}")

# Create tables on startup
create_db_tables()


# Use database dependency from app
get_db = app_get_db


# ==================== FastAPI App ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n" + "="*60)
    print("🚀 AI Studio Backend Starting...")
    print("="*60)
    yield
    # Shutdown
    print("\n" + "="*60)
    print("🛑 Shutting down...")
    print("="*60)


# Determine server URLs based on environment
# If DATABASE_URL exists (production), use Render URL; otherwise use local/ngrok URLs
IS_PRODUCTION = os.getenv("DATABASE_URL") is not None
if IS_PRODUCTION:
    # Production (Render) - only show production URL
    SERVERS_CONFIG = [
        {
            "url": "https://ai-studio-backend-ijkp.onrender.com",
            "description": "Production Server"
        }
    ]
else:
    # Development (Local) - show ngrok and local URLs
    SERVERS_CONFIG = [
        {
            "url": "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio",
            "description": "Development server (via ngrok)"
        },
        {
            "url": "http://localhost:8888/AIStudio",
            "description": "Local via reverse proxy"
        },
        {
            "url": "http://localhost:8000",
            "description": "Local direct"
        }
    ]

app = FastAPI(
    title="AI Studio Backend",
    version="1.0.0",
    description="Backend API with Database + Ngrok Support",
    lifespan=lifespan,
    docs_url=None,  # Disable default docs, we'll create custom ones
    redoc_url=None,  # Disable default redoc
    openapi_url="/openapi.json",
    servers=SERVERS_CONFIG
)

# Mount assets directory - Must happen BEFORE adding middleware
# We mount /assets to the directory containing images/, so:
# URL: /assets/images/models/file.jpg → File: assets/images/models/file.jpg
ASSETS_BASE_DIR = os.path.join(os.path.dirname(__file__), "assets")
ASSETS_IMAGES_DIR = os.path.join(ASSETS_BASE_DIR, "images")

os.makedirs(os.path.join(ASSETS_IMAGES_DIR, "models"), exist_ok=True)
os.makedirs(os.path.join(ASSETS_IMAGES_DIR, "generated"), exist_ok=True)
os.makedirs(os.path.join(ASSETS_IMAGES_DIR, "uploads"), exist_ok=True)
os.makedirs(os.path.join(ASSETS_IMAGES_DIR, "looks"), exist_ok=True)
os.makedirs(os.path.join(ASSETS_IMAGES_DIR, "products"), exist_ok=True)

print(f"📁 Assets base directory: {ASSETS_BASE_DIR}")
print(f"📁 Images directory: {ASSETS_IMAGES_DIR}")

# Mount /assets to the assets/ directory (which contains images/)
app.mount("/assets", StaticFiles(directory=ASSETS_BASE_DIR, html=False), name="assets")
print(f"✅ Mounted /assets → {ASSETS_BASE_DIR}")

# Verify files exist
test_files = os.listdir(os.path.join(ASSETS_IMAGES_DIR, "models"))
print(f"📂 Found {len(test_files)} files in images/models/")

# CORS Configuration (AFTER static files mount)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set public URL environment variable for storage service
os.environ["NGROK_PUBLIC_URL"] = "https://zestfully-chalky-nikia.ngrok-free.dev"

# Include ALL API routes (auth, admin, models, looks)
from app.api.v1.api import api_router
from app.core.config import settings

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# ==================== Custom Swagger UI ====================
from fastapi.responses import HTMLResponse

@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def custom_swagger_ui():
    """Custom Swagger UI that works correctly behind reverse proxy"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
        <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
        <title>AI Studio Backend - API Documentation</title>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
        const ui = SwaggerUIBundle({
            url: window.location.pathname.includes('/AIStudio') 
                ? '/AIStudio/openapi.json' 
                : '/openapi.json',
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout",
            // Add header to bypass ngrok browser warning
            requestInterceptor: (req) => {
                req.headers['ngrok-skip-browser-warning'] = 'true';
                return req;
            }
        })
        </script>
    </body>
    </html>
    """

@app.get("/redoc", response_class=HTMLResponse, include_in_schema=False)
async def custom_redoc():
    """Custom ReDoc that works correctly behind reverse proxy"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Studio Backend - API Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body { margin: 0; padding: 0; }
        </style>
    </head>
    <body>
        <redoc spec-url='/openapi.json'></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"></script>
        <script>
        // Override fetch to add ngrok bypass header
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            if (args[1]) {
                args[1].headers = args[1].headers || {};
                args[1].headers['ngrok-skip-browser-warning'] = 'true';
            } else {
                args[1] = { headers: { 'ngrok-skip-browser-warning': 'true' } };
            }
            return originalFetch.apply(this, args);
        };
        </script>
    </body>
    </html>
    """


# ==================== Root Endpoints ====================

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "🎉 Welcome to AI Studio Backend!",
        "status": "running",
        "version": "2.0.0",
        "features": [
            "Google OAuth Authentication",
            "JWT Authorization",
            "User Management",
            "Access Request Approval",
            "Role-Based Access Control",
            "Models & Looks Management"
        ],
        "docs": "/docs",
        "api_endpoints": {
            "authentication": "/api/v1/auth",
            "admin": "/api/v1/admin",
            "models": "/api/v1/models",
            "looks": "/api/v1/looks"
        }
    }


@app.get("/debug/openapi-test")
async def test_openapi_generation():
    """Debug endpoint to test OpenAPI schema generation"""
    try:
        schema = app.openapi()
        return {
            "status": "success",
            "endpoints_count": len(schema.get("paths", {})),
            "schemas_count": len(schema.get("components", {}).get("schemas", {}))
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check with database status"""
    from app.models.user import User
    from app.models.access_request import AccessRequest
    from app.models.model import Model
    from app.models.look import Look
    
    try:
        # Test database connection by counting records
        user_count = db.query(User).count()
        request_count = db.query(AccessRequest).count()
        model_count = db.query(Model).count()
        look_count = db.query(Look).count()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        user_count = request_count = model_count = look_count = 0
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "statistics": {
            "users": user_count,
            "access_requests": request_count,
            "models": model_count,
            "looks": look_count
        },
        "message": "AI Studio Backend is running! ✅"
    }


# ==================== Main Function ====================

def start_server_with_ngrok(ngrok_token: Optional[str] = None):
    """Start server with ngrok tunnel"""
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Starting AI Studio Backend with Database + Ngrok")
    print("="*60)
    
    # Check for ngrok token
    if ngrok_token:
        conf.get_default().auth_token = ngrok_token
        print("✅ Ngrok auth token configured")
    else:
        print("⚠️  No ngrok token provided - using default (may have limits)")
    
    # Start ngrok tunnel
    try:
        public_url = ngrok.connect(8000)
        print("\n" + "="*60)
        print("✅ Backend is LIVE!")
        print("="*60)
        print(f"📍 Local URL:  http://localhost:8000")
        print(f"🌍 Public URL: {public_url}")
        print(f"📚 API Docs:   {public_url}/docs")
        print(f"❤️  Health:     {public_url}/health")
        print(f"💾 Database:   SQLite (ai_studio.db)")
        print("="*60)
        print("\n💡 Copy the Public URL above for your Google AI Studio frontend")
        print("📖 Open the API Docs URL to test all endpoints")
        print("⚠️  Press Ctrl+C to stop the server\n")
    except Exception as e:
        print(f"⚠️  Could not create ngrok tunnel: {e}")
        print("📍 Server will run locally only at http://localhost:8000")
        print("💡 Get a free ngrok token at https://ngrok.com\n")
    
    # Start server
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down server...")
    finally:
        try:
            ngrok.kill()
            print("✅ Ngrok tunnel closed")
        except:
            pass


if __name__ == "__main__":
    # Get ngrok token from environment or command line
    ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
    
    if not ngrok_token:
        print("\n" + "="*60)
        print("📝 OPTIONAL: Set NGROK_AUTH_TOKEN for custom domain")
        print("="*60)
        print("Get your free token at: https://ngrok.com")
        print("Set it: export NGROK_AUTH_TOKEN='your-token-here'")
        print("="*60 + "\n")
    
    start_server_with_ngrok(ngrok_token)

