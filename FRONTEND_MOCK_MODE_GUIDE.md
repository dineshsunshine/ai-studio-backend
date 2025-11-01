# Video Generation Mock Mode - Frontend Integration

## Overview

Add a `mockMode` parameter to video generation API calls to enable mock/testing mode. When `mockMode: true`, the backend will skip Google Veo API calls and return a test video after a random 8-15 second delay.

**Benefits:**
- Test UX/UI without hitting paid Google Veo API
- Faster development and testing cycles
- No API costs during testing

---

## API Integration

### **Endpoint:** `POST /api/v1/video-jobs`

### **New Parameter:**

Add `mockMode` to your FormData:

```javascript
const formData = new FormData();
formData.append('prompt', 'Your video prompt');
formData.append('model', 'veo-3.1-fast-generate-preview');
formData.append('resolution', '720p');
formData.append('aspectRatio', '16:9');
formData.append('durationSeconds', 4);
formData.append('generateAudio', 'false');
formData.append('mockMode', 'true');  // <--- NEW PARAMETER!
// ... other fields ...

fetch('/api/v1/video-jobs', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

---

## Parameter Details

- **Name:** `mockMode` (or `mock_mode` in snake_case)
- **Type:** Boolean
- **Default:** `false` (real mode)
- **Values:** `'true'` or `'false'` (as string in FormData)
- **Location:** FormData parameter (same level as `prompt`, `model`, etc.)

---

## Behavior

### **Mock Mode (`mockMode: true`):**
- ✅ Skips Google Veo API call (no API costs)
- ✅ Waits random 8-15 seconds (simulates real generation)
- ✅ Returns test video URL from Cloudinary
- ✅ Still consumes 50 tokens (simulates real behavior)
- ✅ Shows progress updates (20% → 40% → 60% → 80% → 100%)
- ✅ Returns same response format as real mode

### **Real Mode (`mockMode: false` or omitted):**
- ✅ Calls Google Veo API normally
- ✅ Generates actual video based on prompt/images
- ✅ Standard video generation flow

---

## Response Format

Both modes return the same response structure:

```json
{
  "id": "job-id-here",
  "status": "SUCCEEDED",
  "statusMessage": "Video generated successfully (Mock Mode)",
  "cloudinaryUrl": "https://res.cloudinary.com/.../video.mp4",
  "progressPercentage": 100,
  "logs": [...],
  // ... other fields
}
```

**Note:** In mock mode, `statusMessage` will include "(Mock Mode)" text.

---

## Example Implementation

```javascript
// Toggle mock mode based on environment or user setting
const isDevelopment = process.env.NODE_ENV === 'development';
const useMockMode = isDevelopment || userSettings.useMockMode;

const formData = new FormData();
formData.append('prompt', videoPrompt);
formData.append('model', 'veo-3.1-fast-generate-preview');
formData.append('resolution', '720p');
formData.append('aspectRatio', '16:9');
formData.append('durationSeconds', 4);
formData.append('generateAudio', 'false');
formData.append('mockMode', useMockMode ? 'true' : 'false');  // Conditional mock mode

if (initialImage) {
  formData.append('initialImage', initialImage);
}

const response = await fetch('/api/v1/video-jobs', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`
  },
  body: formData
});
```

---

## UI/UX Recommendations

1. **Toggle Switch:** Add a "Mock Mode" toggle in development/testing environment
2. **Visual Indicator:** Show a badge/indicator when mock mode is active (e.g., "🎭 Mock Mode")
3. **Status Messages:** Display "(Mock Mode)" in status messages if applicable
4. **Testing:** Use mock mode for:
   - UI/UX testing
   - Progress indicator testing
   - Error handling testing
   - User flow testing

---

## Notes

- **Tokens:** Mock mode still consumes 50 tokens (to simulate real behavior)
- **Video URL:** Mock mode returns a fixed test video URL (same for all mock jobs)
- **Timing:** Random 8-15 second delay simulates real generation time
- **Production:** Set `mockMode: false` in production to use real API

---

**Backend Changes:**
- Added `mockMode` parameter to `POST /api/v1/video-jobs`
- Added `mock_mode` column to `video_jobs` table
- Worker checks `mock_mode` flag and skips Veo API if true
- Returns test video URL from Cloudinary after simulated delay

