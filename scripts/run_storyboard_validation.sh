#!/bin/bash
# run_storyboard_validation.sh
# Runs full validation of storyboard contract against live backend at 127.0.0.1:8010

set -e
BASE_URL="${SMOKE_BASE_URL:-http://127.0.0.1:8010}"
TOKEN="${SMOKE_TOKEN:-}"

echo "==> Storyboard Contract Validation @ $BASE_URL"
echo "=========================================="

# 1. Health check
echo -e "\n[1] Health check"
HEALTH=$(curl -s "$BASE_URL/health")
echo "  Response: $HEALTH"

# 2. Get or create token
if [ -z "$TOKEN" ]; then
  echo -e "\n[2] Getting token (registering test user)..."
  REG=$(curl -s -X POST "$BASE_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"username":"smoke_test_v2","email":"smoke_v2@test.com","password":"SmokeTest123!","full_name":"Smoke Test"}')
  
  TOKEN=$(echo "$REG" | jq -r '.access_token // empty')
  
  if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "  Register failed, trying login..."
    LOGIN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
      -H "Content-Type: application/json" \
      -d '{"email":"smoke_v2@test.com","password":"SmokeTest123!"}')
    TOKEN=$(echo "$LOGIN" | jq -r '.access_token // empty')
  fi
  
  if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "  ERROR: Could not get token"
    exit 1
  fi
fi

echo "  Token obtained: ${TOKEN:0:20}..."

# 3. Get or create project
echo -e "\n[3] Getting/creating test project..."
PROJECTS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/projects")
PROJECT_ID=$(echo "$PROJECTS" | jq -r '.projects[0].id // empty')

if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "null" ]; then
  echo "  Creating new project..."
  PROJECT=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"Smoke Test Project","description":"For storyboard testing"}' \
    "$BASE_URL/api/projects")
  PROJECT_ID=$(echo "$PROJECT" | jq -r '.id // empty')
fi

echo "  Using project: $PROJECT_ID"

# 4. Add script to project
echo -e "\n[4] Adding script to project..."
curl -s -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"script_text":"SCENE 1\nInt. OFFICE - DAY\nJOHN enters the room.\n\nSCENE 2\nExt. STREET - DAY\nMARY walks down the street.\n\nSCENE 3\nInt. KITCHEN - NIGHT\nJOHN and MARY cook dinner."' \
  "$BASE_URL/api/projects/$PROJECT_ID/script" | jq -C . | head -5

# 5. Get storyboard options
echo -e "\n[5] GET /api/projects/$PROJECT_ID/storyboard/options"
OPTIONS=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/api/projects/$PROJECT_ID/storyboard/options")
echo "$OPTIONS" | jq -C '.modes'

MODES=$(echo "$OPTIONS" | jq -r '.modes[]')
if echo "$MODES" | grep -q "SELECTED_SCENES"; then
  echo "  ✅ SELECTED_SCENES found in modes"
else
  echo "  ❌ SELECTED_SCENES NOT found in modes"
fi

# 6. Generate storyboard with SELECTED_SCENES
echo -e "\n[6] POST generate SELECTED_SCENES scene_numbers=[1]"
GEN=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"generation_mode":"SELECTED_SCENES","scene_numbers":[1],"shots_per_scene":1,"style_preset":"cinematic_realistic","overwrite":true}' \
  "$BASE_URL/api/projects/$PROJECT_ID/storyboard/generate")

echo "$GEN" | jq -C '{status, mode, total_scenes, total_shots}'

MODE=$(echo "$GEN" | jq -r '.mode')
TOTAL_SCENES=$(echo "$GEN" | jq -r '.total_scenes')
TOTAL_SHOTS=$(echo "$GEN" | jq -r '.total_shots')

if [ "$MODE" = "SELECTED_SCENES" ]; then
  echo "  ✅ mode is SELECTED_SCENES"
else
  echo "  ❌ mode is NOT SELECTED_SCENES (got: $MODE)"
fi

if [ "$TOTAL_SCENES" = "1" ]; then
  echo "  ✅ total_scenes = 1"
else
  echo "  ❌ total_scenes != 1 (got: $TOTAL_SCENES)"
fi

if [ "$TOTAL_SHOTS" = "1" ]; then
  echo "  ✅ total_shots = 1"
else
  echo "  ❌ total_shots != 1 (got: $TOTAL_SHOTS)"
fi

# 7. Get storyboard filtered by scene_number=1
echo -e "\n[7] GET /api/projects/$PROJECT_ID/storyboard?scene_number=1"
SHOTS=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/api/projects/$PROJECT_ID/storyboard?scene_number=1")
echo "$SHOTS" | jq -C '{mode, scene_number, shot_count: (.shots | length)}'

# 8. Check pipeline endpoints
echo -e "\n[8] Checking pipeline aliases..."
STATUS1=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/workflows/presets")
STATUS2=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/pipelines/presets")
STATUS3=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/pipelines/jobs")

echo "  /api/workflows/presets: $STATUS1"
echo "  /api/pipelines/presets: $STATUS2"
echo "  /api/pipelines/jobs: $STATUS3"

if [ "$STATUS2" != "404" ]; then
  echo "  ✅ /api/pipelines/presets does not 404"
else
  echo "  ❌ /api/pipelines/presets returns 404"
fi

echo -e "\n==> Validation complete"
