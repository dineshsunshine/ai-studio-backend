# 🔑 Ngrok Account Setup Guide

## Overview

This guide explains how to use your ngrok account with the AI Studio backend to get better performance, reliability, and a static domain.

---

## 🎁 Benefits of Using Your Ngrok Account

| Feature | Without Account | With Account |
|---------|----------------|--------------|
| **Domain** | Random URL each time | Static, permanent URL ✅ |
| **Rate Limits** | Very limited | Much higher ✅ |
| **Session Duration** | 2 hours max | 8+ hours ✅ |
| **Bandwidth** | Limited | Higher limits ✅ |
| **Monitoring** | None | Dashboard analytics ✅ |
| **Support** | None | Email support ✅ |

---

## 📋 Setup Steps

### Step 1: Get Your Auth Token

1. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
2. Sign in to your account
3. Copy your auth token (format: `2abc123DEF456_7gHiJkLmNoPqRsTuVwXyZ`)

### Step 2: Add Token to .env File

Your `.env` file has been created at:
```
/Users/dgolani/Documents/AI_Studio/backend/.env
```

**Edit the file** and replace this line:
```bash
NGROK_AUTH_TOKEN=YOUR_NGROK_AUTH_TOKEN_HERE
```

With your actual token:
```bash
NGROK_AUTH_TOKEN=2abc123DEF456_7gHiJkLmNoPqRsTuVwXyZ
```

#### Quick Edit Command:
```bash
nano /Users/dgolani/Documents/AI_Studio/backend/.env
```

Or use your favorite editor (VSCode, Sublime Text, etc.)

### Step 3: Save the File

After adding your token, save the file:
- In nano: Press `Ctrl+X`, then `Y`, then `Enter`
- In other editors: Just save normally

### Step 4: Start Everything

Use the convenient startup script:

```bash
cd /Users/dgolani/Documents/AI_Studio/backend
./start_everything.sh
```

Or manually:

```bash
# Kill any existing processes
lsof -ti:8888 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
pkill -f ngrok 2>/dev/null

# Start reverse proxy (includes ngrok)
cd /Users/dgolani/Documents/AI_Studio/backend
source venv/bin/activate
python reverse_proxy.py &

# Start backend
python api_with_db_and_ngrok.py &
```

---

## 🌐 Your Static Domain

Once you've added your auth token, this URL will be **yours permanently**:

```
https://zestfully-chalky-nikia.ngrok-free.dev
```

### Your API Endpoints:

| Service | URL |
|---------|-----|
| API Documentation | `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs` |
| Models API | `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/` |
| Looks API | `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/looks/` |
| Frontend | `https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/` |
| SampleAppGpt | `https://zestfully-chalky-nikia.ngrok-free.dev/SampleAppGpt/` |

---

## 🔍 Verifying It's Working

### Check if ngrok is using your account:

1. **Check the logs:**
   ```bash
   tail -f /tmp/reverse_proxy.log
   ```

2. **Look for these indicators:**
   - ✅ Should show your domain: `zestfully-chalky-nikia.ngrok-free.dev`
   - ✅ Should NOT show errors about rate limits
   - ✅ Should connect successfully

3. **Visit your ngrok dashboard:**
   - Go to: https://dashboard.ngrok.com
   - Click "Endpoints" or "Status"
   - You should see your active tunnel listed

### Test the API:

```bash
# Test health endpoint
curl https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/health

# Should return:
# {"status":"healthy"}
```

---

## 📊 Monitoring Your Usage

### View Active Tunnels:
```bash
# In your browser
https://dashboard.ngrok.com/endpoints

# Shows:
# - Active connections
# - Request count
# - Data transferred
# - Uptime
```

### View Logs:
```bash
# Reverse proxy logs (includes ngrok startup)
tail -f /tmp/reverse_proxy.log

# Backend API logs
tail -f /tmp/backend.log
```

---

## 🛠️ Troubleshooting

### Problem: "Authentication failed" error

**Solution:**
1. Verify your token is correct in `.env`
2. No extra spaces or quotes around the token
3. Token should be on a single line

### Problem: "Endpoint already online" (ERR_NGROK_334)

**Solution:**
```bash
# Kill all ngrok processes
pkill -f ngrok

# Wait a few seconds
sleep 3

# Restart
./start_everything.sh
```

### Problem: Token not being read

**Solution:**
1. Check `.env` file exists:
   ```bash
   ls -la /Users/dgolani/Documents/AI_Studio/backend/.env
   ```

2. Check the token is set correctly:
   ```bash
   grep NGROK_AUTH_TOKEN /Users/dgolani/Documents/AI_Studio/backend/.env
   ```

3. Make sure there are no syntax errors in `.env`

### Problem: Still getting random URLs

**Solution:**
1. Your token must be set correctly
2. The `NGROK_DOMAIN` must match your reserved domain
3. Your account must have a reserved domain set up
4. Check your ngrok dashboard to confirm the domain

---

## 🎯 Advanced Features (with Paid Plans)

If you upgrade your ngrok account, you get additional features:

### Free Plan (what you have):
- ✅ 1 static domain
- ✅ 1 active tunnel
- ✅ Basic analytics
- ✅ 40 connections/minute

### Personal Plan ($8/month):
- ✅ 3 static domains
- ✅ 3 active tunnels simultaneously
- ✅ Custom domains
- ✅ IP restrictions
- ✅ 120 connections/minute

### Pro Plan ($20/month):
- ✅ 10 static domains
- ✅ 10 active tunnels
- ✅ Advanced analytics
- ✅ SSO
- ✅ 600 connections/minute

For most development work, the **free plan is perfectly fine!**

---

## 📚 Additional Resources

### Official Ngrok Documentation:
- Getting Started: https://ngrok.com/docs/getting-started
- Dashboard: https://dashboard.ngrok.com
- API Reference: https://ngrok.com/docs/api

### Your Backend Documentation:
- Complete Guide: `COMPLETE_NGROK_BYPASS_SOLUTION.md`
- Startup Script: `start_everything.sh`
- Reverse Proxy Setup: `NGROK_MULTI_PROJECT_SETUP.md`

---

## 🆘 Getting Help

### If something doesn't work:

1. **Check the logs:**
   ```bash
   tail -f /tmp/reverse_proxy.log
   tail -f /tmp/backend.log
   ```

2. **Verify processes are running:**
   ```bash
   lsof -ti:8888  # Should show reverse proxy
   lsof -ti:8000  # Should show backend
   ```

3. **Test locally first:**
   ```bash
   curl http://localhost:8888/AIStudio/api/v1/health
   ```

4. **Then test through ngrok:**
   ```bash
   curl https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/health
   ```

### Still stuck?

- Check ngrok dashboard: https://dashboard.ngrok.com
- View ngrok status page: https://status.ngrok.com
- Contact ngrok support (if you have a paid plan)

---

## ✅ Quick Checklist

Before you start, make sure:

- [ ] You have your ngrok auth token
- [ ] Token is added to `.env` file
- [ ] `.env` file is in the correct location
- [ ] No syntax errors in `.env`
- [ ] No other processes using ports 8888 or 8000
- [ ] Virtual environment is activated
- [ ] All dependencies are installed

Then run:
```bash
./start_everything.sh
```

And you're done! 🎉

---

## 🎉 Success!

Once everything is running, you should see:

```
✨ STARTUP COMPLETE! ✨

🌐 Your APIs are now available at:
   https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs
```

**This URL is now yours permanently!** Share it with your frontend developers and start building! 🚀

