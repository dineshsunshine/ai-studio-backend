# Frontend Implementation Guide: User Settings API

## Overview

We've moved all user settings from browser localStorage to the backend database. This ensures your customized settings (theme + AI tool configurations) are consistent across all devices and sessions.

---

## What Changed

**Before:** Settings stored in browser's `localStorage`:
- `theme` - Lost when clearing browser data
- `appSettings` - Not synced across devices

**Now:** Settings stored in the database:
- Persistent across all devices
- Backed up and secure
- Single source of truth

---

## Data Structure

Your settings object structure:

```typescript
interface UserSettings {
  theme: 'light' | 'dark';
  toolSettings: {
    lookCreator: {
      systemPrompt: string;
      sceneDescriptions: {
        studio: string;
        beach: string;
        city: string;
        forest: string;
      };
    };
    copywriter: {
      systemPrompt: string;
    };
    finishingStudio: {
      systemPrompt: string;
    };
    modelManager: {
      systemPrompt: string;
    };
  };
}
```

---

## API Endpoints

All endpoints require authentication. Include your access token in the `Authorization` header.

### API 1: Get User Settings

**Endpoint:** `GET /AIStudio/api/v1/settings`

**When to call:** On app startup, after user logs in

**Headers required:**
```javascript
{
  "Authorization": "Bearer user_access_token_here"
}
```

**What you'll get back:**

```javascript
{
  "theme": "dark",
  "toolSettings": {
    "lookCreator": {
      "systemPrompt": "You are an expert fashion AI assistant...",
      "sceneDescriptions": {
        "studio": "A clean, minimalist photography studio...",
        "beach": "A serene beach setting during golden hour...",
        "city": "An urban cityscape with modern architecture...",
        "forest": "A lush forest clearing with natural light..."
      }
    },
    "copywriter": {
      "systemPrompt": "You are a professional fashion copywriter..."
    },
    "finishingStudio": {
      "systemPrompt": "You are an expert image editing AI..."
    },
    "modelManager": {
      "systemPrompt": "You are an AI assistant for fashion model management..."
    }
  }
}
```

**What to do:**
- Store this in your app's state (Redux, Context, Zustand, etc.)
- Apply the theme to your UI
- Use toolSettings when calling AI tools
- If user has never customized settings, you'll get the defaults

**Special behavior:**
- If the user has no settings yet (new user), the backend automatically creates and returns default settings
- You'll always get a valid settings object back

**Example implementation:**

```javascript
async function fetchUserSettings() {
  try {
    const response = await fetch('/AIStudio/api/v1/settings', {
      headers: {
        'Authorization': `Bearer ${userToken}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch settings');
    }
    
    const settings = await response.json();
    
    // Apply theme
    setTheme(settings.theme);
    
    // Store tool settings
    setToolSettings(settings.toolSettings);
    
    return settings;
  } catch (error) {
    console.error('Error fetching settings:', error);
    // Fall back to defaults if fetch fails
    return getDefaultSettings();
  }
}
```

---

### API 2: Update User Settings

**Endpoint:** `PUT /AIStudio/api/v1/settings`

**When to call:** When user saves changes to their settings

**Headers required:**
```javascript
{
  "Authorization": "Bearer user_access_token_here",
  "Content-Type": "application/json"
}
```

**What to send:**

The complete settings object with all fields (even if only one field changed):

```javascript
{
  "theme": "light",
  "toolSettings": {
    "lookCreator": {
      "systemPrompt": "Updated prompt here...",
      "sceneDescriptions": {
        "studio": "...",
        "beach": "...",
        "city": "...",
        "forest": "..."
      }
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

The updated settings object (same structure as input):

```javascript
{
  "theme": "light",
  "toolSettings": { ... }
}
```

**What to do:**
- Update your app's state with the returned settings
- Apply new theme if changed
- Show success message: "Settings saved successfully!"
- The settings are now persisted in the database

**Example implementation:**

```javascript
async function saveUserSettings(settings) {
  try {
    const response = await fetch('/AIStudio/api/v1/settings', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${userToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(settings)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to save settings');
    }
    
    const updatedSettings = await response.json();
    
    // Update state
    setTheme(updatedSettings.theme);
    setToolSettings(updatedSettings.toolSettings);
    
    // Show success
    showSuccessMessage('Settings saved successfully!');
    
    return updatedSettings;
  } catch (error) {
    console.error('Error saving settings:', error);
    showErrorMessage('Failed to save settings. Please try again.');
    throw error;
  }
}
```

**Important notes:**
- You must send the **complete** settings object (theme + toolSettings)
- Don't send partial updates - always send all fields
- Theme must be either "light" or "dark"
- The backend validates the structure before saving
- If validation fails, you'll get a 400 Bad Request error

---

### API 3: Reset Settings to Default

**Endpoint:** `POST /AIStudio/api/v1/settings/reset`

**When to call:** When user clicks "Reset All Settings" button

**Headers required:**
```javascript
{
  "Authorization": "Bearer user_access_token_here"
}
```

**No request body needed**

**What you'll get back:**

The default settings object:

```javascript
{
  "theme": "light",  // Default theme
  "toolSettings": {
    "lookCreator": {
      "systemPrompt": "...", // Default prompts
      "sceneDescriptions": { ... }
    },
    "copywriter": { "systemPrompt": "..." },
    "finishingStudio": { "systemPrompt": "..." },
    "modelManager": { "systemPrompt": "..." }
  }
}
```

**What to do:**
- Update your app's state with the default settings
- Apply default theme
- Show confirmation: "Settings reset to defaults"
- All user customizations are lost (consider adding a confirmation dialog before calling this)

**Example implementation:**

```javascript
async function resetSettingsToDefault() {
  // Show confirmation first
  const confirmed = await showConfirmDialog(
    'Reset All Settings?',
    'This will reset your theme and all tool settings to default values. Your customizations will be lost.',
    'Reset',
    'Cancel'
  );
  
  if (!confirmed) return;
  
  try {
    const response = await fetch('/AIStudio/api/v1/settings/reset', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userToken}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to reset settings');
    }
    
    const defaultSettings = await response.json();
    
    // Update state
    setTheme(defaultSettings.theme);
    setToolSettings(defaultSettings.toolSettings);
    
    // Show success
    showSuccessMessage('Settings reset to defaults');
    
    return defaultSettings;
  } catch (error) {
    console.error('Error resetting settings:', error);
    showErrorMessage('Failed to reset settings. Please try again.');
    throw error;
  }
}
```

---

### API 4: Get Settings with Metadata (Optional)

**Endpoint:** `GET /AIStudio/api/v1/settings/info`

**When to call:** If you need to display when settings were last updated

**Headers required:**
```javascript
{
  "Authorization": "Bearer user_access_token_here"
}
```

**What you'll get back:**

```javascript
{
  "theme": "dark",
  "toolSettings": {
    "lookCreator": { ... },
    "copywriter": { ... },
    "finishingStudio": { ... },
    "modelManager": { ... }
  },
  "updatedAt": "2025-10-10T12:30:00Z"
}
```

**What to do:**
- Use `theme` and `toolSettings` for your app settings
- Use `updatedAt` to show "Last updated: 2 hours ago"

---

## Migration Guide: localStorage to Backend

### Step 1: Update App Initialization

**Old code (localStorage):**
```javascript
function initializeApp() {
  // Load theme
  const savedTheme = localStorage.getItem('theme') || 'light';
  setTheme(savedTheme);
  
  // Load app settings
  const savedSettings = localStorage.getItem('appSettings');
  if (savedSettings) {
    setToolSettings(JSON.parse(savedSettings));
  } else {
    setToolSettings(DEFAULT_TOOL_SETTINGS);
  }
}
```

**New code (backend):**
```javascript
async function initializeApp() {
  // Fetch from backend
  try {
    const settings = await fetchUserSettings();
    setTheme(settings.theme);
    setToolSettings(settings.toolSettings);
  } catch (error) {
    // Fallback to defaults if backend fails
    setTheme('light');
    setToolSettings(DEFAULT_TOOL_SETTINGS);
  }
}
```

---

### Step 2: Update Theme Toggle

**Old code (localStorage):**
```javascript
function toggleTheme() {
  const newTheme = theme === 'light' ? 'dark' : 'light';
  localStorage.setItem('theme', newTheme);
  setTheme(newTheme);
}
```

**New code (backend):**
```javascript
async function toggleTheme() {
  const newTheme = theme === 'light' ? 'dark' : 'light';
  
  // Save to backend
  const newSettings = {
    theme: newTheme,
    toolSettings: toolSettings  // Include existing tool settings
  };
  
  try {
    await saveUserSettings(newSettings);
    setTheme(newTheme);
  } catch (error) {
    showErrorMessage('Failed to save theme preference');
  }
}
```

---

### Step 3: Update Tool Settings Save

**Old code (localStorage):**
```javascript
function saveToolSettings(newToolSettings) {
  localStorage.setItem('appSettings', JSON.stringify(newToolSettings));
  setToolSettings(newToolSettings);
  showSuccessMessage('Settings saved!');
}
```

**New code (backend):**
```javascript
async function saveToolSettings(newToolSettings) {
  const newSettings = {
    theme: theme,  // Include current theme
    toolSettings: newToolSettings
  };
  
  try {
    await saveUserSettings(newSettings);
    setToolSettings(newToolSettings);
    showSuccessMessage('Settings saved!');
  } catch (error) {
    showErrorMessage('Failed to save settings');
  }
}
```

---

### Step 4: Update Reset All Settings

**Old code (localStorage):**
```javascript
function resetAllSettings() {
  localStorage.setItem('theme', 'light');
  localStorage.setItem('appSettings', JSON.stringify(DEFAULT_TOOL_SETTINGS));
  setTheme('light');
  setToolSettings(DEFAULT_TOOL_SETTINGS);
  showSuccessMessage('Settings reset!');
}
```

**New code (backend):**
```javascript
async function resetAllSettings() {
  const confirmed = await showConfirmDialog('Reset all settings?', '...');
  if (!confirmed) return;
  
  try {
    const defaultSettings = await resetSettingsToDefault();
    setTheme(defaultSettings.theme);
    setToolSettings(defaultSettings.toolSettings);
    showSuccessMessage('Settings reset!');
  } catch (error) {
    showErrorMessage('Failed to reset settings');
  }
}
```

---

### Step 5: Remove localStorage Code

Once migration is complete, remove all `localStorage` references for settings:

```javascript
// Remove these:
localStorage.getItem('theme')
localStorage.setItem('theme', ...)
localStorage.getItem('appSettings')
localStorage.setItem('appSettings', ...)
localStorage.removeItem('theme')
localStorage.removeItem('appSettings')
```

---

## Error Handling

### Handle These Cases:

**401 Unauthorized:**
```javascript
{
  "detail": "Could not validate credentials"
}
```
→ User not logged in or token expired. Redirect to login.

**400 Bad Request (for PUT):**
```javascript
{
  "detail": [
    {
      "loc": ["body", "theme"],
      "msg": "Input should be 'light' or 'dark'",
      "type": "literal_error"
    }
  ]
}
```
→ Invalid settings structure. Check that:
- `theme` is either "light" or "dark"
- All required fields in `toolSettings` are present
- All prompts are non-empty strings

**500 Internal Server Error:**
```javascript
{
  "detail": "Internal server error"
}
```
→ Backend error. Show generic error message and retry.

---

## Default Settings Values

The backend maintains these default values. Your frontend should use the same defaults as a fallback:

```javascript
const DEFAULT_SETTINGS = {
  theme: "light",
  toolSettings: {
    lookCreator: {
      systemPrompt: "You are an expert fashion AI assistant specializing in creating cohesive, stylish outfit looks. Your role is to help users discover and curate fashionable combinations from their product catalog. When creating a look, consider color harmony, style consistency, seasonal appropriateness, and current trends. Provide thoughtful recommendations that balance creativity with wearability. Always explain your choices briefly to help users understand the styling rationale.",
      sceneDescriptions: {
        studio: "A clean, minimalist photography studio with soft, diffused lighting. White or light gray backdrop. Professional fashion photography setup with even illumination highlighting the outfit details.",
        beach: "A serene beach setting during golden hour. Soft sand, gentle waves in the background. Natural sunlight creating a warm, relaxed atmosphere. Perfect for casual, summery fashion.",
        city: "An urban cityscape with modern architecture. Clean streets, contemporary buildings, natural daylight. Sophisticated metropolitan environment ideal for showcasing street style and urban fashion.",
        forest: "A lush forest clearing with dappled natural light filtering through the trees. Green foliage backdrop creating an organic, earthy atmosphere. Perfect for natural, bohemian, or outdoor-inspired fashion."
      }
    },
    copywriter: {
      systemPrompt: "You are a professional fashion copywriter and marketing expert. Your role is to craft compelling, conversion-focused product descriptions and marketing copy. Write in an engaging, aspirational tone that highlights key features, benefits, and styling possibilities. Use vivid, sensory language while remaining concise and scannable. Always include relevant details like materials, fit, and care instructions when available. Tailor your writing style to match the brand voice: sophisticated yet accessible, inspiring yet authentic."
    },
    finishingStudio: {
      systemPrompt: "You are an expert image editing AI specializing in fashion photography post-production. Your role is to enhance product and look images while maintaining natural, authentic results. Focus on color correction, lighting adjustments, background refinement, and subtle retouching. Preserve the integrity of the products while making them look their absolute best. Avoid over-editing or creating unrealistic representations. Provide professional, magazine-quality results suitable for e-commerce and marketing materials."
    },
    modelManager: {
      systemPrompt: "You are an AI assistant for fashion model and product image management. Your role is to help organize, tag, and categorize fashion imagery effectively. Analyze images to identify key attributes like clothing type, color palette, style category, season, and mood. Provide accurate, consistent metadata that improves searchability and organization. Suggest relevant tags and categories that align with fashion industry standards and user needs. Be detailed yet concise in your descriptions and classifications."
    }
  }
};
```

---

## Complete Example: Settings Page Component

```javascript
import { useState, useEffect } from 'react';

function SettingsPage() {
  const [theme, setThemeState] = useState('light');
  const [toolSettings, setToolSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, []);
  
  async function loadSettings() {
    setLoading(true);
    try {
      const response = await fetch('/AIStudio/api/v1/settings', {
        headers: {
          'Authorization': `Bearer ${getUserToken()}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to load settings');
      
      const data = await response.json();
      setThemeState(data.theme);
      setToolSettings(data.toolSettings);
      
      // Apply theme to UI
      applyTheme(data.theme);
    } catch (error) {
      console.error('Error loading settings:', error);
      // Use defaults on error
      setThemeState('light');
      setToolSettings(DEFAULT_TOOL_SETTINGS);
    } finally {
      setLoading(false);
    }
  }
  
  async function saveSettings(newTheme, newToolSettings) {
    setSaving(true);
    try {
      const response = await fetch('/AIStudio/api/v1/settings', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${getUserToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          theme: newTheme,
          toolSettings: newToolSettings
        })
      });
      
      if (!response.ok) throw new Error('Failed to save settings');
      
      const updated = await response.json();
      setThemeState(updated.theme);
      setToolSettings(updated.toolSettings);
      applyTheme(updated.theme);
      
      alert('Settings saved successfully!');
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Failed to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  }
  
  async function handleThemeToggle() {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    await saveSettings(newTheme, toolSettings);
  }
  
  async function handleToolSettingsSave(newToolSettings) {
    await saveSettings(theme, newToolSettings);
  }
  
  async function handleResetAll() {
    const confirmed = confirm('Reset all settings to defaults?');
    if (!confirmed) return;
    
    try {
      const response = await fetch('/AIStudio/api/v1/settings/reset', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getUserToken()}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to reset settings');
      
      const defaults = await response.json();
      setThemeState(defaults.theme);
      setToolSettings(defaults.toolSettings);
      applyTheme(defaults.theme);
      
      alert('Settings reset to defaults');
    } catch (error) {
      console.error('Error resetting settings:', error);
      alert('Failed to reset settings. Please try again.');
    }
  }
  
  if (loading) return <div>Loading settings...</div>;
  if (!toolSettings) return <div>Failed to load settings</div>;
  
  return (
    <div className="settings-page">
      <h2>Settings</h2>
      
      {/* Theme Toggle */}
      <section>
        <h3>Appearance</h3>
        <label>
          Theme:
          <button onClick={handleThemeToggle}>
            {theme === 'light' ? '🌙 Switch to Dark' : '☀️ Switch to Light'}
          </button>
        </label>
      </section>
      
      {/* Tool Settings */}
      <section>
        <h3>AI Tool Settings</h3>
        
        <h4>Look Creator</h4>
        <textarea
          value={toolSettings.lookCreator.systemPrompt}
          onChange={(e) => setToolSettings({
            ...toolSettings,
            lookCreator: {
              ...toolSettings.lookCreator,
              systemPrompt: e.target.value
            }
          })}
          rows={4}
        />
        
        {/* Other tool settings... */}
      </section>
      
      {/* Actions */}
      <div className="actions">
        <button 
          onClick={() => handleToolSettingsSave(toolSettings)} 
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
        <button onClick={handleResetAll}>
          Reset All Settings
        </button>
      </div>
    </div>
  );
}
```

---

## Testing Checklist

- [ ] Settings load correctly on app startup
- [ ] User sees default settings if never customized
- [ ] Theme toggle works and saves to backend
- [ ] Theme persists across browser refresh
- [ ] Theme syncs across different devices
- [ ] Can edit system prompts for each tool
- [ ] Can edit scene descriptions
- [ ] Save button updates settings in backend
- [ ] Settings persist across browser refresh
- [ ] Settings sync across different devices
- [ ] Reset button restores all defaults (theme + tools)
- [ ] Reset shows confirmation dialog
- [ ] Error messages shown for failed saves
- [ ] 401 errors redirect to login
- [ ] Invalid theme value shows validation error
- [ ] Settings work offline (with fallback to cached/default)

---

## URLs Quick Reference

**Backend Base URL:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio
```

**Settings Endpoints:**
```
GET  /api/v1/settings       - Get user settings (theme + toolSettings)
PUT  /api/v1/settings       - Update user settings  
POST /api/v1/settings/reset - Reset to defaults (theme + toolSettings)
GET  /api/v1/settings/info  - Get settings with metadata
```

---

## Benefits of Backend Settings

✅ **Persistent:** Settings saved even if browser data is cleared  
✅ **Synced:** Same settings (theme + tools) across all devices  
✅ **Backed up:** Settings are backed up with database  
✅ **Secure:** Protected by authentication  
✅ **Auditable:** Track when settings were last changed  
✅ **Extensible:** Easy to add new settings without frontend changes  

---

## Summary

You're moving from localStorage to backend database for ALL settings:

1. **On login:** Fetch settings from `GET /api/v1/settings`
   - Returns: `{ theme, toolSettings }`

2. **On theme toggle:** Send complete settings to `PUT /api/v1/settings`
   - Body: `{ theme: "dark", toolSettings: {...} }`

3. **On tool settings save:** Send complete settings to `PUT /api/v1/settings`
   - Body: `{ theme: "light", toolSettings: {...} }`

4. **On reset all:** Call `POST /api/v1/settings/reset`
   - Returns: Default theme and default toolSettings

The backend automatically creates default settings for new users (theme: "light" + default tool settings), so you'll always get valid settings back. Just replace your localStorage calls with API calls and you're done!

Good luck! 🚀
