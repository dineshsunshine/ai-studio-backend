# 🎨 Models API - Unified Documentation

## 🌐 Base URL
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models
```

---

## 📚 Interactive Documentation
**Explore and test all endpoints:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
```

---

## 🎯 API Endpoints

### 1. Create Model (Upload OR Generate)
**POST** `/api/v1/models/`

**One endpoint, two ways to create:**
- **Option A:** Upload an existing image
- **Option B:** Generate with AI from a text description

**Content-Type:** `multipart/form-data`

---

### 📤 Option A: Upload an Existing Image

**Form Fields:**
- `name` (required): Name of the model
- `image` (required): Image file (JPEG, PNG, GIF, WebP)

**Example (cURL):**
```bash
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/" \
  -F "name=Emma Watson" \
  -F "image=@/path/to/photo.jpg"
```

**Example (JavaScript):**
```javascript
// HTML: <input type="file" id="imageInput" accept="image/*">
//       <input type="text" id="nameInput" placeholder="Model name">
//       <button onclick="uploadModel()">Upload</button>

async function uploadModel() {
  const name = document.getElementById('nameInput').value;
  const imageFile = document.getElementById('imageInput').files[0];
  
  const formData = new FormData();
  formData.append('name', name);
  formData.append('image', imageFile);
  
  const response = await fetch(
    'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/',
    {
      method: 'POST',
      body: formData  // Don't set Content-Type header - browser will set it automatically
    }
  );
  
  if (response.ok) {
    const model = await response.json();
    console.log('✅ Model uploaded:', model);
    console.log('📷 Image URL:', model.imageUrl);
    // Display image: <img src="${model.imageUrl}" alt="${model.name}">
  } else {
    const error = await response.json();
    console.error('❌ Error:', error.detail);
  }
}
```

**Example (React):**
```jsx
import React, { useState } from 'react';

function UploadModelForm() {
  const [name, setName] = useState('');
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const formData = new FormData();
    formData.append('name', name);
    formData.append('image', image);
    
    try {
      const response = await fetch(
        'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/',
        {
          method: 'POST',
          body: formData
        }
      );
      
      const model = await response.json();
      console.log('✅ Model created:', model);
      alert(`Model "${model.name}" uploaded successfully!`);
      
      // Reset form
      setName('');
      setImage(null);
    } catch (error) {
      console.error('❌ Error:', error);
      alert('Failed to upload model');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Model name"
        required
      />
      
      <input
        type="file"
        onChange={(e) => setImage(e.target.files[0])}
        accept="image/*"
        required
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Uploading...' : 'Upload Model'}
      </button>
    </form>
  );
}
```

---

### 🤖 Option B: Generate with AI

**Form Fields:**
- `name` (required): Name of the model
- `promptDetails` (required): Text description for AI to generate the image

**Example (cURL):**
```bash
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/" \
  -F "name=Sophia" \
  -F "promptDetails=woman 25 indian, elegant red evening gown, professional photography, studio lighting"
```

**Example (JavaScript):**
```javascript
// HTML: <input type="text" id="nameInput" placeholder="Model name">
//       <textarea id="promptInput" placeholder="Describe the model..."></textarea>
//       <button onclick="generateModel()">Generate with AI</button>

async function generateModel() {
  const name = document.getElementById('nameInput').value;
  const promptDetails = document.getElementById('promptInput').value;
  
  const formData = new FormData();
  formData.append('name', name);
  formData.append('promptDetails', promptDetails);
  
  const response = await fetch(
    'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/',
    {
      method: 'POST',
      body: formData
    }
  );
  
  if (response.ok) {
    const model = await response.json();
    console.log('✅ Model generated:', model);
    console.log('📷 Generated image URL:', model.imageUrl);
    console.log('📝 Prompt used:', model.promptDetails);
    // Display: <img src="${model.imageUrl}" alt="${model.name}">
  } else {
    const error = await response.json();
    console.error('❌ Error:', error.detail);
  }
}
```

**Example (React):**
```jsx
import React, { useState } from 'react';

function GenerateModelForm() {
  const [name, setName] = useState('');
  const [promptDetails, setPromptDetails] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedModel, setGeneratedModel] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const formData = new FormData();
    formData.append('name', name);
    formData.append('promptDetails', promptDetails);
    
    try {
      const response = await fetch(
        'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/',
        {
          method: 'POST',
          body: formData
        }
      );
      
      const model = await response.json();
      console.log('✅ AI model generated:', model);
      setGeneratedModel(model);
      
      // Reset form
      setName('');
      setPromptDetails('');
    } catch (error) {
      console.error('❌ Error:', error);
      alert('Failed to generate model');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Model name (e.g., Sophia)"
          required
        />
        
        <textarea
          value={promptDetails}
          onChange={(e) => setPromptDetails(e.target.value)}
          placeholder="Describe the model... (e.g., woman 25 indian, elegant red dress, professional photography)"
          rows="4"
          required
        />
        
        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate with AI'}
        </button>
      </form>
      
      {generatedModel && (
        <div className="result">
          <h3>{generatedModel.name}</h3>
          <img src={generatedModel.imageUrl} alt={generatedModel.name} />
          <p>Prompt: {generatedModel.promptDetails}</p>
        </div>
      )}
    </div>
  );
}
```

---

### 📋 Response Format

**Success (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Sophia",
  "imageUrl": "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/assets/models/abc123.jpg",
  "promptDetails": "woman 25 indian, elegant red dress",
  "createdAt": "2025-10-09T12:00:00Z",
  "updatedAt": "2025-10-09T12:00:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "detail": "Please provide either 'image' (for upload) OR 'promptDetails' (for AI generation)."
}
```

---

### 2. List All Models
**GET** `/api/v1/models/`

**Query Parameters:**
- `skip` (optional): Number to skip for pagination (default: 0)
- `limit` (optional): Max items to return (default: 100)

**Example (JavaScript):**
```javascript
async function getAllModels() {
  const response = await fetch(
    'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/?limit=20'
  );
  
  const data = await response.json();
  console.log(`Found ${data.total} models`);
  
  data.models.forEach(model => {
    console.log(`${model.name}: ${model.imageUrl}`);
  });
  
  return data.models;
}
```

**Response:**
```json
{
  "models": [
    {
      "id": "abc-123",
      "name": "Emma Watson",
      "imageUrl": "https://.../assets/models/...",
      "promptDetails": null,
      "createdAt": "2025-10-09T10:00:00Z",
      "updatedAt": "2025-10-09T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### 3. Get Single Model
**GET** `/api/v1/models/{id}`

**Example (JavaScript):**
```javascript
async function getModel(modelId) {
  const response = await fetch(
    `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/${modelId}`
  );
  
  if (response.ok) {
    const model = await response.json();
    return model;
  } else {
    throw new Error('Model not found');
  }
}
```

---

### 4. Delete Model
**DELETE** `/api/v1/models/{id}`

**Example (JavaScript):**
```javascript
async function deleteModel(modelId) {
  if (!confirm('Are you sure you want to delete this model?')) {
    return;
  }
  
  const response = await fetch(
    `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/${modelId}`,
    {
      method: 'DELETE'
    }
  );
  
  if (response.status === 204) {
    console.log('✅ Model deleted successfully');
    return true;
  } else {
    throw new Error('Failed to delete model');
  }
}
```

---

## 💡 Complete Service Class (Copy & Use!)

```javascript
// models-api-service.js

const API_BASE = 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models';

export const ModelsAPI = {
  /**
   * Upload a model with an existing image file
   */
  async uploadModel(name, imageFile) {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('image', imageFile);
    
    const response = await fetch(`${API_BASE}/`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload model');
    }
    
    return response.json();
  },
  
  /**
   * Generate a model using AI from a text prompt
   */
  async generateModel(name, promptDetails) {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('promptDetails', promptDetails);
    
    const response = await fetch(`${API_BASE}/`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to generate model');
    }
    
    return response.json();
  },
  
  /**
   * Get all models
   */
  async getAllModels(skip = 0, limit = 100) {
    const response = await fetch(`${API_BASE}/?skip=${skip}&limit=${limit}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch models');
    }
    
    return response.json();
  },
  
  /**
   * Get a single model by ID
   */
  async getModel(modelId) {
    const response = await fetch(`${API_BASE}/${modelId}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Model not found');
      }
      throw new Error('Failed to fetch model');
    }
    
    return response.json();
  },
  
  /**
   * Delete a model
   */
  async deleteModel(modelId) {
    const response = await fetch(`${API_BASE}/${modelId}`, {
      method: 'DELETE'
    });
    
    if (response.status !== 204) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete model');
    }
    
    return true;
  }
};

// Usage Examples:

// Upload existing image
// const model = await ModelsAPI.uploadModel('Emma Watson', fileInput.files[0]);

// Generate with AI
// const model = await ModelsAPI.generateModel('Sophia', 'woman 25 indian, elegant dress');

// Get all models
// const { models, total } = await ModelsAPI.getAllModels();

// Delete a model
// await ModelsAPI.deleteModel(modelId);
```

---

## 🎨 AI Prompt Writing Guide

### Good Prompts for AI Generation

**Template:**
```
[gender] [age] [ethnicity], [clothing description], [style/mood], [technical details]
```

**Examples:**

✅ **Good Prompts:**
```
woman 25 indian, elegant red evening gown, confident smile, professional photography, studio lighting

man 30 caucasian, black suit and tie, business professional, corporate headshot style

woman 28 african, casual denim jacket, friendly expression, natural outdoor lighting

man 35 asian, traditional formal wear, cultural heritage style, high resolution photography
```

❌ **Bad Prompts (Too Vague):**
```
pretty girl
a person
model photo
```

### Prompt Components:

1. **Basic Info:**
   - Gender: woman, man
   - Age: 20s, 25, 30
   - Ethnicity: indian, caucasian, african, asian, hispanic, etc.

2. **Clothing:**
   - elegant evening gown
   - casual summer dress
   - business suit
   - traditional formal wear
   - denim jacket and jeans

3. **Expression/Pose:**
   - confident smile
   - serious expression
   - friendly demeanor
   - professional pose

4. **Style/Technical:**
   - professional photography
   - studio lighting
   - natural outdoor lighting
   - high resolution
   - fashion photography style

---

## 🧪 Testing

### Test Upload:
```bash
# Create test image (or use existing)
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/" \
  -F "name=Test Upload" \
  -F "image=@test.jpg"
```

### Test AI Generation:
```bash
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/" \
  -F "name=AI Generated Model" \
  -F "promptDetails=woman 25 indian, elegant red dress, professional photography"
```

---

## ✅ Summary

### Single Endpoint:
```
POST /api/v1/models/
```

### Two Ways to Create:
1. **Upload:** Send `name` + `image` file
2. **Generate:** Send `name` + `promptDetails` text

### Response:
Always returns the same format with:
- `id` (UUID)
- `name` (string)
- `imageUrl` (public URL)
- `promptDetails` (string or null)
- `createdAt` (timestamp)
- `updatedAt` (timestamp)

### Other Endpoints:
- `GET /api/v1/models/` - List all
- `GET /api/v1/models/{id}` - Get one
- `DELETE /api/v1/models/{id}` - Delete

---

**Share this with your AI frontend developer - everything they need is here! 🚀**


