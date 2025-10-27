# 🌐 AI Studio Backend - Public API Documentation

## 📡 Public API Base URLs

### Main API Base URL
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio
```

### Interactive API Documentation (Swagger UI)
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
```

### Alternative API Documentation (ReDoc)
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/redoc
```

---

## 🎯 Models API Endpoints

### Base URL for Models API
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models
```

---

## 📋 Complete API Endpoints

### 1. Health Check
**URL:** `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/health`  
**Method:** `GET`  
**Description:** Check backend health and database status

**Example:**
```bash
curl https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-09T10:00:00",
  "database": "connected",
  "total_tasks": 3,
  "message": "API is running with database! ✅"
}
```

---

### 2. Get All Models
**URL:** `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/`  
**Method:** `GET`  
**Description:** Fetch all fashion models

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100)

**Example:**
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/?skip=0&limit=10"
```

**Response:**
```json
{
  "models": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Emma Watson",
      "image_url": "https://example.com/image.jpg",
      "prompt_details": null,
      "created_at": "2025-10-09T10:00:00Z",
      "updated_at": "2025-10-09T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### 3. Upload Model (with Image File)
**URL:** `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/upload`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`  
**Description:** Upload a new model with an image file

**Form Fields:**
- `name` (required): Name of the model
- `image` (required): Image file (JPEG, PNG, etc.)

**Example:**
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

const result = await response.json();
console.log(result);
```

**Response (201 Created):**
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

---

### 4. Generate AI Model
**URL:** `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/generate`  
**Method:** `POST`  
**Content-Type:** `application/json`  
**Description:** Generate a model image using AI (Google Imagen)

**Request Body:**
```json
{
  "name": "Sophia",
  "prompt_details": "wearing elegant evening gown, long dark hair, confident smile"
}
```

**Example:**
```bash
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sophia",
    "prompt_details": "wearing elegant evening gown, long dark hair, confident smile"
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
      prompt_details: 'wearing elegant evening gown, long dark hair, confident smile'
    })
  }
);

const result = await response.json();
console.log(result);
```

**Response (201 Created):**
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

---

### 5. Get Single Model
**URL:** `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/{model_id}`  
**Method:** `GET`  
**Description:** Get a specific model by ID

**Example:**
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/123e4567-e89b-12d3-a456-426614174000"
```

**Response:**
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

---

### 6. Delete Model
**URL:** `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/{model_id}`  
**Method:** `DELETE`  
**Description:** Delete a model and its associated image

**Example:**
```bash
curl -X DELETE "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/123e4567-e89b-12d3-a456-426614174000"
```

**JavaScript Example:**
```javascript
const response = await fetch(
  'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/123e4567-e89b-12d3-a456-426614174000',
  {
    method: 'DELETE'
  }
);

if (response.status === 204) {
  console.log('Model deleted successfully');
}
```

**Response:** `204 No Content` (success with no body)

---

## 🔧 Additional Endpoints

### Tasks API (Legacy)

#### Get All Tasks
**URL:** `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks`  
**Method:** `GET`

#### Create Task
**URL:** `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks`  
**Method:** `POST`  
**Body:**
```json
{
  "title": "Task Title",
  "description": "Task Description",
  "completed": false
}
```

#### Update Task
**URL:** `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks/{task_id}`  
**Method:** `PUT`

#### Delete Task
**URL:** `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks/{task_id}`  
**Method:** `DELETE`

---

## 🌐 Interactive Documentation

### Swagger UI (Recommended)
**URL:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs

- ✅ Interactive API explorer
- ✅ Try endpoints directly in browser
- ✅ See request/response schemas
- ✅ Test with real data

### ReDoc (Alternative)
**URL:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/redoc

- ✅ Beautiful, clean documentation
- ✅ Detailed schema information
- ✅ Easy to navigate

---

## 🔐 CORS & Headers

### CORS
All endpoints support CORS with:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

### Required Headers for JSON Requests
```
Content-Type: application/json
```

### Required Headers for File Uploads
```
Content-Type: multipart/form-data
```

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

## 📱 Frontend Integration Example

### Complete JavaScript Example

```javascript
// Configuration
const API_BASE_URL = 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models';

// 1. Get all models
async function getAllModels() {
  const response = await fetch(`${API_BASE_URL}/`);
  const data = await response.json();
  console.log('Total models:', data.total);
  console.log('Models:', data.models);
  return data;
}

// 2. Upload a model
async function uploadModel(name, imageFile) {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('image', imageFile);
  
  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData
  });
  
  if (response.status === 201) {
    const model = await response.json();
    console.log('Model uploaded:', model);
    return model;
  } else {
    const error = await response.json();
    console.error('Upload failed:', error);
    throw new Error(error.detail);
  }
}

// 3. Generate AI model
async function generateModel(name, promptDetails) {
  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: name,
      prompt_details: promptDetails
    })
  });
  
  if (response.status === 201) {
    const model = await response.json();
    console.log('Model generated:', model);
    return model;
  } else {
    const error = await response.json();
    console.error('Generation failed:', error);
    throw new Error(error.detail);
  }
}

// 4. Delete a model
async function deleteModel(modelId) {
  const response = await fetch(`${API_BASE_URL}/${modelId}`, {
    method: 'DELETE'
  });
  
  if (response.status === 204) {
    console.log('Model deleted successfully');
    return true;
  } else {
    const error = await response.json();
    console.error('Delete failed:', error);
    throw new Error(error.detail);
  }
}

// Usage examples:
// await getAllModels();
// await uploadModel('Emma', fileInput.files[0]);
// await generateModel('Sophia', 'wearing elegant red dress');
// await deleteModel('model-id-here');
```

---

## 🧪 Testing with cURL

### Test Health
```bash
curl https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/health
```

### Test Models API
```bash
curl https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/
```

### Upload Model
```bash
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/upload" \
  -F "name=Test Model" \
  -F "image=@/path/to/image.jpg"
```

### Generate AI Model
```bash
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/generate" \
  -H "Content-Type: application/json" \
  -d '{"name":"AI Model","prompt_details":"casual outfit, friendly smile"}'
```

---

## 💡 Important Notes

### 1. Ngrok Free Tier
- The public URL (`https://zestfully-chalky-nikia.ngrok-free.dev`) is active as long as ngrok is running
- If ngrok restarts, you may get a different URL
- For production, consider ngrok paid plans or deploy to a cloud service

### 2. File Storage
- Currently using local storage (`/tmp/uploads/`)
- Image URLs will be `http://localhost:8000/uploads/...` (local)
- For production, configure Google Cloud Storage (see MODELS_API_GUIDE.md)

### 3. AI Generation
- Currently using mock/placeholder images
- To enable real AI generation, set `ENABLE_AI_GENERATION=true` and configure Google Cloud
- See MODELS_API_GUIDE.md for setup instructions

### 4. Rate Limits
- No rate limits currently configured
- Consider adding rate limiting for production

---

## 📞 Quick Links

- **Interactive Docs:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
- **Models API:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/
- **Health Check:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/health

---

## 🎉 Ready to Use!

Your public API is live and ready for integration with your Google AI Studio frontend!

**Start testing:**
1. Open the interactive docs: https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
2. Expand the "models" section
3. Click "Try it out" on any endpoint
4. Test with real data!

Happy coding! 🚀


