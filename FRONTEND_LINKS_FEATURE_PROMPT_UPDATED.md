# Links Feature - Frontend Integration Guide

## ⚠️ FIELD NAMES UPDATED

**The Links API has been updated with better field names:**

- `clientName` → `title` (Link title)
- `clientPhone` → `description` (Link description, optional)

All examples below reflect the NEW field names.

---

## Overview

Implement a "Links" feature that allows users to create shareable collections of looks. Each link has a unique short URL that can be shared to view the selected looks.

---

## Core Concept

1. **User** creates a **Link** containing multiple **Looks**
2. **Link** has a title, description, and a unique alphanumeric ID
3. **Short URL** is generated automatically (e.g., `https://domain.com/l/AB12CD34`)
4. **Anyone** with the short URL can view all looks in that link (no login required)
5. **User** can manage (edit/delete) their links
6. **Cover Image** can be added to each link for visual appeal

---

## API Base URL

All endpoints are relative to your configured API base URL:

**Development**: `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1`  
**Production**: `https://ai-studio-backend-ijkp.onrender.com/api/v1`

---

## API Endpoints

### 1. Create Link

**Endpoint**: `POST /links/`  
**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "title": "Spring Collection 2025",
  "description": "Elegant spring looks for modern women",
  "lookIds": ["look-uuid-1", "look-uuid-2", "look-uuid-3"]
}
```

**Fields**:
- `title` (string, required, 1-255 chars): Link title/name
- `description` (string, optional, max 1000 chars): Link description
- `lookIds` (array, required, min 1 item): Array of look UUIDs to include

**Response** (201 Created):
```json
{
  "id": "link-uuid",
  "linkId": "AB12CD34",
  "title": "Spring Collection 2025",
  "description": "Elegant spring looks for modern women",
  "coverImageUrl": null,
  "shortUrl": "https://yourdomain.com/l/AB12CD34",
  "looks": [
    {
      "id": "look-uuid-1",
      "title": "Casual Summer",
      "notes": "Perfect for...",
      "generatedImageUrl": "https://...",
      "products": [...],
      "createdAt": "2025-10-11T12:00:00Z"
    }
  ],
  "createdAt": "2025-10-11T12:30:00Z",
  "updatedAt": "2025-10-11T12:30:00Z"
}
```

**Validation**:
- All looks must exist and belong to the user
- At least 1 look is required
- Title cannot be empty

---

### 2. List User's Links

**Endpoint**: `GET /links/`  
**Authentication**: Required (Bearer token)

**Query Parameters** (all optional):
- `skip` (int, default: 0): Number of records to skip
- `limit` (int, default: 100, max: 100): Number of records to return

**Response** (200 OK):
```json
{
  "links": [
    {
      "id": "link-uuid",
      "linkId": "AB12CD34",
      "title": "Spring Collection 2025",
      "description": "Elegant spring looks",
      "coverImageUrl": "https://...",
      "shortUrl": "https://yourdomain.com/l/AB12CD34",
      "looks": [...],
      "createdAt": "2025-10-11T12:00:00Z",
      "updatedAt": "2025-10-11T12:00:00Z"
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 100
}
```

---

### 3. Get Single Link

**Endpoint**: `GET /links/{link_id}`  
**Authentication**: Required (Bearer token)

**Path Parameters**:
- `link_id` (string): The UUID of the link (NOT the alphanumeric link ID)

**Response** (200 OK):
```json
{
  "id": "link-uuid",
  "linkId": "AB12CD34",
  "title": "Spring Collection 2025",
  "description": "Elegant spring looks",
  "coverImageUrl": "https://...",
  "shortUrl": "https://yourdomain.com/l/AB12CD34",
  "looks": [...],
  "createdAt": "2025-10-11T12:00:00Z",
  "updatedAt": "2025-10-11T12:00:00Z"
}
```

**Error Responses**:
- 404: Link not found or doesn't belong to you

---

### 4. Update Link

**Endpoint**: `PATCH /links/{link_id}`  
**Authentication**: Required (Bearer token)

**Path Parameters**:
- `link_id` (string): The UUID of the link

**Request Body** (all fields optional):
```json
{
  "title": "Summer Collection 2025",
  "description": "Beach-ready summer looks",
  "lookIds": ["look-uuid-1", "look-uuid-4"]
}
```

**Response** (200 OK):
```json
{
  "id": "link-uuid",
  "linkId": "AB12CD34",
  "title": "Summer Collection 2025",
  "description": "Beach-ready summer looks",
  "coverImageUrl": "https://...",
  "shortUrl": "https://yourdomain.com/l/AB12CD34",
  "looks": [...],
  "createdAt": "2025-10-11T12:00:00Z",
  "updatedAt": "2025-10-11T13:00:00Z"
}
```

**Notes**:
- Only the link owner can update it
- At least 1 look is required if updating `lookIds`
- All looks must exist and belong to the user

---

### 5. Delete Link

**Endpoint**: `DELETE /links/{link_id}`  
**Authentication**: Required (Bearer token)

**Path Parameters**:
- `link_id` (string): The UUID of the link

**Response** (200 OK):
```json
{
  "message": "Link deleted successfully"
}
```

**Notes**:
- Only the link owner can delete it
- The short URL will no longer work after deletion

---

### 6. Get Shared Link (Public)

**Endpoint**: `GET /links/shared/{alphanumeric_link_id}`  
**Authentication**: NOT required (public endpoint)

**Path Parameters**:
- `alphanumeric_link_id` (string): The short link ID (e.g., "AB12CD34")

**Response** (200 OK):
```json
{
  "linkId": "AB12CD34",
  "title": "Spring Collection 2025",
  "description": "Elegant spring looks",
  "coverImageUrl": "https://...",
  "looks": [
    {
      "id": "look-uuid",
      "title": "Casual Summer",
      "notes": "Perfect for...",
      "generatedImageUrl": "https://...",
      "products": [...],
      "createdAt": "2025-10-11T12:00:00Z"
    }
  ],
  "createdAt": "2025-10-11T12:00:00Z"
}
```

**Notes**:
- This endpoint does NOT require authentication
- Anyone with the link can view it
- User information is NOT included in the response

---

### 7. Upload/Update Cover Image

**Endpoint**: `PUT /links/{link_id}/cover`  
**Authentication**: Required (Bearer token)

**Path Parameters**:
- `link_id` (string): The UUID of the link

**Request Body** (multipart/form-data):
- `cover_image` (file): Image file (JPEG, PNG, WebP, or GIF)

**Response** (200 OK):
```json
{
  "id": "link-uuid",
  "linkId": "AB12CD34",
  "title": "Spring Collection 2025",
  "description": "Elegant spring looks",
  "coverImageUrl": "https://storage.com/image.jpg",
  "shortUrl": "https://yourdomain.com/l/AB12CD34",
  "looks": [...],
  "createdAt": "2025-10-11T12:00:00Z",
  "updatedAt": "2025-10-11T13:00:00Z"
}
```

**Notes**:
- Replaces existing cover image if present
- Old image is automatically deleted
- Only link owner can upload

---

### 8. Remove Cover Image

**Endpoint**: `DELETE /links/{link_id}/cover`  
**Authentication**: Required (Bearer token)

**Path Parameters**:
- `link_id` (string): The UUID of the link

**Response** (200 OK):
```json
{
  "id": "link-uuid",
  "linkId": "AB12CD34",
  "title": "Spring Collection 2025",
  "description": "Elegant spring looks",
  "coverImageUrl": null,
  "shortUrl": "https://yourdomain.com/l/AB12CD34",
  "looks": [...],
  "createdAt": "2025-10-11T12:00:00Z",
  "updatedAt": "2025-10-11T13:30:00Z"
}
```

---

## Implementation Flow

### Creating a Link

1. User selects multiple looks they want to share
2. User enters link title and optional description
3. Frontend calls `POST /links/` with:
   - `title`
   - `description` (optional)
   - `lookIds` (array of selected look UUIDs)
4. Backend returns the created link with `shortUrl`
5. Frontend displays the short URL for the user to copy/share

### Viewing a Shared Link

**Option A: React App Handles Routing** (Recommended)
1. User opens `https://yourdomain.com/AIStudio/l/AB12CD34`
2. React app sees route `/AIStudio/l/:linkId`
3. React app calls `GET /api/v1/links/shared/AB12CD34`
4. Display looks in a beautiful UI

**Option B: Backend Serves HTML** (Already implemented)
1. User opens `https://yourdomain.com/AIStudio/l/AB12CD34`
2. Backend serves a standalone HTML page
3. HTML page fetches data from `GET /api/v1/links/shared/AB12CD34`
4. Displays looks automatically

### Managing Links

1. User views list of their links via `GET /links/`
2. To edit: Call `PATCH /links/{id}` with updated fields
3. To delete: Call `DELETE /links/{id}`
4. To upload cover: Call `PUT /links/{id}/cover` with image file
5. To remove cover: Call `DELETE /links/{id}/cover`

---

## TypeScript Integration Examples

### Type Definitions

```typescript
interface Look {
  id: string;
  title: string;
  notes: string;
  generatedImageUrl: string;
  products: Product[];
  createdAt: string;
}

interface Link {
  id: string;
  linkId: string;
  title: string;
  description: string | null;
  coverImageUrl: string | null;
  shortUrl: string;
  looks: Look[];
  createdAt: string;
  updatedAt: string;
}

interface LinkListResponse {
  links: Link[];
  total: number;
  skip: number;
  limit: number;
}

interface SharedLink {
  linkId: string;
  title: string;
  description: string | null;
  coverImageUrl: string | null;
  looks: Look[];
  createdAt: string;
}
```

### Create Link

```typescript
async function createLink(accessToken: string, title: string, description: string, lookIds: string[]) {
  const response = await fetch(`${config.apiBaseUrl}/links/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
      'ngrok-skip-browser-warning': '1'
    },
    body: JSON.stringify({
      title,
      description,
      lookIds
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create link');
  }

  return await response.json() as Link;
}
```

### List Links

```typescript
async function listLinks(accessToken: string, skip = 0, limit = 100) {
  const response = await fetch(
    `${config.apiBaseUrl}/links/?skip=${skip}&limit=${limit}`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': '1'
      }
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch links');
  }

  return await response.json() as LinkListResponse;
}
```

### Get Single Link

```typescript
async function getLink(accessToken: string, linkId: string) {
  const response = await fetch(`${config.apiBaseUrl}/links/${linkId}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'ngrok-skip-browser-warning': '1'
    }
  });

  if (!response.ok) {
    throw new Error('Failed to fetch link');
  }

  return await response.json() as Link;
}
```

### Update Link

```typescript
async function updateLink(
  accessToken: string,
  linkDatabaseId: string,
  updates: { title?: string, description?: string, lookIds?: string[] }
) {
  const response = await fetch(`${config.apiBaseUrl}/links/${linkDatabaseId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
      'ngrok-skip-browser-warning': '1'
    },
    body: JSON.stringify(updates)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update link');
  }

  return await response.json() as Link;
}
```

### Delete Link

```typescript
async function deleteLink(accessToken: string, linkDatabaseId: string) {
  const response = await fetch(`${config.apiBaseUrl}/links/${linkDatabaseId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'ngrok-skip-browser-warning': '1'
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete link');
  }

  return await response.json();
}
```

### Get Shared Link (No Auth)

```typescript
async function getSharedLink(alphanumericLinkId: string) {
  const response = await fetch(
    `${config.apiBaseUrl}/links/shared/${alphanumericLinkId}`,
    {
      headers: {
        'ngrok-skip-browser-warning': '1'
      }
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch shared link');
  }

  return await response.json() as SharedLink;
}
```

### Upload Cover Image

```typescript
async function uploadCoverImage(accessToken: string, linkId: string, imageFile: File) {
  const formData = new FormData();
  formData.append('cover_image', imageFile);

  const response = await fetch(`${config.apiBaseUrl}/links/${linkId}/cover`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'ngrok-skip-browser-warning': '1'
    },
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload cover image');
  }

  return await response.json() as Link;
}
```

### Remove Cover Image

```typescript
async function removeCoverImage(accessToken: string, linkId: string) {
  const response = await fetch(`${config.apiBaseUrl}/links/${linkId}/cover`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'ngrok-skip-browser-warning': '1'
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to remove cover image');
  }

  return await response.json() as Link;
}
```

---

## UI Recommendations

### Links List Page

Display user's links in a grid or list:

```
┌─────────────────────────────────────────┐
│  My Links                    [+ New Link]│
├─────────────────────────────────────────┤
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ [Cover Image or Placeholder]     │   │
│  ├──────────────────────────────────┤   │
│  │ Spring Collection 2025           │   │
│  │ Elegant spring looks             │   │
│  │ 5 looks • AB12CD34               │   │
│  │ [Copy Link] [Edit] [Delete]      │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ [Cover Image or Placeholder]     │   │
│  ├──────────────────────────────────┤   │
│  │ Summer Collection 2025           │   │
│  │ Beach-ready looks                │   │
│  │ 3 looks • XY98ZW12               │   │
│  │ [Copy Link] [Edit] [Delete]      │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Create/Edit Link Form

```
┌─────────────────────────────────────────┐
│  Create New Link                    [X]  │
├─────────────────────────────────────────┤
│                                          │
│  Link Title *                            │
│  ┌────────────────────────────────────┐ │
│  │ Spring Collection 2025             │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Description (Optional)                  │
│  ┌────────────────────────────────────┐ │
│  │ Elegant spring looks for modern    │ │
│  │ women                              │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Select Looks *                          │
│  ┌────────────────────────────────────┐ │
│  │ ☑ Casual Summer Look               │ │
│  │ ☐ Formal Evening Wear              │ │
│  │ ☑ Business Casual                  │ │
│  │ ☑ Weekend Brunch                   │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Cover Image (Optional)                  │
│  [Upload Image] or drag & drop           │
│                                          │
│            [Cancel]     [Create Link]    │
└─────────────────────────────────────────┘
```

### Shared Link View

The backend already provides a beautiful standalone HTML viewer at `/l/{linkId}`. However, if you want to implement it in your React app:

```
┌─────────────────────────────────────────┐
│                                          │
│  [========== Cover Image ==========]    │
│                                          │
│          Spring Collection 2025         │
│       Elegant spring looks for          │
│              modern women               │
│                                          │
├─────────────────────────────────────────┤
│                                          │
│  ┌────────────┐  ┌────────────┐        │
│  │   Look 1   │  │   Look 2   │        │
│  │  [Image]   │  │  [Image]   │        │
│  │  Title     │  │  Title     │        │
│  │  Products  │  │  Products  │        │
│  └────────────┘  └────────────┘        │
│                                          │
│  ┌────────────┐  ┌────────────┐        │
│  │   Look 3   │  │   Look 4   │        │
│  │  [Image]   │  │  [Image]   │        │
│  │  Title     │  │  Title     │        │
│  │  Products  │  │  Products  │        │
│  └────────────┘  └────────────┘        │
│                                          │
│   Created with AI Studio ✨             │
└─────────────────────────────────────────┘
```

---

## Testing

### Test Creating a Link

1. Log in to get access token
2. Create or select 2-3 looks
3. Call `POST /links/` with title, description, and look IDs
4. Verify you receive `shortUrl` in response
5. Copy the short URL

### Test Viewing Shared Link

1. Open the short URL in an incognito window (no login)
2. Verify all looks are displayed
3. Verify title and description are shown
4. Verify no authentication errors

### Test Cover Image

1. Create a link
2. Upload a cover image using `PUT /links/{id}/cover`
3. View the shared link and verify the cover image appears
4. Update the cover image (upload a new one)
5. Verify the old image is replaced
6. Delete the cover image using `DELETE /links/{id}/cover`
7. Verify it's removed

### Test Editing

1. Create a link
2. Call `PATCH /links/{id}` to update title
3. Call `PATCH /links/{id}` to update description
4. Call `PATCH /links/{id}` to update look IDs
5. Verify changes reflect immediately

### Test Deletion

1. Create a test link
2. Call `DELETE /links/{id}`
3. Verify the short URL returns 404

---

## Error Handling

### Common Errors

**404 Not Found**:
- Link doesn't exist
- Link has been deleted
- Look IDs don't exist

**403 Forbidden**:
- Trying to edit/delete someone else's link
- Trying to include looks that don't belong to you

**400 Bad Request**:
- Missing required fields
- Empty title
- Empty lookIds array
- Invalid UUID format

**401 Unauthorized**:
- Missing or invalid access token
- Token expired

---

## Important Notes

1. **Link ID vs Database ID**:
   - `id`: UUID for database operations (create, update, delete)
   - `linkId`: Alphanumeric code for sharing (e.g., "AB12CD34")

2. **Short URL Format**:
   - Dev: `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/l/{linkId}`
   - Prod: `https://ai-studio-backend-ijkp.onrender.com/l/{linkId}`

3. **Public Access**:
   - `/links/shared/{linkId}` endpoint is public
   - No authentication required
   - Perfect for sharing with clients

4. **Cover Image**:
   - Optional but recommended for visual appeal
   - Supports JPEG, PNG, WebP, GIF
   - Automatically resized/optimized by backend
   - Stored in cloud storage (Cloudinary in production)

5. **Field Name Changes**:
   - Use `title` instead of `clientName`
   - Use `description` instead of `clientPhone`
   - All endpoints updated to use new names

---

## Questions?

If you encounter any issues or need clarification:

1. Check the Swagger UI documentation:
   - Dev: `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs`
   - Prod: `https://ai-studio-backend-ijkp.onrender.com/docs`

2. Test endpoints directly in Swagger UI

3. Check the backend logs for error details

---

**The backend is ready! Start implementing the Links feature with the new field names.** 🚀

