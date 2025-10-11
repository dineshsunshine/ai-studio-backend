# Links Feature - Frontend Integration Guide

## Overview

Implement a "Links" feature that allows users to create shareable collections of looks for their clients. Each link has a unique short URL that can be shared with clients to view the selected looks.

---

## Core Concept

1. **User** creates a **Link** containing multiple **Looks**
2. **Link** has client information (name, phone) and a unique alphanumeric ID
3. **Short URL** is generated automatically (e.g., `https://domain.com/l/AB12CD34`)
4. **Client** opens the short URL and views all looks in that link (no login required)
5. **User** can manage (edit/delete) their links

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
  "clientName": "John Doe",
  "clientPhone": "+1234567890",
  "lookIds": ["look-uuid-1", "look-uuid-2", "look-uuid-3"]
}
```

**Response** (201 Created):
```json
{
  "id": "link-uuid",
  "linkId": "AB12CD34",
  "clientName": "John Doe",
  "clientPhone": "+1234567890",
  "shortUrl": "https://yourdomain.com/l/AB12CD34",
  "looks": [
    {
      "id": "look-uuid-1",
      "title": "Summer Look",
      "notes": "Beach outfit",
      "generatedImageUrl": "https://...",
      "products": [
        {
          "id": "product-uuid",
          "name": "White Dress",
          "designer": "Gucci",
          "price": 1200.00,
          "sku": "GUC-123",
          "productUrl": "https://...",
          "thumbnailUrl": "https://...",
          "createdAt": "2025-10-11T12:00:00Z"
        }
      ],
      "createdAt": "2025-10-11T12:00:00Z",
      "updatedAt": "2025-10-11T12:00:00Z"
    }
  ],
  "createdAt": "2025-10-11T12:00:00Z",
  "updatedAt": "2025-10-11T12:00:00Z"
}
```

**Error Responses**:
- `404`: One or more looks not found or don't belong to you
- `401`: Unauthorized (invalid or missing token)

---

### 2. List Links

**Endpoint**: `GET /links/`  
**Authentication**: Required (Bearer token)

**Query Parameters**:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Max records to return (default: 100, max: 1000)

**Response** (200 OK):
```json
{
  "links": [
    {
      "id": "link-uuid",
      "linkId": "AB12CD34",
      "clientName": "John Doe",
      "clientPhone": "+1234567890",
      "shortUrl": "https://yourdomain.com/l/AB12CD34",
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

---

### 3. Get Single Link (by Database ID)

**Endpoint**: `GET /links/{linkId}`  
**Authentication**: Required (Bearer token)

**Path Parameters**:
- `linkId`: Database UUID of the link

**Response** (200 OK):
```json
{
  "id": "link-uuid",
  "linkId": "AB12CD34",
  "clientName": "John Doe",
  "clientPhone": "+1234567890",
  "shortUrl": "https://yourdomain.com/l/AB12CD34",
  "looks": [...],
  "createdAt": "2025-10-11T12:00:00Z",
  "updatedAt": "2025-10-11T12:00:00Z"
}
```

**Error Responses**:
- `404`: Link not found
- `403`: Forbidden (link belongs to another user)

---

### 4. Update Link

**Endpoint**: `PATCH /links/{linkId}`  
**Authentication**: Required (Bearer token)

**Path Parameters**:
- `linkId`: Database UUID of the link

**Request Body** (all fields optional):
```json
{
  "clientName": "Jane Smith",
  "clientPhone": "+1987654321",
  "lookIds": ["look-uuid-1", "look-uuid-4"]
}
```

**Response** (200 OK):
```json
{
  "id": "link-uuid",
  "linkId": "AB12CD34",
  "clientName": "Jane Smith",
  "clientPhone": "+1987654321",
  "shortUrl": "https://yourdomain.com/l/AB12CD34",
  "looks": [...],
  "createdAt": "2025-10-11T12:00:00Z",
  "updatedAt": "2025-10-11T12:30:00Z"
}
```

**Notes**:
- You can update client info only, looks only, or both
- When updating looks, provide the complete new list of look IDs
- The `linkId` (alphanumeric) never changes, only the content

**Error Responses**:
- `404`: Link or one of the looks not found
- `403`: Forbidden (link belongs to another user)

---

### 5. Delete Link

**Endpoint**: `DELETE /links/{linkId}`  
**Authentication**: Required (Bearer token)

**Path Parameters**:
- `linkId`: Database UUID of the link

**Response** (204 No Content): Empty response body

**Notes**:
- Deleting a link does NOT delete the looks themselves
- Only the link (collection) is removed
- The short URL will stop working

**Error Responses**:
- `404`: Link not found
- `403`: Forbidden (link belongs to another user)

---

### 6. Get Shared Link (Public - No Auth)

**Endpoint**: `GET /links/shared/{alphanumericLinkId}`  
**Authentication**: NOT required (public endpoint)

**Path Parameters**:
- `alphanumericLinkId`: The short alphanumeric ID (e.g., "AB12CD34")

**Response** (200 OK):
```json
{
  "linkId": "AB12CD34",
  "clientName": "John Doe",
  "looks": [
    {
      "id": "look-uuid",
      "title": "Summer Look",
      "notes": "Beach outfit",
      "generatedImageUrl": "https://...",
      "products": [...],
      "createdAt": "2025-10-11T12:00:00Z",
      "updatedAt": "2025-10-11T12:00:00Z"
    }
  ],
  "createdAt": "2025-10-11T12:00:00Z"
}
```

**Notes**:
- This is a PUBLIC endpoint - no authentication required
- Used when clients open the short URL
- Does NOT include phone number or user information (for privacy)

**Error Responses**:
- `404`: Link not found or has been deleted

---

## Integration Flow

### Creating a Link

1. User selects multiple looks they want to share
2. User enters client name and optional phone number
3. Frontend calls `POST /links/` with:
   - `clientName`
   - `clientPhone` (optional)
   - `lookIds` (array of selected look UUIDs)
4. Backend returns the created link with `shortUrl`
5. Frontend displays the `shortUrl` for user to copy/share

### Viewing Client's Shared Link

1. Client receives short URL (e.g., `https://yourdomain.com/l/AB12CD34`)
2. When client opens URL, your frontend should:
   - Extract the alphanumeric ID from URL path (e.g., "AB12CD34")
   - Call `GET /links/shared/AB12CD34` (no auth needed)
   - Display all looks from the response
3. Show all looks with their images and product details
4. Client can view all information but cannot edit

### Managing Links

1. User views all their links via `GET /links/`
2. Display list showing:
   - Client name
   - Number of looks
   - Short URL
   - Created date
3. User can:
   - **Edit**: Update client info or change which looks are included
   - **Delete**: Remove the link entirely
   - **Copy URL**: Copy short URL to clipboard
   - **View**: See full details of the link

---

## Important Notes

### Authentication Headers

For all authenticated endpoints, include:
```javascript
headers: {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json',
  'ngrok-skip-browser-warning': 'true'
}
```

### Short URL Format

The backend returns the full short URL in the format:
- **Development**: `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/l/{linkId}`
- **Production**: `https://ai-studio-backend-ijkp.onrender.com/l/{linkId}`

You should display this URL prominently and provide a "Copy to Clipboard" button.

### Link ID vs Database ID

- **Database ID** (`id`): UUID used for CRUD operations (edit, delete)
- **Link ID** (`linkId`): Short alphanumeric code used for sharing
- Always use database ID for management operations
- Use link ID only for the public sharing endpoint

### Validation Rules

**Client Name**:
- Required
- Minimum 1 character
- Maximum 255 characters

**Client Phone**:
- Optional
- Maximum 50 characters
- No format validation on backend (format as you prefer on frontend)

**Look IDs**:
- Required
- Minimum 1 look
- All looks must exist and belong to the user

### Error Handling

Common errors to handle:
- **401 Unauthorized**: User not logged in or token expired
- **403 Forbidden**: Trying to access/modify another user's link
- **404 Not Found**: Link or looks don't exist
- **422 Unprocessable Entity**: Validation errors (check error details)

---

## Example Usage (JavaScript/TypeScript)

### Creating a Link

```typescript
async function createLink(accessToken: string, clientName: string, clientPhone: string, lookIds: string[]) {
  const response = await fetch(`${config.apiBaseUrl}/links/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true'
    },
    body: JSON.stringify({
      clientName,
      clientPhone,
      lookIds
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create link');
  }
  
  return await response.json();
}
```

### Fetching All Links

```typescript
async function fetchLinks(accessToken: string, skip: number = 0, limit: number = 100) {
  const response = await fetch(
    `${config.apiBaseUrl}/links/?skip=${skip}&limit=${limit}`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'ngrok-skip-browser-warning': 'true'
      }
    }
  );
  
  if (!response.ok) {
    throw new Error('Failed to fetch links');
  }
  
  return await response.json();
}
```

### Getting Shared Link (Public)

```typescript
async function fetchSharedLink(alphanumericLinkId: string) {
  const response = await fetch(
    `${config.apiBaseUrl}/links/shared/${alphanumericLinkId}`,
    {
      headers: {
        'ngrok-skip-browser-warning': 'true'
      }
    }
  );
  
  if (!response.ok) {
    throw new Error('Link not found or has been deleted');
  }
  
  return await response.json();
}
```

### Updating a Link

```typescript
async function updateLink(
  accessToken: string,
  linkDatabaseId: string,
  updates: { clientName?: string, clientPhone?: string, lookIds?: string[] }
) {
  const response = await fetch(`${config.apiBaseUrl}/links/${linkDatabaseId}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true'
    },
    body: JSON.stringify(updates)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update link');
  }
  
  return await response.json();
}
```

### Deleting a Link

```typescript
async function deleteLink(accessToken: string, linkDatabaseId: string) {
  const response = await fetch(`${config.apiBaseUrl}/links/${linkDatabaseId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'ngrok-skip-browser-warning': 'true'
    }
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete link');
  }
  
  // 204 No Content - success
  return true;
}
```

---

## Summary

**What you need to implement**:

1. **Link Management Page** (authenticated):
   - List all links
   - Create new link (select looks, enter client info)
   - Edit existing link
   - Delete link
   - Copy short URL to clipboard

2. **Shared Link Viewer Page** (public, no auth):
   - Extract link ID from URL path
   - Fetch link data via public endpoint
   - Display all looks in an attractive layout
   - Show product details for each look

**Key Points**:
- Use database ID (`id`) for management operations
- Use alphanumeric ID (`linkId`) only for public sharing
- Public endpoint requires NO authentication
- All authenticated endpoints need Bearer token
- Short URLs are generated automatically by backend
- Deleting a link doesn't delete the looks

---

## Testing

After Render deploys (~2-3 minutes):

1. Test creating a link with your existing looks
2. Verify the short URL is generated correctly
3. Open the short URL in an incognito window (no auth) to test public access
4. Test editing client info and look selection
5. Test deleting a link

The complete API documentation will be available at:
- **Development**: https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
- **Production**: https://ai-studio-backend-ijkp.onrender.com/docs

