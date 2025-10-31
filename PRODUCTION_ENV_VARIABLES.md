# Production Environment Variables for Render

## ✅ Already Configured in render.yaml

These are already set or auto-configured:

- `DATABASE_URL` - Auto-set from Render database service
- `JWT_ALGORITHM` - Set to `HS256`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Set to `30`
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS` - Set to `7`
- `PYTHON_VERSION` - Set to `3.11.0`
- `PORT` - Auto-set by Render

---

## 🔴 REQUIRED - Must Add Manually in Render Dashboard

These need to be added in your Render service's **Environment** tab:

### 1. Authentication & Security

```bash
# JWT Secret Key (generate a strong random string)
JWT_SECRET_KEY=your-super-secret-jwt-key-here

# Google OAuth (for user login)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# First admin user (email address)
FIRST_ADMIN_EMAIL=your-email@gmail.com
```

### 2. Video Generation (CRITICAL - New!)

```bash
# Google API Key for Veo 3.1 video generation
GOOGLE_API_KEY=AIzaSyBxZ29T3jDIsNT8WKk_HTERs4EyWgBLJlw

# Redis URL for Celery worker queue (video generation needs this)
REDIS_URL=redis://localhost:6379/0
# ⚠️ NOTE: You'll need to add a Redis service in Render or use an external Redis instance
```

### 3. Cloudinary (For Video & Image Storage)

```bash
# Cloudinary credentials (for production video/image storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-api-secret

# Enable Cloudinary storage
USE_CLOUDINARY=true
```

---

## 🟡 Optional but Recommended

```bash
# CORS Origins (if your frontend URL is different from default)
CORS_ORIGINS=https://your-frontend-domain.com,https://your-ngrok-url.ngrok-free.dev

# Ngrok (only if you're using ngrok in production - usually not needed)
NGROK_AUTH_TOKEN=your-ngrok-auth-token
NGROK_DOMAIN=your-ngrok-domain
NGROK_PUBLIC_URL=https://your-domain.ngrok-free.dev/AIStudio
```

---

## 🚨 CRITICAL FOR VIDEO GENERATION

**You MUST add these for video generation to work:**

1. **GOOGLE_API_KEY** - Your Google GenAI API key for Veo 3.1
2. **REDIS_URL** - URL for Redis service (needed for Celery worker queue)
3. **Cloudinary credentials** - For storing generated videos

---

## 📋 Quick Checklist

- [ ] `JWT_SECRET_KEY` (generate strong random string)
- [ ] `GOOGLE_CLIENT_ID`
- [ ] `GOOGLE_CLIENT_SECRET`
- [ ] `FIRST_ADMIN_EMAIL`
- [ ] `GOOGLE_API_KEY` ⚠️ **NEW - Required for video generation**
- [ ] `REDIS_URL` ⚠️ **NEW - Required for video generation**
- [ ] `CLOUDINARY_CLOUD_NAME` ⚠️ **NEW - For video storage**
- [ ] `CLOUDINARY_API_KEY` ⚠️ **NEW - For video storage**
- [ ] `CLOUDINARY_API_SECRET` ⚠️ **NEW - For video storage**
- [ ] `USE_CLOUDINARY=true` ⚠️ **NEW - Enable Cloudinary**

---

## 🛠️ How to Add in Render

1. Go to your Render Dashboard
2. Select your **ai-studio-backend** service
3. Click on **Environment** tab
4. Click **Add Environment Variable**
5. Add each variable above
6. Click **Save Changes**
7. Service will auto-restart

---

## ⚠️ Important Notes

1. **Redis Service**: You'll need to either:
   - Add a Redis service in Render (free tier available)
   - Use an external Redis service (Redis Cloud, Upstash, etc.)
   - Update `REDIS_URL` with your Redis connection string

2. **Video Generation**: Without `GOOGLE_API_KEY` and `REDIS_URL`, video generation will NOT work.

3. **Video Storage**: Without Cloudinary credentials, videos will be stored locally (not recommended for production).

4. **Security**: Never commit secrets to git. All secrets are marked as `sync: false` in render.yaml.

