# 🧪 API Testing Guide

Your backend is running at: **http://localhost:8000**

## 📚 Interactive Documentation

Open these URLs in your browser for **interactive API testing**:

- **Swagger UI (Recommended)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

The Swagger UI lets you test all endpoints directly from your browser! 🎉

---

## 🔧 Testing with cURL (Command Line)

### 1️⃣ Root Endpoint
```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "message": "🎉 Welcome to AI Studio Backend!",
  "status": "running",
  "docs": "/docs",
  "endpoints": {
    "health": "/health",
    "tasks": "/tasks"
  }
}
```

---

### 2️⃣ Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-09T08:07:24.996456",
  "message": "API is running perfectly! ✅"
}
```

---

### 3️⃣ Create a Task (POST)
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Task",
    "description": "This is a test task",
    "completed": false
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "title": "My First Task",
  "description": "This is a test task",
  "completed": false,
  "created_at": "2025-10-09T08:07:25.959130"
}
```

---

### 4️⃣ Get All Tasks
```bash
curl http://localhost:8000/tasks
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "title": "My First Task",
    "description": "This is a test task",
    "completed": false,
    "created_at": "2025-10-09T08:07:25.959130"
  }
]
```

---

### 5️⃣ Get a Specific Task
```bash
curl http://localhost:8000/tasks/1
```

---

### 6️⃣ Update a Task (PUT)
```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task",
    "description": "Task has been updated",
    "completed": true
  }'
```

---

### 7️⃣ Delete a Task
```bash
curl -X DELETE http://localhost:8000/tasks/1
```

**Expected Response:**
```json
{
  "message": "Task 1 deleted successfully"
}
```

---

## 🌐 Testing with Browser/Postman

### Using Swagger UI (Easiest!)

1. Open http://localhost:8000/docs in your browser
2. You'll see all available endpoints
3. Click on any endpoint to expand it
4. Click "Try it out"
5. Fill in the parameters
6. Click "Execute"
7. See the response!

### Using Postman

1. Create a new request
2. Set URL: `http://localhost:8000/tasks`
3. Set Method: `POST`
4. Go to "Body" tab
5. Select "raw" and "JSON"
6. Paste:
   ```json
   {
     "title": "Test from Postman",
     "description": "Testing API",
     "completed": false
   }
   ```
7. Click "Send"

---

## 🧪 Test Scenarios

### Scenario 1: Create and Retrieve Tasks
```bash
# Create 3 tasks
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" \
  -d '{"title":"Task 1","description":"First task","completed":false}'

curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" \
  -d '{"title":"Task 2","description":"Second task","completed":false}'

curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" \
  -d '{"title":"Task 3","description":"Third task","completed":true}'

# Get all tasks
curl http://localhost:8000/tasks
```

### Scenario 2: Complete Workflow
```bash
# 1. Create a task
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" \
  -d '{"title":"Important Task","description":"Must complete","completed":false}'

# 2. Get the task (assuming ID is 1)
curl http://localhost:8000/tasks/1

# 3. Update to mark as completed
curl -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" \
  -d '{"title":"Important Task","description":"Completed!","completed":true}'

# 4. Verify update
curl http://localhost:8000/tasks/1

# 5. Delete the task
curl -X DELETE http://localhost:8000/tasks/1
```

---

## 🚀 Integration with Google AI Studio

You can use these endpoints from Google AI Studio by making HTTP requests to:

```
http://localhost:8000/tasks
```

### Example: Fetch data from AI Studio
```javascript
// In your Google AI Studio frontend
fetch('http://localhost:8000/tasks')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

### Example: Create task from AI Studio
```javascript
fetch('http://localhost:8000/tasks', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'Task from AI Studio',
    description: 'Created via frontend',
    completed: false
  })
})
.then(response => response.json())
.then(data => console.log('Success:', data))
.catch(error => console.error('Error:', error));
```

---

## 🛑 Stop the Server

To stop the server, press **Ctrl+C** in the terminal where it's running.

---

## 📝 Notes

- This is a **test API** with in-memory storage
- Data will be lost when the server restarts
- For production, we'll add PostgreSQL database
- All endpoints support CORS for easy frontend integration

---

## ✅ Next Steps

1. **Test all endpoints** using Swagger UI
2. **Integrate with your Google AI Studio frontend**
3. **Let me know what specific features you need**
4. **We'll add database support** when you're ready

Enjoy testing! 🚀


