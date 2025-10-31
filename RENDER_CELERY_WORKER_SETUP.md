# Complete Guide: Setting Up Celery Background Worker on Render

**Based on official Render documentation:** https://render.com/docs/deploy-celery

## 📋 Prerequisites
- ✅ Your main backend service is already running on Render
- ✅ Redis service is created on Render
- ✅ You have your Redis URL (e.g., `redis://red-xxxxx:6379`)

---

## 🚀 Step-by-Step Instructions

### Step 1: Create Background Worker Service

1. **Go to Render Dashboard**
   - Navigate to https://dashboard.render.com
   - Click the **"+ New"** button (top right)
   - Select **"Background Worker"**

### Step 2: Connect Your Repository

1. **Select Source Code**
   - Choose **"Git Provider"** tab
   - Find and select: **`dineshsunshine / ai-studio-backend`**
   - Click to connect

### Step 3: Configure Service Settings

Fill in the following fields:

#### **Name:**
```
ai-studio-video-worker
```
(Or any name you prefer)

#### **Region:**
```
Oregon (or your preferred region)
```

#### **Branch:**
```
main
```
(Or your default branch)

#### **Root Directory:**
```
backend
```
(Leave empty if your repo root contains all files directly)

#### **Environment:**
```
Python 3
```
(Select **Python 3**, NOT Docker)

#### **Build Command:**
```
pip install --upgrade pip && pip install -r requirements.txt
```

#### **Start Command:**
```
celery -A app.core.celery_app worker --loglevel=info --concurrency=3 --queues=video_generation --pool=prefork
```

**Note:** According to [Render's official documentation](https://render.com/docs/deploy-celery), the format is:
- `celery --app <module> worker --loglevel <level> --concurrency <number>`
- For our app: `celery -A app.core.celery_app worker --loglevel=info --concurrency=3 --queues=video_generation --pool=prefork`

⚠️ **IMPORTANT:** Make sure you select **Python 3** environment, NOT Docker. If you see Docker settings, go back and select Python.

### Step 4: Add Environment Variables

Click **"Add Environment Variable"** and add ALL of these (copy from your main backend service):

#### **Critical Variables:**

1. **REDIS_URL**
   - Key: `REDIS_URL`
   - Value: `redis://red-d42dbtjipnbc73c8ed4g:6379`
   - (Use your actual Redis URL)

2. **DATABASE_URL**
   - Key: `DATABASE_URL`
   - Value: (Same as your backend service)
   - Or: Use "Add from Database" if connected to your database service

3. **GOOGLE_API_KEY**
   - Key: `GOOGLE_API_KEY`
   - Value: (Your Google API key for Veo)

4. **Cloudinary Credentials:**
   - `CLOUDINARY_CLOUD_NAME` = (Your cloud name)
   - `CLOUDINARY_API_KEY` = (Your API key)
   - `CLOUDINARY_API_SECRET` = (Your API secret)
   - `USE_CLOUDINARY` = `true`

5. **JWT & Auth:**
   - `JWT_SECRET_KEY` = (Same as backend)
   - `JWT_ALGORITHM` = `HS256`
   - `GOOGLE_CLIENT_ID` = (Same as backend)
   - `GOOGLE_CLIENT_SECRET` = (Same as backend)

6. **Other Variables:**
   - Copy ALL other environment variables from your main backend service
   - They should be identical

### Step 5: Advanced Settings (Optional)

- **Plan:** Free (or upgrade to Starter for no cold starts)
- **Auto-Deploy:** Enable (so it auto-updates when you push to main)

### Step 6: Create the Worker

Click **"Create Background Worker"** at the bottom.

---

## ✅ Verification Steps

After the worker deploys, check the **Logs** tab. You should see:

```
✅ Settings loaded from .env file
✅ Connected to redis://red-xxxxx:6379/0
[2025-XX-XX XX:XX:XX,XXX: INFO/MainProcess] celery@xxxxx ready.
```

**You should see:**
- ✅ Celery worker starting messages
- ✅ "Connected to redis://..."
- ✅ "celery@... ready"
- ✅ `[tasks] . app.workers.video_worker.process_video_generation`

**You should NOT see:**
- ❌ Uvicorn messages (that's for web servers, not workers)
- ❌ "Application startup complete" (that's FastAPI/Uvicorn)

---

## 🔧 Troubleshooting

### Issue: Worker shows Uvicorn logs instead of Celery

**Solution:** Check your **Start Command**:
- ❌ Wrong: `python start_production.py`
- ✅ Correct: `celery -A app.core.celery_app worker --loglevel=info --concurrency=3 --queues=video_generation --pool=prefork`

### Issue: "Connection refused" to Redis

**Solution:** 
1. Check `REDIS_URL` is set correctly
2. Verify Redis service is running
3. Use Internal Redis URL from your Redis service (not external)

### Issue: Jobs still pending

**Solution:**
1. Verify worker logs show "ready" status
2. Check worker is listening to `video_generation` queue
3. Ensure worker has same environment variables as backend

### Issue: Can't find "Start Command" field

**Solution:**
1. Make sure you selected **Python 3** environment (not Docker)
2. The Start Command field appears after selecting Python
3. If you see Docker settings, delete the service and recreate with Python

---

## 📊 Expected Worker Logs

When everything is working correctly, you should see logs like:

```
[2025-10-31 15:00:00,000: INFO/MainProcess] Connected to redis://red-xxxxx:6379/0
[2025-10-31 15:00:00,000: INFO/MainProcess] mingle: searching for neighbors
[2025-10-31 15:00:00,000: INFO/MainProcess] mingle: all alone
[2025-10-31 15:00:00,000: INFO/MainProcess] celery@worker-name ready.

[tasks]
  . app.workers.video_worker.process_video_generation
```

---

## 🎯 Next Steps

Once the worker is running:
1. Your PENDING video jobs should automatically start processing
2. Monitor progress at: https://ai-studio-backend-ijkp.onrender.com/video-monitor
3. Check worker logs to see job processing in real-time

---

## 🔗 Resources

- **Official Render Celery Guide:** https://render.com/docs/deploy-celery ⭐
- Render Background Workers: https://render.com/docs/background-workers
- Celery Documentation: https://docs.celeryproject.org/

---

**Need Help?** If you're stuck on any step, check the worker logs in Render Dashboard for error messages!

