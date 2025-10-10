# 📚 AI Studio Backend - API Documentation for Frontend Integration

## 🌐 Interactive API Documentation

### **Live Interactive Docs (Swagger UI):**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
```
**Features:**
- ✅ Try all endpoints directly in browser
- ✅ See request/response schemas
- ✅ Copy cURL commands
- ✅ Test with real data

### **Alternative Docs (ReDoc):**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/redoc
```

---

## 🎯 Base URLs

**Production (Public):**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio
```

**Local Development:**
```
http://localhost:8000
```

---

## 📋 Module 1: Tasks API (Testing/Demo Module)

### Overview
Simple CRUD API for managing tasks. Good for testing and learning the API structure.

### Base Endpoint
```
/tasks
```

---

### 1.1 Get All Tasks

**Endpoint:** `GET /tasks`

**Description:** Fetch all tasks with optional filtering

**Query Parameters:**
- `skip` (optional): Number to skip for pagination (default: 0)
- `limit` (optional): Max items to return (default: 100)
- `completed` (optional): Filter by completion status (true/false)

**Example Request:**
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks?completed=false&limit=10"
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Complete API integration",
    "description": "Integrate Models API with frontend",
    "completed": false,
    "created_at": "2025-10-09T10:00:00",
    "updated_at": "2025-10-09T10:00:00"
  }
]
```

**JavaScript Example:**
```javascript
const response = await fetch(
  'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks'
);
const tasks = await response.json();
console.log(tasks);
```

---

### 1.2 Create Task

**Endpoint:** `POST /tasks`

**Description:** Create a new task

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "New Task",
  "description": "Task description",
  "completed": false
}
```

**Example Request:**
```bash
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Integrate Models API",
    "description": "Connect frontend to Models endpoints",
    "completed": false
  }'
```

**Response (201 Created):**
```json
{
  "id": 2,
  "title": "Integrate Models API",
  "description": "Connect frontend to Models endpoints",
  "completed": false,
  "created_at": "2025-10-09T10:05:00",
  "updated_at": "2025-10-09T10:05:00"
}
```

**JavaScript Example:**
```javascript
const response = await fetch(
  'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      title: 'Integrate Models API',
      description: 'Connect frontend to Models endpoints',
      completed: false
    })
  }
);
const newTask = await response.json();
console.log(newTask);
```

---

### 1.3 Get Single Task

**Endpoint:** `GET /tasks/{task_id}`

**Description:** Get a specific task by ID

**Example Request:**
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks/1"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Complete API integration",
  "description": "Integrate Models API with frontend",
  "completed": false,
  "created_at": "2025-10-09T10:00:00",
  "updated_at": "2025-10-09T10:00:00"
}
```

**JavaScript Example:**
```javascript
const taskId = 1;
const response = await fetch(
  `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks/${taskId}`
);
const task = await response.json();
```

---

### 1.4 Update Task

**Endpoint:** `PUT /tasks/{task_id}`

**Description:** Update an existing task

**Request Body (all fields optional):**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}
```

**Example Request:**
```bash
curl -X PUT "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Complete API integration",
  "description": "Integrate Models API with frontend",
  "completed": true,
  "created_at": "2025-10-09T10:00:00",
  "updated_at": "2025-10-09T10:10:00"
}
```

**JavaScript Example:**
```javascript
const response = await fetch(
  `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks/1`,
  {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      completed: true
    })
  }
);
const updatedTask = await response.json();
```

---

### 1.5 Delete Task

**Endpoint:** `DELETE /tasks/{task_id}`

**Description:** Delete a task

**Example Request:**
```bash
curl -X DELETE "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks/1"
```

**Response:** `204 No Content` (success, no body)

**JavaScript Example:**
```javascript
const response = await fetch(
  `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/tasks/1`,
  {
    method: 'DELETE'
  }
);

if (response.status === 204) {
  console.log('Task deleted successfully');
}
```

---

### 1.6 Get Task Statistics

**Endpoint:** `GET /stats`

**Description:** Get statistics about tasks

**Example Request:**
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/stats"
```

**Response (200 OK):**
```json
{
  "total_tasks": 10,
  "completed": 5,
  "pending": 5,
  "completion_rate": "50.0%"
}
```

**JavaScript Example:**
```javascript
const response = await fetch(
  'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/stats'
);
const stats = await response.json();
```

---

## 📋 Module 2: Models API (Fashion Models Management)

### Overview
Complete CRUD API for managing fashion model images. Supports file uploads and AI generation.

### Base Endpoint
```
/api/v1/models
```

---

### 2.1 Get All Models

**Endpoint:** `GET /api/v1/models/`

**Description:** Fetch all fashion models

**Query Parameters:**
- `skip` (optional): Number to skip for pagination (default: 0)
- `limit` (optional): Max items to return (default: 100)

**Example Request:**
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/?limit=20"
```

**Response (200 OK):**
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
    },
    {
      "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "name": "Sophia AI",
      "image_url": "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/assets/generated/def456.png",
      "prompt_details": "wearing elegant red evening gown, confident smile",
      "created_at": "2025-10-09T10:05:00Z",
      "updated_at": "2025-10-09T10:05:00Z"
    }
  ],
  "total": 2
}
```

**JavaScript Example:**
```javascript
async function getAllModels(skip = 0, limit = 100) {
  const response = await fetch(
    `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/?skip=${skip}&limit=${limit}`
  );
  const data = await response.json();
  return data;
}

// Usage
const { models, total } = await getAllModels();
console.log(`Found ${total} models`, models);
```

---

### 2.2 Upload Model (with Image File)

**Endpoint:** `POST /api/v1/models/upload`

**Description:** Upload a new model with an image file

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `name` (required): Name of the model
- `image` (required): Image file (JPEG, PNG, etc.)

**Example Request (cURL):**
```bash
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/upload" \
  -F "name=Emma Watson" \
  -F "image=@/path/to/photo.jpg"
```

**Response (201 Created):**
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

**JavaScript Example (with HTML form):**
```javascript
async function uploadModel(name, imageFile) {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('image', imageFile);
  
  const response = await fetch(
    'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/upload',
    {
      method: 'POST',
      body: formData
    }
  );
  
  if (response.status === 201) {
    const model = await response.json();
    console.log('Model uploaded:', model);
    return model;
  } else {
    const error = await response.json();
    throw new Error(error.detail);
  }
}

// Usage with file input
const fileInput = document.querySelector('input[type="file"]');
const nameInput = document.querySelector('input[name="modelName"]');

document.querySelector('form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const model = await uploadModel(nameInput.value, fileInput.files[0]);
  console.log('Uploaded model:', model);
  // Display image: <img src="${model.image_url}" />
});
```

**React Example:**
```jsx
import React, { useState } from 'react';

function ModelUpload() {
  const [name, setName] = useState('');
  const [image, setImage] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('name', name);
    formData.append('image', image);
    
    const response = await fetch(
      'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/upload',
      {
        method: 'POST',
        body: formData
      }
    );
    
    const model = await response.json();
    console.log('Model uploaded:', model);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="text" 
        value={name} 
        onChange={(e) => setName(e.target.value)}
        placeholder="Model name"
      />
      <input 
        type="file" 
        onChange={(e) => setImage(e.target.files[0])}
        accept="image/*"
      />
      <button type="submit">Upload</button>
    </form>
  );
}
```

---

### 2.3 Generate AI Model

**Endpoint:** `POST /api/v1/models/generate`

**Description:** Generate a model image using AI (Google Imagen)

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "name": "Sophia",
  "prompt_details": "wearing elegant evening gown, long dark hair, confident smile, professional photography"
}
```

**Example Request:**
```bash
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sophia",
    "prompt_details": "wearing elegant evening gown, long dark hair, confident smile"
  }'
```

**Response (201 Created):**
```json
{
  "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "name": "Sophia",
  "image_url": "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/assets/generated/def456.png",
  "prompt_details": "wearing elegant evening gown, long dark hair, confident smile",
  "created_at": "2025-10-09T10:05:00Z",
  "updated_at": "2025-10-09T10:05:00Z"
}
```

**JavaScript Example:**
```javascript
async function generateAIModel(name, promptDetails) {
  const response = await fetch(
    'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/generate',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: name,
        prompt_details: promptDetails
      })
    }
  );
  
  if (response.status === 201) {
    const model = await response.json();
    console.log('AI model generated:', model);
    return model;
  } else {
    const error = await response.json();
    throw new Error(error.detail);
  }
}

// Usage
const model = await generateAIModel(
  'Sophia',
  'wearing elegant red dress, professional photography, studio lighting'
);
console.log('Generated image URL:', model.image_url);
```

**Note:** Currently returns mock/placeholder images. Enable real AI generation by configuring Google Cloud (see setup guide).

---

### 2.4 Get Single Model

**Endpoint:** `GET /api/v1/models/{model_id}`

**Description:** Get a specific model by ID

**Example Request:**
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/550e8400-e29b-41d4-a716-446655440000"
```

**Response (200 OK):**
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

**JavaScript Example:**
```javascript
async function getModel(modelId) {
  const response = await fetch(
    `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/${modelId}`
  );
  
  if (response.ok) {
    return await response.json();
  } else if (response.status === 404) {
    throw new Error('Model not found');
  } else {
    const error = await response.json();
    throw new Error(error.detail);
  }
}

// Usage
const model = await getModel('550e8400-e29b-41d4-a716-446655440000');
```

---

### 2.5 Delete Model

**Endpoint:** `DELETE /api/v1/models/{model_id}`

**Description:** Delete a model and its associated image

**Example Request:**
```bash
curl -X DELETE "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/550e8400-e29b-41d4-a716-446655440000"
```

**Response:** `204 No Content` (success, no body)

**JavaScript Example:**
```javascript
async function deleteModel(modelId) {
  const response = await fetch(
    `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/${modelId}`,
    {
      method: 'DELETE'
    }
  );
  
  if (response.status === 204) {
    console.log('Model deleted successfully');
    return true;
  } else if (response.status === 404) {
    throw new Error('Model not found');
  } else {
    const error = await response.json();
    throw new Error(error.detail);
  }
}

// Usage with confirmation
if (confirm('Are you sure you want to delete this model?')) {
  await deleteModel('550e8400-e29b-41d4-a716-446655440000');
  // Refresh list or remove from UI
}
```

---

## 📋 Module 3: Health & Utility Endpoints

### 3.1 Health Check

**Endpoint:** `GET /health`

**Description:** Check backend health and database status

**Example Request:**
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/health"
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-09T10:00:00",
  "database": "connected",
  "total_tasks": 5,
  "message": "API is running with database! ✅"
}
```

**JavaScript Example:**
```javascript
async function checkHealth() {
  const response = await fetch(
    'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/health'
  );
  const health = await response.json();
  
  if (health.status === 'healthy') {
    console.log('✅ Backend is healthy');
  } else {
    console.warn('⚠️ Backend health degraded:', health);
  }
  
  return health;
}
```

---

### 3.2 Root Endpoint

**Endpoint:** `GET /`

**Description:** API welcome message

**Example Request:**
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/"
```

**Response (200 OK):**
```json
{
  "message": "🎉 Welcome to AI Studio Backend!",
  "status": "running",
  "database": "SQLite",
  "docs": "/docs",
  "endpoints": {
    "health": "/health",
    "tasks": "/tasks",
    "models": "/api/v1/models"
  }
}
```

---

## ❌ Error Responses

### Common HTTP Status Codes:

#### 400 Bad Request
```json
{
  "detail": "Uploaded file must be an image"
}
```

#### 404 Not Found
```json
{
  "detail": "Model with id {id} not found"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Failed to upload image: {error message}"
}
```

---

## 🔐 CORS Configuration

All endpoints support CORS:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

No authentication required (for now).

---

## 💡 Complete Integration Examples

### Example 1: Model Gallery Component (React)

```jsx
import React, { useState, useEffect } from 'react';

const API_BASE = 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models';

function ModelGallery() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/`);
      const data = await response.json();
      setModels(data.models);
    } catch (error) {
      console.error('Error loading models:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (modelId) => {
    if (!confirm('Delete this model?')) return;
    
    try {
      const response = await fetch(`${API_BASE}/${modelId}`, {
        method: 'DELETE'
      });
      
      if (response.status === 204) {
        setModels(models.filter(m => m.id !== modelId));
        alert('Model deleted successfully');
      }
    } catch (error) {
      alert('Error deleting model');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="model-gallery">
      {models.map(model => (
        <div key={model.id} className="model-card">
          <img src={model.image_url} alt={model.name} />
          <h3>{model.name}</h3>
          {model.prompt_details && (
            <p className="prompt">{model.prompt_details}</p>
          )}
          <button onClick={() => handleDelete(model.id)}>
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}

export default ModelGallery;
```

### Example 2: Complete CRUD Service (JavaScript)

```javascript
// models-service.js
const API_BASE = 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models';

export const modelsService = {
  // Get all models
  async getAll(skip = 0, limit = 100) {
    const response = await fetch(`${API_BASE}/?skip=${skip}&limit=${limit}`);
    return response.json();
  },

  // Get single model
  async getById(id) {
    const response = await fetch(`${API_BASE}/${id}`);
    if (!response.ok) {
      throw new Error('Model not found');
    }
    return response.json();
  },

  // Upload model
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
      headers: {
        'Content-Type': 'application/json'
      },
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
// import { modelsService } from './models-service';
// const models = await modelsService.getAll();
// const newModel = await modelsService.upload('Emma', fileInput.files[0]);
```

---

## 🧪 Testing

### Quick Test Script:
```bash
# Test health
curl https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/health

# Get all models
curl https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/

# Upload model
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/upload" \
  -F "name=Test Model" \
  -F "image=@test.jpg"

# Generate AI model
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/generate" \
  -H "Content-Type: application/json" \
  -d '{"name":"AI Model","prompt_details":"casual outfit"}'
```

---

## 📞 Support & Resources

- **Interactive Docs:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
- **ReDoc:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/redoc
- **Health Check:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/health

---

## ✅ Quick Reference

### All Endpoints:

**Tasks:**
- `GET /tasks` - List tasks
- `POST /tasks` - Create task
- `GET /tasks/{id}` - Get task
- `PUT /tasks/{id}` - Update task  
- `DELETE /tasks/{id}` - Delete task
- `GET /stats` - Task statistics

**Models:**
- `GET /api/v1/models/` - List models
- `POST /api/v1/models/upload` - Upload model
- `POST /api/v1/models/generate` - Generate AI model
- `GET /api/v1/models/{id}` - Get model
- `DELETE /api/v1/models/{id}` - Delete model

**Health:**
- `GET /health` - Health check
- `GET /` - API info

---

Share this document with your frontend developer! All APIs are live and ready for integration! 🚀

