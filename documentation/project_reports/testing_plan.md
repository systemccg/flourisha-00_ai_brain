# Flourisha API Testing Plan

**Generated:** 2025-12-29 (Pacific Time)
**Purpose:** Copy-paste test commands to verify API functionality

---

## Quick Start

### 1. Start the API Server

```bash
cd /root/flourisha/00_AI_Brain/api
uv run uvicorn main:app --port 8000 --reload
```

Keep this terminal running. Open a new terminal for testing.

---

## Section 1: Health & System Tests (No Auth Required)

### Test 1.1: Basic Health Check
```bash
curl -s http://localhost:8000/api/health | python3 -m json.tool
```
**Expected:** `"success": true`, `"status": "healthy"`

### Test 1.2: Root Endpoint
```bash
curl -s http://localhost:8000/ | python3 -m json.tool
```
**Expected:** Links to `/docs` and `/api/health`

### Test 1.3: Rate Limit Status
```bash
curl -s http://localhost:8000/api/rate-limit | python3 -m json.tool
```
**Expected:** Rate limit config with `is_authenticated: false`

### Test 1.4: OpenAPI Docs
```bash
curl -s http://localhost:8000/openapi.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Endpoints: {len(d[\"paths\"])} paths')"
```
**Expected:** Shows number of API paths (100+)

### Test 1.5: Swagger UI
Open in browser: http://localhost:8000/docs

---

## Section 2: Health Dashboard Tests

### Test 2.1: Service Health Overview
```bash
curl -s http://localhost:8000/api/health-dashboard/services | python3 -m json.tool
```
**Expected:** Status of Supabase, Neo4j, Voice Server

### Test 2.2: Supabase Health
```bash
curl -s http://localhost:8000/api/health-dashboard/supabase | python3 -m json.tool
```
**Expected:** Supabase connection status

### Test 2.3: Neo4j Health
```bash
curl -s http://localhost:8000/api/health-dashboard/neo4j | python3 -m json.tool
```
**Expected:** Neo4j connection and node counts

---

## Section 3: Search Tests

### Test 3.1: Basic Search (requires auth or returns error)
```bash
curl -s http://localhost:8000/api/search?q=test | python3 -m json.tool
```
**Expected:** Either search results or `401 Unauthorized`

---

## Section 4: Skills Tests

### Test 4.1: List Skills (File-based)
```bash
curl -s http://localhost:8000/api/skills | python3 -m json.tool
```
**Expected:** List of PAI skills from ~/.claude/skills/

### Test 4.2: Get Specific Skill
```bash
curl -s http://localhost:8000/api/skills/CORE | python3 -m json.tool
```
**Expected:** CORE skill content

---

## Section 5: PARA Navigation Tests

### Test 5.1: List PARA Categories
```bash
curl -s http://localhost:8000/api/para | python3 -m json.tool
```
**Expected:** Projects, Areas, Resources, Archives

### Test 5.2: List Projects
```bash
curl -s http://localhost:8000/api/para/projects | python3 -m json.tool
```
**Expected:** List of directories in 01f_Flourisha_Projects

---

## Section 6: Webhook Tests

### Test 6.1: Webhook Status
```bash
curl -s http://localhost:8000/api/webhooks/status | python3 -m json.tool
```
**Expected:** Webhook configuration status

### Test 6.2: ClickUp Webhook (simulation)
```bash
curl -s -X POST http://localhost:8000/api/webhooks/clickup \
  -H "Content-Type: application/json" \
  -d '{"event": "taskCreated", "task_id": "test123"}' | python3 -m json.tool
```
**Expected:** Webhook received acknowledgment

---

## Section 7: Cron Tests (Admin Auth Required)

### Test 7.1: Cron Health
```bash
curl -s http://localhost:8000/api/crons/health | python3 -m json.tool
```
**Expected:** Cron system health status

---

## Section 8: Migration Tests (Admin Auth Required)

### Test 8.1: Migration Health
```bash
curl -s http://localhost:8000/api/migrations/health | python3 -m json.tool
```
**Expected:** Migration system health

### Test 8.2: Schema Introspection
```bash
curl -s http://localhost:8000/api/migrations/schema | python3 -m json.tool
```
**Expected:** Database schema info (may require admin auth)

---

## Section 9: YouTube Tests

### Test 9.1: List YouTube Endpoints
```bash
curl -s http://localhost:8000/api/youtube | python3 -m json.tool
```
**Expected:** YouTube router info or list of channels

---

## Section 10: Hedra Tests (Requires HEDRA_API_KEY)

### Test 10.1: Hedra Config Status
```bash
curl -s http://localhost:8000/api/hedra/config/status | python3 -m json.tool
```
**Expected:** API key configured status (503 if not configured)

---

## Section 11: Nango Tests (Requires NANGO_SECRET_KEY)

### Test 11.1: Nango Config Status
```bash
curl -s http://localhost:8000/api/nango/config/status | python3 -m json.tool
```
**Expected:** Nango configuration status

---

## Batch Test Script

Save this as `test_api.sh` and run with `bash test_api.sh`:

```bash
#!/bin/bash
# Flourisha API Test Script

BASE_URL="http://localhost:8000"

echo "=== Flourisha API Tests ==="
echo ""

echo "1. Health Check..."
curl -s $BASE_URL/api/health | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'   Status: {d.get(\"data\",{}).get(\"status\",\"unknown\")}')"

echo "2. Rate Limit..."
curl -s $BASE_URL/api/rate-limit | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'   Success: {d.get(\"success\",False)}')"

echo "3. Health Dashboard..."
curl -s $BASE_URL/api/health-dashboard/services | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'   Success: {d.get(\"success\",False)}')"

echo "4. Skills List..."
curl -s $BASE_URL/api/skills | python3 -c "import json,sys; d=json.load(sys.stdin); skills=d.get('data',{}).get('skills',[]); print(f'   Found: {len(skills)} skills')"

echo "5. PARA Categories..."
curl -s $BASE_URL/api/para | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'   Success: {d.get(\"success\",False)}')"

echo "6. OpenAPI Spec..."
curl -s $BASE_URL/openapi.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'   Paths: {len(d.get(\"paths\",{}))}')"

echo ""
echo "=== Tests Complete ==="
```

---

## Python Test Script

Save this as `test_api.py` and run with `python3 test_api.py`:

```python
#!/usr/bin/env python3
"""Flourisha API Test Script"""

import httpx
import json
from typing import Any

BASE_URL = "http://localhost:8000"

def test_endpoint(name: str, path: str, method: str = "GET", data: Any = None) -> bool:
    """Test a single endpoint."""
    try:
        url = f"{BASE_URL}{path}"
        if method == "GET":
            response = httpx.get(url, timeout=10)
        else:
            response = httpx.post(url, json=data, timeout=10)

        result = response.json()
        success = result.get("success", False) or response.status_code == 200
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {name}: {path}")
        return success
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        return False

def main():
    print("=" * 50)
    print("Flourisha API Test Suite")
    print("=" * 50)
    print()

    tests = [
        ("Health Check", "/api/health"),
        ("Root", "/"),
        ("Rate Limit", "/api/rate-limit"),
        ("Health Dashboard", "/api/health-dashboard/services"),
        ("Skills List", "/api/skills"),
        ("CORE Skill", "/api/skills/CORE"),
        ("PARA Root", "/api/para"),
        ("Webhooks Status", "/api/webhooks/status"),
        ("Crons Health", "/api/crons/health"),
        ("Migrations Health", "/api/migrations/health"),
    ]

    passed = 0
    failed = 0

    for name, path in tests:
        if test_endpoint(name, path):
            passed += 1
        else:
            failed += 1

    print()
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

if __name__ == "__main__":
    main()
```

---

## Testing with Authentication

To test authenticated endpoints, you need a Firebase JWT token.

### Option 1: Get Token from Firebase SDK
```python
import firebase_admin
from firebase_admin import auth

# Initialize Firebase (requires service account)
firebase_admin.initialize_app()

# Create a custom token for testing
custom_token = auth.create_custom_token("test-user-id")
print(f"Token: {custom_token.decode()}")
```

### Option 2: Use Test Token Header
Add to your curl commands:
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" ...
```

### Option 3: Temporarily Disable Auth (Development Only)
In development, you can modify the auth middleware to bypass authentication.

---

## Test Results Checklist

| Test | Expected | Your Result |
|------|----------|-------------|
| Health Check | ✅ success: true | |
| Rate Limit | ✅ success: true | |
| Health Dashboard | ✅ services status | |
| Skills List | ✅ skills array | |
| PARA | ✅ categories | |
| Webhooks | ✅ status info | |
| Hedra | ⚠️ 503 if no key | |
| Nango | ⚠️ 503 if no key | |

---

## Troubleshooting

### Server Won't Start
```bash
# Check if port is in use
lsof -i :8000

# Kill existing process
pkill -f "uvicorn main:app"
```

### Import Errors
```bash
# Reinstall dependencies
cd /root/flourisha/00_AI_Brain/api
uv sync
```

### Environment Variables Not Loading
```bash
# Verify .env exists
ls -la /root/.claude/.env

# Test config loading
cd /root/flourisha/00_AI_Brain/api
python3 -c "from config import get_settings; s = get_settings(); print(f'Supabase: {bool(s.supabase_url)}')"
```

---

*Report generated by Flourisha AI Agent*
