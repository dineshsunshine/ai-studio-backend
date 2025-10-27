#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                      ║${NC}"
echo -e "${BLUE}║                    Testing Models API Endpoints                      ║${NC}"
echo -e "${BLUE}║                                                                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"

BASE_URL="http://localhost:8000/api/v1/models"

# Test 1: Get all models (should be empty initially)
echo -e "\n${GREEN}1. GET All Models (initial)${NC}"
curl -s -X GET "$BASE_URL/" | python3 -m json.tool

# Test 2: Create a test image
echo -e "\n${GREEN}2. Creating test image...${NC}"
python3 << 'EOF'
from PIL import Image, ImageDraw, ImageFont

# Create a test image
img = Image.new('RGB', (400, 600), color=(200, 200, 250))
draw = ImageDraw.Draw(img)

# Add text
text = "Test Model\nImage"
bbox = draw.textbbox((0, 0), text)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
position = ((400 - text_width) // 2, (600 - text_height) // 2)
draw.text(position, text, fill=(50, 50, 50))

# Save
img.save('/tmp/test_model_image.jpg')
print("✅ Test image created at /tmp/test_model_image.jpg")
EOF

# Test 3: Upload a model
echo -e "\n${GREEN}3. POST Upload Model${NC}"
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/upload" \
  -F "name=Test Model Upload" \
  -F "image=@/tmp/test_model_image.jpg")

echo "$UPLOAD_RESPONSE" | python3 -m json.tool

# Extract model ID from response
MODEL_ID=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

# Test 4: Generate an AI model
echo -e "\n${GREEN}4. POST Generate AI Model${NC}"
GENERATE_RESPONSE=$(curl -s -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Generated Model",
    "prompt_details": "wearing casual summer outfit, friendly smile, short hair"
  }')

echo "$GENERATE_RESPONSE" | python3 -m json.tool

# Extract AI model ID
AI_MODEL_ID=$(echo "$GENERATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

# Test 5: Get all models (should have 2 now)
echo -e "\n${GREEN}5. GET All Models (after uploads)${NC}"
curl -s -X GET "$BASE_URL/" | python3 -m json.tool

# Test 6: Get single model
if [ -n "$MODEL_ID" ]; then
    echo -e "\n${GREEN}6. GET Single Model (ID: $MODEL_ID)${NC}"
    curl -s -X GET "$BASE_URL/$MODEL_ID" | python3 -m json.tool
fi

# Test 7: Delete model
if [ -n "$MODEL_ID" ]; then
    echo -e "\n${GREEN}7. DELETE Model (ID: $MODEL_ID)${NC}"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/$MODEL_ID")
    if [ "$HTTP_CODE" = "204" ]; then
        echo -e "${GREEN}✅ Model deleted successfully (204 No Content)${NC}"
    else
        echo -e "${RED}❌ Failed to delete model (HTTP $HTTP_CODE)${NC}"
    fi
fi

# Test 8: Verify deletion
echo -e "\n${GREEN}8. GET All Models (after deletion)${NC}"
curl -s -X GET "$BASE_URL/" | python3 -m json.tool

# Cleanup
if [ -n "$AI_MODEL_ID" ]; then
    echo -e "\n${GREEN}9. Cleanup: Deleting AI model${NC}"
    curl -s -o /dev/null -X DELETE "$BASE_URL/$AI_MODEL_ID"
    echo -e "${GREEN}✅ Cleanup complete${NC}"
fi

echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                      ║${NC}"
echo -e "${BLUE}║                       Testing Complete! ✅                            ║${NC}"
echo -e "${BLUE}║                                                                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"


