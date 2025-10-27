# 🚀 Step-by-Step Guide: Run Both Projects with ONE Ngrok

## 📋 What You'll Achieve

After following these steps:
- ✅ AI Studio Backend running on `localhost:8000`
- ✅ SampleAppGpt running on `localhost:8080`
- ✅ ONE ngrok URL accessing both projects
- ✅ AI Studio at: `https://your-url.ngrok.io/backend`
- ✅ SampleAppGpt at: `https://your-url.ngrok.io/app`

---

## 🎯 Step-by-Step Instructions

### **Step 1: Stop All Existing Processes**

Open a terminal and run:

```bash
# Stop any existing ngrok
pkill ngrok

# Stop any existing servers on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Stop any existing servers on port 8888 (proxy)
lsof -ti:8888 | xargs kill -9 2>/dev/null || true
```

**Why?** Clean slate - removes any conflicting processes.

---

### **Step 2: Start AI Studio Backend**

**Terminal 1 (AI Studio):**

```bash
cd /Users/dgolani/Documents/AI_Studio/backend
source venv/bin/activate
python api_with_db_and_ngrok.py
```

**Expected Output:**
```
🚀 Starting AI Studio Backend...
INFO: Uvicorn running on http://0.0.0.0:8000
```

**✅ Checkpoint:** 
- Leave this terminal open
- Backend is running on port 8000
- Test: Open http://localhost:8000/health in browser

---

### **Step 3: Start Your SampleAppGpt Application**

**Terminal 2 (SampleAppGpt):**

```bash
cd ~/SampleAppGpt
# Run your app's start command here
# Example: npm start, python app.py, etc.
# Make sure it runs on port 8080
```

**✅ Checkpoint:**
- Leave this terminal open
- Your app is running on port 8080
- Test: Open http://localhost:8080 in browser

---

### **Step 4: Start Reverse Proxy**

**Terminal 3 (Reverse Proxy):**

```bash
cd /Users/dgolani/Documents/AI_Studio/backend
python3 reverse_proxy.py
```

**Expected Output:**
```
🔀 Reverse Proxy Server
📍 Proxy running on: http://localhost:8888

📋 Route Configuration:
   /backend        → localhost:8000
   /app            → localhost:8080
```

**✅ Checkpoint:**
- Leave this terminal open
- Proxy is routing traffic on port 8888
- Test routes:
  ```bash
  curl http://localhost:8888/backend/health
  curl http://localhost:8888/app/
  ```

---

### **Step 5: Start Ngrok (Your Terminal)**

**Terminal 4 (Can be anywhere - even in ~/SampleAppGpt):**

```bash
# You can run this from ANY directory
cd ~/SampleAppGpt  # or wherever you want

# Start ngrok pointing to the proxy
ngrok http 8888
```

**Expected Output:**
```
ngrok by @inconshreveable

Session Status    online
Forwarding        https://abc123.ngrok-free.app -> http://localhost:8888
```

**✅ Checkpoint:**
- Copy the "Forwarding" URL (e.g., `https://abc123.ngrok-free.app`)
- This ONE URL now serves BOTH projects!

---

### **Step 6: Test Your Setup**

**Replace `YOUR-URL` with your actual ngrok URL from Step 5.**

#### Test AI Studio Backend:

Open in browser or use curl:
```bash
# Health check
curl https://YOUR-URL.ngrok-free.app/backend/health

# API docs (open in browser)
https://YOUR-URL.ngrok-free.app/backend/docs

# Tasks endpoint
curl https://YOUR-URL.ngrok-free.app/backend/tasks
```

#### Test SampleAppGpt:

```bash
# Your app's home
curl https://YOUR-URL.ngrok-free.app/app/

# Or open in browser
https://YOUR-URL.ngrok-free.app/app/
```

#### Test Route Map:

```bash
# See all available routes
https://YOUR-URL.ngrok-free.app/
```

---

## 🎨 Summary of What's Running

| Terminal | Service | Port | Command |
|----------|---------|------|---------|
| Terminal 1 | AI Studio Backend | 8000 | `python api_with_db_and_ngrok.py` |
| Terminal 2 | SampleAppGpt | 8080 | Your app's start command |
| Terminal 3 | Reverse Proxy | 8888 | `python3 reverse_proxy.py` |
| Terminal 4 | Ngrok | - | `ngrok http 8888` |

---

## 🌐 URL Structure

Once ngrok is running, you get ONE URL that routes to both:

```
https://abc123.ngrok-free.app/
├── /backend/*  → AI Studio Backend (port 8000)
│   ├── /backend/health
│   ├── /backend/tasks
│   └── /backend/docs
│
└── /app/*      → SampleAppGpt (port 8080)
    ├── /app/
    └── /app/api/...
```

---

## 🔧 Troubleshooting

### Issue: "Port 8000 already in use"

**Solution:**
```bash
lsof -ti:8000 | xargs kill -9
```
Then restart AI Studio Backend (Step 2)

---

### Issue: "Port 8080 already in use"

**Solution:**
```bash
lsof -ti:8080 | xargs kill -9
```
Then restart SampleAppGpt (Step 3)

---

### Issue: "Port 8888 already in use"

**Solution:**
```bash
lsof -ti:8888 | xargs kill -9
```
Then restart Reverse Proxy (Step 4)

---

### Issue: "Ngrok already online" error

**Solution:**
```bash
pkill ngrok
```
Then restart Ngrok (Step 5)

---

### Issue: Routes not working

**Check each service individually:**

```bash
# Test backend directly
curl http://localhost:8000/health

# Test your app directly
curl http://localhost:8080/

# Test through proxy
curl http://localhost:8888/backend/health
curl http://localhost:8888/app/

# Test through ngrok
curl https://YOUR-URL.ngrok-free.app/backend/health
```

Find which step fails and restart that service.

---

## 💡 Pro Tips

### Tip 1: Keep Terminals Organized

Use terminal tabs or split screens:
```
┌─────────────┬─────────────┐
│ AI Studio   │ SampleAppGpt│
├─────────────┼─────────────┤
│ Proxy       │ Ngrok       │
└─────────────┴─────────────┘
```

---

### Tip 2: Create a Startup Script

Save time by creating `start_all.sh`:

```bash
#!/bin/bash

echo "🚀 Starting all services..."

# Start AI Studio Backend
cd /Users/dgolani/Documents/AI_Studio/backend
source venv/bin/activate
python api_with_db_and_ngrok.py > /tmp/backend.log 2>&1 &

# Wait for backend to start
sleep 3

# Start Reverse Proxy
python3 reverse_proxy.py > /tmp/proxy.log 2>&1 &

# Wait for proxy to start
sleep 2

echo "✅ Services started!"
echo "📍 Backend: http://localhost:8000"
echo "📍 Proxy: http://localhost:8888"
echo ""
echo "🎯 Next steps:"
echo "1. Start your SampleAppGpt on port 8080"
echo "2. Run: ngrok http 8888"
```

Make it executable:
```bash
chmod +x start_all.sh
./start_all.sh
```

---

### Tip 3: Check What's Running

Quick command to see all services:
```bash
ps aux | grep -E "api_with_db|reverse_proxy|ngrok" | grep -v grep
```

---

### Tip 4: View Proxy Logs

See what requests are being routed:
```bash
tail -f /tmp/proxy.log
```

---

## 🎯 Quick Reference Card

**Start Everything:**
```bash
# Terminal 1: AI Studio
cd /Users/dgolani/Documents/AI_Studio/backend && source venv/bin/activate && python api_with_db_and_ngrok.py

# Terminal 2: Your App
cd ~/SampleAppGpt && [your-app-command]

# Terminal 3: Proxy
cd /Users/dgolani/Documents/AI_Studio/backend && python3 reverse_proxy.py

# Terminal 4: Ngrok
ngrok http 8888
```

**URLs:**
```
Local Backend:    http://localhost:8000
Local App:        http://localhost:8080
Local Proxy:      http://localhost:8888

Public Backend:   https://your-url.ngrok.io/backend
Public App:       https://your-url.ngrok.io/app
```

**Stop Everything:**
```bash
pkill ngrok
lsof -ti:8000 | xargs kill -9
lsof -ti:8080 | xargs kill -9
lsof -ti:8888 | xargs kill -9
```

---

## ✅ Checklist

Before starting, make sure you have:
- [ ] Python 3 installed
- [ ] AI Studio backend set up (`venv` exists)
- [ ] SampleAppGpt ready to run on port 8080
- [ ] Ngrok installed
- [ ] 4 terminal windows ready

After setup:
- [ ] Terminal 1: Backend running (port 8000)
- [ ] Terminal 2: SampleAppGpt running (port 8080)
- [ ] Terminal 3: Proxy running (port 8888)
- [ ] Terminal 4: Ngrok running (shows forwarding URL)
- [ ] Can access: https://url/backend/health
- [ ] Can access: https://url/app/

---

## 🎊 You're Done!

Both projects are now accessible through ONE ngrok URL!

**Share these URLs:**
- Backend API: `https://your-url.ngrok.io/backend`
- Your App: `https://your-url.ngrok.io/app`

**Need to stop?**
Press `Ctrl+C` in each terminal, or run:
```bash
pkill ngrok
lsof -ti:8000,8080,8888 | xargs kill -9
```

---

*For detailed troubleshooting, see: NGROK_MULTI_PROJECT_SETUP.md*


