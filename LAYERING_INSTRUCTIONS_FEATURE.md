# Layering Instructions Feature - Backend Implementation

## Overview

The Look Creator tool now supports two modes for layering products on models:
- **Simple Mode**: Uses a default layering instruction
- **Advanced Mode**: Uses a customizable layering instruction template

## Backend Changes

### 1. Database Schema (No Migration Required)

The `user_settings` table already has a `tool_settings` JSON column. Two new fields have been added to the `lookCreator` object within this JSON:

```json
{
  "toolSettings": {
    "lookCreator": {
      "systemPrompt": "...",
      "sceneDescriptions": {...},
      "simpleLayeringInstruction": "...",      // NEW
      "advancedLayeringInstructionTemplate": "..." // NEW
    }
  }
}
```

### 2. Pydantic Schema Updates

**File:** `app/schemas/settings.py`

Updated `LookCreatorSettings` to include:
```python
class LookCreatorSettings(BaseModel):
    systemPrompt: str
    sceneDescriptions: SceneDescriptions
    simpleLayeringInstruction: str  # NEW
    advancedLayeringInstructionTemplate: str  # NEW
```

### 3. Default Settings

**File:** `app/core/default_settings.py`

```python
"lookCreator": {
    # ... existing fields ...
    "simpleLayeringInstruction": "Layer the products from bottom to top in the order they were provided, starting with foundational pieces (e.g., pants, skirts) and ending with outer layers (e.g., jackets, coats).",
    "advancedLayeringInstructionTemplate": "Layer the products according to the following custom instruction: {custom_instruction}"
}
```

### 4. Data Migration

All existing user settings have been automatically migrated to include these two new fields with their default values.

## API Endpoints

### GET /api/v1/settings

**Response includes the new fields:**

```json
{
  "theme": "light",
  "toolSettings": {
    "lookCreator": {
      "systemPrompt": "Your primary directive is to create...",
      "sceneDescriptions": {
        "studio": "...",
        "beach": "...",
        "city": "...",
        "forest": "..."
      },
      "simpleLayeringInstruction": "Layer the products from bottom to top...",
      "advancedLayeringInstructionTemplate": "Layer the products according to: {custom_instruction}"
    },
    "copywriter": {...},
    "finishingStudio": {...},
    "modelManager": {...}
  }
}
```

### PUT /api/v1/settings

**Request body accepts the new fields:**

```json
{
  "theme": "light",
  "toolSettings": {
    "lookCreator": {
      "systemPrompt": "...",
      "sceneDescriptions": {...},
      "simpleLayeringInstruction": "Your custom simple instruction",
      "advancedLayeringInstructionTemplate": "Your custom template with {custom_instruction}"
    },
    ...
  }
}
```

### POST /api/v1/settings/reset

Resets all settings including the two new layering instruction fields to their default values.

## Validation

Both fields are **required** and must have at least 1 character:
- `simpleLayeringInstruction`: min_length=1
- `advancedLayeringInstructionTemplate`: min_length=1

Pydantic automatically validates these constraints on all API operations.

## Frontend Integration

### Simple Mode

1. Fetch settings via `GET /api/v1/settings`
2. Use `toolSettings.lookCreator.simpleLayeringInstruction` directly
3. No user editing required in Simple Mode

### Advanced Mode

1. User can customize `toolSettings.lookCreator.advancedLayeringInstructionTemplate` in Settings page
2. The template should contain `{custom_instruction}` placeholder
3. Frontend replaces `{custom_instruction}` with user's actual instruction at runtime
4. Save via `PUT /api/v1/settings`

## Example Usage

**Simple Mode:**
```javascript
const settings = await getSettings();
const instruction = settings.toolSettings.lookCreator.simpleLayeringInstruction;
// Use: "Layer the products from bottom to top in the order they were provided..."
```

**Advanced Mode:**
```javascript
const settings = await getSettings();
const template = settings.toolSettings.lookCreator.advancedLayeringInstructionTemplate;
const userInstruction = "Put the jacket on top, then add accessories";
const finalInstruction = template.replace('{custom_instruction}', userInstruction);
// Use: "Layer the products according to the following custom instruction: Put the jacket on top, then add accessories"
```

## Migration Status

✅ Existing users: Automatically migrated (1 user updated)  
✅ New users: Will receive defaults automatically  
✅ Backend: Restarted and running (PID: 21976)  
✅ All API endpoints: Updated and validated  

## Testing

Test the new fields with:

```bash
# Get settings
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-domain.ngrok-free.dev/AIStudio/api/v1/settings

# Update settings
curl -X PUT \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "light",
    "toolSettings": {
      "lookCreator": {
        ...
        "simpleLayeringInstruction": "Custom simple instruction",
        "advancedLayeringInstructionTemplate": "Custom template {custom_instruction}"
      }
    }
  }' \
  https://your-domain.ngrok-free.dev/AIStudio/api/v1/settings

# Reset to defaults
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-domain.ngrok-free.dev/AIStudio/api/v1/settings/reset
```

## Summary

✅ Two new fields added to Look Creator settings  
✅ Database schema updated (JSON field)  
✅ Pydantic validation enforces required fields  
✅ Default values configured  
✅ Existing user data migrated  
✅ All API endpoints support new fields  
✅ Backend restarted and ready  

**The backend is fully ready for frontend integration!** 🚀


