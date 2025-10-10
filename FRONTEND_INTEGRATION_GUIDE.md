# Frontend Integration Guide - Fixing Ngrok Warning Issues

## 🚨 Problem: Frontend Getting HTML Instead of JSON

If your frontend is receiving HTML (the ngrok warning page) instead of JSON responses, it's because your API requests are **missing the bypass header**.

---

## ✅ The Solution (Simple!)

Add this header to **ALL API requests**:
```
ngrok-skip-browser-warning: true
```

That's it! This works on **all ngrok plans** (Free, Hobby, Pro, Enterprise).

---

## 🧪 Test Your API First

Before changing your frontend code, verify your API works:

### Using cURL:
```bash
curl -H "ngrok-skip-browser-warning: true" \
  https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/
```

### Using Postman:
1. Open Postman
2. Create a GET request to: `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/`
3. Add header: `ngrok-skip-browser-warning: true`
4. Send → You should get JSON!

### Using Test Page:
Open this page in your browser:
```
file:///Users/dgolani/Documents/AI_Studio/backend/frontend/test_api.html
```

Or via ngrok:
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/
```

---

## 📋 Implementation by Framework

### React

#### Option 1: Using Fetch (Manual header each time)

```javascript
import React, { useState, useEffect } from 'react';

function ModelsList() {
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchModels();
    }, []);

    const fetchModels = async () => {
        try {
            const response = await fetch(
                'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/',
                {
                    headers: {
                        'ngrok-skip-browser-warning': 'true'
                    }
                }
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            setModels(data.models);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div>
            <h1>Models</h1>
            {models.map(model => (
                <div key={model.id}>
                    <h3>{model.name}</h3>
                    <img src={model.imageUrl} alt={model.name} />
                </div>
            ))}
        </div>
    );
}

export default ModelsList;
```

#### Option 2: Using Axios (Recommended - Set Once)

**Step 1:** Install axios
```bash
npm install axios
```

**Step 2:** Create an API utility file (`src/utils/api.js`):
```javascript
import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
    baseURL: 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio',
    headers: {
        'ngrok-skip-browser-warning': 'true'
    }
});

// Export configured instance
export default api;
```

**Step 3:** Use it in your components:
```javascript
import React, { useState, useEffect } from 'react';
import api from './utils/api';

function ModelsList() {
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/api/v1/models/')
            .then(response => {
                setModels(response.data.models);
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching models:', error);
                setLoading(false);
            });
    }, []);

    if (loading) return <div>Loading...</div>;

    return (
        <div>
            <h1>Models ({models.length})</h1>
            {models.map(model => (
                <div key={model.id}>
                    <h3>{model.name}</h3>
                    <img src={model.imageUrl} alt={model.name} />
                </div>
            ))}
        </div>
    );
}

export default ModelsList;
```

**Step 4:** For POST requests (uploading):
```javascript
const uploadModel = async (name, imageFile) => {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('image', imageFile);

    try {
        const response = await api.post('/api/v1/models/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    } catch (error) {
        console.error('Upload failed:', error);
        throw error;
    }
};
```

---

### Vue 3

#### Step 1: Create API plugin (`src/plugins/api.js`):
```javascript
import axios from 'axios';

const api = axios.create({
    baseURL: 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio',
    headers: {
        'ngrok-skip-browser-warning': 'true'
    }
});

export default {
    install: (app) => {
        app.config.globalProperties.$api = api;
        app.provide('api', api);
    }
};

export { api };
```

#### Step 2: Register plugin in `main.js`:
```javascript
import { createApp } from 'vue';
import App from './App.vue';
import apiPlugin from './plugins/api';

const app = createApp(App);
app.use(apiPlugin);
app.mount('#app');
```

#### Step 3: Use in components:
```vue
<template>
  <div>
    <h1>Models</h1>
    <div v-if="loading">Loading...</div>
    <div v-else>
      <div v-for="model in models" :key="model.id">
        <h3>{{ model.name }}</h3>
        <img :src="model.imageUrl" :alt="model.name" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue';

const api = inject('api');
const models = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const response = await api.get('/api/v1/models/');
    models.value = response.data.models;
  } catch (error) {
    console.error('Error:', error);
  } finally {
    loading.value = false;
  }
});
</script>
```

---

### Angular

#### Step 1: Create API service (`src/app/services/api.service.ts`):
```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio';
  private headers = new HttpHeaders({
    'ngrok-skip-browser-warning': 'true'
  });

  constructor(private http: HttpClient) { }

  getModels(): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/v1/models/`, {
      headers: this.headers
    });
  }

  createModel(name: string, image: File): Observable<any> {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('image', image);

    // Note: Don't set Content-Type for FormData - Angular sets it automatically
    const headers = new HttpHeaders({
      'ngrok-skip-browser-warning': 'true'
    });

    return this.http.post(`${this.baseUrl}/api/v1/models/`, formData, {
      headers: headers
    });
  }

  deleteModel(id: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/api/v1/models/${id}/`, {
      headers: this.headers
    });
  }
}
```

#### Step 2: Use in component:
```typescript
import { Component, OnInit } from '@angular/core';
import { ApiService } from './services/api.service';

@Component({
  selector: 'app-models',
  template: `
    <h1>Models</h1>
    <div *ngIf="loading">Loading...</div>
    <div *ngFor="let model of models">
      <h3>{{ model.name }}</h3>
      <img [src]="model.imageUrl" [alt]="model.name" />
    </div>
  `
})
export class ModelsComponent implements OnInit {
  models: any[] = [];
  loading = true;

  constructor(private apiService: ApiService) { }

  ngOnInit(): void {
    this.apiService.getModels().subscribe({
      next: (data) => {
        this.models = data.models;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error:', error);
        this.loading = false;
      }
    });
  }
}
```

---

### Vanilla JavaScript

```javascript
// Create a reusable API client
const API = {
    baseURL: 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio',
    headers: {
        'ngrok-skip-browser-warning': 'true'
    },

    async get(endpoint) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            headers: this.headers
        });
        return response.json();
    },

    async post(endpoint, data) {
        const headers = { ...this.headers };
        let body;

        if (data instanceof FormData) {
            body = data;
            // Don't set Content-Type for FormData - browser sets it with boundary
        } else {
            headers['Content-Type'] = 'application/json';
            body = JSON.stringify(data);
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers: headers,
            body: body
        });
        return response.json();
    },

    async delete(endpoint) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'DELETE',
            headers: this.headers
        });
        return response.status === 204 ? null : response.json();
    }
};

// Usage examples
async function loadModels() {
    try {
        const data = await API.get('/api/v1/models/');
        console.log('Models:', data.models);
    } catch (error) {
        console.error('Error:', error);
    }
}

async function uploadModel(name, file) {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('image', file);

    try {
        const model = await API.post('/api/v1/models/', formData);
        console.log('Created model:', model);
    } catch (error) {
        console.error('Upload failed:', error);
    }
}
```

---

## 🔧 Troubleshooting

### Issue 1: Still Getting HTML Response

**Check:**
1. Is the header spelled correctly? `ngrok-skip-browser-warning`
2. Is the value `'true'` (as a string)?
3. Are you adding it to **every** request?

**Test:**
```javascript
// Open browser console and run:
fetch('https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/', {
    headers: { 'ngrok-skip-browser-warning': 'true' }
})
.then(r => r.json())
.then(d => console.log(d));

// You should see JSON, not HTML
```

---

### Issue 2: CORS Error

If you see CORS errors, it's likely your backend CORS configuration. Check `/Users/dgolani/Documents/AI_Studio/backend/.env`:

```bash
# Make sure CORS_ORIGINS is commented out or includes your frontend origin
#CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

The backend has CORS configured to allow all origins by default.

---

### Issue 3: Images Not Loading

If images return 404, make sure to add the header when loading images:

**React Example:**
```javascript
const ModelImage = ({ imageUrl, alt }) => {
    const [imageSrc, setImageSrc] = useState('');

    useEffect(() => {
        fetch(imageUrl, {
            headers: { 'ngrok-skip-browser-warning': 'true' }
        })
        .then(response => response.blob())
        .then(blob => {
            const objectUrl = URL.createObjectURL(blob);
            setImageSrc(objectUrl);
        });

        return () => {
            if (imageSrc) URL.revokeObjectURL(imageSrc);
        };
    }, [imageUrl]);

    return <img src={imageSrc} alt={alt} />;
};
```

---

## 💰 About Your Hobby Account

The ngrok warning page says **"upgrade to paid account"** to remove the warning for **BROWSER visits** (when you type URLs directly).

But for **API calls** (which your frontend makes), the header bypass works on **ALL plans**:
- ✅ Free Plan
- ✅ Hobby Plan (you)
- ✅ Pro Plan
- ✅ Enterprise Plan

Your Hobby account **IS working** and you're getting:
- ✅ 3 static domains (vs 1 on free)
- ✅ 3 active tunnels (vs 1 on free)
- ✅ 120 connections/minute (vs 40 on free)
- ✅ Custom domain support
- ✅ IP restrictions
- ✅ Email support

The warning you see when typing URLs in the browser is **normal and expected** on all plans. Just click "Visit Site" once per session.

---

## ✅ Final Checklist

Before deploying your frontend:

- [ ] Header added to HTTP client configuration
- [ ] Test all API endpoints with the header
- [ ] Images load correctly
- [ ] POST/PUT/DELETE requests include header
- [ ] Error handling in place
- [ ] Test on multiple devices (desktop, mobile, tablet)
- [ ] Test on different networks (WiFi, mobile data)

---

## 📚 Additional Resources

- **Test Page:** `/Users/dgolani/Documents/AI_Studio/backend/frontend/test_api.html`
- **API Documentation:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
- **Models API Guide:** `/Users/dgolani/Documents/AI_Studio/backend/MODELS_API_UNIFIED_DOCUMENTATION.md`
- **Looks API Guide:** `/Users/dgolani/Documents/AI_Studio/backend/LOOKS_API_DOCUMENTATION.md`
- **Ngrok Warning Explained:** `/Users/dgolani/Documents/AI_Studio/backend/UNDERSTANDING_NGROK_WARNING.md`

---

## 🆘 Still Having Issues?

1. **Check backend logs:**
   ```bash
   tail -f /tmp/backend.log
   ```

2. **Check reverse proxy logs:**
   ```bash
   tail -f /tmp/reverse_proxy.log
   ```

3. **Test API directly with cURL:**
   ```bash
   curl -v -H "ngrok-skip-browser-warning: true" \
     https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/
   ```

4. **Check browser console** for exact error messages

---

Last Updated: October 10, 2025

