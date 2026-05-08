#!/usr/bin/env bash
set -euo pipefail

echo "=== Smoke: Storyboard Visual Cycle (render_status, asset association) ==="

FAILS=0
BACKEND_FILE="src/schemas/shot_schema.py"
FRONTEND_FILE="src_frontend/src/components/storyboard/ShotCard.tsx"
FRONTEND_TYPES="src_frontend/src/types/storyboard.ts"
SERVICE_FILE="src/services/storyboard_service.py"

# ---- BACKEND CHECKS ----

# Test 1: render_job_id field exists in StoryboardShotResponse
echo -n "  [BE] Check render_job_id field in shot_schema... "
if grep -q "render_job_id" "$BACKEND_FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — render_job_id not found in StoryboardShotResponse"
  FAILS=$((FAILS + 1))
fi

# Test 2: render_status field exists in StoryboardShotResponse
echo -n "  [BE] Check render_status field in shot_schema... "
if grep -q "render_status" "$BACKEND_FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — render_status not found in StoryboardShotResponse"
  FAILS=$((FAILS + 1))
fi

# Test 3: _should_enqueue_render includes SEQUENCE mode
echo -n "  [BE] Check _should_enqueue_render includes SEQUENCE... "
if grep -q "StoryboardGenerationMode.SEQUENCE" "$SERVICE_FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — SEQUENCE mode not in _should_enqueue_render"
  FAILS=$((FAILS + 1))
fi

# Test 4: list_storyboard_shots populates asset URLs
echo -n "  [BE] Check list_storyboard_shots populates asset URLs... "
if grep -q "shot.thumbnail_url" "$SERVICE_FILE" 2>/dev/null && \
   grep -q "shot.preview_url" "$SERVICE_FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — asset URL population not found in list_storyboard_shots"
  FAILS=$((FAILS + 1))
fi

# Test 5: list_storyboard_shots computes render_status
echo -n "  [BE] Check render_status computation in list_storyboard_shots... "
if grep -q "shot.render_status" "$SERVICE_FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — render_status computation not found in list_storyboard_shots"
  FAILS=$((FAILS + 1))
fi

# Test 6: render_job_id stored on shot metadata during generate
echo -n "  [BE] Check render_job_id persistence on Shot metadata... "
if grep -q 'meta\["render_job_id"\]' "$SERVICE_FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — render_job_id not persisted on shot metadata"
  FAILS=$((FAILS + 1))
fi

# Test 7: Progress message differentiates structure vs visual
echo -n "  [BE] Check progress message for render pending... "
if grep -q "Render pendiente" "$SERVICE_FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — progress message does not mention render pending"
  FAILS=$((FAILS + 1))
fi

# ---- FRONTEND CHECKS ----

# Test 8: render_job_id in TypeScript StoryboardShot type
echo -n "  [FE] Check render_job_id in TypeScript types... "
if grep -q "render_job_id" "$FRONTEND_TYPES" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — render_job_id not found in TypeScript StoryboardShot"
  FAILS=$((FAILS + 1))
fi

# Test 9: render_status in TypeScript StoryboardShot type
echo -n "  [FE] Check render_status in TypeScript types... "
if grep -q "render_status" "$FRONTEND_TYPES" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — render_status not found in TypeScript StoryboardShot"
  FAILS=$((FAILS + 1))
fi

# Test 10: ShotCard shows render_status badge
echo -n "  [FE] Check render_status badge in ShotCard... "
if grep -q "RENDER_STATUS_CONFIG" "$FRONTEND_FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — render_status badge config not found in ShotCard"
  FAILS=$((FAILS + 1))
fi

# Test 11: ShotCard shows render_pending placeholder
echo -n "  [FE] Check render_pending placeholder text... "
if grep -q "Imagen pendiente de generar o asociar" "$FRONTEND_FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — placeholder text not found in ShotCard"
  FAILS=$((FAILS + 1))
fi

# Test 12: ShotCard shows render_job_id
echo -n "  [FE] Check render_job_id display in ShotCard... "
if grep -q "render_job_id" "$FRONTEND_FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — render_job_id display not found in ShotCard"
  FAILS=$((FAILS + 1))
fi

# Test 13: ShotCard shows generation_job_id
echo -n "  [FE] Check generation_job_id display in ShotCard... "
if grep -q "generation_job_id" "$FRONTEND_FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — generation_job_id display not found in ShotCard"
  FAILS=$((FAILS + 1))
fi

# ---- PYTHON COMPILATION CHECK ----
echo -n "  [BE] Python compilation... "
if python3 -m py_compile "$BACKEND_FILE" 2>/dev/null && \
   python3 -m py_compile "$SERVICE_FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — Python compilation error"
  FAILS=$((FAILS + 1))
fi

echo ""
if [ "$FAILS" -eq 0 ]; then
  echo "SMOKE PASS — Storyboard Visual Cycle validated."
else
  echo "SMOKE FAIL — $FAILS issues found."
  exit 1
fi
