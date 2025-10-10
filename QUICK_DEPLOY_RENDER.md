# Quick Deploy to Render - Step by Step

## Overview

This is the fastest way to get your AI Studio live on the internet for free.

**Time Required:** 30 minutes  
**Cost:** FREE (with limitations)  
**Result:** Public URL like `https://ai-studio.onrender.com`

---

## Prerequisites

- [x] GitHub account
- [x] Your AI Studio code
- [x] Google OAuth credentials (you already have these)

---

## Step 1: Prepare Code for Deployment (5 mins)

### A. Update requirements.txt

Add PostgreSQL support:

```bash
cd /Users/dgolani/Documents/AI_Studio/backend
```

Add this line to `requirements.txt`:
```
psycopg2-binary==2.9.9
```

### B. Create Production Startup File

Create `start_production.py`:

```python
"""
Production startup - no ngrok, uses provided PORT
"""
import os
import uvicorn
from api_with_db_and_ngrok import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
```

### C. Create render.yaml

Create `render.yaml` in project root:

```yaml
services:
  - type: web
    name: ai-studio-backend
    env: python
    region: oregon
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python start_production.py"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: ai-studio-db
          property: connectionString

databases:
  - name: ai-studio-db
    databaseName: ai_studio
    user: ai_studio_user
    plan: free
```

---

## Step 2: Push to GitHub (5 mins)

### A. Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
*.so

# Environment
.env
.env.local

# Database
*.db
*.db-journal

# Logs
*.log
nohup.out

# Assets (images will be stored in cloud)
assets/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
```

### B. Initialize Git & Push

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Render deployment"

# Create repo on GitHub (go to github.com and create a new repo named "ai-studio-backend")

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ai-studio-backend.git

# Push
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy on Render (10 mins)

### A. Sign Up

1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub
4. Authorize Render to access your repos

### B. Deploy from Blueprint

1. Click "New +" button (top right)
2. Select "Blueprint"
3. Connect your `ai-studio-backend` repository
4. Render will detect `render.yaml`
5. Click "Apply"

### C. Wait for Initial Deploy

- Render creates PostgreSQL database (~2 mins)
- Render builds your app (~3 mins)
- First deploy takes ~5 minutes total

---

## Step 4: Configure Environment Variables (5 mins)

### A. Go to Your Web Service

1. Click on `ai-studio-backend` service
2. Go to "Environment" tab
3. Click "Add Environment Variable"

### B. Add These Variables

```bash
GOOGLE_CLIENT_ID
Value: your_client_id.apps.googleusercontent.com

GOOGLE_CLIENT_SECRET
Value: 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

JWT_SECRET_KEY
Value: your-super-secret-jwt-key-change-this-in-production-12345

JWT_ALGORITHM
Value: HS256

JWT_ACCESS_TOKEN_EXPIRE_MINUTES
Value: 30

JWT_REFRESH_TOKEN_EXPIRE_DAYS
Value: 7

FIRST_ADMIN_EMAIL
Value: golanicharu@gmail.com
```

### C. Save & Redeploy

- Click "Save Changes"
- Render will automatically redeploy (~2 mins)

---

## Step 5: Update Google OAuth (3 mins)

Your Render URL will be something like:
```
https://ai-studio-backend-xxxx.onrender.com
```

1. Go to https://console.cloud.google.com
2. APIs & Services → Credentials
3. Click your OAuth 2.0 Client ID
4. Add to **Authorized redirect URIs:**
   ```
   https://ai-studio-backend-xxxx.onrender.com
   https://ai-studio-backend-xxxx.onrender.com/api/v1/auth/google
   ```
5. Add to **Authorized JavaScript origins:**
   ```
   https://ai-studio-backend-xxxx.onrender.com
   ```
6. Click "Save"

---

## Step 6: Initialize Database (2 mins)

### A. Run Migration Script

In Render dashboard:
1. Go to your service
2. Click "Shell" tab
3. Run:
   ```bash
   python scripts/migrate_database.py
   ```

### B. Create Admin User

Still in Shell:
```bash
python scripts/create_admin.py
```

---

## Step 7: Test Your Deployment! 🎉

### A. Check API Health

Visit: `https://your-app.onrender.com/health`

You should see:
```json
{
  "status": "healthy",
  "message": "AI Studio Backend is running"
}
```

### B. Check Swagger UI

Visit: `https://your-app.onrender.com/docs`

You should see the full API documentation!

### C. Test Authentication

1. Open your frontend
2. Update API base URL to: `https://your-app.onrender.com`
3. Try logging in with Google

---

## Important Notes

### Free Tier Limitations

❗ **Render Free Tier:**
- Sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds (cold start)
- 750 hours/month free (enough for 1 service running 24/7)

💡 **To avoid cold starts:**
- Upgrade to paid plan ($7/month)
- Or use a uptime monitor (like UptimeRobot) to ping every 10 mins

### Database Backups

🔒 **Free PostgreSQL:**
- 90-day data retention
- No automatic backups on free tier

💡 **For production:**
- Upgrade to Starter plan ($7/month) for backups

---

## Troubleshooting

### Build Failed

**Error:** `Module not found`
- Check `requirements.txt` has all dependencies
- Make sure it includes `psycopg2-binary`

### App Won't Start

**Check logs:**
1. Render Dashboard → Your Service → Logs
2. Look for error messages

**Common issues:**
- Missing environment variables
- Database connection failed
- Port binding error

### Database Connection Error

**Check:**
1. Database service is running
2. `DATABASE_URL` env var is set
3. `psycopg2-binary` is in requirements.txt

### Google OAuth Error

**Check:**
1. Render URL is added to Google Console
2. No trailing slashes in redirect URIs
3. Environment variables are set correctly

---

## Monitoring Your App

### View Logs

Render Dashboard → Service → Logs

Shows real-time logs of your application.

### Check Metrics

Render Dashboard → Service → Metrics

Shows:
- CPU usage
- Memory usage
- Request count

### Set Up Alerts

1. Service → Settings
2. Scroll to "Notifications"
3. Add your email for deploy notifications

---

## Next Steps

### 1. Set Up Image Storage (Recommended)

Your local `assets/` folder won't persist on Render.

**Option A: Cloudinary (Easiest)**
- Free tier: 25GB
- Sign up: https://cloudinary.com
- I can help integrate it

**Option B: AWS S3**
- More control
- Pay per use

### 2. Custom Domain (Optional)

1. Buy domain (e.g., from Namecheap, Google Domains)
2. Render Dashboard → Service → Settings → Custom Domain
3. Add your domain
4. Update DNS records as shown
5. Render provides free SSL

### 3. Upgrade to Paid Plan (For Production)

**Starter Plan - $7/month:**
- No sleep/cold starts
- Better performance
- Database backups

---

## Cost Breakdown

### Free Tier (Current)
```
Web Service:  $0/month (free tier)
Database:     $0/month (free tier)
Total:        $0/month
```

### Paid Tier (Recommended for Production)
```
Web Service:  $7/month (Starter)
Database:     $7/month (Starter)
Total:        $14/month
```

---

## Your Deployed URLs

After deployment, you'll have:

**Base URL:**
```
https://ai-studio-backend-xxxx.onrender.com
```

**API Endpoints:**
```
https://ai-studio-backend-xxxx.onrender.com/api/v1/auth/google
https://ai-studio-backend-xxxx.onrender.com/api/v1/models
https://ai-studio-backend-xxxx.onrender.com/api/v1/looks
https://ai-studio-backend-xxxx.onrender.com/api/v1/settings
https://ai-studio-backend-xxxx.onrender.com/api/v1/admin/users
https://ai-studio-backend-xxxx.onrender.com/api/v1/admin/defaults
```

**Swagger UI:**
```
https://ai-studio-backend-xxxx.onrender.com/docs
```

---

## Support

If you get stuck:

1. **Check Render Docs:** https://render.com/docs
2. **Check Logs:** Dashboard → Logs
3. **Contact Me:** I can help debug!

---

## Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created and deployed
- [ ] Environment variables set
- [ ] Google OAuth URLs updated
- [ ] Database migrated
- [ ] Admin user created
- [ ] `/health` endpoint working
- [ ] `/docs` showing Swagger UI
- [ ] Frontend connected to new URL
- [ ] Google login working

---

🎉 **Congratulations!** Your AI Studio is now live on the internet!

Your app is accessible from anywhere in the world at:
`https://your-app.onrender.com`

