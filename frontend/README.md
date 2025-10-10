# 🎨 AI Studio - Test Frontend

## Quick Access

**Just open this file in your browser:**
```
/Users/dgolani/Documents/AI_Studio/backend/frontend/index.html
```

Or double-click the `index.html` file!

---

## What It Does

A beautiful, interactive web interface to test all CRUD operations on your backend API.

### Features:

✅ **Statistics Dashboard** - Real-time task stats  
✅ **Create Tasks** - Add new tasks with title, description  
✅ **View Tasks** - Beautiful card layout with all details  
✅ **Update Tasks** - Mark complete, edit inline  
✅ **Delete Tasks** - Remove with confirmation  
✅ **Filter** - Show all, pending, or completed tasks  
✅ **Health Check** - Test API connection  
✅ **API Viewer** - See all API responses in real-time  
✅ **Change URL** - Switch between different backends  

---

## Auto-Configuration

The frontend automatically connects to:
```
https://zestfully-chalky-nikia.ngrok-free.dev
```

You can change this anytime using the "Change URL" button.

---

## Screenshots of What You'll See:

### Top Section:
- 📊 4 stat cards showing total, completed, pending tasks, and completion rate
- All stats update in real-time!

### Create Section:
- Form to create new tasks
- Title (required)
- Description (optional)
- Mark as completed checkbox
- Create button

### Tasks Section:
- Filter buttons (All / Pending / Completed)
- Refresh and Health Check buttons
- Task cards with:
  - Task title and ID
  - Description
  - Created/updated timestamps
  - Action buttons (Mark Complete, Edit, Delete)

### API Response:
- Shows JSON response from every API call
- Helps debug and understand what's happening

---

## How to Test CRUD:

### Create (C):
1. Fill in "Title" field
2. Optionally add description
3. Click "Create Task"
4. ✅ See task appear below!

### Read (R):
1. Click "🔄 Refresh Tasks"
2. View all tasks
3. Use filters to see pending/completed only
4. Click on any task card to see details

### Update (U):
1. Click "✏️ Edit" on any task
2. Enter new title/description
3. Or click "Mark Complete/Pending" toggle
4. ✅ See task update instantly!

### Delete (D):
1. Click "🗑️ Delete" on any task
2. Confirm deletion
3. ✅ Task removed!

---

## Optional: Serve with HTTP Server

If you want to serve it properly (not required):

```bash
cd /Users/dgolani/Documents/AI_Studio/backend/frontend
python3 serve.py
```

Then open: http://localhost:3000

---

## Troubleshooting:

### "API not responding"?
- Check if backend is running:
  ```bash
  curl https://zestfully-chalky-nikia.ngrok-free.dev/health
  ```
- Click "❤️ Health Check" button in the frontend

### "Can't create tasks"?
- Make sure the backend API URL is correct
- Check the API Response box for error messages

### Want to test a different backend?
- Click "Change URL" button
- Enter new backend URL
- Frontend will reconnect automatically

---

## Tech Stack:

- **Pure HTML/CSS/JavaScript** - No frameworks, no build step
- **Vanilla JS** - Works everywhere
- **Responsive Design** - Works on mobile too
- **Beautiful UI** - Gradient backgrounds, smooth animations
- **Real-time Updates** - Instant feedback on all actions

---

## Files:

```
frontend/
├── index.html    - Main frontend (this is all you need!)
├── serve.py      - Optional HTTP server
└── README.md     - This file
```

---

## Pro Tips:

💡 **Bookmark** the index.html file for quick access  
💡 **Keep browser console open** (F12) to see network requests  
💡 **Use filters** to organize tasks by status  
💡 **API Response box** shows what's happening behind the scenes  

---

**Enjoy testing your backend!** 🚀

*The frontend is completely standalone - no installation, no dependencies, just open and use!*

