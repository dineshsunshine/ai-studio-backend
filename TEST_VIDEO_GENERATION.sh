#!/bin/bash
#
# Quick Test Script for Video Generation
#
# This script helps you test the video generation system.
# You need a JWT token to test.
#

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🧪 Video Generation Test Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if JWT token is provided
if [ -z "$1" ]; then
    echo "❌ ERROR: JWT token required"
    echo ""
    echo "Usage:"
    echo "  ./TEST_VIDEO_GENERATION.sh YOUR_JWT_TOKEN"
    echo ""
    echo "To get a JWT token:"
    echo "  1. Login to your frontend"
    echo "  2. Copy the JWT token from localStorage"
    echo "  3. Or use curl to login and get the token"
    echo ""
    exit 1
fi

JWT_TOKEN=$1
BASE_URL="https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio"

echo "🔍 Testing Video Generation System..."
echo ""

# Test 1: Check health
echo "1️⃣  Testing health endpoint..."
HEALTH=$(curl -s "${BASE_URL}/api/v1/health" -H "ngrok-skip-browser-warning: true")
echo "   Response: $HEALTH"
echo ""

# Test 2: Check token balance
echo "2️⃣  Checking token balance..."
SUBSCRIPTION=$(curl -s "${BASE_URL}/api/v1/subscription/info" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "ngrok-skip-browser-warning: true")
echo "   Subscription: $SUBSCRIPTION"
echo ""

# Test 3: Create video generation job
echo "3️⃣  Creating video generation job..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v1/video-jobs" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "ngrok-skip-browser-warning: true" \
  -F "prompt=A cinematic shot of a beautiful sunset over mountains" \
  -F "model=veo-3.1-fast-generate-preview" \
  -F "resolution=1080p" \
  -F "aspectRatio=16:9" \
  -F "durationSeconds=4")

echo "   Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Extract job ID
JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$JOB_ID" ]; then
    echo "❌ Failed to create job. Check the error above."
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Job created successfully!"
echo ""
echo "Job ID: $JOB_ID"
echo ""
echo "📊 Monitor progress at:"
echo "   ${BASE_URL}/video-monitor"
echo ""
echo "🔍 Check job status:"
echo "   curl ${BASE_URL}/api/v1/video-jobs/${JOB_ID} \\"
echo "     -H \"Authorization: Bearer ${JWT_TOKEN}\" \\"
echo "     -H \"ngrok-skip-browser-warning: true\""
echo ""
echo "⏳ Video generation takes 3-10 minutes..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

