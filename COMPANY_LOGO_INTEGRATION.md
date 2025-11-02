# 🏢 Company Logo Branding Feature - Frontend Integration Guide

## Overview

Users can now upload a company logo from their settings that will be displayed on all their sharable lookbook links for professional branding.

---

## User Flow

### 1. Upload Logo (Settings Page)
User goes to settings and:
1. Clicks "Upload Company Logo" button
2. Selects an image file (PNG, JPG, WebP, GIF)
3. Logo is uploaded and displayed on sharable links

### 2. View Logo (Sharable Link)
When a client visits a sharable link, they see:
- Company logo at the top/header (user configurable)
- Creates professional branding experience

### 3. Delete Logo
User can remove logo from settings anytime

---

## API Endpoints

### Upload/Update Logo

**Endpoint:** `PUT /api/v1/settings/logo`

**Authentication:** Required (JWT)

**Request:**
```
Content-Type: multipart/form-data

Field: logo_file (file)
- Accepts: PNG, JPG, WebP, GIF
- Max size: Per your storage service limits
```

**Response:**
```json
{
  "companyLogoUrl": "https://res.cloudinary.com/...",
  "message": "Logo uploaded successfully"
}
```

**Error Responses:**
```json
{
  "detail": "Invalid file type. Allowed types: image/png, image/jpeg, image/webp, image/gif"
}
```

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('logo_file', logoFileInput.files[0]);

const response = await fetch('/api/v1/settings/logo', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${jwtToken}`
  },
  body: formData
});

const data = await response.json();
console.log('Logo URL:', data.companyLogoUrl);
```

---

### Delete Logo

**Endpoint:** `DELETE /api/v1/settings/logo`

**Authentication:** Required (JWT)

**Response:**
```json
{
  "message": "Logo deleted successfully",
  "companyLogoUrl": null
}
```

---

### Get Settings (includes logo)

**Endpoint:** `GET /api/v1/settings`

**Authentication:** Required (JWT)

**Response:**
```json
{
  "theme": "dark",
  "companyLogoUrl": "https://res.cloudinary.com/...",
  "toolSettings": {
    "lookCreator": { ... },
    "copywriter": { ... },
    "finishingStudio": { ... },
    "modelManager": { ... }
  }
}
```

---

### Update Settings (including logo URL)

**Endpoint:** `PUT /api/v1/settings`

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "theme": "dark",
  "companyLogoUrl": "https://res.cloudinary.com/...",
  "toolSettings": { ... }
}
```

---

## Frontend Implementation

### 1. Settings Panel - Logo Upload

```javascript
// HTML
<div class="logo-section">
  <label>Company Logo</label>
  <input type="file" id="logoUpload" accept="image/png,image/jpeg,image/webp,image/gif">
  <button onclick="uploadLogo()">Upload Logo</button>
  {companyLogoUrl && (
    <>
      <img src={companyLogoUrl} alt="Company Logo" style={{maxWidth: '200px'}} />
      <button onclick="deleteLogo()">Delete Logo</button>
    </>
  )}
</div>

// JavaScript
async function uploadLogo() {
  const file = document.getElementById('logoUpload').files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('logo_file', file);

  try {
    const response = await fetch('/api/v1/settings/logo', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
      },
      body: formData
    });

    if (response.ok) {
      const data = await response.json();
      // Update local state with new logo URL
      setCompanyLogoUrl(data.companyLogoUrl);
      alert('Logo uploaded successfully!');
      // Refresh settings
      fetchSettings();
    }
  } catch (error) {
    console.error('Upload failed:', error);
    alert('Failed to upload logo');
  }
}

async function deleteLogo() {
  try {
    const response = await fetch('/api/v1/settings/logo', {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
      }
    });

    if (response.ok) {
      setCompanyLogoUrl(null);
      alert('Logo deleted successfully');
      // Refresh settings
      fetchSettings();
    }
  } catch (error) {
    console.error('Delete failed:', error);
    alert('Failed to delete logo');
  }
}
```

---

### 2. Display Logo on Sharable Link Page

```javascript
// When fetching sharable link data
async function loadSharableLink(linkId) {
  const response = await fetch(`/api/v1/links/shared/${linkId}`, {
    headers: { 'ngrok-skip-browser-warning': '1' }
  });

  const linkData = await response.json();
  
  // linkData.companyLogoUrl contains the company logo
  // linkData.title - link title
  // linkData.description - link description
  // linkData.coverImageUrl - cover image
  // linkData.looks[] - array of looks
  
  return linkData;
}

// Display on page
function displaySharableLink(linkData) {
  const container = document.getElementById('linkContainer');
  
  // Display header with logo
  const header = document.createElement('div');
  header.className = 'link-header';
  
  if (linkData.companyLogoUrl) {
    const logo = document.createElement('img');
    logo.src = linkData.companyLogoUrl;
    logo.alt = 'Company Logo';
    logo.className = 'company-logo';
    logo.style.maxWidth = '200px';
    logo.style.height = 'auto';
    header.appendChild(logo);
  }
  
  const title = document.createElement('h1');
  title.textContent = linkData.title;
  header.appendChild(title);
  
  if (linkData.description) {
    const desc = document.createElement('p');
    desc.textContent = linkData.description;
    header.appendChild(desc);
  }
  
  container.appendChild(header);
  
  // Display looks...
}
```

---

### 3. Settings Fetch (React Example)

```javascript
import { useEffect, useState } from 'react';

export function SettingsPanel() {
  const [settings, setSettings] = useState(null);
  const [companyLogoUrl, setCompanyLogoUrl] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/v1/settings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSettings(data);
        setCompanyLogoUrl(data.companyLogoUrl);
      }
    } catch (error) {
      console.error('Fetch settings failed:', error);
    }
  };

  const handleLogoUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);

    const formData = new FormData();
    formData.append('logo_file', file);

    try {
      const response = await fetch('/api/v1/settings/logo', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setCompanyLogoUrl(data.companyLogoUrl);
      }
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteLogo = async () => {
    try {
      const response = await fetch('/api/v1/settings/logo', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        }
      });

      if (response.ok) {
        setCompanyLogoUrl(null);
      }
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  return (
    <div className="settings-panel">
      <h2>Company Branding</h2>
      
      <div className="logo-section">
        <label>Company Logo</label>
        <input
          type="file"
          accept="image/png,image/jpeg,image/webp,image/gif"
          onChange={handleLogoUpload}
          disabled={uploading}
        />
        
        {companyLogoUrl && (
          <>
            <img
              src={companyLogoUrl}
              alt="Company Logo"
              style={{ maxWidth: '200px', marginTop: '16px' }}
            />
            <button
              onClick={handleDeleteLogo}
              style={{ marginTop: '8px' }}
            >
              Delete Logo
            </button>
          </>
        )}
      </div>

      {/* Rest of settings... */}
    </div>
  );
}
```

---

## Sharable Link Display (HTML/CSS)

```html
<!-- Header with Logo -->
<div class="link-header">
  {% if companyLogoUrl %}
    <img src="{{ companyLogoUrl }}" alt="Company Logo" class="company-logo">
  {% endif %}
  
  <h1>{{ title }}</h1>
  {% if description %}
    <p class="description">{{ description }}</p>
  {% endif %}
</div>

<!-- CSS -->
<style>
  .link-header {
    text-align: center;
    padding: 40px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 40px;
  }

  .company-logo {
    max-width: 250px;
    height: auto;
    margin-bottom: 24px;
    filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
  }

  .link-header h1 {
    font-size: clamp(28px, 5vw, 48px);
    margin: 16px 0;
  }

  .link-header .description {
    color: rgba(255, 255, 255, 0.6);
    font-size: 16px;
    max-width: 600px;
    margin: 12px auto 0;
  }

  /* Light mode */
  .light-mode .link-header {
    border-bottom-color: rgba(0, 0, 0, 0.1);
  }

  .light-mode .link-header .description {
    color: rgba(0, 0, 0, 0.6);
  }
</style>
```

---

## Data Flow

```
Settings Page:
  User selects logo image
       ↓
  PUT /api/v1/settings/logo
       ↓
  Backend uploads to Cloudinary
       ↓
  Stores URL in user_settings.company_logo_url
       ↓
  Returns companyLogoUrl to frontend

───────────────────────────────

Sharable Link Page:
  GET /api/v1/links/shared/{linkId}
       ↓
  Backend queries user_settings for company_logo_url
       ↓
  Includes companyLogoUrl in response
       ↓
  Frontend displays logo in header
```

---

## Validation & Error Handling

**File Type Validation:**
- Only PNG, JPG, WebP, GIF allowed
- Backend validates content-type
- Return 400 Bad Request if invalid

**Storage:**
- Files stored on Cloudinary in `logos/` folder
- Old logo automatically deleted when new one uploaded
- Logo URL stored as string in database (nullable)

**Error Cases:**
```javascript
// Invalid file type
{
  "detail": "Invalid file type. Allowed types: image/png, image/jpeg, image/webp, image/gif"
}

// Upload fails
{
  "detail": "Failed to upload logo"
}

// Not authenticated
{
  "detail": "Not authenticated"
}
```

---

## Testing Checklist

- [ ] Upload PNG logo
- [ ] Upload JPG logo
- [ ] Upload WebP logo
- [ ] Upload invalid format (should fail)
- [ ] Delete logo
- [ ] Verify logo appears on sharable link
- [ ] Switch between light/dark mode (logo should display)
- [ ] Check logo in public sharable link
- [ ] Verify old logo deleted when uploading new one

---

## Notes

- Logo is optional (nullable field)
- Each user has their own company logo
- Logo displays on all that user's sharable links
- Logo URL is publicly accessible (no auth required)
- Use CDN URL from Cloudinary for best performance
- Logo persists across settings updates

---

**Happy branding! 🎨**
