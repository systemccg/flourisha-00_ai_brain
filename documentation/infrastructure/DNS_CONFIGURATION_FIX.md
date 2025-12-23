# DNS Configuration Fix - Cloudflare Setup Issue

**Issue**: 404 errors when accessing qa-*.leadingai.info even though Cloudflare is configured

**Root Cause**: Cloudflare is set to "Proxied" (orange cloud) but your server isn't configured to handle Cloudflare's routing

**Solution**: Two options - pick one:

---

## Option 1: DNS Only (Recommended - Simpler)

This makes Cloudflare just do DNS, without proxying:

### Steps:

1. **Log into Cloudflare Dashboard** for leadingai.info
2. **Find the wildcard DNS record** for `*`
3. **Click the orange cloud icon** to change from "Proxied" to "DNS only" (should turn gray)
4. **Wait 1-2 minutes** for change to propagate

### Verify:
```bash
dig qa-test.leadingai.info +short
# Should show YOUR server's public IP (2605:a141:2288:3489::1 or IPv4)
```

### Then test:
```bash
curl -H "Host: qa-test.leadingai.info" https://your-server-ip/api/health
# Should work via HTTPS
```

---

## Option 2: Keep Proxied (Advanced)

If you want Cloudflare's DDoS protection and caching:

### Problem:
Cloudflare is sending traffic to their servers, not your server. You need to configure your origin server.

### Steps:

1. **Add Origin Server to Cloudflare**:
   - Go to Cloudflare DNS settings
   - Edit the A record for `*`
   - Set Content to: Your IPv4 address (if available) OR configure IPv6
   - Disable "Proxy" initially to get it working

2. **Configure Cloudflare SSL**:
   - Go to SSL/TLS settings
   - Set to "Full" or "Full (strict)"
   - This lets Cloudflare handle the HTTPS

3. **For IPv6** (your setup):
   - Add AAAA record: `*` → `2605:a141:2288:3489::1`
   - Set to "Proxied" (orange cloud)

4. **Verify Traefik has IPv6 support**:
   - Check your Traefik is listening on IPv6

---

## Quick Fix (Option 1 - Recommended)

Since you want things working quickly:

```
Cloudflare Dashboard → DNS Records
Find: * (wildcard) A/AAAA record
Click: Orange cloud icon
Select: DNS only (gray cloud)
Wait: 1-2 minutes
Test: curl https://qa-test.leadingai.info/api/health
```

**After this change, your qa-*.leadingai.info URLs will work with Traefik.**

---

## Why This Happened

- ✅ Cloudflare DNS is configured correctly
- ✅ Your server is configured correctly
- ❌ Cloudflare is set to "Proxied" (orange) which intercepts traffic
- ❌ Your server isn't configured as Cloudflare origin, so Cloudflare returns errors

**DNS Only mode (gray cloud)** just forwards the domain to your IP without proxying.

---

## What You'll See After Fix

```bash
# Before fix:
$ curl https://qa-test.leadingai.info/api/health
404 page not found

# After DNS Only fix:
$ curl https://qa-test.leadingai.info/api/health
{error or success from Traefik}

# After local testing:
$ docker-sandbox-cli.sh init
SANDBOX_ID=$(output)
docker-sandbox-cli.sh exec "$SANDBOX_ID" "python3 -m uvicorn main:app --host 0.0.0.0 --port 8000"
curl https://qa-{short-id}.leadingai.info/api/health
✅ Works!
```

---

## Testing After Fix

```bash
# 1. Verify DNS resolves to your IP
dig qa-test.leadingai.info +short
# Should show your server IP

# 2. Test Traefik routing (with Host header)
curl -H "Host: qa-test.leadingai.info" https://localhost/
# Should show Traefik response or app response

# 3. Test via domain name
curl https://qa-test.leadingai.info/
# Should work!

# 4. Test Docker sandbox
SANDBOX_ID=$(docker-sandbox-cli.sh init)
docker-sandbox-cli.sh get-host "$SANDBOX_ID"
# Returns: https://qa-{short-id}.leadingai.info
curl https://qa-{short-id}.leadingai.info/
# Should work!
```

---

## Summary

**Do this one thing**:
1. Open Cloudflare Dashboard
2. Find the wildcard DNS record (`*`)
3. Click the orange cloud → change to gray (DNS only)
4. Wait 1-2 minutes
5. Test with `curl https://qa-test.leadingai.info/`

**That's it.** Your Docker sandboxes will work with public URLs.

