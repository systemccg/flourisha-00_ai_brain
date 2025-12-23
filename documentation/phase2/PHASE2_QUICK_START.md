Hey# Phase 2: Docker Sandbox - Quick Start Guide

**Status**: ✅ READY TO USE
**Date**: 2025-12-04

---

## One-Minute Summary

Phase 2 Docker sandboxes are **ready to use right now**. They work identically to E2B but:
- ✅ **10x faster** (3 seconds vs 30 seconds startup)
- ✅ **Zero cost** ($0/hour vs $0.13-0.44/hour)
- ✅ **Unlimited runtime** (no 1-hour timeout)

---

## Using Docker Sandboxes

### Command Syntax

```bash
docker-sandbox-cli.sh init                              # Create sandbox
docker-sandbox-cli.sh exec <id> "<command>"            # Run command
docker-sandbox-cli.sh upload <id> <local> <remote>     # Copy file in
docker-sandbox-cli.sh download <id> <remote> <local>   # Copy file out
docker-sandbox-cli.sh kill <id>                        # Delete sandbox
docker-sandbox-cli.sh get-host <id>                    # Get public URL
```

### Example: Build & Test Calculator

```bash
# 1. Create sandbox
SANDBOX_ID=$(docker-sandbox-cli.sh init)
echo "Sandbox: $SANDBOX_ID"

# 2. Upload files
docker-sandbox-cli.sh upload "$SANDBOX_ID" main.py /code/main.py
docker-sandbox-cli.sh upload "$SANDBOX_ID" index.html /code/index.html

# 3. Start app
docker-sandbox-cli.sh exec "$SANDBOX_ID" \
  "cd /code && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000"

# 4. Test (from server, works now)
docker-sandbox-cli.sh exec "$SANDBOX_ID" \
  "curl http://localhost:8000/api/history"

# 5. Get public URL (for external access after DNS configured)
docker-sandbox-cli.sh get-host "$SANDBOX_ID"

# 6. Clean up
docker-sandbox-cli.sh kill "$SANDBOX_ID"
```

---

## Testing Inside Sandbox

These work **right now** without DNS configuration:

```bash
# Test API from inside sandbox
docker-sandbox-cli.sh exec <id> "curl http://localhost:8000/api/health"

# Test with Python requests
docker-sandbox-cli.sh exec <id> "python3 << 'EOF'
import requests
resp = requests.get('http://localhost:8000/api/history')
print(resp.json())
EOF"

# Check what's running
docker-sandbox-cli.sh exec <id> "ps aux | grep python"
```

---

## Disler's 4-Phase Pattern

### Phase 1: PLAN ✅
Write specification with success criteria

### Phase 2: BUILD ✅
```bash
SANDBOX_ID=$(docker-sandbox-cli.sh init)
docker-sandbox-cli.sh upload "$SANDBOX_ID" main.py /code/main.py
docker-sandbox-cli.sh exec "$SANDBOX_ID" "python3 main.py"
```

### Phase 3: HOST ✅
App automatically accessible at:
```
Internal: localhost:8000
Public: https://qa-{short-id}.leadingai.info (after DNS configured)
```

### Phase 4: TEST ✅
```bash
# Internal API test
docker-sandbox-cli.sh exec "$SANDBOX_ID" "curl http://localhost:8000/api/health"

# External test (after DNS configured)
curl https://qa-{short-id}.leadingai.info/api/health

# Browser test (Playwright MCP on public URL)
# Use Playwright MCP skill with the public URL
```

---

## What Works NOW

| Feature | Status | Details |
|---------|--------|---------|
| Create sandbox | ✅ | `docker-sandbox-cli.sh init` |
| Run commands | ✅ | `docker-sandbox-cli.sh exec` |
| Upload files | ✅ | `docker-sandbox-cli.sh upload` |
| Download files | ✅ | `docker-sandbox-cli.sh download` |
| Delete sandbox | ✅ | `docker-sandbox-cli.sh kill` |
| Internal API test | ✅ | curl localhost:8000 |
| FastAPI | ✅ | Pre-installed |
| Python 3.10 | ✅ | Pre-installed |
| Node.js | ✅ | Pre-installed |
| SQLite | ✅ | Pre-installed |

---

## What Needs DNS Setup

| Feature | Status | Requirements |
|---------|--------|---------------|
| External URL access | ⏳ | Cloudflare DNS wildcard |
| Browser access | ⏳ | DNS resolution working |
| Playwright MCP testing | ⏳ | DNS + external access |

**To enable**: Configure Cloudflare with wildcard A record for `*` → your server IP

---

## Practical Examples

### Example 1: Simple FastAPI App

```bash
SANDBOX_ID=$(docker-sandbox-cli.sh init)

# Create simple app
docker-sandbox-cli.sh exec "$SANDBOX_ID" "cat > /code/app.py << 'EOF'
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Docker!"}
EOF"

# Run it
docker-sandbox-cli.sh exec "$SANDBOX_ID" \
  "cd /code && python3 -m uvicorn app:app --host 0.0.0.0 --port 8000"

# Test
docker-sandbox-cli.sh exec "$SANDBOX_ID" "curl http://localhost:8000"

# Clean up
docker-sandbox-cli.sh kill "$SANDBOX_ID"
```

### Example 2: Python Script

```bash
SANDBOX_ID=$(docker-sandbox-cli.sh init)

# Upload script
docker-sandbox-cli.sh upload "$SANDBOX_ID" my_script.py /code/script.py

# Run it
docker-sandbox-cli.sh exec "$SANDBOX_ID" "python3 /code/script.py"

# Download results
docker-sandbox-cli.sh download "$SANDBOX_ID" /code/results.txt ./results.txt

# Clean up
docker-sandbox-cli.sh kill "$SANDBOX_ID"
```

### Example 3: Node.js App

```bash
SANDBOX_ID=$(docker-sandbox-cli.sh init)

# Upload package.json
docker-sandbox-cli.sh upload "$SANDBOX_ID" package.json /code/package.json

# Install and run
docker-sandbox-cli.sh exec "$SANDBOX_ID" \
  "cd /code && npm install && npm start"

# Clean up
docker-sandbox-cli.sh kill "$SANDBOX_ID"
```

---

## Troubleshooting

### Sandbox won't start
```bash
# Check Docker is running
docker ps

# Check image exists
docker images | grep flourisha-sandbox

# Check disk space
df -h

# Check available memory
free -h
```

### Command execution fails
```bash
# Check container is running
docker ps | grep $SANDBOX_ID

# Check logs
docker logs $SANDBOX_ID

# Try simpler command
docker-sandbox-cli.sh exec "$SANDBOX_ID" "echo hello"
```

### File upload fails
```bash
# Check source file exists
ls -l /path/to/file

# Check disk space
docker-sandbox-cli.sh exec "$SANDBOX_ID" "df -h /code"

# Try with absolute path
docker-sandbox-cli.sh upload "$SANDBOX_ID" /absolute/path/file /code/file
```

### Cleanup issues
```bash
# Force kill if needed
docker kill $SANDBOX_ID
docker rm $SANDBOX_ID

# Remove network
docker network rm flourisha-sandbox-net-*

# Check cleanup script runs
/root/flourisha/00_AI_Brain/scripts/cleanup-old-sandboxes.sh
```

---

## Resource Limits

Each sandbox has:
- **RAM**: 2GB (hard limit)
- **CPU**: 2 cores
- **Disk**: 10GB (configurable)
- **Network**: Isolated per sandbox

If app needs more resources, modify CLI script.

---

## Documentation

- **Complete Guide**: `/root/flourisha/00_AI_Brain/PHASE2_STATUS.md`
- **Validation Report**: `/root/.claude/scratchpad/2025-12-04-calculator-build/PHASE2B_VALIDATION_REPORT.md`
- **Deployment Notes**: `/root/.claude/scratchpad/2025-12-04-calculator-build/PHASE2_DEPLOYMENT_NOTES.md`
- **DNS Setup**: See PHASE2_STATUS.md for Cloudflare configuration

---

## Next Steps

1. **Use Docker for next project** - Same workflow as E2B but faster
2. **Build test app** - Create simple app and test with docker-sandbox-cli.sh
3. **Configure DNS** (optional) - When ready for external access

---

## CLI Location

```
/root/flourisha/00_AI_Brain/scripts/docker-sandbox-cli.sh
```

All commands use this script. It's executable and ready to use.

---

**Everything is ready. Start building!** ✅

