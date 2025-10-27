# Cloudinary Setup Guide for AI Studio

## Why Cloudinary?

- ✅ **25GB storage + 25GB bandwidth FREE**
- ✅ Built-in CDN for fast image delivery
- ✅ Automatic image optimization
- ✅ Permanent storage (never loses files)
- ✅ Easy integration

---

## Step 1: Get Cloudinary Credentials

### Create Account

1. Go to: https://cloudinary.com/users/register_free
2. Sign up with your email
3. Verify your email
4. You'll be taken to the dashboard

### Get Your Credentials

After signing in, you'll see your **Account Details** on the dashboard:

```
Cloud Name: your-cloud-name
API Key: 123456789012345
API Secret: AbCdEfGhIjKlMnOpQrStUvWxYz
```

**Important**: Copy these values - you'll need them!

---

## Step 2: Add Credentials to Render

### On Render Dashboard:

1. Go to: https://dashboard.render.com/
2. Select your service: **`ai-studio-backend`**
3. Click **"Environment"** tab
4. Add these environment variables:

```
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=AbCdEfGhIjKlMnOpQrStUvWxYz
USE_CLOUDINARY=true
```

5. Click **"Save Changes"**
6. Render will auto-deploy (~2-3 minutes)

---

## Step 3: That's It!

Once deployed:
- ✅ All new images will be stored on Cloudinary
- ✅ Images will have permanent URLs
- ✅ No more lost images after service restarts
- ✅ Fast CDN delivery worldwide

---

## Image URL Format

**Old (local storage)**:
```
https://ai-studio-backend-ijkp.onrender.com/assets/images/models/abc.jpeg
```

**New (Cloudinary)**:
```
https://res.cloudinary.com/your-cloud-name/image/upload/v1234567890/models/abc.jpeg
```

---

## Configuration Details

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CLOUDINARY_CLOUD_NAME` | Your Cloudinary cloud name | `my-cloud` |
| `CLOUDINARY_API_KEY` | Your API Key | `123456789012345` |
| `CLOUDINARY_API_SECRET` | Your API Secret | `AbCdEfGhIjKlMnOpQr` |
| `USE_CLOUDINARY` | Enable Cloudinary | `true` |

### Folder Structure in Cloudinary

Images will be organized as:
```
cloudinary/
├── models/          (Model images)
├── looks/           (Look images)
├── products/        (Product thumbnails)
├── generated/       (AI-generated images)
└── uploads/         (General uploads)
```

---

## Testing

### After Deployment

1. **Upload a test model** via your frontend
2. **Check the image URL** in the API response
3. It should start with: `https://res.cloudinary.com/`
4. **Open the URL** in a browser - image should load instantly

### Check Cloudinary Dashboard

1. Go to: https://console.cloudinary.com/
2. Click **"Media Library"**
3. You should see your uploaded images organized by folder

---

## Benefits

### 1. Permanent Storage
- Files never disappear (unlike Render free tier)
- Database + files both persist

### 2. Fast CDN Delivery
- Images served from nearest location to users
- Automatic caching
- Much faster than serving from Render

### 3. Image Optimization
- Cloudinary automatically optimizes images
- Reduces bandwidth and improves load times
- Can transform images on-the-fly (resize, crop, etc.)

### 4. Free Tier Limits

**Generous free tier**:
- 25 GB storage
- 25 GB bandwidth/month
- 25,000 transformations/month
- More than enough for most applications!

---

## Troubleshooting

### Issue: "Invalid credentials"

**Solution**: Double-check your credentials in Render environment variables:
- Cloud name should be lowercase, no spaces
- API Key should be numbers only
- API Secret should be exact (case-sensitive)

### Issue: "Module not found: cloudinary"

**Solution**: The `cloudinary` package is already in `requirements.txt`. Render should install it automatically. If not, check Render logs during build.

### Issue: Images still using local storage

**Check**:
1. `USE_CLOUDINARY=true` is set in Render environment
2. Service has redeployed after adding env vars
3. Check Render logs for any Cloudinary errors

### Issue: "Resource not found"

**Solution**: This means the image was uploaded but the URL is incorrect. Check:
- Cloud name in environment matches your Cloudinary account
- Image exists in Cloudinary Media Library

---

## Migration from Local Storage

### What Happens to Old Images?

Old images stored locally on Render will:
- ❌ Be lost when service restarts (as before)
- ❌ Not be migrated automatically

New images will:
- ✅ Be stored on Cloudinary permanently
- ✅ Survive service restarts

### If You Want to Migrate Old Images

You would need to:
1. Download old images from database URLs (if still available)
2. Re-upload them via the API
3. They'll be stored on Cloudinary

**Note**: Since Render's free tier is ephemeral, old images are likely already gone unless you just uploaded them.

---

## Advanced Features (Optional)

### Image Transformations

Cloudinary allows on-the-fly transformations by modifying the URL:

```
# Original
https://res.cloudinary.com/my-cloud/image/upload/v123/models/abc.jpeg

# Resize to 300x300
https://res.cloudinary.com/my-cloud/image/upload/w_300,h_300,c_fill/v123/models/abc.jpeg

# Auto quality optimization
https://res.cloudinary.com/my-cloud/image/upload/q_auto/v123/models/abc.jpeg
```

This can be added later for optimization!

---

## Security

### Keeping Secrets Safe

✅ **DO**:
- Store credentials in Render environment variables
- Never commit credentials to Git
- Use `.env` files for local development (already in `.gitignore`)

❌ **DON'T**:
- Put credentials in code files
- Share API Secret publicly
- Commit `.env` files to Git

---

## Cost Monitoring

### Check Usage

1. Go to: https://console.cloudinary.com/
2. Click **"Dashboard"**
3. See your current usage:
   - Storage used
   - Bandwidth used this month
   - Transformations used

### If You Exceed Free Tier

You'll be notified, but you won't be charged unless you upgrade to a paid plan.

---

## Next Steps After Setup

1. ✅ Add Cloudinary credentials to Render
2. ✅ Wait for deployment
3. ✅ Test by uploading an image
4. ✅ Verify image URL starts with `res.cloudinary.com`
5. ✅ Check Cloudinary dashboard to see your images

**Total setup time**: ~5 minutes

---

## Support

- **Cloudinary Docs**: https://cloudinary.com/documentation
- **API Reference**: https://cloudinary.com/documentation/image_upload_api_reference
- **Community**: https://community.cloudinary.com/

---

## Summary

**What you need**:
1. Cloudinary account (free)
2. Three environment variables on Render
3. That's it!

**What you get**:
- Permanent image storage
- Fast CDN delivery
- No more lost images
- Professional image hosting

🚀 Ready to set up? Just add those environment variables on Render!


