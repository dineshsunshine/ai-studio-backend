PRODUCTION-READY BACKEND ARCHITECTURE TEMPLATE
===============================================

Build a complete backend with local development using ngrok and cloud production deployment.

TECH STACK:
-----------
- FastAPI (Python web framework)
- SQLAlchemy ORM (database)
- PostgreSQL (production database)
- SQLite (local development database)
- ngrok (local public URL)
- Render (production hosting)
- Google OAuth (authentication)
- Cloudinary (production image storage)

LOCAL DEVELOPMENT SETUP:
------------------------
1. Use SQLite for local database (file-based, no setup needed)
2. Expose local server via ngrok tunnel with custom domain
3. Serve static files locally from /assets/ directory
4. Run reverse proxy to handle multiple projects on different paths
5. Store images locally in assets/images/ folder

PROJECT STRUCTURE:
------------------
backend/
├── app/
│   ├── api/v1/endpoints/     # API route handlers
│   ├── models/               # SQLAlchemy database models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── core/
│   │   ├── config.py         # Environment configuration
│   │   ├── database.py       # Database connection
│   │   ├── auth.py           # JWT authentication
│   │   └── storage.py        # File upload handling
│   └── main.py               # FastAPI app initialization
├── scripts/
│   └── migrate_database.py   # Database migration utilities
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── reverse_proxy.py          # (Optional) Multi-project routing
└── local_server.py           # Local development server with ngrok

CORE FEATURES TO IMPLEMENT:
----------------------------
1. OAuth authentication with JWT tokens
2. Role-based access control (admin/regular user)
3. User registration and approval workflow
4. CRUD operations for your domain entities
5. File upload and storage (local + cloud)
6. Database migrations (SQLite → PostgreSQL compatible)
7. User-specific settings/preferences
8. Public/shareable resource URLs (if needed)

DATABASE STRATEGY:
------------------
1. Use environment variable IS_PRODUCTION to switch databases
2. Local: SQLite (sqlite:///./database.db)
3. Production: PostgreSQL (from DATABASE_URL env var)
4. All models use String(36) for IDs (UUID compatible with both)
5. Use SQLAlchemy Column types that work on both databases
6. Create migration scripts that handle schema changes gracefully

AUTHENTICATION FLOW:
--------------------
1. Frontend sends Google ID token to /api/v1/auth/google
2. Backend verifies token with Google
3. Check if user exists and is approved
4. Return JWT access token (24-hour expiry)
5. All protected endpoints require Authorization: Bearer <token>
6. New users submit access requests for admin approval

FILE STORAGE STRATEGY:
----------------------
Local Development:
- Store in backend/assets/{category}/
- Serve via FastAPI StaticFiles at /assets/
- Use ngrok URL: https://domain.ngrok-free.dev/{project-path}/assets/...

Production:
- Use cloud storage (Cloudinary/S3/GCS) for permanent storage
- Upload via cloud provider SDK
- Return public cloud URLs
- Avoid local filesystem (cloud platforms often have ephemeral storage)

ENVIRONMENT VARIABLES:
----------------------
# Database
DATABASE_URL=sqlite:///./database.db  # or postgresql://...
IS_PRODUCTION=false  # true on cloud

# Authentication
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-secret
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# File Storage
USE_CLOUD_STORAGE=true  # true for production
CLOUD_STORAGE_PROVIDER=cloudinary  # or s3, gcs
CLOUD_STORAGE_KEY=your-key
CLOUD_STORAGE_SECRET=your-secret
CLOUD_STORAGE_BUCKET=your-bucket-name

# ngrok (local only)
NGROK_AUTH_TOKEN=your-ngrok-token
NGROK_DOMAIN=your-custom-domain.ngrok-free.dev

# Admin
FIRST_ADMIN_EMAIL=admin@example.com

# Optional
BASE_URL=http://localhost:8000
API_PREFIX=/api/v1

PRODUCTION DEPLOYMENT (Cloud Platform):
----------------------------------------
Platform Options: Render, Railway, Heroku, AWS, GCP, Azure

Steps:
1. Create managed PostgreSQL database instance
2. Create web service/app from GitHub repo
3. Set all environment variables in platform dashboard
4. Configure start command: python start_production.py
5. Enable auto-deploy from GitHub main branch
6. Set up cloud storage (Cloudinary/S3/GCS)
7. Configure custom domain (if needed)
8. Set up monitoring and logging

MIGRATION PATTERN:
------------------
Create admin-only migration endpoints for schema changes:
- POST /api/v1/migrate/{migration-name}
- Check current state before applying changes
- Skip steps already completed
- Handle partial migrations gracefully
- Verify final state after completion
- Make migrations idempotent (safe to run multiple times)

KEY IMPLEMENTATION DETAILS:
---------------------------
1. Use Pydantic for request/response validation
2. Implement proper error handling with HTTP status codes
3. Add CORS middleware for frontend communication
4. Include ngrok-skip-browser-warning header in API calls
5. Use relationship() with lazy="selectin" for eager loading
6. Implement pagination for list endpoints (skip/limit)
7. Add created_at/updated_at timestamps to all models
8. Use CASCADE delete for related records
9. Store JSON data in JSONB columns (PostgreSQL) or JSON (SQLite)
10. Always sanitize and validate user inputs

API STRUCTURE:
--------------
/api/v1/
├── auth/
│   ├── /login               (POST - OAuth or standard login)
│   ├── /register            (POST - New user registration)
│   ├── /me                  (GET - Current user info)
│   ├── /logout              (POST - Logout)
│   └── /request-access      (POST - Request account access)
├── admin/
│   ├── /users               (GET/PATCH - Manage users)
│   ├── /access-requests     (GET - View pending requests)
│   ├── /access-requests/{id}/approve  (POST - Approve)
│   └── /access-requests/{id}/reject   (POST - Reject)
├── {your-resource}/
│   ├── /                    (GET list, POST create)
│   ├── /{id}                (GET single, PATCH update, DELETE)
│   ├── /{id}/upload         (POST - File upload for resource)
│   └── /{id}/{action}       (POST - Custom actions)
├── settings/
│   ├── /                    (GET/PUT - User settings)
│   └── /reset               (POST - Reset to defaults)
└── migrate/                 (Admin-only migration endpoints)

REVERSE PROXY SETUP (Optional - Multi-Project):
-----------------------------------------------
If running multiple projects on one ngrok tunnel:

Create reverse_proxy.py to route projects:
- Listen on single port (8000)
- Route /{project-1}/* → Project 1 (port 8001)
- Route /{project-2}/* → Project 2 (port 3000)
- Add CORS headers
- Handle preflight OPTIONS requests
- Forward all HTTP methods (GET, POST, PATCH, DELETE, etc.)

Benefits:
- Single ngrok tunnel for multiple projects
- Each project has its own URL path
- Centralized CORS handling

SWAGGER UI CONFIGURATION:
--------------------------
Configure FastAPI to work behind reverse proxy (if using):
- Set servers=[{"url": "/{your-path}", "description": "Local"}]
- Use root_path="/{your-path}" for proper route generation
- Add custom /docs endpoint for correct OpenAPI schema URL
- Configure oauth2_redirect_url for authentication

For standalone deployment:
- Use default FastAPI settings
- Swagger available at /docs
- ReDoc at /redoc

TESTING STRATEGY:
-----------------
1. Use Swagger UI for API testing
2. Create simple HTML test pages for quick validation
3. Test with actual frontend integration
4. Verify both local (ngrok) and production (Render) work
5. Test migrations on a copy of production database first

COMMON PITFALLS TO AVOID:
-------------------------
1. Hardcoding URLs - use environment variables
2. Forgetting to handle both SQLite and PostgreSQL differences
3. Not making migrations idempotent
4. Storing files on Render's filesystem (it's ephemeral)
5. Not handling CORS properly
6. Missing ngrok warning bypass header
7. Using incompatible SQL types between SQLite and PostgreSQL
8. Not validating user permissions properly
9. Exposing sensitive data in API responses
10. Forgetting to commit database transactions

DEPLOYMENT CHECKLIST:
---------------------
□ Environment variables set on cloud platform
□ Cloud storage (Cloudinary/S3/GCS) configured
□ PostgreSQL database created and initialized
□ GitHub auto-deploy enabled
□ Database migrations run successfully
□ First admin user created
□ OAuth credentials updated for production domain
□ CORS origins include production frontend URL
□ Files served from cloud storage (not local filesystem)
□ Health check endpoint responding (GET /health)
□ API documentation accessible (Swagger at /docs)
□ All endpoints tested with production data
□ SSL/HTTPS enabled
□ Domain name configured (if custom)
□ Monitoring and error tracking set up

MAINTENANCE:
------------
1. Run migrations before deploying schema changes
2. Monitor application logs for errors
3. Keep dependencies updated (requirements.txt)
4. Backup production database regularly (automated)
5. Test locally with ngrok before pushing to production
6. Document all API changes for frontend developers
7. Use migration endpoints for schema updates
8. Use semantic versioning for API updates (v1, v2)
9. Monitor database performance and optimize queries
10. Review and rotate secrets/tokens periodically
11. Keep cloud storage organized with proper folder structure
12. Set up alerts for critical errors and downtime

