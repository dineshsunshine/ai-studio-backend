#!/bin/bash

# ============================================
# AI Studio - Complete Startup Script
# ============================================
# This script starts:
# 1. Reverse Proxy (with ngrok on port 8888)
# 2. AI Studio Backend (port 8000)
# ============================================

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║              🚀 STARTING AI STUDIO - COMPLETE SETUP                  ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Navigate to backend directory
cd /Users/dgolani/Documents/AI_Studio/backend

# Check if .env file exists and has auth token
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo ""
    echo "Please create .env file first with your ngrok token."
    echo "See instructions above."
    exit 1
fi

if grep -q "YOUR_NGROK_AUTH_TOKEN_HERE" .env; then
    echo "⚠️  WARNING: You haven't set your ngrok auth token yet!"
    echo ""
    echo "Please edit: /Users/dgolani/Documents/AI_Studio/backend/.env"
    echo "And replace YOUR_NGROK_AUTH_TOKEN_HERE with your actual token"
    echo ""
    echo "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧹 STEP 1: Cleaning up any existing processes..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Kill existing processes
lsof -ti:8888 | xargs kill -9 2>/dev/null && echo "✅ Killed process on port 8888" || echo "ℹ️  No process on port 8888"
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Killed process on port 8000" || echo "ℹ️  No process on port 8000"

# Kill any existing ngrok tunnels
pkill -f ngrok 2>/dev/null && echo "✅ Killed existing ngrok processes" || echo "ℹ️  No ngrok processes running"

sleep 2

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 STEP 2: Starting Reverse Proxy (with ngrok)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Activate virtual environment and start reverse proxy
source venv/bin/activate
nohup python reverse_proxy.py > /tmp/reverse_proxy.log 2>&1 &
PROXY_PID=$!

echo "✅ Reverse proxy started (PID: $PROXY_PID)"
echo "📋 Logs: tail -f /tmp/reverse_proxy.log"

sleep 3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 STEP 3: Starting AI Studio Backend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start backend (no need to start ngrok again - reverse proxy already did it)
nohup python api_with_db_and_ngrok.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "📋 Logs: tail -f /tmp/backend.log"

sleep 3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 STEP 4: Verifying services..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sleep 2

# Check if processes are still running
if ps -p $PROXY_PID > /dev/null; then
    echo "✅ Reverse proxy is running"
else
    echo "❌ Reverse proxy failed to start"
    echo "Check logs: tail -f /tmp/reverse_proxy.log"
fi

if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start"
    echo "Check logs: tail -f /tmp/backend.log"
fi

# Check if ports are listening
sleep 1
if lsof -ti:8888 > /dev/null 2>&1; then
    echo "✅ Port 8888 (reverse proxy) is listening"
else
    echo "❌ Port 8888 is not listening"
fi

if lsof -ti:8000 > /dev/null 2>&1; then
    echo "✅ Port 8000 (backend) is listening"
else
    echo "❌ Port 8000 is not listening"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║                    ✨ STARTUP COMPLETE! ✨                           ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Your APIs are now available at:"
echo ""
echo "   📚 API Documentation:"
echo "      https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/docs"
echo ""
echo "   🎨 Models API:"
echo "      https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/models/"
echo ""
echo "   👗 Looks API:"
echo "      https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/api/v1/looks/"
echo ""
echo "   🏠 Frontend:"
echo "      https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio/"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Useful Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   View reverse proxy logs:"
echo "      tail -f /tmp/reverse_proxy.log"
echo ""
echo "   View backend logs:"
echo "      tail -f /tmp/backend.log"
echo ""
echo "   Stop all services:"
echo "      lsof -ti:8888 | xargs kill -9"
echo "      lsof -ti:8000 | xargs kill -9"
echo "      pkill -f ngrok"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 TIP: If SampleAppGpt is running on port 8080, it's also accessible at:"
echo "         https://zestfully-chalky-nikia.ngrok-free.dev/SampleAppGpt/"
echo ""


