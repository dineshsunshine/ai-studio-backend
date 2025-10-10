# 🔀 Multiple Projects with ONE Ngrok Tunnel

## ✅ Solution to All Your Requirements!

This setup allows you to:
1. ✅ Run **ONE ngrok** instance serving multiple projects
2. ✅ Each project has its **own path/directory** in the URL
3. ✅ Run ngrok from **your own terminal**

---

## 🎯 How It Works

```
Your Terminal: ngrok http 8888
                    ↓
            Reverse Proxy (Port 8888)
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
  localhost:8000          localhost:8080
  (AI Studio Backend)     (Your App)
```

**One ngrok URL, multiple projects!**

---

## 🚀 Step-by-Step Setup

### Step 1: Stop All Existing Ngrok Tunnels

From any terminal:
```bash
pkill ngrok
```

### Step 2: Start the Reverse Proxy

From THIS project's backend directory:
```bash
cd /Users/dgolani/Documents/AI_Studio/backend
python3 reverse_proxy.py
```

**Keep this terminal open!** The proxy will run here.

### Step 3: Start Your Backend Services

Make sure both services are running:

**AI Studio Backend (Port 8000):**
```bash
# If not already running:
cd /Users/dgolani/Documents/AI_Studio/backend
source venv/bin/activate
python api_with_db_and_ngrok.py
```

**Your Other App (Port 8080):**
```bash
# Start your app on port 8080 as usual
# (whatever command you normally use)
```

### Step 4: Start Ngrok from YOUR Terminal

**From ANY directory you want** (e.g., your app's directory):
```bash
ngrok http 8888
```

**That's it!** ✨

---

## 🌐 Accessing Your Projects

Once ngrok starts, you'll get ONE public URL like:
```
https://abc123.ngrok-free.app
```

### Access AI Studio Backend:
```
https://abc123.ngrok-free.app/backend/health
https://abc123.ngrok-free.app/backend/tasks
https://abc123.ngrok-free.app/backend/docs
```

### Access Your Other App:
```
https://abc123.ngrok-free.app/app/
https://abc123.ngrok-free.app/app/api/...
```

### Root URL (Help Page):
```
https://abc123.ngrok-free.app/
```
Shows a nice help page with all available routes!

---

## 📋 URL Path Structure

| URL Path | Goes To | Description |
|----------|---------|-------------|
| `/backend/*` | Port 8000 | AI Studio Backend API |
| `/app/*` | Port 8080 | Your Application |
| `/` | Proxy help | Shows route map |

**Examples:**

```
https://your-url.ngrok.io/backend/health    → http://localhost:8000/health
https://your-url.ngrok.io/backend/tasks     → http://localhost:8000/tasks
https://your-url.ngrok.io/app/             → http://localhost:8080/
https://your-url.ngrok.io/app/api/users    → http://localhost:8080/api/users
```

---

## 🔧 Configuration

To add more projects or change ports, edit `reverse_proxy.py`:

```python
ROUTES = {
    '/backend': 8000,    # AI Studio Backend
    '/app': 8080,        # Your application
    '/other': 3000,      # Add more projects here!
}
```

---

## 🧪 Testing

### 1. Test Locally First:

```bash
# Test backend through proxy
curl http://localhost:8888/backend/health

# Test your app through proxy  
curl http://localhost:8888/app/
```

### 2. Test with Ngrok:

Once ngrok is running, test with the public URL:
```bash
curl https://your-url.ngrok.io/backend/health
curl https://your-url.ngrok.io/app/
```

---

## 📊 Complete Terminal Setup

**Terminal 1 - Reverse Proxy:**
```bash
cd /Users/dgolani/Documents/AI_Studio/backend
python3 reverse_proxy.py
```

**Terminal 2 - AI Studio Backend:**
```bash
cd /Users/dgolani/Documents/AI_Studio/backend
source venv/bin/activate
python api_with_db_and_ngrok.py
```

**Terminal 3 - Your App:**
```bash
cd /path/to/your/app
# Your app's start command (on port 8080)
```

**Terminal 4 (YOUR TERMINAL) - Ngrok:**
```bash
cd /wherever/you/want
ngrok http 8888
```

---

## 🎨 Frontend Integration

Update your frontend to use the new paths:

**For AI Studio Frontend:**
```javascript
// OLD
const API_URL = 'https://abc123.ngrok.io';

// NEW
const API_URL = 'https://abc123.ngrok.io/backend';
```

**For Your App's Frontend:**
```javascript
const API_URL = 'https://abc123.ngrok.io/app';
```

---

## 💡 Pro Tips

### 1. Bookmark the Route Map

Open `http://localhost:8888/` in your browser to see all available routes!

### 2. Check Proxy Logs

The proxy terminal shows all requests being routed:
```
[PROXY] 127.0.0.1 - "GET /backend/health HTTP/1.1" 200 -
[PROXY] 127.0.0.1 - "GET /app/api/users HTTP/1.1" 200 -
```

### 3. Add More Projects Anytime

Just edit the `ROUTES` dictionary in `reverse_proxy.py` and restart!

### 4. Run from Startup Script

Create a simple startup script to run everything:

```bash
#!/bin/bash
# start_all.sh

# Start proxy in background
cd /Users/dgolani/Documents/AI_Studio/backend
python3 reverse_proxy.py &

# Start backend in background  
python api_with_db_and_ngrok.py &

# Start your app
cd /path/to/your/app
your-app-command

# Then manually run: ngrok http 8888
```

---

## 🔍 Troubleshooting

### "Connection refused" errors?

**Check if services are running:**
```bash
# Test backend
curl http://localhost:8000/health

# Test your app
curl http://localhost:8080/

# Test proxy
curl http://localhost:8888/backend/health
```

### Proxy not starting?

**Port 8888 might be in use:**
```bash
lsof -ti:8888 | xargs kill -9
```

Then restart the proxy.

### Need to change proxy port?

Edit `reverse_proxy.py` and change:
```python
PROXY_PORT = 8888  # Change to your preferred port
```

Then update ngrok command: `ngrok http YOUR_PORT`

---

## ✅ Summary

**Before (Problem):**
```
ngrok http 8000  ← Only one tunnel allowed!
ngrok http 8080  ← Error: already online
```

**After (Solution):**
```
python3 reverse_proxy.py     ← Routes traffic
ngrok http 8888              ← ONE tunnel, multiple projects!

Access:
  https://url.ngrok.io/backend  → Port 8000
  https://url.ngrok.io/app      → Port 8080
```

---

## 🎯 Benefits

✅ **One Ngrok Tunnel** - No more "already online" errors  
✅ **Multiple Projects** - Route by URL path  
✅ **Your Terminal** - Run ngrok wherever you want  
✅ **Clean URLs** - Each project has its own path  
✅ **Easy to Extend** - Add more projects anytime  
✅ **Free Tier** - Works with ngrok free account  

---

## 🚀 Quick Start Checklist

- [ ] Kill existing ngrok: `pkill ngrok`
- [ ] Start reverse proxy: `python3 reverse_proxy.py`
- [ ] Start backend on port 8000
- [ ] Start your app on port 8080
- [ ] From YOUR terminal: `ngrok http 8888`
- [ ] Test: `https://your-url.ngrok.io/backend/health`
- [ ] Test: `https://your-url.ngrok.io/app/`
- [ ] Update frontend URLs to include `/backend` or `/app`

---

**You're all set!** 🎉

*Now you can run ONE ngrok tunnel and access all your projects through different URL paths!*

