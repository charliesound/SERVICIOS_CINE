#!/usr/bin/env bash
set -euo pipefail

echo "=== Smoke: Storyboard Sequence Selection UX ==="

FAILS=0
FILE="src_frontend/src/pages/StoryboardBuilderPage.tsx"

# Test 1: Verify "Seleccionar secuencia" button exists
echo -n "  Check 'Seleccionar secuencia' button... "
if grep -q "Seleccionar secuencia" "$FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — 'Seleccionar secuencia' button not found"
  FAILS=$((FAILS + 1))
fi

# Test 2: Verify "Generar storyboard de esta secuencia" exists
echo -n "  Check 'Generar storyboard de esta secuencia'... "
if grep -q "Generar storyboard de esta secuencia" "$FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — 'Generar storyboard de esta secuencia' not found"
  FAILS=$((FAILS + 1))
fi

# Test 3: Verify selectedSequenceId state exists
echo -n "  Check selectedSequenceId state... "
if grep -q "selectedSequenceId" "$FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — selectedSequenceId state not found"
  FAILS=$((FAILS + 1))
fi

# Test 4: Verify no direct generate without selectedSequenceId
echo -n "  Check generate guard (no direct call without selection)... "
# handleGenerateSequence should only be called when selectedSequenceId is truthy
if grep -q "handleGenerateSequence(selectedSequenceId)" "$FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — handleGenerateSequence requires selectedSequenceId"
  FAILS=$((FAILS + 1))
fi

# Test 5: Verify sequence count display "secuencias disponibles"
echo -n "  Check sequence count text... "
if grep -q "secuencias disponibles" "$FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — sequence counter text not found"
  FAILS=$((FAILS + 1))
fi

# Test 6: Verify handlePlanSequenceFromList exists
echo -n "  Check handlePlanSequenceFromList handler... "
if grep -q "handlePlanSequenceFromList" "$FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — handlePlanSequenceFromList not found"
  FAILS=$((FAILS + 1))
fi

# Test 7: Verify "Planificar storyboard" button exists
echo -n "  Check 'Planificar storyboard' button... "
if grep -q "Planificar storyboard" "$FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — 'Planificar storyboard' not found"
  FAILS=$((FAILS + 1))
fi

# Test 8: Verify guard message exists
echo -n "  Check guard message for unselected sequence... "
if grep -q "Primero selecciona una secuencia" "$FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — guard message 'Primero selecciona una secuencia' not found"
  FAILS=$((FAILS + 1))
fi

# Test 9: Verify dedupeList helper exists in this file
echo -n "  Check dedupeList helper... "
if grep -q "function dedupeList" "$FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — dedupeList helper not found"
  FAILS=$((FAILS + 1))
fi

# Test 10: Verify "Secuencia seleccionada:" confirmation text
echo -n "  Check selected confirmation text... "
if grep -q "Secuencia seleccionada:" "$FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — 'Secuencia seleccionada:' confirmation not found"
  FAILS=$((FAILS + 1))
fi

# Test 11: Verify plan result display block exists
echo -n "  Check plan result display... "
if grep -q "Plan de storyboard:" "$FILE" 2>/dev/null; then
  echo "OK"
else
  echo "FAIL — plan result display not found"
  FAILS=$((FAILS + 1))
fi

# Test 12: Verify guard also exists in Tab 3
echo -n "  Check guard message in Tab 3... "
TAB3_GUARD=$(grep -c "Primero selecciona una secuencia en la pesta" "$FILE" 2>/dev/null || true)
if [ "$TAB3_GUARD" -ge 1 ]; then
  echo "OK"
else
  echo "FAIL — Tab 3 guard message not found"
  FAILS=$((FAILS + 1))
fi

# Test 13: Verify no auto-select of first sequence
echo -n "  Check no auto-select of first sequence... "
if grep -q "setSelectedSequenceId(data\[0\].sequence_id)" "$FILE" 2>/dev/null; then
  echo "FAIL — still auto-selects first sequence"
  FAILS=$((FAILS + 1))
else
  echo "OK"
fi

echo ""
if [ "$FAILS" -eq 0 ]; then
  echo "SMOKE PASS — Storyboard Sequence Selection UX validated."
else
  echo "SMOKE FAIL — $FAILS issues found."
  exit 1
fi
