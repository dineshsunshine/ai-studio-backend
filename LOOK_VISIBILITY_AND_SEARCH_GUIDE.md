# Look Visibility & Search Feature - Frontend Integration Guide

## Overview

This guide explains how to integrate the new **Look Visibility** and **Search** features into the frontend application.

### What's New?

1. **Look Visibility System**: Looks can now be private, shared with specific users, or public
2. **Filtered Views**: Browse looks by category (My Looks, Shared With Me, Public)
3. **Search Functionality**: Search looks by title, notes, product names, or SKUs

---

## 1. Look Visibility System

### Visibility Options

| Visibility | Description | Who Can See It |
|-----------|-------------|----------------|
| `private` | Default setting | Only the creator |
| `shared` | Shared with specific users | Creator + selected users |
| `public` | Available to everyone | All authenticated users |

---

## 2. API Endpoints

### 2.1 Create a Look with Visibility

**Endpoint:** `POST /api/v1/looks/`

**Request Body:**
```json
{
  "title": "Summer Outfit",
  "notes": "Perfect for beach vacation",
  "generatedImageBase64": "data:image/png;base64,...",
  "visibility": "private",
  "sharedWithUserIds": ["user-id-1", "user-id-2"],
  "products": [
    {
      "sku": "SKU123",
      "name": "Floral Dress",
      "designer": "Brand Name",
      "price": 299.99,
      "productUrl": "https://...",
      "thumbnailBase64": "data:image/png;base64,..."
    }
  ]
}
```

**New Fields:**
- `visibility`: (optional, default: `"private"`) - One of: `"private"`, `"shared"`, or `"public"`
- `sharedWithUserIds`: (optional) - Array of user IDs to share with. **Only used when `visibility` is set to `"shared"`**

**Response:**
```json
{
  "id": "look-uuid",
  "title": "Summer Outfit",
  "notes": "Perfect for beach vacation",
  "generatedImageUrl": "https://...",
  "visibility": "shared",
  "sharedWith": [
    {
      "id": "user-id-1",
      "email": "user1@example.com",
      "name": "User One"
    }
  ],
  "products": [...],
  "createdAt": "2025-01-01T12:00:00",
  "updatedAt": "2025-01-01T12:00:00"
}
```

---

### 2.2 List Looks with Filters and Search

**Endpoint:** `GET /api/v1/looks/`

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `view_type` | string (optional) | Filter by view type | `my_private`, `shared_with_me`, `public` |
| `search` | string (optional) | Search keyword | `summer dress` |
| `skip` | integer (optional) | Pagination offset (default: 0) | `0` |
| `limit` | integer (optional) | Results per page (default: 100, max: 1000) | `20` |

**View Type Options:**

- `my_private`: Shows all looks created by the current user (regardless of visibility)
- `shared_with_me`: Shows looks that other users have shared with you
- `public`: Shows all public looks from all users
- *(no view_type)*: Defaults to showing your own looks

**Examples:**

```javascript
// Get my private looks
GET /api/v1/looks/?view_type=my_private&skip=0&limit=20

// Get looks shared with me
GET /api/v1/looks/?view_type=shared_with_me

// Get all public looks
GET /api/v1/looks/?view_type=public

// Search across all my looks
GET /api/v1/looks/?search=summer

// Search within public looks
GET /api/v1/looks/?view_type=public&search=designer%20dress
```

**Response:**
```json
{
  "looks": [
    {
      "id": "look-uuid",
      "title": "Summer Outfit",
      "notes": "Perfect for beach vacation",
      "generatedImageUrl": "https://...",
      "visibility": "public",
      "sharedWith": [],
      "products": [...],
      "createdAt": "2025-01-01T12:00:00",
      "updatedAt": "2025-01-01T12:00:00"
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

---

### 2.3 Update Look Visibility

**Endpoint:** `PATCH /api/v1/looks/{look_id}/visibility`

**Use Case:** Change a look's visibility after it's created (e.g., make it public, share with more users, or make it private again)

**Request Body:**
```json
{
  "visibility": "shared",
  "sharedWithUserIds": ["user-id-3", "user-id-4"]
}
```

**Response:**
Returns the updated look with new visibility settings (same structure as create/get look).

**Important Notes:**
- When changing from `shared` to `private` or `public`, existing shares are cleared
- When changing to `shared`, you must provide the complete list of `sharedWithUserIds` (it replaces the old list, not appends)
- Only the look creator (or admin) can update visibility

---

### 2.4 Get Single Look

**Endpoint:** `GET /api/v1/looks/{look_id}`

**Response:** Returns the full look details including `visibility` and `sharedWith` fields.

---

### 2.5 Update Look (Title/Notes Only)

**Endpoint:** `PATCH /api/v1/looks/{look_id}`

**Request Body:**
```json
{
  "title": "Updated Title",
  "notes": "Updated notes"
}
```

**Note:** This endpoint only updates title and notes. Use the `/visibility` endpoint to change sharing settings.

---

### 2.6 Delete Look

**Endpoint:** `DELETE /api/v1/looks/{look_id}`

**Response:** `204 No Content`

**Note:** Deleting a look removes it for everyone, including users it was shared with.

---

## 3. Frontend Implementation Guide

### 3.1 Look Creation Flow

**Step 1: Add Visibility Selector to Create Form**

```javascript
// Example UI component state
const [visibility, setVisibility] = useState('private');
const [selectedUsers, setSelectedUsers] = useState([]);

// UI elements
<Select value={visibility} onChange={(e) => setVisibility(e.target.value)}>
  <option value="private">Private (Only Me)</option>
  <option value="shared">Shared (Select Users)</option>
  <option value="public">Public (Everyone)</option>
</Select>

{visibility === 'shared' && (
  <MultiSelectUsers 
    value={selectedUsers} 
    onChange={setSelectedUsers}
  />
)}
```

**Step 2: Include Visibility in API Request**

```javascript
const createLook = async (lookData) => {
  const payload = {
    title: lookData.title,
    notes: lookData.notes,
    generatedImageBase64: lookData.imageBase64,
    visibility: visibility, // 'private', 'shared', or 'public'
    sharedWithUserIds: visibility === 'shared' ? selectedUsers : undefined,
    products: lookData.products
  };
  
  const response = await fetch('/api/v1/looks/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });
  
  return await response.json();
};
```

---

### 3.2 Lookbook Views Implementation

**Create Three Tabs/Sections:**

1. **My Looks** - `view_type=my_private`
2. **Shared With Me** - `view_type=shared_with_me`
3. **Public Gallery** - `view_type=public`

**Example Implementation:**

```javascript
const LookbookTabs = () => {
  const [activeTab, setActiveTab] = useState('my_private');
  const [looks, setLooks] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  
  const fetchLooks = async (viewType, search = '') => {
    const params = new URLSearchParams({
      view_type: viewType,
      skip: 0,
      limit: 50
    });
    
    if (search) {
      params.append('search', search);
    }
    
    const response = await fetch(`/api/v1/looks/?${params}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    setLooks(data.looks);
  };
  
  useEffect(() => {
    fetchLooks(activeTab, searchQuery);
  }, [activeTab, searchQuery]);
  
  return (
    <div>
      <Tabs value={activeTab} onChange={setActiveTab}>
        <Tab value="my_private">My Looks</Tab>
        <Tab value="shared_with_me">Shared With Me</Tab>
        <Tab value="public">Public Gallery</Tab>
      </Tabs>
      
      <SearchBar 
        value={searchQuery} 
        onChange={setSearchQuery}
        placeholder="Search by title, notes, product name, or SKU..."
      />
      
      <LookGrid looks={looks} />
    </div>
  );
};
```

---

### 3.3 Search Implementation

**Search Scope:**

The search functionality searches across:
- Look title
- Look notes
- Product names
- Product SKUs

**Debounced Search Example:**

```javascript
import { useState, useEffect } from 'react';
import { debounce } from 'lodash';

const SearchBar = ({ viewType }) => {
  const [searchInput, setSearchInput] = useState('');
  const [results, setResults] = useState([]);
  
  // Debounce search to avoid excessive API calls
  const debouncedSearch = debounce(async (query) => {
    if (!query) {
      // Fetch default results
      fetchLooks(viewType);
      return;
    }
    
    const params = new URLSearchParams({
      view_type: viewType,
      search: query
    });
    
    const response = await fetch(`/api/v1/looks/?${params}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    setResults(data.looks);
  }, 300); // Wait 300ms after user stops typing
  
  useEffect(() => {
    debouncedSearch(searchInput);
  }, [searchInput]);
  
  return (
    <input 
      type="search"
      value={searchInput}
      onChange={(e) => setSearchInput(e.target.value)}
      placeholder="Search looks..."
    />
  );
};
```

---

### 3.4 Update Visibility After Creation

**Use Case:** User wants to change who can see their look after publishing it.

**Implementation:**

```javascript
const updateLookVisibility = async (lookId, newVisibility, sharedUserIds = []) => {
  const payload = {
    visibility: newVisibility,
    sharedWithUserIds: newVisibility === 'shared' ? sharedUserIds : undefined
  };
  
  const response = await fetch(`/api/v1/looks/${lookId}/visibility`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });
  
  return await response.json();
};

// Example: Make a look public
await updateLookVisibility('look-uuid', 'public');

// Example: Share with specific users
await updateLookVisibility('look-uuid', 'shared', ['user-1', 'user-2']);

// Example: Make a look private again
await updateLookVisibility('look-uuid', 'private');
```

---

### 3.5 Display Visibility Status in UI

**Show visibility badge on each look card:**

```javascript
const VisibilityBadge = ({ visibility, sharedWith }) => {
  const badges = {
    private: { icon: '🔒', text: 'Private', color: 'gray' },
    shared: { icon: '👥', text: `Shared (${sharedWith.length})`, color: 'blue' },
    public: { icon: '🌍', text: 'Public', color: 'green' }
  };
  
  const badge = badges[visibility];
  
  return (
    <span className={`badge badge-${badge.color}`}>
      {badge.icon} {badge.text}
    </span>
  );
};

// Usage in look card
<div className="look-card">
  <img src={look.generatedImageUrl} />
  <VisibilityBadge 
    visibility={look.visibility} 
    sharedWith={look.sharedWith} 
  />
  <h3>{look.title}</h3>
</div>
```

---

## 4. Best Practices

### 4.1 Default Visibility
- Set default visibility to `private` to protect user privacy
- Allow users to explicitly choose to share or make public

### 4.2 User Selection for Sharing
- Fetch list of users from your user management API
- Filter out the current user from the selection list
- Show user email and name for easy identification
- Consider adding a "Share with all team members" quick action

### 4.3 Search UX
- Implement debounced search (300-500ms delay)
- Show loading state while searching
- Display "No results found" message with clear copy
- Allow clearing search to return to default view
- Highlight matching text in results (optional but recommended)

### 4.4 Visibility Indicators
- Always show a clear visual indicator of visibility status
- Use consistent icons: 🔒 Private, 👥 Shared, 🌍 Public
- Consider color coding: Gray for private, Blue for shared, Green for public

### 4.5 Pagination
- Implement infinite scroll or traditional pagination
- Default `limit` of 20-50 looks per page is recommended
- Show total count when available

### 4.6 Error Handling
```javascript
try {
  const response = await fetch('/api/v1/looks/', {
    // ... request config
  });
  
  if (!response.ok) {
    if (response.status === 403) {
      // User doesn't have permission
      showError("You don't have permission to view this look");
    } else if (response.status === 404) {
      // Look not found
      showError("Look not found");
    } else {
      // Generic error
      showError("Something went wrong. Please try again.");
    }
    return;
  }
  
  const data = await response.json();
  // Handle success
} catch (error) {
  showError("Network error. Please check your connection.");
}
```

---

## 5. Migration & Backward Compatibility

### For Existing Looks

All existing looks will automatically have `visibility: "private"` after the migration runs. This ensures:
- No existing looks are accidentally made public
- User privacy is maintained
- Users must explicitly choose to share or make looks public

### No Breaking Changes

The API is fully backward compatible:
- `visibility` defaults to `"private"` if not provided
- `sharedWithUserIds` is optional and ignored unless `visibility` is `"shared"`
- All existing endpoints continue to work exactly as before
- New fields (`visibility`, `sharedWith`) are added to responses but don't break existing parsing

---

## 6. Quick Implementation Checklist

Frontend developers should implement the following:

- [ ] Add visibility dropdown/selector to look creation form
- [ ] Add user multi-select for sharing (shown only when visibility is "shared")
- [ ] Include `visibility` and `sharedWithUserIds` in create look API call
- [ ] Create three tabs/views in lookbook: My Looks, Shared With Me, Public
- [ ] Add search bar to each tab
- [ ] Implement debounced search with API integration
- [ ] Update look card component to display visibility badge
- [ ] Add "Edit Visibility" option in look detail/edit view
- [ ] Implement the update visibility API call
- [ ] Add tooltips/help text explaining visibility options
- [ ] Test all three view types with and without search
- [ ] Test pagination in each view
- [ ] Handle edge cases (empty states, network errors, permissions)

---

## 7. API Summary Table

| Endpoint | Method | Purpose | New Query Params | New Request Fields | New Response Fields |
|----------|--------|---------|------------------|-------------------|---------------------|
| `/api/v1/looks/` | POST | Create look | - | `visibility`, `sharedWithUserIds` | `visibility`, `sharedWith` |
| `/api/v1/looks/` | GET | List looks | `view_type`, `search` | - | `visibility`, `sharedWith` (for each look) |
| `/api/v1/looks/{id}` | GET | Get single look | - | - | `visibility`, `sharedWith` |
| `/api/v1/looks/{id}` | PATCH | Update title/notes | - | - | `visibility`, `sharedWith` |
| `/api/v1/looks/{id}/visibility` | PATCH | **NEW** Update visibility | - | `visibility`, `sharedWithUserIds` | `visibility`, `sharedWith` |
| `/api/v1/looks/{id}` | DELETE | Delete look | - | - | - |

---

## 8. Testing Scenarios

Before going live, test these scenarios:

1. **Create Private Look**: Verify it appears only in "My Looks" tab
2. **Create Public Look**: Verify it appears in both "My Looks" and "Public Gallery"
3. **Create Shared Look**: Share with User B, verify User B sees it in "Shared With Me"
4. **Change Visibility**: Create private, change to public, verify it now shows in public gallery
5. **Search Private**: Search your own looks by product name
6. **Search Public**: Search public gallery by title
7. **Search Shared**: Search "Shared With Me" tab
8. **Pagination**: Load 100+ looks, test pagination/infinite scroll
9. **Empty States**: Test each tab when no looks match the criteria
10. **Permissions**: Try to access another user's private look (should fail with 403)

---

## 9. Support & Questions

If you encounter any issues or need clarification:

1. Check the Swagger documentation at `/AIStudio/docs` for detailed API schemas
2. All datetime fields are in ISO 8601 format
3. All IDs are UUIDs (string format)
4. Authentication is required for all endpoints (use JWT token in Authorization header)
5. Use `ngrok-skip-browser-warning: true` header if testing through ngrok

---

## Example: Complete Create Look Flow

```javascript
// Complete example combining all features
const CreateLookForm = () => {
  const [formData, setFormData] = useState({
    title: '',
    notes: '',
    visibility: 'private',
    sharedWithUserIds: [],
    generatedImageBase64: '',
    products: []
  });
  
  const [allUsers, setAllUsers] = useState([]);
  
  // Fetch users for sharing (assuming you have a users endpoint)
  useEffect(() => {
    fetchUsers().then(users => setAllUsers(users));
  }, []);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const payload = {
      title: formData.title,
      notes: formData.notes,
      generatedImageBase64: formData.generatedImageBase64,
      visibility: formData.visibility,
      sharedWithUserIds: formData.visibility === 'shared' 
        ? formData.sharedWithUserIds 
        : undefined,
      products: formData.products
    };
    
    try {
      const response = await fetch('/api/v1/looks/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) throw new Error('Failed to create look');
      
      const createdLook = await response.json();
      
      // Show success message
      showSuccess(`Look created! It is now ${createdLook.visibility}.`);
      
      // Redirect to lookbook
      navigate('/lookbook');
      
    } catch (error) {
      showError('Failed to create look. Please try again.');
      console.error(error);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="text" 
        value={formData.title}
        onChange={(e) => setFormData({...formData, title: e.target.value})}
        placeholder="Look Title"
      />
      
      <textarea 
        value={formData.notes}
        onChange={(e) => setFormData({...formData, notes: e.target.value})}
        placeholder="Notes (optional)"
      />
      
      <select 
        value={formData.visibility}
        onChange={(e) => setFormData({...formData, visibility: e.target.value})}
      >
        <option value="private">🔒 Private - Only I can see this</option>
        <option value="shared">👥 Shared - Share with specific users</option>
        <option value="public">🌍 Public - Everyone can see this</option>
      </select>
      
      {formData.visibility === 'shared' && (
        <MultiSelect 
          options={allUsers}
          value={formData.sharedWithUserIds}
          onChange={(ids) => setFormData({...formData, sharedWithUserIds: ids})}
          placeholder="Select users to share with"
        />
      )}
      
      {/* Image and products fields */}
      
      <button type="submit">Create Look</button>
    </form>
  );
};
```

---

**End of Guide** ✨

For the latest API documentation, always refer to the Swagger UI at:
- **Development:** `https://your-ngrok-url.ngrok-free.dev/AIStudio/docs`
- **Production:** `https://your-production-url.com/AIStudio/docs`

