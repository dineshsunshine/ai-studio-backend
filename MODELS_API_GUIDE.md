# Models API - Complete Guide

## 🎯 Overview

The Models API provides endpoints for managing fashion model images. Models can be:
1. **Uploaded** - Upload your own image files
2. **AI-Generated** - Generate images using Google's Imagen AI model

---

## 📋 API Endpoints

### Base URL
```
Local:  http://localhost:8000/api/v1/models
Public: https://your-ngrok-url.ngrok.io/AIStudio/api/v1/models
```

---

## 🔍 1. GET All Models

**Endpoint:** `GET /api/v1/models/`

**Description:** Fetch all models from the database

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/models/?skip=0&limit=10"
```

**Example Response:**
```json
{
  "models": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Emma",
      "image_url": "https://storage.googleapis.com/bucket/models/image.jpg",
      "prompt_details": null,
      "created_at": "2025-10-09T10:00:00Z",
      "updated_at": "2025-10-09T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

## 📤 2. POST Upload Model

**Endpoint:** `POST /api/v1/models/upload`

**Description:** Upload a new model with an image file

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `name` (required): Name of the model
- `image` (required): Image file (JPEG, PNG, etc.)

**Example Request (using curl):**
```bash
curl -X POST "http://localhost:8000/api/v1/models/upload" \
  -F "name=Emma Watson" \
  -F "image=@/path/to/image.jpg"
```

**Example Request (using Python):**
```python
import requests

url = "http://localhost:8000/api/v1/models/upload"
files = {"image": open("model_photo.jpg", "rb")}
data = {"name": "Emma Watson"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

**Example Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Emma Watson",
  "image_url": "http://localhost:8000/uploads/models/unique-id.jpg",
  "prompt_details": null,
  "created_at": "2025-10-09T10:00:00Z",
  "updated_at": "2025-10-09T10:00:00Z"
}
```

**Status Code:** `201 Created`

---

## 🤖 3. POST Generate Model with AI

**Endpoint:** `POST /api/v1/models/generate`

**Description:** Generate a model image using AI (Google Imagen)

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "name": "Sophia",
  "prompt_details": "wearing elegant evening gown, long dark hair, confident smile"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/models/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sophia",
    "prompt_details": "wearing elegant evening gown, long dark hair, confident smile"
  }'
```

**Example Response:**
```json
{
  "id": "456e7890-e89b-12d3-a456-426614174001",
  "name": "Sophia",
  "image_url": "http://localhost:8000/uploads/models/sophia-generated.png",
  "prompt_details": "wearing elegant evening gown, long dark hair, confident smile",
  "created_at": "2025-10-09T10:05:00Z",
  "updated_at": "2025-10-09T10:05:00Z"
}
```

**Status Code:** `201 Created`

**Note:** 
- If AI generation is not enabled (`ENABLE_AI_GENERATION=false`), a mock placeholder image will be generated instead
- The full prompt sent to the AI includes professional photography context automatically

---

## 🗑️ 4. DELETE Model

**Endpoint:** `DELETE /api/v1/models/{model_id}`

**Description:** Delete a model and its associated image

**Path Parameters:**
- `model_id` (required): UUID of the model to delete

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/models/123e4567-e89b-12d3-a456-426614174000"
```

**Response:** No content

**Status Code:** `204 No Content`

---

## 🔍 5. GET Single Model

**Endpoint:** `GET /api/v1/models/{model_id}`

**Description:** Get a specific model by ID

**Path Parameters:**
- `model_id` (required): UUID of the model

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/models/123e4567-e89b-12d3-a456-426614174000"
```

**Example Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Emma Watson",
  "image_url": "http://localhost:8000/uploads/models/unique-id.jpg",
  "prompt_details": null,
  "created_at": "2025-10-09T10:00:00Z",
  "updated_at": "2025-10-09T10:00:00Z"
}
```

**Status Code:** `200 OK`

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with these settings:

```bash
# Database
DATABASE_URL=sqlite:///./ai_studio.db

# Cloud Storage (Optional - defaults to local storage)
USE_GCS=false
GCS_BUCKET_NAME=ai-studio-models
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# AI Generation (Optional - defaults to mock images)
ENABLE_AI_GENERATION=false
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Local Storage
LOCAL_UPLOAD_DIR=/tmp/uploads
BASE_URL=http://localhost:8000
```

### Storage Options

#### Option 1: Local File Storage (Default)
- Files stored in `/tmp/uploads/`
- Accessible via `http://localhost:8000/uploads/`
- Perfect for development and testing
- No additional setup required

#### Option 2: Google Cloud Storage
1. Set `USE_GCS=true`
2. Create a GCS bucket
3. Set `GCS_BUCKET_NAME=your-bucket-name`
4. Configure service account credentials
5. Set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`

### AI Generation Options

#### Option 1: Mock Images (Default)
- Simple placeholder images
- No AI setup required
- Perfect for testing the API flow

#### Option 2: Google Imagen AI
1. Set `ENABLE_AI_GENERATION=true`
2. Set your Google Cloud project: `GOOGLE_CLOUD_PROJECT=your-project-id`
3. Enable Vertex AI API in your Google Cloud project
4. Configure authentication

---

## 🧪 Testing the API

### Quick Test Script

```bash
#!/bin/bash

# 1. Upload a model
echo "1. Uploading model..."
curl -X POST "http://localhost:8000/api/v1/models/upload" \
  -F "name=Test Model" \
  -F "image=@test_image.jpg"

echo -e "\n\n2. Generating AI model..."
# 2. Generate an AI model
curl -X POST "http://localhost:8000/api/v1/models/generate" \
  -H "Content-Type: application/json" \
  -d '{"name":"AI Model","prompt_details":"casual outfit, friendly smile"}'

echo -e "\n\n3. Getting all models..."
# 3. Get all models
curl -X GET "http://localhost:8000/api/v1/models/"

echo -e "\n\n4. Deleting model (replace ID)..."
# 4. Delete a model (replace with actual ID)
# curl -X DELETE "http://localhost:8000/api/v1/models/YOUR-MODEL-ID"
```

### Using the Interactive API Docs

1. Start your backend server
2. Open in browser: `http://localhost:8000/docs`
3. Expand the "models" section
4. Try the endpoints with the "Try it out" button

---

## ❌ Error Responses

### 400 Bad Request
```json
{
  "detail": "Uploaded file must be an image"
}
```

### 404 Not Found
```json
{
  "detail": "Model with id {id} not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to upload image: {error message}"
}
```

---

## 📊 Database Schema

```sql
CREATE TABLE models (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image_url VARCHAR(512) NOT NULL,
    prompt_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_models_name ON models(name);
CREATE INDEX idx_models_created_at ON models(created_at);
```

---

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create database tables:**
   ```bash
   python -c "from app.models.model import Model; from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

3. **Start the server:**
   ```bash
   python api_with_db_and_ngrok.py
   ```

4. **Test the API:**
   ```bash
   curl http://localhost:8000/api/v1/models/
   ```

---

## 💡 Tips & Best Practices

1. **Image Formats:** Support for JPEG, PNG, GIF, WebP
2. **File Sizes:** Consider adding file size limits for uploads
3. **Validation:** All image files are validated before upload
4. **URLs:** Image URLs are public and accessible without authentication
5. **Cleanup:** Deleting a model also deletes its image from storage
6. **Pagination:** Use `skip` and `limit` for large datasets
7. **Error Handling:** All endpoints return appropriate HTTP status codes

---

## 🔐 Security Considerations

- Add authentication/authorization if needed
- Validate file types and sizes
- Sanitize file names
- Consider rate limiting for uploads
- Use HTTPS in production
- Restrict CORS origins in production

---

## 📱 Frontend Integration Example

```javascript
// Upload a model
async function uploadModel(name, imageFile) {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('image', imageFile);
  
  const response = await fetch('http://localhost:8000/api/v1/models/upload', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Generate AI model
async function generateModel(name, promptDetails) {
  const response = await fetch('http://localhost:8000/api/v1/models/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, prompt_details: promptDetails })
  });
  
  return await response.json();
}

// Get all models
async function getAllModels() {
  const response = await fetch('http://localhost:8000/api/v1/models/');
  return await response.json();
}

// Delete model
async function deleteModel(modelId) {
  await fetch(`http://localhost:8000/api/v1/models/${modelId}`, {
    method: 'DELETE'
  });
}
```

---

## ✅ Checklist

- [ ] Database table created
- [ ] API endpoints tested
- [ ] Image upload working
- [ ] AI generation configured (optional)
- [ ] Cloud storage configured (optional)
- [ ] Error handling verified
- [ ] Frontend integration complete

---

Happy coding! 🎉


