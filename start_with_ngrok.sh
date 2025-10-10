#!/bin/bash

echo ""
echo "=========================================================="
echo "🚀 Starting AI Studio Backend with Database + Ngrok"
echo "=========================================================="
echo ""

# Stop any existing servers on port 8000
echo "🛑 Stopping any existing servers..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

# Kill existing ngrok tunnels
echo "🛑 Closing existing ngrok tunnels..."
pkill -f ngrok 2>/dev/null || true
sleep 2

# Start the server in background
cd /Users/dgolani/Documents/AI_Studio/backend
source venv/bin/activate

echo "🚀 Starting server..."
python api_with_db_and_ngrok.py > server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to initialize..."
sleep 5

# Check if server started successfully
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Server started successfully!"
else
    echo "❌ Server failed to start. Check server.log for details"
    exit 1
fi

# Display server information
echo ""
echo "=========================================================="
echo "✅ AI Studio Backend is LIVE!"
echo "=========================================================="
echo ""
echo "📍 Local URL:     http://localhost:8000"
echo "📚 API Docs:      http://localhost:8000/docs"
echo "❤️  Health Check:  http://localhost:8000/health"
echo "💾 Database:      SQLite (ai_studio.db)"
echo ""

# Check for ngrok status
if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
    PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data['tunnels'] else 'none')" 2>/dev/null)
    
    if [ "$PUBLIC_URL" != "none" ] && [ -n "$PUBLIC_URL" ]; then
        echo "🌍 Public URL:    $PUBLIC_URL"
        echo "   (Note: This URL may be for port 8080, not 8000)"
        echo ""
    fi
fi

echo "=========================================================="
echo ""
echo "💡 To get a public URL for port 8000:"
echo "   1. Sign up at https://ngrok.com (free)"
echo "   2. Get your auth token"
echo "   3. Run: ngrok http 8000"
echo ""
echo "📖 Test the API: sh test_database_crud.sh"
echo "🛑 To stop: kill $SERVER_PID"
echo ""
echo "Server PID: $SERVER_PID (running in background)"
echo "Server logs: tail -f server.log"
echo ""

