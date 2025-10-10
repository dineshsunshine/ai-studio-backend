# Admin Default Settings - Implementation Summary

## Overview

Admins can now manage default settings that all new users receive and that users get when they reset their settings. This provides a centralized way to control the initial experience for all users without changing code.

---

## What This Feature Does

### For Admins
- **View** current default settings (theme + tool settings)
- **Update** default settings that new users will receive
- **Reset** defaults to original system hardcoded values

### Impact
- ✅ **New users** automatically get admin-configured defaults when approved
- ✅ **Existing users** who click "Reset" get current admin-configured defaults
- ❌ **Existing users** with custom settings are NOT affected

---

## Database Changes

### New Table: `default_settings`

```sql
CREATE TABLE default_settings (
    id VARCHAR(36) PRIMARY KEY,
    default_theme VARCHAR(10) NOT NULL DEFAULT 'light',
    default_tool_settings JSON NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    updated_by VARCHAR(36)  -- Admin user ID who last updated
)
```

**Singleton Pattern:** Only one record exists in this table at all times.

---

## New API Endpoints

All endpoints require admin authentication (`role: "admin"`).

### 1. Get Current Defaults

**Endpoint:** `GET /api/v1/admin/defaults`

**Response:**
```json
{
  "defaultTheme": "light",
  "defaultToolSettings": {
    "lookCreator": {
      "systemPrompt": "...",
      "sceneDescriptions": {...},
      "simpleLayeringInstruction": "...",
      "advancedLayeringInstructionTemplate": "..."
    },
    "copywriter": {"systemPrompt": "..."},
    "finishingStudio": {"systemPrompt": "..."},
    "modelManager": {"systemPrompt": "..."}
  },
  "updatedAt": "2025-10-10T12:00:00Z",
  "updatedBy": "admin-user-id"
}
```

---

### 2. Update Defaults

**Endpoint:** `PUT /api/v1/admin/defaults`

**Request Body:**
```json
{
  "defaultTheme": "dark",
  "defaultToolSettings": {
    "lookCreator": {...},
    "copywriter": {...},
    "finishingStudio": {...},
    "modelManager": {...}
  }
}
```

**Response:** Same as GET (with updated values and timestamp)

---

### 3. Reset to System Defaults

**Endpoint:** `POST /api/v1/admin/defaults/reset`

**No request body needed**

**Response:** Same as GET (with system hardcoded defaults)

---

## Code Changes

### New Files

1. **`app/models/default_settings_model.py`**
   - SQLAlchemy model for `default_settings` table

2. **`app/schemas/default_settings_schema.py`**
   - Pydantic schemas: `DefaultSettingsData`, `DefaultSettingsResponse`

3. **`app/api/v1/endpoints/admin_defaults.py`**
   - Admin endpoints for managing defaults
   - Helper function: `get_or_create_default_settings()`

4. **`FRONTEND_ADMIN_DEFAULTS_PROMPT.md`**
   - Complete plain English guide for frontend developer

---

### Modified Files

1. **`app/core/default_settings.py`**
   - Added `get_current_defaults(db)` function
   - This function retrieves admin-configured defaults from database
   - Falls back to hardcoded defaults if no DB record exists

2. **`app/api/v1/endpoints/admin.py`**
   - `approve_access_request()` now uses `get_current_defaults(db)`
   - New users get admin-configured defaults instead of hardcoded ones

3. **`app/api/v1/endpoints/settings.py`**
   - `get_or_create_user_settings()` uses `get_current_defaults(db)`
   - `reset_user_settings()` uses `get_current_defaults(db)`
   - Reset now applies admin-configured defaults, not hardcoded ones

4. **`app/api/v1/api.py`**
   - Registered `admin_defaults` router under `/admin` prefix

5. **`app/models/__init__.py`**
   - Added `DefaultSettingsModel` import

---

## How It Works

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Admin updates defaults via PUT /api/v1/admin/defaults   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │  default_settings table      │
          │  (updated in database)       │
          └──────────────┬───────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌────────────────────┐         ┌──────────────────────┐
│ New user approved  │         │ User clicks "Reset"  │
│                    │         │                      │
│ get_current_       │         │ get_current_         │
│ defaults(db)       │         │ defaults(db)         │
│                    │         │                      │
│ → Creates user     │         │ → Updates user       │
│   settings with    │         │   settings with      │
│   admin defaults   │         │   admin defaults     │
└────────────────────┘         └──────────────────────┘
```

---

## Testing

### Test as Admin

1. **Login as admin** (golanicharu@gmail.com or your admin email)

2. **Get current defaults:**
   ```bash
   curl -X GET 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/admin/defaults' \
     -H 'Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN'
   ```

3. **Update defaults:**
   ```bash
   curl -X PUT 'https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/admin/defaults' \
     -H 'Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN' \
     -H 'Content-Type: application/json' \
     -d '{
       "defaultTheme": "dark",
       "defaultToolSettings": {
         "lookCreator": {...},
         "copywriter": {...},
         "finishingStudio": {...},
         "modelManager": {...}
       }
     }'
   ```

4. **Verify new user gets updated defaults:**
   - Approve a new user
   - That user should automatically have `theme: "dark"`

5. **Verify reset uses updated defaults:**
   - As any user, call `POST /api/v1/settings/reset`
   - User should receive `theme: "dark"`

---

## Security

- All endpoints protected by `require_admin` dependency
- Only users with `role: "admin"` can access
- Regular users get `403 Forbidden` error
- Tracks which admin made changes (`updated_by` field)

---

## Frontend Implementation

A complete guide for the frontend developer is available at:
**`FRONTEND_ADMIN_DEFAULTS_PROMPT.md`**

This guide includes:
- Plain English explanation of the feature
- Complete API integration details
- Request/response examples
- UI recommendations
- Error handling
- Testing checklist

---

## Swagger Documentation

Visit: **https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs**

Look for the **"admin-defaults"** tag to see all endpoints with interactive testing.

---

## Key Points

1. **Single Source of Truth:** Database holds the current defaults, not localStorage or hardcoded values
2. **Backward Compatible:** If no DB record exists, falls back to hardcoded defaults
3. **Non-Destructive:** Changing defaults does NOT affect existing users' current settings
4. **Auditable:** Tracks who updated defaults and when
5. **Resetable:** Admins can restore system hardcoded defaults anytime

---

## Future Enhancements

Potential future features:
- Version history of default changes
- Default templates (e.g., "Fashion Brand", "E-commerce", etc.)
- Preview mode to see defaults before applying
- Bulk apply defaults to all users (with confirmation)
- Per-tool defaults (update only Look Creator defaults, etc.)

---

## Support

If you need help or encounter issues:
1. Check Swagger UI for endpoint details
2. Review `FRONTEND_ADMIN_DEFAULTS_PROMPT.md` for integration guide
3. Check backend logs: `tail -f /tmp/backend.log`
4. Verify admin role: `SELECT role FROM users WHERE email = 'your@email.com'`

---

**Implementation Date:** October 10, 2025  
**Backend Version:** 1.0  
**Status:** ✅ Production Ready

