from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base
import os

# Import all models to ensure they're registered with SQLAlchemy
from app.models import subscription  # noqa

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=None,  # Disable default docs, we'll create custom
    redoc_url=None  # Disable default redoc, we'll create custom
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving images
# __file__ is at /path/to/backend/app/main.py
# assets is at /path/to/backend/assets
backend_dir = os.path.dirname(os.path.dirname(__file__))  # Get backend directory
assets_dir = os.path.join(backend_dir, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    print(f"✅ Mounted /assets → {assets_dir}")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }


@app.get(f"{settings.API_V1_PREFIX}/docs", response_class=HTMLResponse, include_in_schema=False)
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
                ? '/AIStudio/api/v1/openapi.json' 
                : '/api/v1/openapi.json',
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


@app.get(f"{settings.API_V1_PREFIX}/redoc", response_class=HTMLResponse, include_in_schema=False)
async def custom_redoc():
    """Custom ReDoc that works correctly behind reverse proxy"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Studio Backend - API Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body {{ margin: 0; padding: 0; }}
        </style>
    </head>
    <body>
        <redoc spec-url='{settings.API_V1_PREFIX}/openapi.json'></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"></script>
        <script>
        // Override fetch to add ngrok bypass header
        const originalFetch = window.fetch;
        window.fetch = function(...args) {{
            if (args[1]) {{
                args[1].headers = args[1].headers || {{}};
                args[1].headers['ngrok-skip-browser-warning'] = 'true';
            }} else {{
                args[1] = {{ headers: {{ 'ngrok-skip-browser-warning': 'true' }} }};
            }}
            return originalFetch.apply(this, args);
        }};
        </script>
    </body>
    </html>
    """


@app.get("/l/{link_id}", response_class=HTMLResponse, include_in_schema=False)
async def serve_shared_link(link_id: str):
    """Serve the shared link HTML page for public viewing"""
    # Read the shared_link.html file
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "shared_link.html")
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Lookbook page not found</h1><p>The shared link template is missing.</p>",
            status_code=404
        )


