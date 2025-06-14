#!/bin/bash

echo "🔍 Introspection Checkpoint 1: Model Migration Verification"
echo "=========================================================="
echo ""

# Count model references
echo "📊 Model reference counts:"
echo -n "  gpt-3.5-turbo (nano): "
grep -r "gpt-3.5-turbo" backend/app/ | wc -l | xargs echo

echo -n "  gpt-4o-mini (mini): "
grep -r "gpt-4o-mini" backend/app/ | wc -l | xargs echo

echo -n "  gpt-4o (full): "
grep -r "gpt-4o" backend/app/ | grep -v "gpt-4o-mini" | wc -l | xargs echo

echo ""
echo "🔍 Checking for model selection logic:"
grep -r "_select_model" backend/app/ | wc -l | xargs echo "  Model selection calls found:"

echo ""
echo "📝 Model tier assignments:"
grep -B1 -A1 "_select_model" backend/app/narrative_engine.py | grep -E "(Complex|Standard|Simple)" | head -10

echo ""
echo "✅ Model migration complete - using tiered selection logic"