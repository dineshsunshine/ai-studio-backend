#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

echo ""
echo "=========================================================="
echo "🧪 Testing AI Studio Backend - Database CRUD Operations"
echo "=========================================================="
echo ""

# Wait for server to be ready
echo "⏳ Waiting for server to be ready..."
sleep 2

# Test 1: Health Check
echo -e "${BLUE}1️⃣  Testing Health Check${NC}"
echo "GET $BASE_URL/health"
curl -s $BASE_URL/health | python3 -m json.tool
echo ""

# Test 2: Create Task 1
echo -e "${BLUE}2️⃣  Creating Task 1 (CREATE)${NC}"
echo "POST $BASE_URL/tasks"
TASK1=$(curl -s -X POST $BASE_URL/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build AI Studio Frontend",
    "description": "Integrate with Google AI Studio",
    "completed": false
  }')
echo "$TASK1" | python3 -m json.tool
TASK1_ID=$(echo "$TASK1" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo -e "${GREEN}✅ Created Task ID: $TASK1_ID${NC}"
echo ""

# Test 3: Create Task 2
echo -e "${BLUE}3️⃣  Creating Task 2 (CREATE)${NC}"
echo "POST $BASE_URL/tasks"
TASK2=$(curl -s -X POST $BASE_URL/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Setup Database",
    "description": "Configure PostgreSQL with SQLAlchemy",
    "completed": true
  }')
echo "$TASK2" | python3 -m json.tool
TASK2_ID=$(echo "$TASK2" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo -e "${GREEN}✅ Created Task ID: $TASK2_ID${NC}"
echo ""

# Test 4: Create Task 3
echo -e "${BLUE}4️⃣  Creating Task 3 (CREATE)${NC}"
echo "POST $BASE_URL/tasks"
TASK3=$(curl -s -X POST $BASE_URL/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Deploy with Ngrok",
    "description": "Enable public URL access",
    "completed": false
  }')
echo "$TASK3" | python3 -m json.tool
TASK3_ID=$(echo "$TASK3" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo -e "${GREEN}✅ Created Task ID: $TASK3_ID${NC}"
echo ""

# Test 5: Get All Tasks (READ)
echo -e "${BLUE}5️⃣  Getting All Tasks (READ)${NC}"
echo "GET $BASE_URL/tasks"
curl -s $BASE_URL/tasks | python3 -m json.tool
echo ""

# Test 6: Get Specific Task (READ)
echo -e "${BLUE}6️⃣  Getting Task #$TASK1_ID (READ)${NC}"
echo "GET $BASE_URL/tasks/$TASK1_ID"
curl -s $BASE_URL/tasks/$TASK1_ID | python3 -m json.tool
echo ""

# Test 7: Update Task (UPDATE)
echo -e "${BLUE}7️⃣  Updating Task #$TASK1_ID (UPDATE)${NC}"
echo "PUT $BASE_URL/tasks/$TASK1_ID"
curl -s -X PUT $BASE_URL/tasks/$TASK1_ID \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build AI Studio Frontend - IN PROGRESS",
    "description": "Integrating with Google AI Studio - 50% done",
    "completed": false
  }' | python3 -m json.tool
echo -e "${GREEN}✅ Task Updated${NC}"
echo ""

# Test 8: Partial Update (UPDATE)
echo -e "${BLUE}8️⃣  Marking Task #$TASK3_ID as Completed (PARTIAL UPDATE)${NC}"
echo "PUT $BASE_URL/tasks/$TASK3_ID"
curl -s -X PUT $BASE_URL/tasks/$TASK3_ID \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }' | python3 -m json.tool
echo -e "${GREEN}✅ Task Marked as Completed${NC}"
echo ""

# Test 9: Filter Completed Tasks
echo -e "${BLUE}9️⃣  Getting Only Completed Tasks (READ with Filter)${NC}"
echo "GET $BASE_URL/tasks?completed=true"
curl -s "$BASE_URL/tasks?completed=true" | python3 -m json.tool
echo ""

# Test 10: Get Statistics
echo -e "${BLUE}🔟 Getting Task Statistics${NC}"
echo "GET $BASE_URL/stats"
curl -s $BASE_URL/stats | python3 -m json.tool
echo ""

# Test 11: Delete Task (DELETE)
echo -e "${BLUE}1️⃣1️⃣  Deleting Task #$TASK2_ID (DELETE)${NC}"
echo "DELETE $BASE_URL/tasks/$TASK2_ID"
curl -s -X DELETE $BASE_URL/tasks/$TASK2_ID
echo -e "${GREEN}✅ Task Deleted${NC}"
echo ""

# Test 12: Verify Deletion
echo -e "${BLUE}1️⃣2️⃣  Verifying Task was Deleted${NC}"
echo "GET $BASE_URL/tasks/$TASK2_ID"
curl -s $BASE_URL/tasks/$TASK2_ID | python3 -m json.tool
echo ""

# Test 13: Final Task List
echo -e "${BLUE}1️⃣3️⃣  Final Task List${NC}"
echo "GET $BASE_URL/tasks"
curl -s $BASE_URL/tasks | python3 -m json.tool
echo ""

# Test 14: Final Statistics
echo -e "${BLUE}1️⃣4️⃣  Final Statistics${NC}"
echo "GET $BASE_URL/stats"
curl -s $BASE_URL/stats | python3 -m json.tool
echo ""

echo "=========================================================="
echo -e "${GREEN}✅ All CRUD Tests Completed!${NC}"
echo "=========================================================="
echo ""
echo "📋 Summary of Tests:"
echo "  ✅ CREATE - Created 3 tasks"
echo "  ✅ READ   - Retrieved all tasks and specific tasks"
echo "  ✅ UPDATE - Updated tasks (full and partial)"
echo "  ✅ DELETE - Deleted a task"
echo "  ✅ FILTER - Filtered by completion status"
echo "  ✅ STATS  - Retrieved statistics"
echo ""
echo "💾 Database: Check ai_studio.db file for persistence"
echo "📚 API Docs: $BASE_URL/docs"
echo ""


