#!/bin/bash
#
# Start Celery Worker for Video Generation
#
# This script starts the background worker that processes video generation jobs.
# Make sure Redis is running before starting the worker!
#

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎬 Starting Celery Worker for Video Generation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Redis is running
if ! nc -z localhost 6379 2>/dev/null; then
    echo "❌ ERROR: Redis is not running on localhost:6379"
    echo ""
    echo "Please start Redis first:"
    echo "  brew install redis   # Install Redis (macOS)"
    echo "  redis-server         # Start Redis"
    echo ""
    exit 1
fi

echo "✅ Redis is running"
echo ""

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  WARNING: GOOGLE_API_KEY is not set"
    echo "   Video generation will fail without Google API key"
    echo "   Add it to your .env file or export it:"
    echo "   export GOOGLE_API_KEY=your_api_key"
    echo ""
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if celery is installed
if ! command -v celery &> /dev/null; then
    echo "❌ ERROR: Celery is not installed"
    echo "   Please install: pip install -r requirements.txt"
    exit 1
fi

echo "🚀 Starting Celery worker..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start Celery worker
celery -A app.core.celery_app worker --loglevel=info --concurrency=2

