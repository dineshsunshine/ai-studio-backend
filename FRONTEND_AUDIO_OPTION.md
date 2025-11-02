# Video Generation API - Audio Option

## Add Audio Generation to Video Requests

The video generation API now supports optional AI-generated audio/sound.

### Implementation

When creating a video job, add the `generateAudio` parameter to your FormData:

```javascript
const formData = new FormData();
formData.append('prompt', 'Your video prompt');
formData.append('model', 'veo-3.1-fast-generate-preview');
formData.append('resolution', '720p');
formData.append('aspectRatio', '16:9');
formData.append('durationSeconds', 4);
formData.append('generateAudio', 'true');  // ← Add this for audio
formData.append('initialImage', imageFile);  // If using image

// Send request
fetch('/api/v1/video-jobs', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

### Parameters

- **`generateAudio`**: Boolean (string `'true'` or `'false'`)
  - Default: `false` (no audio)
  - Set to `'true'` to enable AI-generated audio/sound
  - Optional field - can be omitted if you don't want audio

### Response

The API response includes `generateAudio: true/false` in the job object, confirming whether audio generation was requested.

### Notes

- Audio generation is optional - existing code without this parameter will continue to work (videos will be silent)
- When enabled, Veo will generate appropriate audio/sound for the video based on the prompt and visual content
- No additional configuration needed - just pass `generateAudio: 'true'` in the request


