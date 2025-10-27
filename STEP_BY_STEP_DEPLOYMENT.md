# 🚀 AI Studio - Complete Deployment Guide

## Your Goal
- ✅ Push code to GitHub
- ✅ Auto-deploy to Render (or other platform)
- ✅ Every `git push` automatically updates your live server
- ✅ Database migrations handled properly

---

## Part 1: Prepare Your Code (5 minutes)

### ✅ Step 1: Verify All Files Are Created

Check that these files exist:
```bash
cd /Users/dgolani/Documents/AI_Studio/backend

# Should exist:
ls -la .gitignore
ls -la render.yaml
ls -la start_production.py
ls -la scripts/init_production_db.py
```

All files are already created! ✅

---

## Part 2: Set Up GitHub (10 minutes)

### ✅ Step 2: Create GitHub Repository

1. **Go to GitHub:** https://github.com
2. **Click** "+" (top right) → "New repository"
3. **Settings:**
   - Repository name: `ai-studio-backend`
   - Description: `AI Studio Backend - FastAPI + PostgreSQL`
   - Visibility: `Private` (recommended) or `Public`
   - **DON'T** check "Initialize with README"
4. **Click** "Create repository"

---

### ✅ Step 3: Push Your Code to GitHub

Open Terminal and run:

```bash
# Navigate to your backend folder
cd /Users/dgolani/Documents/AI_Studio/backend

# Initialize git (if not already)
git init

# Add all files (gitignore will exclude sensitive files)
git add .

# Check what will be committed (should NOT see .env or *.db files)
git status

# Create first commit
git commit -m "Initial commit - AI Studio Backend"

# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ai-studio-backend.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**If asked for credentials:**
- GitHub no longer accepts passwords
- Use a **Personal Access Token** instead:
  1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Generate new token
  3. Select `repo` scope
  4. Copy the token
  5. Use it as your password when pushing

---

## Part 3: Deploy to Render (15 minutes)

### ✅ Step 4: Sign Up on Render

1. Go to: https://render.com
2. Click "Get Started for Free"
3. **Sign up with GitHub** (easiest option)
4. Authorize Render to access your repositories

---

### ✅ Step 5: Deploy from Blueprint

1. **In Render Dashboard:**
   - Click "New +" button (top right)
   - Select **"Blueprint"**

2. **Connect Repository:**
   - Find `ai-studio-backend` in the list
   - Click "Connect"

3. **Render reads `render.yaml`:**
   - It will show:
     - ✅ Web Service: `ai-studio-backend`
     - ✅ Database: `ai-studio-db` (PostgreSQL)
   - Click **"Apply"**

4. **Wait for creation (~3 minutes):**
   - Render creates PostgreSQL database
   - Render starts building your app
   - You'll see logs in real-time

---

### ✅ Step 6: Add Environment Variables

1. **While build is running, go to:**
   - Your web service → **"Environment"** tab

2. **Add these secrets** (click "Add Environment Variable"):

```bash
GOOGLE_CLIENT_ID
Value: [paste your client ID].apps.googleusercontent.com

GOOGLE_CLIENT_SECRET
Value: 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

JWT_SECRET_KEY
Value: [generate a random 64-character string]

FIRST_ADMIN_EMAIL
Value: golanicharu@gmail.com
```

**To generate JWT_SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

3. **Click "Save Changes"**
   - Render will automatically redeploy with new variables

---

### ✅ Step 7: Get Your Public URL

After deployment completes (~5 minutes total):

1. **Find your URL:**
   - In Render dashboard, you'll see something like:
   ```
   https://ai-studio-backend-xxxx.onrender.com
   ```

2. **Test it:**
   - Open: `https://ai-studio-backend-xxxx.onrender.com/health`
   - Should see: `{"status": "healthy", ...}`

---

### ✅ Step 8: Initialize Database

1. **In Render Dashboard:**
   - Your service → **"Shell"** tab
   - This opens a terminal on your server

2. **Run initialization script:**
   ```bash
   python scripts/init_production_db.py
   ```

3. **You should see:**
   ```
   📊 Creating database tables...
   ✅ All tables created successfully
   ⚙️  Creating default settings...
   ✅ Default settings created
   👤 Creating admin user: golanicharu@gmail.com
   ✅ Admin user created
   ```

---

### ✅ Step 9: Update Google OAuth

Your new production URL needs to be added to Google Console:

1. **Go to:** https://console.cloud.google.com
2. **Navigate to:** APIs & Services → Credentials
3. **Click your OAuth Client ID**
4. **Add to "Authorized redirect URIs":**
   ```
   https://ai-studio-backend-xxxx.onrender.com
   https://ai-studio-backend-xxxx.onrender.com/api/v1/auth/google
   ```
5. **Add to "Authorized JavaScript origins":**
   ```
   https://ai-studio-backend-xxxx.onrender.com
   ```
6. **Click "Save"**

---

### ✅ Step 10: Test Your Deployment

1. **Check Swagger UI:**
   ```
   https://ai-studio-backend-xxxx.onrender.com/docs
   ```
   Should show full API documentation ✅

2. **Check Health:**
   ```
   https://ai-studio-backend-xxxx.onrender.com/health
   ```
   Should return JSON with status ✅

3. **Update Frontend:**
   - Change API base URL in your frontend to:
   ```
   https://ai-studio-backend-xxxx.onrender.com
   ```

4. **Test Google Login:**
   - Try logging in from your frontend
   - Should work without ngrok warning page! ✅

---

## Part 4: Continuous Deployment (Auto-Updates) 🎉

### ✅ Now Every Time You Make Changes:

```bash
# Make your code changes
# Example: Update a file
code app/api/v1/endpoints/models.py

# Check what changed
git status

# Add changes
git add .

# Commit with message
git commit -m "Add new feature to models endpoint"

# Push to GitHub
git push

# 🎉 Render automatically detects push and deploys!
# No manual action needed!
```

**Watch it deploy:**
- Go to Render Dashboard → Your Service → "Events" tab
- You'll see deployment progress in real-time
- Takes ~2-3 minutes per deployment

---

## Part 5: Database Migrations

### When You Change Database Schema:

**Example:** You add a new column to `User` model

1. **Update your model** (e.g., `app/models/user.py`)

2. **Create migration script** (in `scripts/migrations/`)

3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add new column to User model"
   git push
   ```

4. **After deployment, run migration:**
   - Render Dashboard → Shell
   - Run your migration script

**Better approach:** Use Alembic (I can set this up for you!)

---

## 🎯 Final Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created and deployed
- [ ] Environment variables added
- [ ] Database initialized
- [ ] Admin user created
- [ ] Google OAuth URLs updated
- [ ] `/health` endpoint works
- [ ] `/docs` shows Swagger UI
- [ ] Frontend connected to new URL
- [ ] Google login works
- [ ] Test creating a model
- [ ] Test creating a look

---

## 📊 Your New Workflow

### Daily Development:

```bash
# 1. Make changes locally
code app/api/v1/endpoints/models.py

# 2. Test locally
python api_with_db_and_ngrok.py

# 3. When ready, commit & push
git add .
git commit -m "Improve model generation"
git push

# 4. Render auto-deploys (2-3 mins)
# 5. Done! Your production app is updated ✅
```

---

## 🔥 Important Notes

### Free Tier Limitations:

⚠️ **Render Free Tier:**
- Sleeps after 15 mins of inactivity
- First request after sleep: ~30 seconds (cold start)
- 750 hours/month (enough for 1 service 24/7)

💡 **To prevent cold starts:**
- Upgrade to Starter plan ($7/month)
- Or use UptimeRobot to ping every 10 mins (free)

### Database Backups:

⚠️ **Free PostgreSQL:**
- 90-day data retention
- No automatic backups

💡 **For production:**
- Upgrade to Starter ($7/month) for daily backups

---

## 🆘 Troubleshooting

### Build Failed:

**Check:**
1. Render Dashboard → Logs
2. Look for error message
3. Common issues:
   - Missing package in `requirements.txt`
   - Python version mismatch
   - Syntax error

**Fix:**
```bash
# Fix the issue locally
git add .
git commit -m "Fix build error"
git push
# Render auto-retries
```

### App Won't Start:

**Check:**
1. Environment variables are set
2. Database is created
3. PORT is being used correctly

**View logs:**
- Render Dashboard → Your Service → Logs

### Database Connection Error:

**Check:**
1. PostgreSQL service is running
2. `DATABASE_URL` is set automatically
3. `psycopg2-binary` is in requirements.txt

---

## 🎊 Success!

Your AI Studio is now:
- ✅ Live on the internet 24/7
- ✅ Auto-deploys from GitHub
- ✅ Using production PostgreSQL
- ✅ No more ngrok!
- ✅ Professional public URL
- ✅ Free SSL/HTTPS

**Your URLs:**
```
API:     https://ai-studio-backend-xxxx.onrender.com
Docs:    https://ai-studio-backend-xxxx.onrender.com/docs
Health:  https://ai-studio-backend-xxxx.onrender.com/health
```

---

## 💡 Next Steps

### Optional Enhancements:

1. **Custom Domain** ($12/year)
   - Buy domain from Namecheap/Google
   - Point to Render
   - `api.yourdomain.com`

2. **Image Storage** (Recommended)
   - Set up Cloudinary (25GB free)
   - Persist images across deployments

3. **Monitoring**
   - Set up UptimeRobot (free)
   - Email alerts if site goes down

4. **Database Migrations**
   - Set up Alembic for proper migrations
   - Version control your schema

**Want help with any of these? Just ask!** 🚀


