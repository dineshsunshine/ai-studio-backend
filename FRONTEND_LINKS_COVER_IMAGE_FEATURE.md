# Links Cover Image Feature - Frontend Integration Guide

## Overview

We've added a cover image (masthead/hero image) feature for shareable links. Users can now upload, update, or remove a custom cover image that will be displayed at the top of their shared lookbook.

---

## Database Changes

**New Field Added to Link Model:**
- `cover_image_url` (String, nullable) - URL of the cover image

---

## API Changes

### 1. Existing Endpoints Updated

The `coverImageUrl` field is now included in all link responses:

#### GET /api/v1/links/ (List Links)
```json
{
  "links": [
    {
      "id": "uuid",
      "linkId": "AB12CD34",
      "clientName": "John Doe",
      "clientPhone": "+1234567890",
      "coverImageUrl": "https://storage.com/image.jpg",  // ← NEW FIELD
      "shortUrl": "https://domain.com/l/AB12CD34",
      "looks": [...],
      "createdAt": "2025-10-11T12:00:00Z",
      "updatedAt": "2025-10-11T12:00:00Z"
    }
  ],
  "total": 10,
  "skip": 0,
  "limit": 100
}
```

#### POST /api/v1/links/ (Create Link)
```json
{
  "id": "uuid",
  "linkId": "AB12CD34",
  "coverImageUrl": null,  // ← NEW FIELD (null for newly created links)
  "clientName": "John Doe",
  ...
}
```

#### GET /api/v1/links/shared/{linkId} (Public Shared Link)
```json
{
  "linkId": "AB12CD34",
  "clientName": "John Doe",
  "coverImageUrl": "https://storage.com/image.jpg",  // ← NEW FIELD
  "looks": [...],
  "createdAt": "2025-10-11T12:00:00Z"
}
```

---

## New API Endpoints

### 2. Upload/Update Cover Image

**Endpoint:** `PUT /api/v1/links/{link_id}/cover`  
**Method:** PUT  
**Authentication:** Required (Bearer token)  
**Content-Type:** `multipart/form-data`

**Path Parameters:**
- `link_id` (string): UUID of the link (not the alphanumeric linkId)

**Request Body:**
```
Form Data:
- cover_image: [File] (required)
```

**Supported File Types:**
- image/jpeg
- image/jpg
- image/png
- image/webp
- image/gif

**Response** (200 OK):
```json
{
  "id": "uuid",
  "linkId": "AB12CD34",
  "clientName": "John Doe",
  "clientPhone": "+1234567890",
  "coverImageUrl": "https://storage.com/new-image.jpg",  // ← Updated
  "shortUrl": "https://domain.com/l/AB12CD34",
  "looks": [...],
  "createdAt": "2025-10-11T12:00:00Z",
  "updatedAt": "2025-10-11T13:00:00Z"
}
```

**Error Responses:**
- `400`: Invalid file type
- `403`: User doesn't own this link
- `404`: Link not found
- `500`: Upload failed

**Behavior:**
- If an old cover image exists, it will be deleted from storage
- New image is uploaded to cloud storage
- Link's `coverImageUrl` is updated with the new URL

---

### 3. Remove Cover Image

**Endpoint:** `DELETE /api/v1/links/{link_id}/cover`  
**Method:** DELETE  
**Authentication:** Required (Bearer token)

**Path Parameters:**
- `link_id` (string): UUID of the link

**Response** (200 OK):
```json
{
  "id": "uuid",
  "linkId": "AB12CD34",
  "clientName": "John Doe",
  "clientPhone": "+1234567890",
  "coverImageUrl": null,  // ← Set to null
  "shortUrl": "https://domain.com/l/AB12CD34",
  "looks": [...],
  "createdAt": "2025-10-11T12:00:00Z",
  "updatedAt": "2025-10-11T14:00:00Z"
}
```

**Error Responses:**
- `403`: User doesn't own this link
- `404`: Link not found

**Behavior:**
- Deletes the cover image from cloud storage
- Sets `coverImageUrl` to `null` in the database

---

## Frontend Implementation Guide

### Displaying Cover Image

When displaying a link (either in link management or shared view), check if `coverImageUrl` exists:

```typescript
function renderLink(link: Link) {
  // Check if cover image exists
  if (link.coverImageUrl) {
    return (
      <div>
        <img 
          src={link.coverImageUrl} 
          alt="Cover Image" 
          style={{
            width: '100%',
            maxHeight: '500px',
            objectFit: 'cover',
            borderRadius: '16px'
          }}
        />
        {/* Rest of the link content */}
      </div>
    );
  }
  
  // No cover image, render normally
  return <div>{/* Link content */}</div>;
}
```

### Uploading Cover Image

```typescript
async function uploadCoverImage(linkId: string, imageFile: File, accessToken: string) {
  const formData = new FormData();
  formData.append('cover_image', imageFile);

  const response = await fetch(`${API_BASE_URL}/api/v1/links/${linkId}/cover`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'ngrok-skip-browser-warning': 'true'
    },
    body: formData  // Don't set Content-Type, browser will set it automatically
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload cover image');
  }

  const updatedLink = await response.json();
  return updatedLink;
}
```

### Removing Cover Image

```typescript
async function removeCoverImage(linkId: string, accessToken: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/links/${linkId}/cover`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'ngrok-skip-browser-warning': 'true'
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to remove cover image');
  }

  const updatedLink = await response.json();
  return updatedLink;
}
```

---

## UI Recommendations

### Link Management Page

Add a "Cover Image" section when creating/editing a link:

```
┌─────────────────────────────────────┐
│  Create New Link                    │
├─────────────────────────────────────┤
│                                     │
│  Client Name: [___________________] │
│  Phone: [___________________]       │
│                                     │
│  Cover Image (Optional):            │
│  ┌────────────────────────────────┐ │
│  │  [Upload Image]  [Remove]      │ │
│  │                                │ │
│  │  ┌──────────────────────────┐ │ │
│  │  │  Preview of cover image  │ │ │
│  │  └──────────────────────────┘ │ │
│  └────────────────────────────────┘ │
│                                     │
│  Select Looks: [□] Look 1          │
│                [□] Look 2          │
│                                     │
│  [Create Link]                      │
└─────────────────────────────────────┘
```

### Shared Link Viewer

The cover image should appear at the top of the lookbook, just below the header:

```
┌─────────────────────────────────────┐
│  ✨ Your Curated Lookbook            │
│  For John Doe                       │
│  Created on October 11, 2025        │
├─────────────────────────────────────┤
│  ┌──────────────────────────────┐  │
│  │                              │  │
│  │   COVER IMAGE (if exists)    │  │
│  │                              │  │
│  └──────────────────────────────┘  │
├─────────────────────────────────────┤
│  ┌─────┐ ┌─────┐ ┌─────┐          │
│  │Look │ │Look │ │Look │          │
│  │  1  │ │  2  │ │  3  │          │
│  └─────┘ └─────┘ └─────┘          │
└─────────────────────────────────────┘
```

---

## Testing

### Development (ngrok)

1. **Upload Cover Image:**
   ```bash
   curl -X PUT \
     https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/links/{link-uuid}/cover \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "ngrok-skip-browser-warning: true" \
     -F "cover_image=@/path/to/image.jpg"
   ```

2. **View Link with Cover:**
   ```
   GET https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/links/{link-uuid}
   ```

3. **Remove Cover Image:**
   ```bash
   curl -X DELETE \
     https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/links/{link-uuid}/cover \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "ngrok-skip-browser-warning: true"
   ```

### Production (Render)

Same URLs but replace with: `https://ai-studio-backend-ijkp.onrender.com/api/v1/links/...`

---

## Key Points

1. ✅ **Optional Feature**: `coverImageUrl` can be `null` - handle both cases
2. ✅ **Automatic Cleanup**: Old cover images are automatically deleted when updated
3. ✅ **File Validation**: Only image files are accepted
4. ✅ **User Ownership**: Users can only modify their own links
5. ✅ **Storage**: Images are stored in cloud storage (same as look/model images)
6. ✅ **Public Access**: Cover images are publicly accessible (no auth needed to view)

---

## Summary

**What changed:**
- Added `coverImageUrl` field to all link responses
- Added `PUT /api/v1/links/{link_id}/cover` to upload/update cover image
- Added `DELETE /api/v1/links/{link_id}/cover` to remove cover image
- Updated shared link viewer HTML to display cover images

**What you need to do:**
- Update your link management UI to allow uploading/removing cover images
- Display cover images when rendering links (if they exist)
- Test with both dev (ngrok) and production (Render) environments

The backend is ready! Render will auto-deploy the changes in ~2-3 minutes.


