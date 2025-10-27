# Frontend Environment Configuration Guide

## Overview

Our AI Studio backend is now available in **two environments**:

1. **Development (Local/Ngrok)**: For testing and development
2. **Production (Render)**: For live/production use

You need to implement environment configuration in the frontend to easily switch between these two systems.

---

## Environment URLs

### Development Environment (Ngrok)
- **Base URL**: `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio`
- **API Base**: `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1`
- **Swagger Docs**: `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs`
- **Assets Base**: `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/assets`

### Production Environment (Render)
- **Base URL**: `https://ai-studio-backend-ijkp.onrender.com`
- **API Base**: `https://ai-studio-backend-ijkp.onrender.com/api/v1`
- **Swagger Docs**: `https://ai-studio-backend-ijkp.onrender.com/docs`
- **Assets Base**: `https://ai-studio-backend-ijkp.onrender.com/assets`

---

## Implementation Steps

### 1. Create an Environment Configuration File

Create a file called `config.ts` (or `config.js`) in your project's `src` directory:

```typescript
// src/config.ts

// Environment type
export type Environment = 'development' | 'production';

// Environment configuration interface
interface EnvironmentConfig {
  apiBaseUrl: string;
  assetsBaseUrl: string;
  docsUrl: string;
  environment: Environment;
}

// Development configuration (Ngrok)
const developmentConfig: EnvironmentConfig = {
  apiBaseUrl: 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1',
  assetsBaseUrl: 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/assets',
  docsUrl: 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs',
  environment: 'development',
};

// Production configuration (Render)
const productionConfig: EnvironmentConfig = {
  apiBaseUrl: 'https://ai-studio-backend-ijkp.onrender.com/api/v1',
  assetsBaseUrl: 'https://ai-studio-backend-ijkp.onrender.com/assets',
  docsUrl: 'https://ai-studio-backend-ijkp.onrender.com/docs',
  environment: 'production',
};

// Current environment (change this to switch environments)
const CURRENT_ENV: Environment = 'production'; // Change to 'development' for ngrok

// Export the active configuration
export const config: EnvironmentConfig = 
  CURRENT_ENV === 'production' ? productionConfig : developmentConfig;

// Helper to check environment
export const isDevelopment = () => config.environment === 'development';
export const isProduction = () => config.environment === 'production';
```

### 2. Use the Configuration in Your API Calls

When making API calls, import and use the `config` object:

```typescript
// Example: src/services/api.ts
import { config } from '../config';

// Authentication API
export const authApi = {
  googleLogin: async (idToken: string) => {
    const response = await fetch(`${config.apiBaseUrl}/auth/google`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Important: Add this header to bypass ngrok browser warning
        'ngrok-skip-browser-warning': 'true',
      },
      body: JSON.stringify({ idToken }),
    });
    return response.json();
  },
  
  getCurrentUser: async (accessToken: string) => {
    const response = await fetch(`${config.apiBaseUrl}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
    });
    return response.json();
  },
};

// Settings API
export const settingsApi = {
  getSettings: async (accessToken: string) => {
    const response = await fetch(`${config.apiBaseUrl}/settings`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
    });
    return response.json();
  },
  
  updateSettings: async (accessToken: string, settings: any) => {
    const response = await fetch(`${config.apiBaseUrl}/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
      body: JSON.stringify(settings),
    });
    return response.json();
  },
  
  resetSettings: async (accessToken: string) => {
    const response = await fetch(`${config.apiBaseUrl}/settings/reset`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
    });
    return response.json();
  },
};

// Models API
export const modelsApi = {
  listModels: async (accessToken: string) => {
    const response = await fetch(`${config.apiBaseUrl}/models/`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
    });
    return response.json();
  },
  
  createModel: async (accessToken: string, formData: FormData) => {
    const response = await fetch(`${config.apiBaseUrl}/models/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
        // Don't set Content-Type for FormData, browser will set it with boundary
      },
      body: formData,
    });
    return response.json();
  },
  
  deleteModel: async (accessToken: string, modelId: string) => {
    const response = await fetch(`${config.apiBaseUrl}/models/${modelId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
    });
    return response.status === 204;
  },
};

// Looks API
export const looksApi = {
  listLooks: async (accessToken: string) => {
    const response = await fetch(`${config.apiBaseUrl}/looks/`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
    });
    return response.json();
  },
  
  createLook: async (accessToken: string, lookData: any) => {
    const response = await fetch(`${config.apiBaseUrl}/looks/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
      body: JSON.stringify(lookData),
    });
    return response.json();
  },
  
  deleteLook: async (accessToken: string, lookId: string) => {
    const response = await fetch(`${config.apiBaseUrl}/looks/${lookId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
    });
    return response.status === 204;
  },
};

// Admin API (for admin users only)
export const adminApi = {
  listUsers: async (accessToken: string) => {
    const response = await fetch(`${config.apiBaseUrl}/admin/users`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
    });
    return response.json();
  },
  
  updateUser: async (accessToken: string, userId: string, updates: any) => {
    const response = await fetch(`${config.apiBaseUrl}/admin/users/${userId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
      body: JSON.stringify(updates),
    });
    return response.json();
  },
  
  listAccessRequests: async (accessToken: string) => {
    const response = await fetch(`${config.apiBaseUrl}/admin/access-requests`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
    });
    return response.json();
  },
  
  approveAccessRequest: async (accessToken: string, requestId: string, role: string = 'user') => {
    const response = await fetch(`${config.apiBaseUrl}/admin/access-requests/${requestId}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
      body: JSON.stringify({ role }),
    });
    return response.json();
  },
  
  rejectAccessRequest: async (accessToken: string, requestId: string, reason?: string) => {
    const response = await fetch(`${config.apiBaseUrl}/admin/access-requests/${requestId}/reject`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
      body: JSON.stringify({ reason }),
    });
    return response.json();
  },
  
  getDefaultSettings: async (accessToken: string) => {
    const response = await fetch(`${config.apiBaseUrl}/admin/defaults`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
    });
    return response.json();
  },
  
  updateDefaultSettings: async (accessToken: string, defaults: any) => {
    const response = await fetch(`${config.apiBaseUrl}/admin/defaults`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true',
      },
      body: JSON.stringify(defaults),
    });
    return response.json();
  },
};
```

### 3. Use Asset URLs Correctly

When displaying images from the backend (model images, look images, product thumbnails):

```typescript
import { config } from '../config';

// The backend returns relative URLs like: "/assets/models/abc123.jpeg"
// You need to prepend the base URL

function getFullImageUrl(relativeUrl: string): string {
  // Remove leading slash if present
  const cleanUrl = relativeUrl.startsWith('/') ? relativeUrl.substring(1) : relativeUrl;
  
  // For assets that start with "/assets/", use assetsBaseUrl directly
  if (relativeUrl.startsWith('/assets/')) {
    // In production: https://ai-studio-backend-ijkp.onrender.com + /assets/models/abc.jpeg
    // In dev: https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio + /assets/models/abc.jpeg
    const baseWithoutAssets = config.assetsBaseUrl.replace('/assets', '');
    return `${baseWithoutAssets}${relativeUrl}`;
  }
  
  return `${config.assetsBaseUrl}/${cleanUrl}`;
}

// Usage example in a React component
function ModelCard({ model }) {
  const fullImageUrl = getFullImageUrl(model.imageUrl);
  
  return (
    <img 
      src={fullImageUrl} 
      alt={model.name}
      onError={(e) => {
        console.error('Failed to load image:', fullImageUrl);
        e.currentTarget.src = '/placeholder-image.png'; // Fallback
      }}
    />
  );
}
```

---

## Switching Between Environments

### Method 1: Simple Manual Toggle (Recommended for now)

In your `config.ts` file, just change the `CURRENT_ENV` constant:

```typescript
// For development/testing with ngrok:
const CURRENT_ENV: Environment = 'development';

// For production:
const CURRENT_ENV: Environment = 'production';
```

### Method 2: Using Environment Variables (Advanced)

If you want automatic environment detection based on build:

```typescript
// src/config.ts

const CURRENT_ENV: Environment = 
  import.meta.env.MODE === 'production' ? 'production' : 'development';
```

Then use build scripts:
- `npm run dev` → Uses development (ngrok)
- `npm run build` → Uses production (Render)

### Method 3: UI Toggle (Optional)

Add a settings panel in your app where admins can switch environments:

```typescript
// Store environment choice in localStorage
export function setEnvironment(env: Environment) {
  localStorage.setItem('api-environment', env);
  window.location.reload(); // Reload to apply changes
}

export function getStoredEnvironment(): Environment {
  return (localStorage.getItem('api-environment') as Environment) || 'production';
}

// Then in config.ts:
const CURRENT_ENV: Environment = getStoredEnvironment();
```

---

## Important Headers for All API Calls

Always include these headers in **every API request**:

```typescript
{
  'ngrok-skip-browser-warning': 'true',  // Bypasses ngrok browser warning
  'Content-Type': 'application/json',     // For POST/PUT with JSON body
  'Authorization': `Bearer ${accessToken}` // For authenticated endpoints
}
```

**Note**: The `ngrok-skip-browser-warning` header is required even for production (Render) calls. It won't cause any issues on production and ensures compatibility with both environments.

---

## Complete API Endpoint Reference

All endpoints are relative to `${config.apiBaseUrl}`:

### Authentication
- `POST /auth/google` - Google OAuth login
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout
- `POST /auth/request-access` - Request access (non-OAuth)
- `GET /auth/request-status?email={email}` - Check access request status

### User Settings
- `GET /settings` - Get user settings
- `PUT /settings` - Update user settings
- `POST /settings/reset` - Reset settings to defaults
- `GET /settings/info` - Get settings with metadata

### Models
- `GET /models/` - List models
- `POST /models/` - Create model (FormData: name, image OR promptDetails)
- `GET /models/{id}` - Get single model
- `DELETE /models/{id}` - Delete model

### Looks
- `GET /looks/` - List looks
- `POST /looks/` - Create look (JSON with base64 images)
- `GET /looks/{id}` - Get single look
- `PATCH /looks/{id}` - Update look (title/notes only)
- `DELETE /looks/{id}` - Delete look

### Admin (Admin users only)
- `GET /admin/users` - List all users
- `PATCH /admin/users/{id}` - Update user role/status
- `DELETE /admin/users/{id}` - Delete user
- `GET /admin/access-requests` - List access requests
- `POST /admin/access-requests/{id}/approve` - Approve request
- `POST /admin/access-requests/{id}/reject` - Reject request
- `GET /admin/defaults` - Get default settings
- `PUT /admin/defaults` - Update default settings
- `POST /admin/defaults/reset` - Reset default settings

### System
- `GET /health` - Health check
- `GET /` - API info

---

## Testing & Debugging

### 1. Test API Connectivity

Add a simple connectivity test in your app:

```typescript
async function testApiConnection() {
  try {
    const response = await fetch(`${config.apiBaseUrl}/health`, {
      headers: { 'ngrok-skip-browser-warning': 'true' }
    });
    const data = await response.json();
    console.log('✅ API connected:', data);
    return true;
  } catch (error) {
    console.error('❌ API connection failed:', error);
    return false;
  }
}
```

### 2. View API Documentation

Open the Swagger docs URL in your browser to see all available endpoints and test them:

- Development: https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
- Production: https://ai-studio-backend-ijkp.onrender.com/docs

### 3. Common Issues

**Issue**: Images not loading
- **Fix**: Make sure you're constructing the full URL correctly (see "Use Asset URLs Correctly" section above)

**Issue**: 401 Unauthorized
- **Fix**: Check that you're including the `Authorization: Bearer {token}` header

**Issue**: CORS errors
- **Fix**: The backend already allows CORS. Make sure you're including the `ngrok-skip-browser-warning` header.

**Issue**: "Network request failed" on production
- **Fix**: Check if Render service is awake (free tier sleeps after inactivity). First request may take 30-60 seconds.

---

## Environment Comparison

| Feature | Development (Ngrok) | Production (Render) |
|---------|---------------------|---------------------|
| **Stability** | May disconnect if laptop sleeps | Always online (24/7) |
| **Speed** | Fast (local machine) | Slower cold starts (free tier) |
| **Database** | SQLite (local file) | PostgreSQL (cloud) |
| **Data Persistence** | Lost if you reset | Permanent |
| **Best For** | Testing, development | Live usage, demos |
| **URL Stability** | Changes if ngrok restarts | Fixed URL |

---

## Recommendation

- **Use Development (Ngrok)** when:
  - You're actively developing new features
  - You need to test quickly with frequent backend changes
  - You're on the same network as the backend developer

- **Use Production (Render)** when:
  - You're demoing to clients or stakeholders
  - You need data to persist
  - Multiple team members need access simultaneously
  - The backend is stable and changes are infrequent

---

## Quick Start Checklist

- [ ] Create `config.ts` file with both environment configurations
- [ ] Set `CURRENT_ENV` to desired environment
- [ ] Replace all hardcoded API URLs with `config.apiBaseUrl`
- [ ] Add `ngrok-skip-browser-warning: true` header to all requests
- [ ] Test connectivity with `/health` endpoint
- [ ] Verify image URLs are constructed correctly
- [ ] Test Google OAuth login
- [ ] Verify all API calls work as expected

---

## Questions or Issues?

If something doesn't work:
1. Check the browser console for error messages
2. Open the Swagger docs to verify the API is accessible
3. Test the `/health` endpoint to confirm connectivity
4. Verify you're using the correct environment URLs
5. Check that all required headers are included in requests

For further assistance, reach out with:
- The specific API endpoint that's failing
- The full error message from the browser console
- Which environment you're using (dev or production)


