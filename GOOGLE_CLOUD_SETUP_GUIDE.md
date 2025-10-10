# Google Cloud Storage Setup Guide

## 🎯 Overview

Your backend currently uses **local file storage** which works great for development. This guide shows you how to enable **Google Cloud Storage** for production use.

---

## ✅ Current Setup (No Action Needed)

**Storage:** Local files (`/tmp/uploads/`)  
**Status:** ✅ Working  
**Image URLs:** `http://localhost:8000/uploads/models/...`

This is perfect for testing and development!

---

## 🌥️ Why Use Google Cloud Storage?

### Benefits:
- ✅ **Permanent Storage** - Files won't be deleted
- ✅ **Global CDN** - Fast access worldwide
- ✅ **Scalable** - No disk space limits
- ✅ **Professional URLs** - `https://storage.googleapis.com/...`
- ✅ **Automatic Backups** - Built-in redundancy

### When to Enable:
- Moving to production
- Need permanent image storage
- Sharing with users globally
- Scaling to many users

---

## 📋 Setup Steps (When Ready)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your **Project ID** (you'll need this)

### Step 2: Enable Required APIs

1. In Google Cloud Console, go to **APIs & Services** > **Library**
2. Search and enable:
   - **Cloud Storage API**
   - **Vertex AI API** (if using AI generation)

### Step 3: Create a Storage Bucket

1. Go to **Cloud Storage** > **Buckets**
2. Click **Create Bucket**
3. Choose a unique name (e.g., `ai-studio-models-production`)
4. Select:
   - **Location:** Choose closest to your users
   - **Storage Class:** Standard
   - **Access Control:** Fine-grained
5. Click **Create**

### Step 4: Set Bucket Permissions (Public Access)

1. Click on your bucket name
2. Go to **Permissions** tab
3. Click **Grant Access**
4. Add principal: `allUsers`
5. Role: **Storage Object Viewer**
6. Click **Save**

**Note:** This makes uploaded images publicly accessible (required for your use case).

### Step 5: Create Service Account

1. Go to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Name: `ai-studio-backend`
4. Click **Create and Continue**
5. Role: **Storage Admin**
6. Click **Continue** then **Done**

### Step 6: Generate Service Account Key

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** > **Create New Key**
4. Choose **JSON** format
5. Click **Create**
6. Save the downloaded JSON file securely

**Important:** Keep this file safe! It's like a password.

### Step 7: Configure Your Backend

#### Option A: Using Environment Variables

Create or update `.env` file in your backend directory:

```bash
# Enable Google Cloud Storage
USE_GCS=true
GCS_BUCKET_NAME=ai-studio-models-production

# Path to your service account key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# Optional: Enable AI Image Generation
ENABLE_AI_GENERATION=false  # Set to true if you want AI generation
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

#### Option B: Export as Shell Variables

```bash
export USE_GCS=true
export GCS_BUCKET_NAME=ai-studio-models-production
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
```

### Step 8: Restart Your Backend

```bash
# Stop current backend
lsof -ti:8000 | xargs kill -9

# Restart with new configuration
cd /Users/dgolani/Documents/AI_Studio/backend
source venv/bin/activate
python api_with_db_and_ngrok.py
```

### Step 9: Test It

```bash
# Upload a test image
curl -X POST "http://localhost:8000/api/v1/models/upload" \
  -F "name=Test GCS" \
  -F "image=@test.jpg"

# Check the image_url in response - should be:
# https://storage.googleapis.com/your-bucket-name/models/...
```

---

## 🧪 Verification

After setup, check if Google Cloud Storage is active:

```bash
curl http://localhost:8000/api/v1/models/upload
```

Look at the `image_url` in the response:
- **Local Storage:** `http://localhost:8000/uploads/...`
- **Google Cloud Storage:** `https://storage.googleapis.com/...`

---

## 💰 Cost Considerations

### Google Cloud Storage Pricing (as of 2025):

**Storage:**
- First 5 GB: ~$0.02/GB/month
- 5-500 GB: ~$0.02/GB/month

**Bandwidth:**
- First 1 GB: Free
- After that: ~$0.12/GB

**For a typical small app:**
- 100 images (~10 MB each) = 1 GB storage
- 1000 views/month = ~1 GB bandwidth
- **Estimated cost:** $0.02 - $0.15/month

**Free Tier:**
- Google Cloud offers $300 free credit for new users
- Free tier for small usage

### Cost Saving Tips:
1. Start with local storage for development
2. Move to GCS only when going to production
3. Set up lifecycle rules to delete old unused images
4. Use appropriate storage class (Standard vs Coldline)

---

## 🔒 Security Best Practices

### 1. Service Account Key
- ✅ Never commit to Git
- ✅ Add to `.gitignore`
- ✅ Store securely
- ✅ Rotate periodically

### 2. Bucket Permissions
- ✅ Use least privilege
- ✅ Public read only (not write)
- ✅ Enable versioning for recovery
- ✅ Set up lifecycle policies

### 3. Environment Variables
- ✅ Use `.env` file (not in Git)
- ✅ Different keys for dev/prod
- ✅ Never hardcode in code

---

## 🐛 Troubleshooting

### Issue: "403 Forbidden" when uploading

**Solution:**
- Check service account has **Storage Admin** role
- Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Ensure service account key is valid

### Issue: "Bucket not found"

**Solution:**
- Check bucket name in `GCS_BUCKET_NAME`
- Verify bucket exists in correct project
- Check project ID matches

### Issue: Images not accessible

**Solution:**
- Check bucket has public read permissions
- Verify `allUsers` has **Storage Object Viewer** role
- Test URL directly in browser

### Issue: Backend still using local storage

**Solution:**
- Verify `USE_GCS=true` in environment
- Restart backend after changing config
- Check backend logs for GCS initialization

---

## 📊 Comparison: Local vs Google Cloud Storage

| Feature | Local Storage | Google Cloud Storage |
|---------|--------------|---------------------|
| **Setup** | ✅ None needed | ⚠️ Requires setup |
| **Cost** | ✅ Free | 💰 ~$0.02/GB/month |
| **Permanence** | ⚠️ Can be deleted | ✅ Permanent |
| **Scalability** | ⚠️ Limited by disk | ✅ Unlimited |
| **Performance** | ✅ Fast locally | ✅ Global CDN |
| **URLs** | ⚠️ localhost:8000 | ✅ storage.googleapis.com |
| **Production Ready** | ❌ No | ✅ Yes |
| **Best For** | 🧪 Development | 🚀 Production |

---

## 🎯 Recommendation

### For Development/Testing (Current):
✅ **Keep using local storage**
- Already configured
- No cost
- Fast and simple
- Perfect for API testing

### For Production (Future):
🌥️ **Switch to Google Cloud Storage**
- Follow this guide
- Professional and scalable
- Better user experience
- Required for real-world use

---

## 📚 Additional Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [GCS Pricing Calculator](https://cloud.google.com/products/calculator)
- [Python Client Library](https://cloud.google.com/python/docs/reference/storage/latest)

---

## ✅ Quick Checklist

When ready to enable Google Cloud Storage:

- [ ] Create Google Cloud project
- [ ] Enable Cloud Storage API
- [ ] Create storage bucket
- [ ] Set bucket to public read
- [ ] Create service account
- [ ] Download service account key
- [ ] Update `.env` file with credentials
- [ ] Set `USE_GCS=true`
- [ ] Restart backend
- [ ] Test image upload
- [ ] Verify image URL uses storage.googleapis.com

---

## 🎉 Summary

**Right Now:**
- ✅ Your backend works with local storage
- ✅ No action needed for development
- ✅ Perfect for testing your API

**When Going to Production:**
- Follow this guide to enable Google Cloud Storage
- Estimated setup time: 15-30 minutes
- Monthly cost: ~$0.02-$0.15 for small usage

**Questions?**
- Check the troubleshooting section
- Review your backend logs
- Test with local storage first

Happy coding! 🚀

