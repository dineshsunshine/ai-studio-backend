# 🚀 Looks API - Quick Start Guide

## Public API URLs

**Base URL:** `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/looks`

**Documentation:** https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs

---

## Quick Examples

### Create a Look
```bash
curl -X POST "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/looks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Summer Beach Look",
    "generatedImageBase64": "data:image/png;base64,iVBORw0KGgo...",
    "products": [
      {
        "name": "Beach Hat",
        "designer": "Gucci",
        "price": 450,
        "thumbnailBase64": "data:image/png;base64,iVBORw0KGgo..."
      }
    ]
  }'
```

### List Looks
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/looks/?skip=0&limit=10"
```

### Get a Look
```bash
curl "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/looks/{id}/"
```

### Update a Look
```bash
curl -X PATCH "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/looks/{id}/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title", "notes": "My favorite look!"}'
```

### Delete a Look
```bash
curl -X DELETE "https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/looks/{id}/"
```

---

## JavaScript Integration

```javascript
// Create a Look
const createLook = async (imageBase64, products) => {
  const response = await fetch(
    'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/looks/',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: 'My Look',
        generatedImageBase64: imageBase64,
        products: products
      })
    }
  );
  return await response.json();
};

// List Looks
const fetchLooks = async (skip = 0, limit = 10) => {
  const response = await fetch(
    `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/looks/?skip=${skip}&limit=${limit}`
  );
  return await response.json();
};

// Delete a Look
const deleteLook = async (lookId) => {
  await fetch(
    `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/looks/${lookId}/`,
    { method: 'DELETE' }
  );
};
```

---

## Key Features

✅ **Base64 Image Upload** - Send images as base64, get back public URLs  
✅ **Pagination** - `skip` and `limit` query parameters  
✅ **CamelCase JSON** - Frontend-friendly field names  
✅ **Cascade Delete** - Deleting a look removes all products and images  
✅ **Full CRUD** - Create, Read, Update, Delete operations  

---

## Response Format

```json
{
  "id": "uuid-string",
  "title": "My Look",
  "notes": "Optional notes",
  "generatedImageUrl": "https://.../assets/looks/uuid.png",
  "products": [
    {
      "id": "uuid-string",
      "name": "Product Name",
      "designer": "Designer",
      "price": 999.99,
      "productUrl": "https://...",
      "thumbnailUrl": "https://.../assets/products/uuid.png",
      "createdAt": "2024-10-27T10:00:00Z"
    }
  ],
  "createdAt": "2024-10-27T10:00:00Z",
  "updatedAt": "2024-10-27T10:00:00Z"
}
```

---

## Error Handling

- **400 Bad Request** - Missing/invalid fields
- **404 Not Found** - Look doesn't exist
- **500 Internal Server Error** - Server error

---

For full documentation, visit: [LOOKS_API_DOCUMENTATION.md](./LOOKS_API_DOCUMENTATION.md)


