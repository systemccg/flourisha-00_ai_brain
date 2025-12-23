#!/bin/bash
# Test E2B Integration for Flourisha
# This tests basic sandbox initialization and simple code execution

set -e

echo "=========================================="
echo "🧪 Flourisha E2B Integration Test"
echo "=========================================="
echo ""

# Load environment
source ~/.claude/.env
if [ -z "$E2B_API_KEY" ]; then
    echo "❌ ERROR: E2B_API_KEY not found in ~/.claude/.env"
    exit 1
fi

echo "✅ E2B API key loaded"
echo ""

# Navigate to sandbox CLI
cd ~/.claude/skills/agent-sandboxes/sandbox_cli/

echo "📝 Test 1: Initialize E2B Sandbox"
echo "Command: uv run sbx init --template fullstack-vue-fastapi-node22 --timeout 43200 --name flourisha-test-$(date +%s)"
echo ""

# Initialize sandbox (capture output to get sandbox ID)
INIT_OUTPUT=$(uv run sbx init --template fullstack-vue-fastapi-node22 --timeout 43200 --name "flourisha-test-$(date +%s)" 2>&1)
SANDBOX_ID=$(echo "$INIT_OUTPUT" | grep -oP '(?<=Sandbox ID: )[^ ]+' | head -1)

if [ -z "$SANDBOX_ID" ]; then
    # Try alternative extraction
    SANDBOX_ID=$(echo "$INIT_OUTPUT" | grep -oP 'sbx_[a-zA-Z0-9]+' | head -1)
fi

echo "Initialization Output:"
echo "$INIT_OUTPUT"
echo ""

if [ -z "$SANDBOX_ID" ]; then
    echo "❌ FAILED: Could not extract Sandbox ID"
    echo "Raw output:"
    echo "$INIT_OUTPUT"
    exit 1
fi

echo "✅ Sandbox initialized successfully"
echo "📌 Sandbox ID: $SANDBOX_ID"
echo ""

# Wait for sandbox to be ready
echo "⏳ Waiting for sandbox to be ready..."
sleep 5

echo ""
echo "📝 Test 2: Execute Python code in sandbox"
echo "Command: uv run sbx exec --sandbox-id $SANDBOX_ID 'python -c \"import sys; print(f\\\"Python {sys.version}\\\")'\"
echo ""

EXEC_OUTPUT=$(uv run sbx exec --sandbox-id "$SANDBOX_ID" 'python -c "import sys; print(f\"Python {sys.version}\")"' 2>&1)
echo "Execution Output:"
echo "$EXEC_OUTPUT"
echo ""

if echo "$EXEC_OUTPUT" | grep -q "Python 3"; then
    echo "✅ Python execution successful"
else
    echo "⚠️  Python execution may have issues (check output above)"
fi

echo ""
echo "📝 Test 3: List sandbox root directory"
echo "Command: uv run sbx files ls --sandbox-id $SANDBOX_ID /"
echo ""

LS_OUTPUT=$(uv run sbx files ls --sandbox-id "$SANDBOX_ID" / 2>&1)
echo "Directory listing:"
echo "$LS_OUTPUT"
echo ""

echo ""
echo "=========================================="
echo "✅ E2B Integration Test Complete"
echo "=========================================="
echo ""
echo "📌 Captured Sandbox ID: $SANDBOX_ID"
echo "⏱️  Sandbox will auto-terminate in 12 hours"
echo "💡 To terminate manually: uv run sbx sandbox kill $SANDBOX_ID"
echo ""
