# Frontend Task: Admin Default Settings Management

## What You Need to Build

An admin-only page where administrators can view and update the default settings that all new users will receive. This is like a "master template" that affects:
- New users when they're approved
- Any user who clicks "Reset to Defaults"

---

## Important Concepts

**What are Default Settings?**
- They are the "master copy" of settings stored on the server
- When a new user joins, they get a copy of these defaults
- When any user clicks "Reset", they get these defaults

**Who can change them?**
- Only users with `role: "admin"` can view or modify default settings

**What happens when you change them?**
- ✅ New users will get the updated defaults
- ✅ Users who reset their settings will get the updated defaults  
- ❌ Existing users' current settings are NOT changed

---

## The Admin Page Should Have

### 1. Default Settings Display

Show all the current default settings in a form, exactly like the regular Settings page, but labeled differently:

```
┌─────────────────────────────────────────┐
│  Default Settings for New Users         │
│  (Admin Only)                            │
├─────────────────────────────────────────┤
│                                         │
│  ⚙️ These settings will be given to:    │
│     • All new users when approved       │
│     • Any user who clicks Reset         │
│                                         │
│  Default Theme: [Light/Dark Toggle]     │
│                                         │
│  Look Creator Defaults:                 │
│  System Prompt: [text area]             │
│  ...all other fields...                 │
│                                         │
│  [Save Default Settings]                │
│  [Reset to System Defaults]             │
│                                         │
│  Last updated: 2 hours ago by Admin     │
└─────────────────────────────────────────┘
```

### 2. Action Buttons

**Save Default Settings Button:**
- Updates the master defaults
- Shows success: "Default settings updated! New users will receive these settings."

**Reset to System Defaults Button:**
- Shows confirmation: "This will restore defaults to original system values. Continue?"
- Resets the master defaults to hardcoded values

---

## API Integration

### API 1: Get Current Default Settings

**Endpoint:** `GET /AIStudio/api/v1/admin/defaults`

**When to call:** When admin opens the Default Settings page

**Headers required:**
```javascript
{
  "Authorization": "Bearer admin_access_token_here"
}
```

**What you'll get back:**

```javascript
{
  "defaultTheme": "light",
  "defaultToolSettings": {
    "lookCreator": {
      "systemPrompt": "Your primary directive is to create...",
      "sceneDescriptions": {
        "studio": "A professional photography studio...",
        "beach": "A serene beach...",
        "city": "A bustling city...",
        "forest": "A magical forest..."
      },
      "simpleLayeringInstruction": "Layer the products from bottom to top...",
      "advancedLayeringInstructionTemplate": "Layer according to: {custom_instruction}"
    },
    "copywriter": {
      "systemPrompt": "You are a senior copywriter..."
    },
    "finishingStudio": {
      "systemPrompt": "You are an expert AI photo editor..."
    },
    "modelManager": {
      "systemPrompt": "4K ultra high definition..."
    }
  },
  "updatedAt": "2025-10-10T12:00:00Z",
  "updatedBy": "admin-user-id-123"
}
```

**What to do:**
- Display all fields in editable form
- Show "Last updated" info at bottom
- Pre-fill the form with these values

---

### API 2: Update Default Settings

**Endpoint:** `PUT /AIStudio/api/v1/admin/defaults`

**When to call:** When admin clicks "Save Default Settings"

**Headers required:**
```javascript
{
  "Authorization": "Bearer admin_access_token_here",
  "Content-Type": "application/json"
}
```

**What to send:**

```javascript
{
  "defaultTheme": "dark",
  "defaultToolSettings": {
    "lookCreator": {
      "systemPrompt": "Updated default prompt...",
      "sceneDescriptions": {
        "studio": "...",
        "beach": "...",
        "city": "...",
        "forest": "..."
      },
      "simpleLayeringInstruction": "...",
      "advancedLayeringInstructionTemplate": "..."
    },
    "copywriter": {
      "systemPrompt": "..."
    },
    "finishingStudio": {
      "systemPrompt": "..."
    },
    "modelManager": {
      "systemPrompt": "..."
    }
  }
}
```

**What you'll get back:**

```javascript
{
  "defaultTheme": "dark",
  "defaultToolSettings": {...},
  "updatedAt": "2025-10-10T14:30:00Z",
  "updatedBy": "current-admin-id"
}
```

**What to do:**
- Show success message: "Default settings updated! New users will receive these settings."
- Update the "Last updated" display
- Keep the form populated with the new values

---

### API 3: Reset to System Defaults

**Endpoint:** `POST /AIStudio/api/v1/admin/defaults/reset`

**When to call:** When admin confirms reset to system defaults

**Headers required:**
```javascript
{
  "Authorization": "Bearer admin_access_token_here"
}
```

**No request body needed**

**What you'll get back:**

```javascript
{
  "defaultTheme": "light",
  "defaultToolSettings": {...},  // System hardcoded defaults
  "updatedAt": "2025-10-10T14:35:00Z",
  "updatedBy": "current-admin-id"
}
```

**What to do:**
- Update form with the system defaults
- Show success: "Defaults reset to system values"
- Update the "Last updated" display

---

## Implementation Example

```javascript
// On page load
async function loadDefaultSettings() {
  try {
    const response = await fetch('/AIStudio/api/v1/admin/defaults', {
      headers: {
        'Authorization': `Bearer ${adminToken}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to load default settings');
    }
    
    const data = await response.json();
    
    // Populate form
    setDefaultTheme(data.defaultTheme);
    setDefaultToolSettings(data.defaultToolSettings);
    
    // Show metadata
    setLastUpdated(data.updatedAt);
    setLastUpdatedBy(data.updatedBy);
    
  } catch (error) {
    console.error('Error loading defaults:', error);
    showErrorMessage('Failed to load default settings');
  }
}

// On save
async function saveDefaultSettings() {
  const newDefaults = {
    defaultTheme: currentDefaultTheme,
    defaultToolSettings: {
      lookCreator: {
        systemPrompt: defaultLookCreatorPrompt,
        sceneDescriptions: {
          studio: defaultStudioScene,
          beach: defaultBeachScene,
          city: defaultCityScene,
          forest: defaultForestScene
        },
        simpleLayeringInstruction: defaultSimpleLayering,
        advancedLayeringInstructionTemplate: defaultAdvancedLayering
      },
      copywriter: { systemPrompt: defaultCopywriterPrompt },
      finishingStudio: { systemPrompt: defaultFinishingPrompt },
      modelManager: { systemPrompt: defaultModelManagerPrompt }
    }
  };
  
  try {
    const response = await fetch('/AIStudio/api/v1/admin/defaults', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${adminToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newDefaults)
    });
    
    if (!response.ok) {
      throw new Error('Failed to save defaults');
    }
    
    const updated = await response.json();
    
    // Update UI
    setLastUpdated(updated.updatedAt);
    setLastUpdatedBy(updated.updatedBy);
    
    showSuccessMessage('Default settings updated! New users will receive these settings.');
    
  } catch (error) {
    console.error('Error saving defaults:', error);
    showErrorMessage('Failed to save default settings');
  }
}

// On reset
async function resetToSystemDefaults() {
  const confirmed = confirm(
    'This will restore default settings to original system values. ' +
    'New users will receive the original defaults. Continue?'
  );
  
  if (!confirmed) return;
  
  try {
    const response = await fetch('/AIStudio/api/v1/admin/defaults/reset', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${adminToken}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to reset defaults');
    }
    
    const resetData = await response.json();
    
    // Update form with system defaults
    setDefaultTheme(resetData.defaultTheme);
    setDefaultToolSettings(resetData.defaultToolSettings);
    setLastUpdated(resetData.updatedAt);
    
    showSuccessMessage('Default settings reset to system values');
    
  } catch (error) {
    console.error('Error resetting defaults:', error);
    showErrorMessage('Failed to reset defaults');
  }
}
```

---

## UI Recommendations

### Access Control
- Only show this page if user has `role: "admin"`
- Add it to admin navigation: "Admin" → "Default Settings"

### Warning Banner
```
⚠️ ADMIN ONLY: Changing these settings will affect all new users 
and anyone who resets their settings. Existing users keep their 
current settings.
```

### Last Updated Info
```
📅 Last updated: 2 hours ago by Admin Name
```

### Form Structure
- Use the same layout as regular Settings page
- But label everything as "Default" to make it clear
- "Default Theme", "Default Look Creator Prompt", etc.

---

## Error Handling

**403 Forbidden:**
```javascript
{
  "detail": "Admin access required"
}
```
→ User is not an admin. Redirect to home or show "Access denied"

**401 Unauthorized:**
```javascript
{
  "detail": "Could not validate credentials"
}
```
→ Token expired. Redirect to login

**400 Bad Request:**
```javascript
{
  "detail": [
    {
      "loc": ["body", "defaultTheme"],
      "msg": "Input should be 'light' or 'dark'"
    }
  ]
}
```
→ Invalid data. Check that theme is "light" or "dark" and all fields are filled

---

## Testing Checklist

- [ ] Only admins can access the page
- [ ] Non-admins see "Access denied"
- [ ] Default settings load correctly
- [ ] Can edit all default fields
- [ ] Save button updates defaults successfully
- [ ] "Last updated" info shows correctly
- [ ] Reset button shows confirmation
- [ ] Reset restores system defaults
- [ ] Error messages shown for failures
- [ ] Success messages shown for saves

---

## Testing the Impact

**To verify it works:**

1. Admin changes default theme to "dark"
2. Admin saves
3. Create a new test user (or have someone request access and approve them)
4. New user logs in
5. New user should see theme = "dark" by default ✅

**OR:**

1. Admin changes a default prompt
2. Admin saves
3. Existing user goes to Settings and clicks "Reset All Settings"
4. Existing user should see the new admin-configured defaults ✅

---

## URLs Quick Reference

**Backend Base URL:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio
```

**Admin Default Settings Endpoints:**
```
GET  /api/v1/admin/defaults        - Get current defaults
PUT  /api/v1/admin/defaults        - Update defaults
POST /api/v1/admin/defaults/reset  - Reset to system defaults
```

---

## Summary

You're building an admin-only page to manage the "master template" settings:

1. **Load defaults:** `GET /api/v1/admin/defaults`
2. **Show in form:** Same structure as regular settings
3. **Save changes:** `PUT /api/v1/admin/defaults`
4. **Reset to system:** `POST /api/v1/admin/defaults/reset`

These defaults affect:
- ✅ New users
- ✅ Users who reset their settings
- ❌ NOT existing users (they keep their current settings)

Good luck! 🚀


