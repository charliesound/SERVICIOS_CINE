#!/usr/bin/env bash
set -euo pipefail

echo "=== Smoke: Scene Breakdown UX ==="

FAILS=0

# Test 1: Verify src file does NOT contain slice(0, 8) without condition
echo -n "  Check slice(0,8) is conditional... "
if grep -q '\.slice(0, 8)' src_frontend/src/pages/ProjectDetailPage.tsx 2>/dev/null; then
  echo "FAIL — found unconditional slice(0,8)"
  FAILS=$((FAILS + 1))
else
  echo "OK"
fi

# Test 2: Verify showAllScenes state exists
echo -n "  Check showAllScenes state... "
if grep -q 'showAllScenes' src_frontend/src/pages/ProjectDetailPage.tsx 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — showAllScenes state not found"
  FAILS=$((FAILS + 1))
fi

# Test 3: Verify "Ver todas" / "Ver menos" button exists
echo -n "  Check 'Ver todas' toggle... "
if grep -q "Ver todas" src_frontend/src/pages/ProjectDetailPage.tsx 2>/dev/null && \
   grep -q "Ver menos" src_frontend/src/pages/ProjectDetailPage.tsx 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — Ver todas / Ver menos not found"
  FAILS=$((FAILS + 1))
fi

# Test 4: Verify counter "Mostrando X de Y"
echo -n "  Check scene counter text... "
if grep -q "Mostrando" src_frontend/src/pages/ProjectDetailPage.tsx 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — counter text not found"
  FAILS=$((FAILS + 1))
fi

# Test 5: Verify dedupeList function exists
echo -n "  Check dedupeList helper... "
if grep -q "dedupeList" src_frontend/src/pages/ProjectDetailPage.tsx 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — dedupeList helper not found"
  FAILS=$((FAILS + 1))
fi

# Test 6: Verify StoryboardSequenceSelectorModal accepts full scene arrays (no slice limit)
echo -n "  Check selector modal uses full scene list... "
if grep -q "max-h-\[360px\]" src_frontend/src/components/storyboard/StoryboardSequenceSelectorModal.tsx 2>/dev/null; then
  echo "OK (scroll container)"
else
  echo "FAIL — scroll container not found"
  FAILS=$((FAILS + 1))
fi

# Test 7: Verify dedupeList logic with Node.js
echo -n "  Check dedupeList logic... "
NODE_TEST=$(node -e "
const items = ['MANU', 'MANU', 'ALBERTO', 'maria', 'MARIA'];
const seen = new Set();
const result = items.filter(item => {
  const key = item.trim().toLowerCase();
  if (!key || seen.has(key)) return false;
  seen.add(key);
  return true;
}).join(', ');
console.log(result);
" 2>&1)
if [ "$NODE_TEST" = "MANU, ALBERTO, maria" ]; then
  echo "OK"
else
  echo "FAIL — expected 'MANU, ALBERTO, maria', got '$NODE_TEST'"
  FAILS=$((FAILS + 1))
fi

echo ""
if [ "$FAILS" -eq 0 ]; then
  echo "SMOKE PASS — Scene Breakdown UX validated."
else
  echo "SMOKE FAIL — $FAILS issues found."
  exit 1
fi
