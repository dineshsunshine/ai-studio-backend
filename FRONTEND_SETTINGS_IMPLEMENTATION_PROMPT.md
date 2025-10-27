# Frontend Task: Implement Settings Page

## What You Need to Build

A Settings page where users can customize their application preferences (theme and AI tool prompts).

---

## The Settings Page Should Have

### 1. Theme Toggle
- A button or switch to change between Light and Dark mode
- Shows current theme
- Saves immediately when toggled

### 2. AI Tool Settings Sections

**Look Creator:**
- Text area for system prompt
- Four text areas for scene descriptions: Studio, Beach, City, Forest

**Copywriter:**
- Text area for system prompt

**Finishing Studio:**
- Text area for system prompt

**Model Manager:**
- Text area for system prompt

### 3. Action Buttons

**Save Settings Button:**
- Saves all changes to the backend
- Shows success message: "Settings saved successfully!"
- Shows error if save fails

**Reset All Settings Button:**
- Shows confirmation dialog: "This will reset your theme and all tool settings to defaults. Continue?"
- If confirmed, resets everything to defaults
- Shows success message: "Settings reset to defaults"

---

## How to Load Settings on Page Open

When the Settings page opens:

1. Call: `GET /AIStudio/api/v1/settings`
2. You'll get back:
```javascript
{
  "theme": "dark",
  "toolSettings": {
    "lookCreator": {
      "systemPrompt": "...",
      "sceneDescriptions": {
        "studio": "...",
        "beach": "...",
        "city": "...",
        "forest": "..."
      }
    },
    "copywriter": { "systemPrompt": "..." },
    "finishingStudio": { "systemPrompt": "..." },
    "modelManager": { "systemPrompt": "..." }
  }
}
```
3. Display this data in your form fields

**Important:** If this is a new user, they'll get default values like "Default setting Look Creator system prompt" - users should customize these!

---

## How to Save Settings

When user clicks "Save Settings":

1. Collect all form values (theme + all tool settings)
2. Call: `PUT /AIStudio/api/v1/settings`
3. Send this structure:
```javascript
{
  "theme": "light",  // or "dark"
  "toolSettings": {
    "lookCreator": {
      "systemPrompt": "text from the text area",
      "sceneDescriptions": {
        "studio": "text from studio text area",
        "beach": "text from beach text area",
        "city": "text from city text area",
        "forest": "text from forest text area"
      }
    },
    "copywriter": {
      "systemPrompt": "text from copywriter text area"
    },
    "finishingStudio": {
      "systemPrompt": "text from finishing studio text area"
    },
    "modelManager": {
      "systemPrompt": "text from model manager text area"
    }
  }
}
```
4. Show success or error message based on response

**Rules:**
- Theme must be exactly "light" or "dark" (lowercase)
- All text areas must have some text (not empty)
- Send the COMPLETE object every time (even if user only changed one field)

---

## How to Toggle Theme

When user toggles the theme switch:

1. Get current theme (light or dark)
2. Switch to opposite: `newTheme = theme === 'light' ? 'dark' : 'light'`
3. Update the theme in your form state
4. Call the save API with the new theme + existing tool settings
5. Apply the new theme to your UI

**Shortcut:** You can save immediately on toggle, or wait for user to click "Save Settings" - your choice!

---

## How to Reset All Settings

When user clicks "Reset All Settings":

1. Show confirmation dialog with message: "This will reset your theme and all tool settings to defaults. Continue?"
2. If user cancels, do nothing
3. If user confirms:
   - Call: `POST /AIStudio/api/v1/settings/reset`
   - No need to send any data in the request body
4. You'll get back the default settings:
```javascript
{
  "theme": "light",
  "toolSettings": {
    "lookCreator": {
      "systemPrompt": "Default setting Look Creator system prompt",
      "sceneDescriptions": {
        "studio": "Default setting studio scene description",
        // ... etc
      }
    },
    // ... etc
  }
}
```
5. Update your form with these default values
6. Apply the default theme to UI
7. Show success message

---

## API Details

**All requests need authentication:** Include your access token in headers
```javascript
headers: {
  'Authorization': 'Bearer YOUR_ACCESS_TOKEN_HERE'
}
```

**Base URL:** `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio`

### API 1: Get Settings
```
GET /api/v1/settings
Response: { theme, toolSettings }
```

### API 2: Save Settings
```
PUT /api/v1/settings
Body: { theme, toolSettings }
Response: { theme, toolSettings }
```

### API 3: Reset Settings
```
POST /api/v1/settings/reset
No body needed
Response: { theme, toolSettings }
```

---

## Example Code Structure

```javascript
// On page load
async function loadSettings() {
  const response = await fetch('/AIStudio/api/v1/settings', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const data = await response.json();
  
  // Set form values
  setTheme(data.theme);
  setLookCreatorPrompt(data.toolSettings.lookCreator.systemPrompt);
  setStudioScene(data.toolSettings.lookCreator.sceneDescriptions.studio);
  // ... set all other fields
}

// On save
async function saveSettings() {
  const settings = {
    theme: currentTheme,
    toolSettings: {
      lookCreator: {
        systemPrompt: lookCreatorPromptValue,
        sceneDescriptions: {
          studio: studioSceneValue,
          beach: beachSceneValue,
          city: citySceneValue,
          forest: forestSceneValue
        }
      },
      copywriter: { systemPrompt: copywriterPromptValue },
      finishingStudio: { systemPrompt: finishingStudioPromptValue },
      modelManager: { systemPrompt: modelManagerPromptValue }
    }
  };
  
  const response = await fetch('/AIStudio/api/v1/settings', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(settings)
  });
  
  if (response.ok) {
    alert('Settings saved successfully!');
  } else {
    alert('Failed to save settings');
  }
}

// On reset
async function resetSettings() {
  if (!confirm('This will reset your theme and all tool settings to defaults. Continue?')) {
    return;
  }
  
  const response = await fetch('/AIStudio/api/v1/settings/reset', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const defaults = await response.json();
  
  // Update all form fields with defaults
  setTheme(defaults.theme);
  // ... update all other fields
  
  alert('Settings reset to defaults');
}
```

---

## Error Handling

**If API returns 401:** User's token expired → Redirect to login

**If API returns 400:** Invalid data format → Check that:
- Theme is "light" or "dark" (lowercase)
- All text fields have content
- The structure matches exactly

**If API fails:** Show error message: "Failed to save settings. Please try again."

---

## UI Recommendations

**Layout:**
```
┌─────────────────────────────────────┐
│  Settings                           │
├─────────────────────────────────────┤
│                                     │
│  Appearance                         │
│  Theme: [Light/Dark Toggle]         │
│                                     │
│  ──────────────────────────────────│
│                                     │
│  Look Creator Settings              │
│  System Prompt:                     │
│  [text area - multiple lines]       │
│                                     │
│  Scene Descriptions:                │
│  Studio: [text area]                │
│  Beach:  [text area]                │
│  City:   [text area]                │
│  Forest: [text area]                │
│                                     │
│  ──────────────────────────────────│
│                                     │
│  Copywriter Settings                │
│  System Prompt:                     │
│  [text area]                        │
│                                     │
│  ──────────────────────────────────│
│                                     │
│  Finishing Studio Settings          │
│  System Prompt:                     │
│  [text area]                        │
│                                     │
│  ──────────────────────────────────│
│                                     │
│  Model Manager Settings             │
│  System Prompt:                     │
│  [text area]                        │
│                                     │
│  ──────────────────────────────────│
│                                     │
│  [Save Settings]  [Reset All]       │
│                                     │
└─────────────────────────────────────┘
```

**Text areas:** Use multiline input with at least 3-4 rows

**Theme toggle:** Can be a switch, button, or dropdown

**Buttons:**
- "Save Settings" - Primary/highlighted button
- "Reset All Settings" - Secondary/warning style

---

## Testing Checklist

- [ ] Page loads and shows current settings
- [ ] Theme toggle changes theme in UI
- [ ] Can edit all text areas
- [ ] Save button saves all changes to backend
- [ ] Success message shows after save
- [ ] Settings persist after page refresh
- [ ] Reset button shows confirmation dialog
- [ ] Reset button restores all defaults
- [ ] Error messages show when API fails
- [ ] 401 errors redirect to login

---

## Summary

1. **Load settings** when page opens: `GET /api/v1/settings`
2. **Show all settings** in form: theme toggle + text areas for all prompts
3. **Save changes** when user clicks Save: `PUT /api/v1/settings`
4. **Reset to defaults** when user clicks Reset: `POST /api/v1/settings/reset`

The backend handles everything - you just need to build the UI and call the right APIs!

**New users will see:** "Default setting [name]" in all fields - these are placeholders they should customize.

Good luck! 🚀


