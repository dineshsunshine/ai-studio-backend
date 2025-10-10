# Development vs Production Strategy

## Overview

You now have two environments:
- **Local Development:** Your laptop with ngrok
- **Production:** Render at https://ai-studio-backend-ijkp.onrender.com/

---

## 🎯 Recommended Workflow

### Daily Development Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR WORKFLOW                           │
└─────────────────────────────────────────────────────────────┘

1. Work Locally (Development)
   ↓
2. Test with ngrok (Optional)
   ↓
3. Commit & Push to GitHub
   ↓
4. Render Auto-Deploys (Production)
   ↓
5. Test Production
```

---

## 🔧 Local Development Setup

### When to Use Local Dev:

✅ **Use Local for:**
- Daily coding and testing
- Trying new features
- Debugging issues
- Quick iterations
- Breaking things without consequences

### How to Run Locally:

```bash
# Terminal 1: Start backend
cd /Users/dgolani/Documents/AI_Studio/backend
python api_with_db_and_ngrok.py

# This gives you:
# - Local API: http://localhost:8000
# - Public URL: https://xxxxx.ngrok-free.app (temporary)
# - Database: SQLite (ai_studio.db)
```

### Local Environment:
```
Database:    SQLite (ai_studio.db)
Images:      Local files (assets/)
URL:         Temporary ngrok URL (changes each restart)
Data:        Test data (can be deleted/reset)
Cost:        Free
Uptime:      Only when your laptop is on
```

---

## 🚀 Production Setup (Render)

### When to Use Production:

✅ **Use Production for:**
- Stable features
- User testing
- Frontend integration
- Demos
- Real user data
- 24/7 availability

### Production Environment:
```
Database:    PostgreSQL (persistent)
Images:      Server files (or use cloud storage later)
URL:         https://ai-studio-backend-ijkp.onrender.com (permanent)
Data:        Real data (backed up)
Cost:        Free tier (with cold starts) or $14/month
Uptime:      24/7 (with occasional cold starts on free tier)
```

---

## 📋 Your Daily Workflow

### Scenario 1: Regular Feature Development

```bash
# 1. Make changes locally
cd /Users/dgolani/Documents/AI_Studio/backend
code app/api/v1/endpoints/models.py

# 2. Test locally (optional ngrok for frontend testing)
python api_with_db_and_ngrok.py

# 3. When it works, commit and push
git add .
git commit -m "Add new feature to models API"
git push

# 4. Render auto-deploys (wait 2-3 mins)
# 5. Test on production URL
```

**Result:** New feature goes live on production automatically! ✅

---

### Scenario 2: Quick Testing (Don't Want to Deploy Yet)

```bash
# 1. Work locally
python api_with_db_and_ngrok.py

# 2. Test with your frontend using ngrok URL
# Frontend → https://xxxxx.ngrok-free.app

# 3. Don't commit yet - keep testing

# 4. When satisfied, commit and push
git add .
git commit -m "Tested feature"
git push
```

**Result:** Test privately before production deployment! ✅

---

### Scenario 3: Hot Fix for Production

```bash
# 1. Identify the bug on production

# 2. Fix locally and test
code app/api/v1/endpoints/auth.py
python api_with_db_and_ngrok.py

# 3. Quick commit and push
git add .
git commit -m "Fix: Critical auth bug"
git push

# 4. Render deploys in ~2-3 mins
# 5. Verify fix on production
```

**Result:** Fast deployment to production! ✅

---

## 🗄️ Database Strategy

### Local Database (SQLite)

**Purpose:** Testing and development

**Location:** `ai_studio.db` (local file)

**Advantages:**
- Fast and simple
- Easy to reset/delete
- No internet needed
- Free

**Use for:**
- Testing new features
- Experimenting with data
- Breaking things safely

**Reset Command:**
```bash
rm ai_studio.db
python scripts/migrate_database.py
python scripts/create_admin.py
```

---

### Production Database (PostgreSQL on Render)

**Purpose:** Real user data

**Location:** Render cloud

**Advantages:**
- Persistent (survives restarts)
- More powerful
- Supports multiple connections
- Backed up (on paid plan)

**Use for:**
- Real user accounts
- Production models/looks
- Actual application data

**⚠️ WARNING:** Never delete production database!

---

## 🌐 URL Strategy

### Local URLs (ngrok)

```
Base URL:    https://xxxxx-xxxxx-xxxxx.ngrok-free.app
Docs:        https://xxxxx-xxxxx-xxxxx.ngrok-free.app/docs
API:         https://xxxxx-xxxxx-xxxxx.ngrok-free.app/api/v1/...

Characteristics:
- Changes every time you restart
- Shows ngrok warning page (use bypass header)
- Temporary
```

**When to use:**
- Testing with frontend developers
- Quick demos
- Temporary sharing

---

### Production URLs (Render)

```
Base URL:    https://ai-studio-backend-ijkp.onrender.com
Docs:        https://ai-studio-backend-ijkp.onrender.com/docs
API:         https://ai-studio-backend-ijkp.onrender.com/api/v1/...

Characteristics:
- Never changes
- No warning pages
- Professional
- 24/7 available
```

**When to use:**
- Frontend production deployment
- Sharing with users
- Demos to stakeholders
- Always-on service

---

## 🎨 Frontend Configuration

### Create Environment Config in Frontend

```javascript
// frontend/config.js

const ENV = {
  development: {
    apiUrl: 'https://xxxxx.ngrok-free.app',  // Your current ngrok URL
    name: 'Development'
  },
  production: {
    apiUrl: 'https://ai-studio-backend-ijkp.onrender.com',
    name: 'Production'
  }
};

// Auto-detect or manual switch
const currentEnv = process.env.NODE_ENV === 'production' 
  ? ENV.production 
  : ENV.development;

export default currentEnv;
```

**Usage in frontend:**
```javascript
import config from './config';

// All API calls use this
const response = await fetch(`${config.apiUrl}/api/v1/models`);
```

**Benefits:**
- Easy switching between dev and prod
- One code change to switch environments
- No hardcoded URLs

---

## 🔐 Google OAuth Configuration

### You Need Both URLs in Google Console

Go to: https://console.cloud.google.com → APIs & Services → Credentials

**Add ALL these to "Authorized redirect URIs":**
```
https://ai-studio-backend-ijkp.onrender.com
https://ai-studio-backend-ijkp.onrender.com/api/v1/auth/google
https://your-current-ngrok-url.ngrok-free.app
https://your-current-ngrok-url.ngrok-free.app/api/v1/auth/google
```

**Add ALL these to "Authorized JavaScript origins":**
```
https://ai-studio-backend-ijkp.onrender.com
https://your-current-ngrok-url.ngrok-free.app
```

**⚠️ NOTE:** Update ngrok URL each time it changes (or upgrade to ngrok paid for static domains)

---

## 🧪 Testing Strategy

### Test Locally First

```bash
# 1. Start local server
python api_with_db_and_ngrok.py

# 2. Test endpoints manually
curl http://localhost:8000/health

# 3. Test with Swagger UI
open http://localhost:8000/docs

# 4. Test with your frontend
# Point frontend to ngrok URL
```

### Test on Production After Deploy

```bash
# 1. After git push, wait for Render deploy (~2-3 mins)

# 2. Test health endpoint
curl https://ai-studio-backend-ijkp.onrender.com/health

# 3. Test with Swagger UI
open https://ai-studio-backend-ijkp.onrender.com/docs

# 4. Test with production frontend
# Point frontend to production URL
```

---

## 📊 Quick Comparison Table

| Feature | Local Dev | Production |
|---------|-----------|------------|
| **URL** | ngrok (temporary) | Render (permanent) |
| **Database** | SQLite | PostgreSQL |
| **Data** | Test data | Real data |
| **Uptime** | When laptop is on | 24/7 |
| **Speed** | Instant | 2-3 min deploy |
| **Cost** | Free | Free (with limits) |
| **Risk** | Safe to break | Must be stable |
| **Use for** | Development | End users |

---

## 🎯 Best Practices

### ✅ DO:

1. **Develop locally first**
   - Test thoroughly before pushing

2. **Use meaningful commit messages**
   - "Fix: Auth bug in login"
   - "Add: New feature to models API"
   - "Update: Default settings schema"

3. **Test on production after each deploy**
   - Visit `/docs` to verify
   - Test critical endpoints

4. **Keep `.env` file local**
   - Never commit secrets to git
   - Set environment variables in Render dashboard

5. **Use git branches for big features** (optional)
   ```bash
   git checkout -b feature/new-ai-model
   # work on feature
   git commit -m "Add new AI model"
   git push origin feature/new-ai-model
   # Create PR on GitHub
   # Merge to main when ready
   ```

---

### ❌ DON'T:

1. **Don't test directly on production**
   - Always test locally first

2. **Don't commit `.env` files**
   - They're already ignored by `.gitignore`

3. **Don't delete production database**
   - It has real user data!

4. **Don't push broken code**
   - Test locally first

5. **Don't hardcode URLs in code**
   - Use environment variables

---

## 🚦 Git Workflow

### Simple Flow (Recommended for Solo Dev)

```bash
# 1. Make changes
code app/api/v1/endpoints/models.py

# 2. Check what changed
git status
git diff

# 3. Add and commit
git add .
git commit -m "Add new endpoint"

# 4. Push
git push

# 5. Render auto-deploys ✅
```

---

### Advanced Flow (For Team/Multiple Features)

```bash
# 1. Create feature branch
git checkout -b feature/new-look-creator

# 2. Make changes
code app/api/v1/endpoints/looks.py

# 3. Commit to feature branch
git add .
git commit -m "Add look creator API"
git push origin feature/new-look-creator

# 4. Create Pull Request on GitHub
# 5. Review and merge to main
# 6. Render deploys from main ✅
```

---

## 🔄 When to Use Which Environment

### Use Local Dev When:
- ✅ Writing new code
- ✅ Testing new features
- ✅ Debugging issues
- ✅ Experimenting
- ✅ Learning
- ✅ Breaking things (safe!)

### Use Production When:
- ✅ Showing to users
- ✅ Frontend integration (stable)
- ✅ Demos to stakeholders
- ✅ Need 24/7 availability
- ✅ Real user data
- ✅ Stable features only

---

## 📞 Troubleshooting

### "My local changes don't show on production"

**Solution:** Did you commit and push?
```bash
git add .
git commit -m "My changes"
git push
```

---

### "Production has an error but local works fine"

**Possible causes:**
1. Database difference (SQLite vs PostgreSQL)
2. Missing environment variable on Render
3. File path issues (absolute vs relative)

**Solution:**
- Check Render logs
- Verify environment variables in Render dashboard
- Test with PostgreSQL locally (optional)

---

### "ngrok URL keeps changing"

**Solution:**
- Free ngrok changes URL every restart
- Upgrade to ngrok paid ($8/month) for static domain
- Or just use production URL for frontend

---

### "Render app is slow (cold start)"

**Solution:**
- Free tier sleeps after 15 mins inactivity
- First request takes ~30 seconds (cold start)
- Upgrade to Starter plan ($7/month) to avoid cold starts
- Or use UptimeRobot to ping every 10 mins (free)

---

## 🎓 Summary

**Your Perfect Workflow:**

```
┌───────────────────────────────────────────────────┐
│                                                   │
│  1. Code locally                                  │
│  2. Test with local server + ngrok (optional)     │
│  3. When it works: git add, commit, push          │
│  4. Render auto-deploys to production             │
│  5. Test production URL                           │
│  6. Done! ✅                                       │
│                                                   │
└───────────────────────────────────────────────────┘
```

**Key Points:**
- 🏠 **Local = Safe playground**
- 🚀 **Production = Real deal**
- 📝 **Git push = Auto-deploy**
- ⏱️ **Deploy time = 2-3 minutes**
- 💰 **Cost = Free (both)**

---

## 🎉 You're All Set!

You now have:
- ✅ Local development environment
- ✅ Production deployment on Render
- ✅ Auto-deploy from GitHub
- ✅ Clear workflow strategy

**Happy coding!** 🚀

