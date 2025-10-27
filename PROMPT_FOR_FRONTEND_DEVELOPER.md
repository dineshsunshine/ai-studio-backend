# Frontend Developer Task: Fix API Integration with Ngrok

## 🎯 Problem

Our API calls are returning HTML (ngrok warning page) instead of JSON data. This is causing frontend errors.

## ✅ Solution Required

Add the header `ngrok-skip-browser-warning: true` to all API requests to our backend.

---

## 📋 Implementation Instructions

### API Base URL
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio
```

### Required Header
All API requests must include this header:
```
ngrok-skip-browser-warning: true
```

---

## 💻 Code Implementation

### If Using Axios (Recommended):

**Step 1:** Install axios if not already installed:
```bash
npm install axios
```

**Step 2:** Create an API utility file (`src/api/client.js` or `src/utils/api.js`):

```javascript
import axios from 'axios';

// Create and configure axios instance
const apiClient = axios.create({
    baseURL: 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio',
    headers: {
        'ngrok-skip-browser-warning': 'true'
    }
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

export default apiClient;
```

**Step 3:** Use in your components:

```javascript
import apiClient from './api/client';

// GET request
const getModels = async () => {
    try {
        const response = await apiClient.get('/api/v1/models/');
        return response.data;
    } catch (error) {
        console.error('Failed to fetch models:', error);
        throw error;
    }
};

// POST request with file upload
const createModel = async (name, imageFile) => {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('image', imageFile);
    
    try {
        const response = await apiClient.post('/api/v1/models/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    } catch (error) {
        console.error('Failed to create model:', error);
        throw error;
    }
};

// DELETE request
const deleteModel = async (modelId) => {
    try {
        await apiClient.delete(`/api/v1/models/${modelId}/`);
        return true;
    } catch (error) {
        console.error('Failed to delete model:', error);
        throw error;
    }
};
```

### If Using Fetch:

Create an API utility file:

```javascript
const API_BASE_URL = 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio';

const defaultHeaders = {
    'ngrok-skip-browser-warning': 'true'
};

export const api = {
    async get(endpoint) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: defaultHeaders
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    },

    async post(endpoint, data) {
        const headers = { ...defaultHeaders };
        let body;

        if (data instanceof FormData) {
            // Don't set Content-Type for FormData - browser sets it automatically
            body = data;
        } else {
            headers['Content-Type'] = 'application/json';
            body = JSON.stringify(data);
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers,
            body
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    },

    async delete(endpoint) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'DELETE',
            headers: defaultHeaders
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.status === 204 ? null : response.json();
    }
};

// Usage example
const models = await api.get('/api/v1/models/');
```

---

## 🧪 Testing Instructions

### Test 1: Browser Console Test
Open your app, press F12 to open console, and paste:

```javascript
fetch('https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/', {
    headers: { 'ngrok-skip-browser-warning': 'true' }
})
.then(r => r.json())
.then(d => console.log('✅ SUCCESS:', d))
.catch(e => console.error('❌ FAILED:', e));
```

**Expected Result:** You should see JSON data with a list of models, not HTML.

### Test 2: Test All Endpoints

```javascript
// Test GET
const testGet = async () => {
    const data = await apiClient.get('/api/v1/models/');
    console.log('Models:', data.models);
};

// Test POST (with dummy file)
const testPost = async () => {
    const blob = new Blob(['test'], { type: 'image/png' });
    const file = new File([blob], 'test.png', { type: 'image/png' });
    const result = await createModel('Test Model', file);
    console.log('Created:', result);
};

// Run tests
testGet();
```

---

## 📚 API Endpoints Available

### Models API
- **GET** `/api/v1/models/` - List all models
- **POST** `/api/v1/models/` - Create model (multipart/form-data)
  - `name` (string, required)
  - `image` (file, optional) OR `promptDetails` (string, optional)
- **GET** `/api/v1/models/{id}/` - Get single model
- **DELETE** `/api/v1/models/{id}/` - Delete model

### Looks API
- **GET** `/api/v1/looks/` - List all looks (with pagination)
- **POST** `/api/v1/looks/` - Create look (JSON with base64 images)
- **GET** `/api/v1/looks/{id}/` - Get single look
- **PATCH** `/api/v1/looks/{id}/` - Update look
- **DELETE** `/api/v1/looks/{id}/` - Delete look

### API Documentation (Interactive)
Visit: https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs

**Note:** When you visit this URL in browser, you'll see a warning page. Click "Visit Site" once, then you can use Swagger UI normally.

---

## ⚠️ Important Notes

1. **Always include the header** `ngrok-skip-browser-warning: true` in every request
2. **For file uploads**, use `FormData` and let the browser set `Content-Type` automatically
3. **For JSON requests**, set `Content-Type: application/json`
4. **Image URLs** in responses will also need the header if you're fetching them programmatically
5. **Error handling** is important - API returns standard HTTP status codes

---

## 🔍 Example: Complete React Component

```jsx
import React, { useState, useEffect } from 'react';
import apiClient from './api/client';

function ModelsPage() {
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadModels();
    }, []);

    const loadModels = async () => {
        try {
            setLoading(true);
            const response = await apiClient.get('/api/v1/models/');
            setModels(response.models);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('name', 'New Model');
        formData.append('image', file);

        try {
            await apiClient.post('/api/v1/models/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            loadModels(); // Reload list
        } catch (err) {
            alert('Upload failed: ' + err.message);
        }
    };

    const handleDelete = async (modelId) => {
        if (!confirm('Delete this model?')) return;

        try {
            await apiClient.delete(`/api/v1/models/${modelId}/`);
            loadModels(); // Reload list
        } catch (err) {
            alert('Delete failed: ' + err.message);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div>
            <h1>Models ({models.length})</h1>
            
            <input 
                type="file" 
                accept="image/*" 
                onChange={handleUpload} 
            />

            <div className="models-grid">
                {models.map(model => (
                    <div key={model.id} className="model-card">
                        <img 
                            src={model.imageUrl} 
                            alt={model.name}
                            onError={(e) => {
                                console.error('Image failed to load:', model.imageUrl);
                            }}
                        />
                        <h3>{model.name}</h3>
                        <button onClick={() => handleDelete(model.id)}>
                            Delete
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ModelsPage;
```

---

## ✅ Acceptance Criteria

- [ ] All API calls include the `ngrok-skip-browser-warning: true` header
- [ ] Models can be fetched and displayed
- [ ] Models can be created via upload or AI generation
- [ ] Models can be deleted
- [ ] Error handling is implemented for all API calls
- [ ] Loading states are shown during API calls
- [ ] Console shows no errors related to HTML responses or CORS

---

## 📖 Additional Resources

- **Complete API Documentation:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
- **Test Page with Working Examples:** Open `/Users/dgolani/Documents/AI_Studio/backend/frontend/test_api.html` in browser
- **Detailed Frontend Guide:** `/Users/dgolani/Documents/AI_Studio/backend/FRONTEND_INTEGRATION_GUIDE.md`

---

## 🆘 If You Need Help

If you encounter issues:

1. Check browser console for errors
2. Verify the header is being sent (check Network tab in DevTools)
3. Test the API endpoint directly with:
   ```bash
   curl -H "ngrok-skip-browser-warning: true" \
     https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/
   ```
4. Ensure you're using the correct base URL (with `/AIStudio`)

---

**Estimated Time:** 30-60 minutes

**Priority:** High - Blocking API integration

**Status:** Ready to implement


