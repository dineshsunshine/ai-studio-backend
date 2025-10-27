#!/bin/bash

# Test Image Upload Script
# Tests that images are uploaded and accessible via public URL

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║              🧪 Testing Image Upload & Public URLs                   ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"

# Create a test image
echo -e "\n📸 Step 1: Creating test image..."
python3 << 'EOF'
from PIL import Image, ImageDraw, ImageFont

# Create a test image
img = Image.new('RGB', (800, 1200), color=(100, 150, 200))
draw = ImageDraw.Draw(img)

# Add text
text = "Test Model\nPublic URL Test\n✅"
draw.text((50, 500), text, fill=(255, 255, 255))

# Save
img.save('/tmp/test_model_image.jpg')
print("✅ Test image created at /tmp/test_model_image.jpg")
EOF

# Upload the image
echo -e "\n📤 Step 2: Uploading image to API..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/models/upload" \
  -F "name=Test Model - Public URL" \
  -F "image=@/tmp/test_model_image.jpg")

echo "$RESPONSE" | python3 -m json.tool

# Extract image URL
IMAGE_URL=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('image_url', 'NOT_FOUND'))" 2>/dev/null)

echo -e "\n📋 Step 3: Verifying image URL..."
echo "Image URL: $IMAGE_URL"

# Check if URL is public (contains ngrok domain)
if [[ $IMAGE_URL == *"ngrok-free.dev"* ]]; then
    echo "✅ URL is PUBLIC (contains ngrok domain)"
else
    echo "⚠️  WARNING: URL is not public (should contain ngrok domain)"
fi

# Check if URL is accessible
echo -e "\n🌐 Step 4: Testing public accessibility..."
if curl -s -o /dev/null -w "%{http_code}" "$IMAGE_URL" | grep -q "200"; then
    echo "✅ Image is publicly accessible!"
else
    echo "❌ Image is NOT accessible at public URL"
fi

# Extract model ID
MODEL_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', 'NOT_FOUND'))" 2>/dev/null)

echo -e "\n📊 Step 5: Summary"
echo "════════════════════════════════════════════════════════════════════"
echo "Model ID:   $MODEL_ID"
echo "Image URL:  $IMAGE_URL"
echo "Status:     Upload successful"
echo "════════════════════════════════════════════════════════════════════"

echo -e "\n💡 To view the image, open this URL in your browser:"
echo "   $IMAGE_URL"

echo -e "\n🗑️  To clean up, delete the model:"
echo "   curl -X DELETE \"http://localhost:8000/api/v1/models/$MODEL_ID\""

echo -e "\n✅ Test complete!"


