# 📦 Assets Directory Structure

## 🎯 Overview

All images and rich assets are now stored in a dedicated, organized directory structure.

## 📁 Directory Structure

```
backend/
├── assets/
│   └── images/
│       ├── models/          # Uploaded model photos
│       ├── generated/       # AI-generated images
│       └── uploads/         # General uploads
```

### Purpose of Each Directory:

#### `assets/images/models/`
- **Purpose:** Store uploaded model photos
- **Usage:** User-uploaded images via `/api/v1/models/upload`
- **Example:** `models/abc123-photo.jpg`

#### `assets/images/generated/`
- **Purpose:** Store AI-generated images
- **Usage:** Images created via `/api/v1/models/generate`
- **Example:** `generated/xyz456-generated.png`

#### `assets/images/uploads/`
- **Purpose:** General file uploads
- **Usage:** Any other uploaded assets
- **Example:** `uploads/profile-pic.jpg`

---

## 🌐 Public URL Structure

### Local URLs:
```
http://localhost:8000/AIStudio/assets/models/image.jpg
```

### Public URLs (via ngrok):
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/assets/models/image.jpg
```

### URL Format:
```
{BASE_URL}/AIStudio/assets/{category}/{filename}
```

Where:
- `{BASE_URL}` = Your ngrok public URL
- `{category}` = models, generated, or uploads
- `{filename}` = Unique filename with UUID

---

## ✅ Benefits

### 1. **Organized Storage**
- Separate directories for different asset types
- Easy to manage and backup
- Clear file organization

### 2. **Public Accessibility**
- All images accessible via public URLs
- Works through ngrok tunnel
- No localhost-only URLs

### 3. **Scalable Structure**
- Easy to add new asset categories
- Clear separation of concerns
- Production-ready organization

### 4. **Version Control Friendly**
- `.gitignore` setup to exclude assets
- Assets directory structure committed
- Large files not in repository

---

## 🔧 Configuration

### Environment Variables:

#### Current (Automatic):
```bash
NGROK_PUBLIC_URL=https://zestfully-chalky-nikia.ngrok-free.dev
```
Set automatically in `api_with_db_and_ngrok.py`

#### Optional (Override):
```bash
# In .env file or environment
BASE_URL=https://your-custom-domain.com
```

### Storage Service:
The storage service (`app/core/storage.py`) automatically:
1. Creates asset directories
2. Saves files in appropriate subdirectories
3. Returns public URLs (ngrok or custom domain)

---

## 📝 Example Usage

### Upload Model Image:
```bash
curl -X POST "http://localhost:8000/api/v1/models/upload" \
  -F "name=Emma Watson" \
  -F "image=@photo.jpg"
```

**Response:**
```json
{
  "id": "abc-123-def",
  "name": "Emma Watson",
  "image_url": "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/assets/models/abc-123.jpg",
  ...
}
```

### Generate AI Image:
```bash
curl -X POST "http://localhost:8000/api/v1/models/generate" \
  -H "Content-Type: application/json" \
  -d '{"name":"Sophia","prompt_details":"elegant dress"}'
```

**Response:**
```json
{
  "id": "xyz-456-abc",
  "name": "Sophia",
  "image_url": "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/assets/generated/xyz-456.png",
  ...
}
```

---

## 🧪 Testing Public URLs

### Test Script:
```bash
cd /Users/dgolani/Documents/AI_Studio/backend
./TEST_IMAGE_UPLOAD.sh
```

This will:
1. Create a test image
2. Upload it to the API
3. Verify the public URL
4. Test accessibility
5. Show you the public URL

### Manual Test:
```bash
# 1. Upload an image
curl -X POST "http://localhost:8000/api/v1/models/upload" \
  -F "name=Test" \
  -F "image=@test.jpg"

# 2. Copy the image_url from response

# 3. Open in browser or test with curl:
curl -I {image_url}
# Should return: 200 OK
```

---

## 🔒 Security & Best Practices

### 1. **File Validation**
- ✅ File type validation (images only)
- ✅ File size limits (can be configured)
- ✅ Sanitized filenames (UUID-based)

### 2. **Access Control**
- ✅ Public read access (for image viewing)
- ✅ Upload requires API access
- ✅ Delete requires API access

### 3. **Storage Management**
```bash
# Check storage usage
du -sh assets/

# Clean up old files (manual for now)
find assets/images/ -type f -mtime +30 -delete
```

### 4. **Backup Strategy**
- Regular backups recommended for production
- Can sync to cloud storage
- Version control excludes large files

---

## 📊 File Organization Example

```
assets/images/
├── models/
│   ├── 550e8400-e29b-41d4-a716-446655440000.jpg
│   ├── 6ba7b810-9dad-11d1-80b4-00c04fd430c8.jpg
│   └── 7c9e6679-7425-40de-944b-e07fc1f90ae7.png
├── generated/
│   ├── ai-123-generated.png
│   ├── ai-456-generated.png
│   └── ai-789-generated.png
└── uploads/
    ├── profile-abc.jpg
    └── banner-xyz.png
```

---

## 🚀 Migration from Old Structure

If you have files in `/tmp/uploads/`, they will continue to work, but new uploads will use the new structure.

### No action needed!
- Old URLs will still work (backward compatible)
- New uploads automatically use new structure
- Storage service handles both formats

---

## 🌥️ Google Cloud Storage Integration

When you enable Google Cloud Storage (later):
- Same directory structure applies
- Bucket structure mirrors local structure
- URLs change to `storage.googleapis.com/...`
- Migration is seamless

---

## 💡 Tips

### 1. **Monitoring Storage**
```bash
# Check total storage used
du -sh assets/

# Count files by category
find assets/images/models -type f | wc -l
find assets/images/generated -type f | wc -l
```

### 2. **Cleanup Old Files**
```bash
# Find files older than 30 days
find assets/images/ -type f -mtime +30

# Delete (be careful!)
find assets/images/ -type f -mtime +30 -delete
```

### 3. **Backup Assets**
```bash
# Create backup
tar -czf assets-backup-$(date +%Y%m%d).tar.gz assets/

# Or sync to cloud
rsync -av assets/ /backup/location/
```

---

## ✅ Summary

**Current Setup:**
- ✅ Organized assets directory structure
- ✅ Public URLs via ngrok
- ✅ Automatic categorization (models/generated/uploads)
- ✅ Production-ready organization
- ✅ Backward compatible with old URLs

**Your Images Are Now:**
- 🌐 Publicly accessible
- 📁 Well organized
- 🔐 Properly secured
- 🚀 Ready for scaling

**Test It:**
```bash
./TEST_IMAGE_UPLOAD.sh
```

Happy coding! 🎉


