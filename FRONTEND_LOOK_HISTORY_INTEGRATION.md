# Frontend Integration Guide: Look History & Lookbook

## 📋 Overview

We've implemented a new feature that separates **Look History** (all generated looks) from **Lookbook** (explicitly saved looks).

### Key Changes:
1. **Consume tokens BEFORE creating looks** (not when saving)
2. **Save looks immediately** after generation (as drafts)
3. **User can save to lookbook** later (explicit action)
4. **Two views**: Lookbook (saved) and History (all)

---

## 🔄 New Flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. User Generates Look → Consume Tokens Immediately         │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. Create Look in Database → isInLookbook: false (draft)    │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. Show Preview Modal → User can Save to Lookbook           │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. (Optional) Save to Lookbook → isInLookbook: true         │
└──────────────────────────────────────────────────────────────┘
```

---

## 🆕 API Changes

### 1. Create Look Response (Updated)

**Endpoint:** `POST /api/v1/looks/`

**Response now includes `isInLookbook` field:**

```json
{
  "id": "abc-123",
  "title": null,
  "notes": null,
  "generatedImageUrl": "https://...",
  "isInLookbook": false,  ← NEW FIELD
  "products": [...],
  "createdAt": "2025-10-27T10:00:00Z",
  "updatedAt": "2025-10-27T10:00:00Z"
}
```

---

### 2. List Looks (Updated)

**Endpoint:** `GET /api/v1/looks/`

**New Query Parameter:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `inLookbookOnly` | boolean | `false` | Filter to show only saved looks |

**Examples:**

```javascript
// Get all looks (history)
GET /api/v1/looks/?inLookbookOnly=false

// Get only lookbook (saved looks)
GET /api/v1/looks/?inLookbookOnly=true
```

**Response:**

```json
{
  "looks": [
    {
      "id": "abc-123",
      "title": "Summer Look",
      "isInLookbook": true,  ← NEW FIELD
      "products": [...],
      ...
    },
    {
      "id": "def-456",
      "title": null,
      "isInLookbook": false,  ← NEW FIELD (draft)
      "products": [...],
      ...
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 100
}
```

---

### 3. Save to Lookbook (NEW)

**Endpoint:** `PATCH /api/v1/looks/{look_id}/save-to-lookbook`

**Description:** Marks a look as saved to lookbook

**Authentication:** Required (JWT)

**Request:**
```
PATCH /api/v1/looks/abc-123/save-to-lookbook
Authorization: Bearer <YOUR_JWT_TOKEN>
```

**Response:** (200 OK)
```json
{
  "id": "abc-123",
  "title": "Summer Look",
  "isInLookbook": true,  ← Updated to true
  "products": [...],
  ...
}
```

**Error Responses:**
- `404`: Look not found
- `403`: You don't have permission to modify this look

---

## 💻 Frontend Implementation

### Step 1: Update Look Generation Flow

**Before:**
```javascript
async function generateLook() {
  // Generate AI image
  const image = await callAI();
  
  // Show preview modal
  showPreview(image);
  
  // User clicks "Save" → Create look + consume tokens
  // ❌ Tokens consumed late
}
```

**After:**
```javascript
async function generateLook() {
  try {
    // 1. Consume tokens FIRST
    const tokenResult = await consumeTokens('multi_modal');
    
    if (!tokenResult.success) {
      showUpgradeModal(tokenResult);
      return;
    }
    
    updateTokenBalance(tokenResult.availableTokens);
    
    // 2. Generate AI image
    const imageBase64 = await callAI();
    
    // 3. Create look immediately (draft)
    const look = await createLook({
      title: null,  // No title yet
      notes: null,
      generatedImageBase64: imageBase64,
      products: selectedProducts
    });
    
    // 4. Show preview modal
    showPreviewModal(look);
    
  } catch (error) {
    handleError(error);
  }
}
```

---

### Step 2: Implement Preview Modal

```javascript
function showPreviewModal(look) {
  // Display:
  // - Generated look image
  // - Products list
  // - Optional title/notes inputs
  // - "Save to Lookbook" button
  // - "Discard" or "Close" button
  
  const modal = `
    <div class="preview-modal">
      <h2>Your Generated Look</h2>
      <img src="${look.generatedImageUrl}" />
      
      <input id="title-input" placeholder="Add a title (optional)" />
      <textarea id="notes-input" placeholder="Add notes (optional)"></textarea>
      
      <div class="products">
        ${look.products.map(p => `<div>${p.name}</div>`).join('')}
      </div>
      
      <div class="actions">
        <button onclick="saveToLookbook('${look.id}')">
          💾 Save to Lookbook
        </button>
        <button onclick="closeModal()">
          Close
        </button>
      </div>
    </div>
  `;
  
  showModal(modal);
}
```

---

### Step 3: Implement Save to Lookbook

```javascript
async function saveToLookbook(lookId) {
  try {
    // 1. Update title/notes if user entered them
    const title = document.getElementById('title-input').value.trim();
    const notes = document.getElementById('notes-input').value.trim();
    
    if (title || notes) {
      await fetch(`${API_BASE}/api/v1/looks/${lookId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${getToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title, notes })
      });
    }
    
    // 2. Mark as saved to lookbook
    const response = await fetch(
      `${API_BASE}/api/v1/looks/${lookId}/save-to-lookbook`,
      {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to save to lookbook');
    }
    
    const updatedLook = await response.json();
    
    // 3. Show success message
    showNotification('✅ Look saved to your lookbook!');
    
    // 4. Close modal
    closeModal();
    
    // 5. Refresh lookbook view if currently open
    if (currentView === 'lookbook') {
      refreshLookbookList();
    }
    
  } catch (error) {
    console.error('Failed to save to lookbook:', error);
    showNotification('❌ Failed to save. Please try again.');
  }
}
```

---

### Step 4: Implement Two Views (Lookbook vs History)

```javascript
// Tab 1: Lookbook (Saved looks only)
async function fetchLookbook() {
  const response = await fetch(
    `${API_BASE}/api/v1/looks/?inLookbookOnly=true`,
    {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    }
  );
  
  const data = await response.json();
  displayLooks(data.looks, 'lookbook-view');
  return data;
}

// Tab 2: History (All looks)
async function fetchHistory() {
  const response = await fetch(
    `${API_BASE}/api/v1/looks/?inLookbookOnly=false`,
    {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    }
  );
  
  const data = await response.json();
  displayLooks(data.looks, 'history-view');
  return data;
}

// Tab switching
function setupTabs() {
  document.getElementById('lookbook-tab').addEventListener('click', () => {
    fetchLookbook();
    currentView = 'lookbook';
  });
  
  document.getElementById('history-tab').addEventListener('click', () => {
    fetchHistory();
    currentView = 'history';
  });
}
```

---

### Step 5: Display Looks with Status Badge

```javascript
function displayLooks(looks, containerId) {
  const container = document.getElementById(containerId);
  
  container.innerHTML = looks.map(look => `
    <div class="look-card">
      <img src="${look.generatedImageUrl}" alt="${look.title || 'Untitled'}" />
      
      <div class="look-info">
        <h3>${look.title || 'Untitled Look'}</h3>
        <p>${look.notes || ''}</p>
        
        ${look.isInLookbook 
          ? '<span class="badge saved">📚 In Lookbook</span>'
          : '<span class="badge draft">📝 Draft</span>'
        }
      </div>
      
      <div class="look-actions">
        ${!look.isInLookbook 
          ? `<button onclick="saveToLookbook('${look.id}')">
               Save to Lookbook
             </button>`
          : ''
        }
        <button onclick="viewLook('${look.id}')">View</button>
        <button onclick="deleteLook('${look.id}')">Delete</button>
      </div>
    </div>
  `).join('');
}
```

---

## 🎨 UI/UX Recommendations

### 1. Badge Styling

```css
.badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.badge.saved {
  background: #4CAF50;
  color: white;
}

.badge.draft {
  background: #FFC107;
  color: #333;
}
```

---

### 2. Preview Modal Actions

- **Primary Button:** "💾 Save to Lookbook" (prominent, blue/green)
- **Secondary Button:** "Close" or "Cancel" (subtle, gray)
- **Optional:** "Delete" button (red, bottom corner)

---

### 3. Tab Navigation

```
┌──────────────────────────────────────────────┐
│  📚 Lookbook (12)  |  📝 History (45)         │  ← Tabs with counts
├──────────────────────────────────────────────┤
│                                              │
│  [Look Cards]                                │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 🧪 Testing Checklist

### Token Consumption
- [ ] Tokens consumed before look creation
- [ ] Insufficient tokens shows upgrade modal
- [ ] Token balance updates immediately
- [ ] No tokens consumed when user closes modal without saving

### Look Creation
- [ ] Look created with `isInLookbook: false` by default
- [ ] Look appears in History immediately
- [ ] Look does NOT appear in Lookbook initially

### Save to Lookbook
- [ ] "Save to Lookbook" button works
- [ ] Look moves to Lookbook after saving
- [ ] Badge changes from "Draft" to "In Lookbook"
- [ ] Title/notes saved correctly

### List Views
- [ ] Lookbook tab shows only saved looks (`isInLookbook: true`)
- [ ] History tab shows all looks
- [ ] Counts display correctly in tabs
- [ ] Pagination works in both views

---

## 🔐 Authentication

All endpoints require JWT authentication:

```javascript
headers: {
  'Authorization': `Bearer ${yourJwtToken}`,
  'Content-Type': 'application/json'
}
```

---

## 📊 Token Consumption

Use the existing token consumption endpoint **BEFORE** generating looks:

```javascript
async function consumeTokens(operation) {
  const response = await fetch(`${API_BASE}/api/v1/subscription/consume`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      operation: operation,  // 'multi_modal' for Look Creator
      description: 'Look generation'
    })
  });
  
  return await response.json();
}
```

**Operation Types:**
- `multi_modal` = 20 tokens (Look Creator)
- `multi_modal_light` = 8 tokens (Finishing Studio)
- `text_to_image` = 10 tokens (Model Manager)
- `image_to_text` = 5 tokens
- `text_to_text` = 3 tokens (Copywriter)

---

## ⚠️ Important Notes

### 1. Backward Compatibility
- All existing looks will have `isInLookbook: true` after migration
- This ensures they appear in Lookbook as before

### 2. Error Handling
Always handle errors gracefully:
- Network failures
- Insufficient tokens
- API errors (404, 403, 500)

### 3. User Experience
- Show loading states during operations
- Provide clear success/error feedback
- Allow users to close modal without saving (look stays in history)

---

## 📚 Related Documentation

- **Token Consumption:** `FRONTEND_TOKEN_CONSUMPTION_GUIDE.md`
- **Backend Implementation:** `LOOK_HISTORY_AND_LOOKBOOK_IMPLEMENTATION_GUIDE.md`
- **API Reference:** Check Swagger UI at `/api/v1/docs`

---

## 🚀 Deployment

### After backend deployment:
1. Wait for Render deployment (~3 minutes)
2. Migration will run automatically on first API call
3. Test endpoints in Swagger UI
4. Update frontend code
5. Deploy frontend

---

## 💡 Example: Complete Flow

```javascript
// Complete look generation flow
async function generateLookComplete(products, scene, layering) {
  const loadingModal = showLoading('Generating your look...');
  
  try {
    // 1. Consume tokens
    const tokenResult = await fetch(`${API_BASE}/api/v1/subscription/consume`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        operation: 'multi_modal',
        description: `Look with ${products.length} products`
      })
    }).then(r => r.json());
    
    if (!tokenResult.success) {
      closeLoading(loadingModal);
      showUpgradeModal({
        operation: 'Look Creation',
        cost: tokenResult.cost,
        available: tokenResult.availableTokens
      });
      return;
    }
    
    updateTokenBalance(tokenResult.availableTokens);
    
    // 2. Generate AI image
    const imageBase64 = await generateAIImage(products, scene, layering);
    
    // 3. Create look
    const look = await fetch(`${API_BASE}/api/v1/looks/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: null,
        notes: null,
        generatedImageBase64: imageBase64,
        products: products.map(p => ({
          sku: p.sku,
          name: p.name,
          designer: p.designer,
          price: p.price,
          productUrl: p.url,
          thumbnailBase64: p.thumbnailBase64
        }))
      })
    }).then(r => r.json());
    
    closeLoading(loadingModal);
    
    // 4. Show preview
    showPreviewModal(look);
    
  } catch (error) {
    closeLoading(loadingModal);
    showError('Failed to generate look: ' + error.message);
  }
}
```

---

## 🎯 Summary

**Key Changes for Frontend:**

1. ✅ Consume tokens **BEFORE** generating looks
2. ✅ Create looks immediately (they'll have `isInLookbook: false`)
3. ✅ Show preview modal after creation
4. ✅ Add "Save to Lookbook" button → calls new endpoint
5. ✅ Implement two views: Lookbook (saved) and History (all)
6. ✅ Add `?inLookbookOnly=true` parameter for Lookbook view

**Benefits:**
- 💰 Fair token consumption (charged on generation, not on save)
- 📊 Complete history tracking (see all generated looks)
- 🎯 Better user control (explicit save action)
- 🚀 Improved UX (preview before committing to lookbook)

---

**Need Help?** Check the backend logs or Swagger UI for detailed API documentation!

