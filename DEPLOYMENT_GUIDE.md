# AI Studio - Deployment Guide

## Overview

This guide covers multiple deployment options for your AI Studio service, from simple to advanced setups.

---

## What You Need to Deploy

1. **FastAPI Backend** (Python application)
2. **Database** (Currently SQLite, recommend PostgreSQL for production)
3. **Static Assets** (Images stored in `assets/` directory)
4. **Environment Variables** (`.env` file secrets)

---

## Deployment Options (Ranked by Ease)

### 🌟 Option 1: Railway (Easiest - Recommended for Quick Start)

**Best for:** Quick deployment, automatic scaling, beginners

**Pros:**
- ✅ One-click deployment from GitHub
- ✅ Built-in PostgreSQL database
- ✅ Automatic SSL/HTTPS
- ✅ Free tier available ($5/month credit)
- ✅ Auto-deploys on git push

**Cons:**
- ❌ Can get expensive at scale
- ❌ Limited free tier

**Setup:**

1. **Push code to GitHub**
   ```bash
   cd /Users/dgolani/Documents/AI_Studio/backend
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/ai-studio-backend.git
   git push -u origin main
   ```

2. **Sign up at Railway**
   - Go to https://railway.app
   - Sign in with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `ai-studio-backend` repo

3. **Add PostgreSQL**
   - In Railway dashboard, click "New" → "Database" → "PostgreSQL"
   - Railway automatically sets `DATABASE_URL` environment variable

4. **Configure Environment Variables**
   - Go to your service → "Variables" tab
   - Add all variables from your `.env` file:
     ```
     GOOGLE_CLIENT_ID=your_client_id
     GOOGLE_CLIENT_SECRET=your_client_secret
     JWT_SECRET_KEY=your_secret
     FIRST_ADMIN_EMAIL=your_email
     ```

5. **Add Procfile** (create in project root)
   ```
   web: uvicorn api_with_db_and_ngrok:app --host 0.0.0.0 --port $PORT
   ```

6. **Update code for Railway**
   - Remove ngrok code (Railway provides public URL)
   - Use PostgreSQL instead of SQLite

**Cost:** ~$5-20/month depending on usage

---

### 🚀 Option 2: Render (Easy - Great Free Tier)

**Best for:** Free deployment, simple setup, hobby projects

**Pros:**
- ✅ Generous free tier
- ✅ Auto-deploy from GitHub
- ✅ Built-in PostgreSQL
- ✅ Automatic SSL
- ✅ Easy to use

**Cons:**
- ❌ Free tier has cold starts (slow first request)
- ❌ Free tier spins down after 15 mins inactivity

**Setup:**

1. **Push to GitHub** (same as Railway)

2. **Sign up at Render**
   - Go to https://render.com
   - Sign in with GitHub

3. **Create PostgreSQL Database**
   - Dashboard → "New" → "PostgreSQL"
   - Name: `ai-studio-db`
   - Free tier
   - Copy the "Internal Database URL"

4. **Create Web Service**
   - Dashboard → "New" → "Web Service"
   - Connect your GitHub repo
   - Settings:
     - **Name:** ai-studio-backend
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn api_with_db_and_ngrok:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables**
   - In service settings → "Environment"
   - Add all your `.env` variables
   - Add `DATABASE_URL` from PostgreSQL service

6. **Deploy**
   - Click "Create Web Service"
   - Render auto-deploys

**Your API will be at:** `https://ai-studio-backend.onrender.com`

**Cost:** Free tier available, paid starts at $7/month

---

### ☁️ Option 3: Google Cloud Platform (Moderate - Best for Production)

**Best for:** Production apps, scaling, integration with Google services

**Pros:**
- ✅ Excellent reliability
- ✅ Integrates with Google Cloud Storage (for images)
- ✅ Free tier: $300 credit for 90 days
- ✅ Auto-scaling
- ✅ Global CDN

**Cons:**
- ❌ More complex setup
- ❌ Billing can be confusing

**Setup:**

**A. Deploy Backend (Cloud Run)**

1. **Install Google Cloud SDK**
   ```bash
   # macOS
   brew install --cask google-cloud-sdk
   
   # Login
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Create Dockerfile** (in project root)
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   # Create assets directory
   RUN mkdir -p assets/models assets/looks
   
   CMD ["uvicorn", "api_with_db_and_ngrok:app", "--host", "0.0.0.0", "--port", "8080"]
   ```

3. **Create .dockerignore**
   ```
   venv/
   __pycache__/
   *.pyc
   .env
   ai_studio.db
   nohup.out
   .git/
   ```

4. **Build and Deploy**
   ```bash
   # Build container
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-studio-backend
   
   # Deploy to Cloud Run
   gcloud run deploy ai-studio-backend \
     --image gcr.io/YOUR_PROJECT_ID/ai-studio-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GOOGLE_CLIENT_ID=xxx,GOOGLE_CLIENT_SECRET=xxx
   ```

**B. Database (Cloud SQL - PostgreSQL)**

1. **Create Cloud SQL Instance**
   ```bash
   gcloud sql instances create ai-studio-db \
     --database-version=POSTGRES_15 \
     --tier=db-f1-micro \
     --region=us-central1
   ```

2. **Create Database**
   ```bash
   gcloud sql databases create ai_studio --instance=ai-studio-db
   ```

3. **Connect Cloud Run to Cloud SQL**
   ```bash
   gcloud run services update ai-studio-backend \
     --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:ai-studio-db \
     --set-env-vars DATABASE_URL=postgresql://user:pass@/ai_studio?host=/cloudsql/YOUR_PROJECT_ID:us-central1:ai-studio-db
   ```

**C. Image Storage (Cloud Storage)**

1. **Create Storage Bucket**
   ```bash
   gsutil mb -l us-central1 gs://ai-studio-assets
   gsutil iam ch allUsers:objectViewer gs://ai-studio-assets
   ```

2. **Update code to use GCS** (instead of local file storage)

**Cost:** ~$20-50/month for small/medium usage

---

### 🐳 Option 4: DigitalOcean App Platform (Moderate)

**Best for:** Simplicity + control, predictable pricing

**Pros:**
- ✅ Simple pricing ($5-12/month)
- ✅ Auto-deploy from GitHub
- ✅ Managed PostgreSQL
- ✅ Good documentation

**Cons:**
- ❌ Less features than AWS/GCP
- ❌ No free tier

**Setup:**

1. **Sign up at DigitalOcean**
   - Go to https://www.digitalocean.com

2. **Create App**
   - Apps → Create App
   - Connect GitHub
   - Select repo

3. **Configure**
   - **Type:** Web Service
   - **Run Command:** `uvicorn api_with_db_and_ngrok:app --host 0.0.0.0 --port 8080`
   - **HTTP Port:** 8080

4. **Add PostgreSQL Database**
   - In app settings → Add Component → Database
   - Choose PostgreSQL
   - DigitalOcean sets `DATABASE_URL` automatically

5. **Add Environment Variables**
   - Settings → Environment Variables
   - Add your `.env` variables

**Cost:** $5/month (app) + $7/month (database) = $12/month

---

### 💪 Option 5: AWS (Advanced - Most Powerful)

**Best for:** Enterprise apps, maximum control, complex requirements

**Pros:**
- ✅ Most features
- ✅ Best scaling
- ✅ Global infrastructure
- ✅ Free tier (12 months)

**Cons:**
- ❌ Very complex
- ❌ Steep learning curve
- ❌ Can be expensive

**Setup (High-Level):**

1. **Elastic Beanstalk** (easiest AWS option)
   - Upload your app as a zip
   - AWS handles deployment

2. **RDS PostgreSQL** for database

3. **S3** for image storage

4. **CloudFront** for CDN

**Cost:** ~$30-100/month depending on usage

---

## Database Migration: SQLite → PostgreSQL

Your app currently uses SQLite. For production, you need PostgreSQL.

### Update `app/core/config.py`

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Database (use PostgreSQL in production)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./ai_studio.db"  # fallback to SQLite
    )
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Update `app/core/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Handle PostgreSQL vs SQLite
if settings.DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
else:
    # SQLite
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Update `requirements.txt`

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
google-auth==2.23.4
psycopg2-binary==2.9.9  # Add this for PostgreSQL
python-dotenv==1.0.0
```

---

## Image Storage Options

### Option A: Local File Storage (Current)
- **Pros:** Simple, no extra cost
- **Cons:** Lost on container restart, doesn't scale
- **Use:** Development only

### Option B: Cloud Storage Bucket
- **Google Cloud Storage:** $0.02/GB/month
- **AWS S3:** $0.023/GB/month
- **Cloudinary:** $0 for 25GB (free tier)

### Option C: Cloudinary (Easiest for Images)

**Why Cloudinary:**
- ✅ Free tier: 25GB storage, 25GB bandwidth
- ✅ Built-in image transformations
- ✅ CDN included
- ✅ Very easy to integrate

**Setup:**

1. **Sign up:** https://cloudinary.com
2. **Install SDK:** `pip install cloudinary`
3. **Update image upload code:**

```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="your_cloud_name",
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Upload image
result = cloudinary.uploader.upload(
    image_file,
    folder="ai-studio/models",
    public_id=f"{model_id}"
)

image_url = result['secure_url']  # Public URL
```

---

## Recommended Deployment Strategy

### For Learning/Testing (Free)
```
Backend:   Render (Free tier)
Database:  Render PostgreSQL (Free tier)
Images:    Cloudinary (Free tier - 25GB)

Total Cost: $0/month
```

### For Production (Small Scale)
```
Backend:   Railway or DigitalOcean ($12/month)
Database:  Built-in PostgreSQL
Images:    Cloudinary ($0-9/month)

Total Cost: $12-20/month
```

### For Production (Medium/Large Scale)
```
Backend:   Google Cloud Run (auto-scaling)
Database:  Cloud SQL PostgreSQL
Images:    Google Cloud Storage + CDN

Total Cost: $50-200/month (scales with usage)
```

---

## Step-by-Step: Deploy to Render (Easiest)

Let me walk you through the complete process:

### 1. Prepare Your Code

Create `render.yaml` in project root:

```yaml
services:
  - type: web
    name: ai-studio-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn api_with_db_and_ngrok:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: ai-studio-db
          property: connectionString
      - key: GOOGLE_CLIENT_ID
        sync: false
      - key: GOOGLE_CLIENT_SECRET
        sync: false
      - key: JWT_SECRET_KEY
        sync: false
      - key: FIRST_ADMIN_EMAIL
        sync: false

databases:
  - name: ai-studio-db
    databaseName: ai_studio
    user: ai_studio_user
```

### 2. Update Code for Production

Remove ngrok-specific code from `api_with_db_and_ngrok.py`:

```python
# Remove or comment out:
# - start_server_with_ngrok()
# - ngrok imports
# - ngrok tunnel creation

# Keep just the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
```

### 3. Push to GitHub

```bash
cd /Users/dgolani/Documents/AI_Studio/backend
git init
git add .
git commit -m "Prepare for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-studio-backend.git
git push -u origin main
```

### 4. Deploy on Render

1. Go to https://render.com
2. Click "New +" → "Blueprint"
3. Connect your GitHub repo
4. Render reads `render.yaml` and sets everything up
5. Add your environment variables in the dashboard
6. Click "Apply"

### 5. Get Your Public URL

Render gives you: `https://ai-studio-backend.onrender.com`

Your API endpoints:
- `https://ai-studio-backend.onrender.com/api/v1/auth/google`
- `https://ai-studio-backend.onrender.com/api/v1/models`
- `https://ai-studio-backend.onrender.com/docs` (Swagger UI)

---

## Environment Variables Checklist

Make sure to set these in your hosting platform:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx

# JWT
JWT_SECRET_KEY=your_long_random_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin
FIRST_ADMIN_EMAIL=your@email.com

# Database (usually auto-set by platform)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Optional: Cloudinary (if using)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

---

## Google OAuth Configuration

After deployment, update your Google Cloud Console:

1. Go to https://console.cloud.google.com
2. APIs & Services → Credentials
3. Edit your OAuth Client ID
4. Add to **Authorized redirect URIs:**
   ```
   https://your-app.onrender.com
   https://your-app.onrender.com/api/v1/auth/google
   ```
5. Add to **Authorized JavaScript origins:**
   ```
   https://your-app.onrender.com
   ```

---

## Monitoring & Logs

### Render
- Logs available in dashboard
- Auto-restart on crash

### Railway
- Real-time logs in dashboard
- Metrics graphs

### Google Cloud
- Cloud Logging for logs
- Cloud Monitoring for metrics

---

## Cost Comparison (Monthly)

| Platform | Free Tier | Small App | Medium App | Large App |
|----------|-----------|-----------|------------|-----------|
| **Render** | ✅ Yes (limited) | $7-15 | $20-40 | $50-100 |
| **Railway** | $5 credit | $10-20 | $30-60 | $100+ |
| **DigitalOcean** | ❌ No | $12 | $25-50 | $100+ |
| **Google Cloud** | $300 (90 days) | $20-40 | $50-150 | $200+ |
| **AWS** | 12 months | $30-50 | $80-200 | $300+ |

---

## Next Steps

1. **Choose a platform** (I recommend Render for simplicity)
2. **Migrate database** to PostgreSQL
3. **Set up image storage** (Cloudinary recommended)
4. **Remove ngrok code**
5. **Push to GitHub**
6. **Deploy!**

---

## Need Help?

I can help you with:
1. Creating deployment-ready code
2. Setting up PostgreSQL migration
3. Configuring Cloudinary for images
4. Writing deployment scripts
5. Troubleshooting deployment issues

Just let me know which platform you want to use! 🚀


