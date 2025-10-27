# 🌐 Models API - Public URLs

## Base URL
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio
```

---

## 📚 Interactive Documentation

### Swagger UI (Interactive API Docs)
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
```
**Use this to explore and test all endpoints in your browser**

### ReDoc (Alternative Documentation)
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/redoc
```

### OpenAPI Spec (JSON)
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/openapi.json
```

---

## 📋 Models API Endpoints

### 1. List All Models
**GET** List all fashion models with pagination

**URL:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/
```

**Query Parameters:**
- `skip` (optional): Number to skip for pagination (default: 0)
- `limit` (optional): Max items to return (default: 100)

**Example URLs:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/?limit=20
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/?skip=10&limit=10
```

**cURL Example:**
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/"
```

**JavaScript Example:**
```javascript
const response = await fetch(
  'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/'
);
const data = await response.json();
console.log(data.models); // Array of models
console.log(data.total);  // Total count
```

---

### 2. Upload Model (with Image File)
**POST** Upload a new model with an image file

**URL:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/upload
```

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `name` (required): Name of the model
- `image` (required): Image file (JPEG, PNG, etc.)

**cURL Example:**
```bash
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/upload" \
  -F "name=Emma Watson" \
  -F "image=@/path/to/photo.jpg"
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('name', 'Emma Watson');
formData.append('image', fileInput.files[0]);

const response = await fetch(
  'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/upload',
  {
    method: 'POST',
    body: formData
  }
);
const model = await response.json();
console.log('Uploaded:', model);
console.log('Image URL:', model.image_url); // Public image URL
```

---

### 3. Generate AI Model
**POST** Generate a model image using AI (Google Imagen)

**URL:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/generate
```

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "name": "Sophia",
  "prompt_details": "wearing elegant evening gown, professional photography"
}
```

**cURL Example:**
```bash
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sophia",
    "prompt_details": "wearing elegant red dress, professional photography"
  }'
```

**JavaScript Example:**
```javascript
const response = await fetch(
  'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/generate',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: 'Sophia',
      prompt_details: 'wearing elegant red dress, professional photography'
    })
  }
);
const model = await response.json();
console.log('Generated:', model);
console.log('Image URL:', model.image_url); // Public image URL
```

---

### 4. Get Single Model
**GET** Get a specific model by ID

**URL Pattern:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/{model_id}
```

**Example URL:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/550e8400-e29b-41d4-a716-446655440000
```

**cURL Example:**
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/550e8400-e29b-41d4-a716-446655440000"
```

**JavaScript Example:**
```javascript
const modelId = '550e8400-e29b-41d4-a716-446655440000';
const response = await fetch(
  `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/${modelId}`
);
const model = await response.json();
console.log(model);
```

---

### 5. Delete Model
**DELETE** Delete a model and its associated image

**URL Pattern:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/{model_id}
```

**Example URL:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/550e8400-e29b-41d4-a716-446655440000
```

**cURL Example:**
```bash
curl -X DELETE "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/550e8400-e29b-41d4-a716-446655440000"
```

**JavaScript Example:**
```javascript
const modelId = '550e8400-e29b-41d4-a716-446655440000';
const response = await fetch(
  `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/${modelId}`,
  {
    method: 'DELETE'
  }
);

if (response.status === 204) {
  console.log('Model deleted successfully');
}
```

---

## 🛠️ Utility Endpoints

### Health Check
**GET** Check backend health and database status

**URL:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/health
```

**cURL Example:**
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/health"
```

---

## 📊 Response Examples

### List Models Response
```json
{
  "models": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Emma Watson",
      "image_url": "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/assets/models/abc123.jpg",
      "prompt_details": null,
      "created_at": "2025-10-09T10:00:00Z",
      "updated_at": "2025-10-09T10:00:00Z"
    }
  ],
  "total": 1
}
```

### Upload/Generate Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Emma Watson",
  "image_url": "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/assets/models/abc123.jpg",
  "prompt_details": null,
  "created_at": "2025-10-09T10:00:00Z",
  "updated_at": "2025-10-09T10:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Model not found"
}
```

---

## 🔑 Quick Reference

### All Endpoints:
```
GET    https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/
POST   https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/upload
POST   https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/generate
GET    https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/{id}
DELETE https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/{id}
```

### Image URLs:
All uploaded and generated images are accessible via public URLs:
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/assets/models/{filename}
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/assets/generated/{filename}
```

---

## 💡 Complete Integration Example

```javascript
// models-service.js - Ready to use in your frontend

const API_BASE = 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models';

export const modelsAPI = {
  // Get all models
  async getAll(skip = 0, limit = 100) {
    const response = await fetch(`${API_BASE}/?skip=${skip}&limit=${limit}`);
    return response.json();
  },

  // Get single model
  async getById(id) {
    const response = await fetch(`${API_BASE}/${id}`);
    if (!response.ok) throw new Error('Model not found');
    return response.json();
  },

  // Upload model with image
  async upload(name, imageFile) {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('image', imageFile);

    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return response.json();
  },

  // Generate AI model
  async generate(name, promptDetails) {
    const response = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, prompt_details: promptDetails })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return response.json();
  },

  // Delete model
  async delete(id) {
    const response = await fetch(`${API_BASE}/${id}`, {
      method: 'DELETE'
    });

    if (response.status !== 204) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return true;
  }
};

// Usage:
// import { modelsAPI } from './models-service';
// const models = await modelsAPI.getAll();
// const newModel = await modelsAPI.upload('Emma', fileInput.files[0]);
```

---

## ✅ Features

- ✅ **CORS Enabled** - Works from any domain
- ✅ **Public URLs** - All images accessible worldwide
- ✅ **RESTful Design** - Standard HTTP methods
- ✅ **Comprehensive Errors** - Clear error messages
- ✅ **Pagination Support** - Efficient data loading
- ✅ **File Upload** - Multipart/form-data support
- ✅ **AI Generation** - Google Imagen integration (mock for now)

---

## 📞 Support

- **Interactive Docs:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
- **Complete Guide:** `API_DOCUMENTATION_FOR_FRONTEND.md`
- **Health Check:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/health

---

**Ready for frontend integration! 🚀**


