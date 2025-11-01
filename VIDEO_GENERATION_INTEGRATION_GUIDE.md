# Video Generation API - Integration Guide

## Overview

The video generation system allows users to create AI-generated videos using Google's Veo 3.1 model. Jobs are processed asynchronously in the background, with real-time status updates available via polling.

---

## Quick Start

### 1. Create a Video Generation Job

```javascript
POST /api/v1/video-jobs
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>

{
  "prompt": "A cinematic shot of a sunset over mountains",
  "model": "veo-3.1-fast-generate-preview",
  "resolution": "1080p",
  "aspectRatio": "16:9",
  "durationSeconds": 8
}
```

**Response (202 Accepted):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "user-123",
  "prompt": "A cinematic shot of a sunset over mountains",
  "model": "veo-3.1-fast-generate-preview",
  "resolution": "1080p",
  "aspectRatio": "16:9",
  "durationSeconds": 8,
  "status": "PENDING",
  "statusMessage": "Job queued for processing",
  "progressPercentage": 0,
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "level": "info",
      "message": "📝 Job created"
    }
  ],
  "tokensConsumed": 50,
  "createdAt": "2024-01-15T10:30:00Z"
}
```

### 2. Poll for Job Status

```javascript
GET /api/v1/video-jobs/{jobId}
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "RUNNING",
  "statusMessage": "Video generation in progress...",
  "progressPercentage": 45,
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "level": "info",
      "message": "🚀 Starting video generation"
    },
    {
      "timestamp": "2024-01-15T10:30:15Z",
      "level": "info",
      "message": "☁️  Calling Google Veo API..."
    }
  ]
}
```

### 3. Get Completed Video

Once `status === "SUCCEEDED"`, the `cloudinaryUrl` field will contain the video URL:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "SUCCEEDED",
  "statusMessage": "Video generation completed successfully!",
  "progressPercentage": 100,
  "cloudinaryUrl": "https://res.cloudinary.com/your-cloud/video/upload/v123/ai_studio/videos/550e8400.mp4",
  "completedAt": "2024-01-15T10:35:00Z"
}
```

---

## API Endpoints

### POST /api/v1/video-jobs
Create a new video generation job.

**Authentication:** Required (JWT)

**Request Body (multipart/form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | No* | Text description for video generation |
| `model` | string | Yes | Model name (e.g., 'veo-3.1-fast-generate-preview') |
| `resolution` | string | Yes | '720p' or '1080p' |
| `aspectRatio` | string | Yes | '16:9' or '9:16' |
| `durationSeconds` | number | No | 4 or 8 seconds |
| `mockMode` | string | **Yes** | **REQUIRED**: 'true' to skip Veo API (test mode), 'false' to use real Veo API |
| `generateAudio` | boolean | No | Enable AI-generated audio/sound (default: false) |
| `initialImage` | file | No | Starting frame image |
| `endFrame` | file | No | Ending frame image |
| `referenceImages` | file[] | No | Up to 3 reference images |

*Either `prompt` or `initialImage` is required.

**Token Cost:** 50 tokens (consumed immediately upon job creation)

**Limits:**
- Maximum 3 concurrent jobs per user
- Jobs are queued if limit is reached

**Responses:**
- `202 Accepted` - Job created and queued
- `400 Bad Request` - Invalid parameters
- `402 Payment Required` - Insufficient tokens
- `429 Too Many Requests` - Too many concurrent jobs

---

### GET /api/v1/video-jobs/{jobId}
Get status and details of a specific job.

**Authentication:** Required (JWT)

**Response:** VideoJob object

**Job Statuses:**
- `PENDING` - Queued, waiting to start
- `RUNNING` - Currently processing
- `SUCCEEDED` - Completed successfully
- `FAILED` - Failed with error
- `CANCELLED` - Cancelled by user

---

### GET /api/v1/video-jobs
List all jobs for the current user.

**Authentication:** Required (JWT)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status_filter` | string | null | Filter by status (PENDING, RUNNING, SUCCEEDED, FAILED) |
| `limit` | number | 50 | Maximum results |
| `offset` | number | 0 | Pagination offset |

**Response:**
```json
{
  "jobs": [/* array of VideoJob objects */],
  "total": 42
}
```

---

### GET /api/v1/video-jobs/{jobId}/download
Download the completed video.

**Authentication:** Required (JWT)

**Behavior:** Redirects to Cloudinary URL for fast CDN delivery

**Responses:**
- `302 Found` - Redirects to video URL
- `400 Bad Request` - Video not ready yet
- `404 Not Found` - Job not found

---

### DELETE /api/v1/video-jobs/{jobId}
Delete a job record.

**Authentication:** Required (JWT)

**Note:** Only deletes the database record, not the video file from Cloudinary.

**Response:** `204 No Content`

---

## Frontend Implementation Example

```javascript
// video-generation.js

class VideoGenerationClient {
  constructor(apiBase, authToken) {
    this.apiBase = apiBase;
    this.authToken = authToken;
  }

  async createJob(params) {
    const formData = new FormData();
    
    if (params.prompt) formData.append('prompt', params.prompt);
    formData.append('model', params.model);
    formData.append('resolution', params.resolution);
    formData.append('aspectRatio', params.aspectRatio);
    if (params.durationSeconds) formData.append('durationSeconds', params.durationSeconds);
    
    if (params.initialImage) formData.append('initialImage', params.initialImage);
    if (params.endFrame) formData.append('endFrame', params.endFrame);
    if (params.referenceImages) {
      params.referenceImages.forEach(img => formData.append('referenceImages', img));
    }

    const response = await fetch(`${this.apiBase}/video-jobs`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.authToken}`
      },
      body: formData
    });

    if (response.status === 402) {
      const error = await response.json();
      throw new Error(`Insufficient tokens: ${error.detail.message}`);
    }

    if (!response.ok) {
      throw new Error(`Failed to create job: ${response.statusText}`);
    }

    return await response.json();
  }

  async pollJob(jobId, onUpdate) {
    const poll = async () => {
      const response = await fetch(`${this.apiBase}/video-jobs/${jobId}`, {
        headers: {
          'Authorization': `Bearer ${this.authToken}`
        }
      });

      const job = await response.json();
      onUpdate(job);

      // Continue polling if job is still in progress
      if (job.status === 'PENDING' || job.status === 'RUNNING') {
        setTimeout(poll, 3000); // Poll every 3 seconds
      }
    };

    poll();
  }

  async listJobs(statusFilter = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (statusFilter) params.append('status_filter', statusFilter);

    const response = await fetch(`${this.apiBase}/video-jobs?${params}`, {
      headers: {
        'Authorization': `Bearer ${this.authToken}`
      }
    });

    return await response.json();
  }

  async deleteJob(jobId) {
    await fetch(`${this.apiBase}/video-jobs/${jobId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.authToken}`
      }
    });
  }
}

// Usage Example
const client = new VideoGenerationClient('https://api.example.com/api/v1', userToken);

// Create job
const job = await client.createJob({
  prompt: 'A sunset over mountains',
  model: 'veo-3.1-fast-generate-preview',
  resolution: '1080p',
  aspectRatio: '16:9',
  durationSeconds: 8
});

console.log('Job created:', job.id);

// Poll for updates
client.pollJob(job.id, (updatedJob) => {
  console.log(`Status: ${updatedJob.status} (${updatedJob.progressPercentage}%)`);
  
  if (updatedJob.status === 'SUCCEEDED') {
    console.log('Video ready:', updatedJob.cloudinaryUrl);
    // Display video to user
  } else if (updatedJob.status === 'FAILED') {
    console.error('Generation failed:', updatedJob.errorMessage);
  }
});
```

---

## UI/UX Recommendations

### 1. Job Creation Form
```jsx
<form onSubmit={handleSubmit}>
  <textarea 
    name="prompt" 
    placeholder="Describe your video..." 
    required 
  />
  
  <select name="model" required>
    <option value="veo-3.1-fast-generate-preview">Veo 3.1 Fast (Preview)</option>
  </select>
  
  <select name="resolution" required>
    <option value="720p">720p (HD)</option>
    <option value="1080p">1080p (Full HD)</option>
  </select>
  
  <select name="aspectRatio" required>
    <option value="16:9">16:9 (Landscape)</option>
    <option value="9:16">9:16 (Portrait)</option>
  </select>
  
  <select name="durationSeconds">
    <option value="4">4 seconds</option>
    <option value="8">8 seconds</option>
  </select>
  
  <button type="submit">Generate Video (50 tokens)</button>
</form>
```

### 2. Progress Indicator
```jsx
function VideoJobCard({ job }) {
  return (
    <div className="job-card">
      <div className="job-header">
        <span className="job-id">{job.id}</span>
        <span className={`status status-${job.status.toLowerCase()}`}>
          {job.status}
        </span>
      </div>
      
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${job.progressPercentage}%` }}
        />
        <span className="progress-text">{job.progressPercentage}%</span>
      </div>
      
      <div className="status-message">{job.statusMessage}</div>
      
      {job.status === 'SUCCEEDED' && (
        <video src={job.cloudinaryUrl} controls />
      )}
      
      {job.status === 'FAILED' && (
        <div className="error-message">{job.errorMessage}</div>
      )}
    </div>
  );
}
```

### 3. Real-time Logs (Optional)
```jsx
function LogsPanel({ logs }) {
  return (
    <div className="logs-panel">
      {logs.map((log, idx) => (
        <div key={idx} className={`log-entry log-${log.level}`}>
          <span className="timestamp">{formatTime(log.timestamp)}</span>
          <span className="message">{log.message}</span>
        </div>
      ))}
    </div>
  );
}
```

---

## Error Handling

### Common Errors

**402 Payment Required - Insufficient Tokens**
```json
{
  "detail": {
    "message": "Insufficient tokens. Operation 'video_generation' costs 50 tokens but you have 20.",
    "cost": 50,
    "availableTokens": 20
  }
}
```

**Response:** Show upgrade modal or token purchase prompt.

---

**429 Too Many Requests - Concurrent Job Limit**
```json
{
  "detail": "Maximum 3 concurrent video jobs allowed. Please wait for existing jobs to complete."
}
```

**Response:** Show queue status and estimated wait time.

---

**400 Bad Request - Invalid Parameters**
```json
{
  "detail": "Resolution must be '720p' or '1080p'"
}
```

**Response:** Highlight invalid field and show error message.

---

## Video Monitor Dashboard

A public monitoring dashboard is available at:
- **Dev:** `https://your-ngrok-url.ngrok-free.dev/AIStudio/video-monitor`
- **Production:** `https://your-domain.com/video-monitor`

**Features:**
- Real-time job tracking
- Live progress updates
- Logs visualization
- Video preview
- No authentication required

---

## Testing

### Test Scenarios

1. **Basic Video Generation**
```bash
curl -X POST http://localhost:8000/api/v1/video-jobs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "prompt=A beautiful sunset over mountains" \
  -F "model=veo-3.1-fast-generate-preview" \
  -F "resolution=1080p" \
  -F "aspectRatio=16:9"
```

2. **Poll Job Status**
```bash
curl http://localhost:8000/api/v1/video-jobs/JOB_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. **List All Jobs**
```bash
curl http://localhost:8000/api/v1/video-jobs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Production Deployment

### Environment Variables

Required for production:
```bash
# Google API
GOOGLE_API_KEY=your_google_api_key

# Redis
REDIS_URL=redis://your-redis-url:6379/0

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
USE_CLOUDINARY=true
```

### Start Celery Worker

```bash
# Start the background worker
celery -A app.core.celery_app worker --loglevel=info --concurrency=2
```

For production, use a process manager like Supervisor or systemd.

### Render Setup

1. **Web Service** (already exists)
   - Runs FastAPI server
   
2. **Background Worker** (NEW)
   - Create new "Background Worker" service
   - Start Command: `celery -A app.core.celery_app worker --loglevel=info --concurrency=2`
   - Environment: Same as web service
   
3. **Redis** (NEW)
   - Create Redis instance
   - Copy connection URL to `REDIS_URL` env var

---

## Performance Considerations

- **Generation Time:** 3-10 minutes per video
- **Token Cost:** 50 tokens per job
- **Concurrent Limit:** 3 jobs per user
- **Video Size:** 10-50 MB (1080p, 8 seconds)
- **Storage:** Cloudinary recommended for production
- **Polling Interval:** 3-5 seconds recommended

---

## Troubleshooting

### Job Stuck in PENDING
- Check if Celery worker is running
- Check Redis connection
- View worker logs

### Job Failed Immediately
- Check Google API key is valid
- Verify prompt meets Google's content policy
- Check worker logs for detailed error

### Video URL Not Loading
- Verify Cloudinary configuration
- Check if video was successfully uploaded
- Try downloading directly from Cloudinary

---

## Support

For issues or questions:
- Check worker logs: `celery -A app.core.celery_app worker --loglevel=debug`
- View job logs in the database or monitoring dashboard
- Review API documentation: `/api/v1/docs`

---

**Happy video generating!** 🎬🚀

