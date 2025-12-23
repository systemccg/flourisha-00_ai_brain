# Cloudflare Setup Guide

**Server:** leadingai004.contaboserver.net (66.94.121.10)
**Date:** November 13, 2025
**Purpose:** Secure server behind Cloudflare proxy and close unnecessary port exposures

---

## Current Security Status

### ✅ Already Implemented
- Traefik reverse proxy with Let's Encrypt SSL
- SSH key-only authentication
- Fail2ban with aggressive SSH protection
- UFW firewall enabled
- Tailscale VPN for management tools

### ⚠️ Security Gaps to Address
1. **Direct port exposures** bypassing Cloudflare:
   - Portainer: 9000, 9443 (should be Tailscale-only)
   - n8n: 5678 (should be Traefik-only)
   - Neo4j: 7474, 7687 (7474 should be Traefik-only, 7687 for internal use)

2. **Ports 80/443** open to the entire internet (should be Cloudflare IPs only)

---

## Implementation Plan

### Phase 1: Configure Cloudflare DNS (Do This First!)

**Before making firewall changes**, configure Cloudflare to avoid locking yourself out.

#### Step 1: Add DNS Records in Cloudflare

Go to your Cloudflare dashboard → DNS → Records and add these **A records** with **Proxy enabled** (orange cloud):

| Type | Name | Content | Proxy Status | TTL |
|------|------|---------|--------------|-----|
| A | n8n.leadingai.info | 66.94.121.10 | Proxied 🟠 | Auto |
| A | webui.leadingai.info | 66.94.121.10 | Proxied 🟠 | Auto |
| A | neo4j.leadingai.info | 66.94.121.10 | Proxied 🟠 | Auto |
| A | wordpress.leadingai.info | 66.94.121.10 | Proxied 🟠 | Auto |
| A | db.leadingai.info | 66.94.121.10 | Proxied 🟠 | Auto |
| A | traefik.leadingai.info | 66.94.121.10 | Proxied 🟠 | Auto |

**IMPORTANT:** Make sure the cloud is **ORANGE** (Proxied), not grey!

#### Step 2: Configure Cloudflare SSL/TLS Settings

1. Go to SSL/TLS → Overview
2. Set encryption mode to: **Full (strict)**
   - This works because you have Let's Encrypt certificates via Traefik
   - If you have issues, temporarily use **Flexible** then switch back

3. Go to SSL/TLS → Edge Certificates
   - Enable "Always Use HTTPS" ✅
   - Enable "Automatic HTTPS Rewrites" ✅

#### Step 3: Test DNS Propagation

Wait 2-5 minutes, then test:

```bash
# Check if DNS is resolving through Cloudflare
dig n8n.leadingai.info +short
# Should show Cloudflare IPs (104.x.x.x or 172.x.x.x), not 66.94.121.10

# Test HTTPS access
curl -I https://n8n.leadingai.info
curl -I https://webui.leadingai.info
curl -I https://neo4j.leadingai.info
```

**Do not proceed to Phase 2 until all domains work through Cloudflare!**

---

### Phase 2: Lock Down Firewall to Cloudflare IPs Only

Once DNS is working through Cloudflare, run the firewall lockdown script:

```bash
# Dry run first (see what would happen)
/root/scripts/cloudflare_firewall_setup.sh --dry-run

# Apply changes
sudo /root/scripts/cloudflare_firewall_setup.sh
```

**What this script does:**
1. Backs up current UFW rules to `/root/backups/firewall_TIMESTAMP/`
2. Fetches latest Cloudflare IP ranges
3. Removes unrestricted access to ports 80/443
4. Adds rules to allow ONLY Cloudflare IPs to ports 80/443
5. Preserves SSH (22) and Tailscale (41641) access
6. Reloads UFW

**After running:**
- Test that all sites still work (they should, through Cloudflare)
- Direct IP access will be blocked: `http://66.94.121.10` should fail
- Cloudflare URLs should work: `https://n8n.leadingai.info` should work

---

### Phase 3: Close Direct Service Port Exposures

Now we'll close the remaining security gaps by modifying Docker containers.

#### 3A. Secure Portainer (Tailscale-Only Access)

**Current:** Portainer ports 9000/9443 are exposed to the internet
**Goal:** Bind to Tailscale IP only (100.66.28.67)

```bash
# Stop Portainer
cd /root/portainer
docker compose down

# Edit docker-compose.yml
nano docker-compose.yml
```

**Change:**
```yaml
    ports:
      - "9000:9000"
      - "9443:9443"
```

**To:**
```yaml
    ports:
      - "100.66.28.67:9000:9000"
      - "100.66.28.67:9443:9443"
```

**Restart:**
```bash
docker compose up -d
```

**Test:**
- ❌ Public access should fail: `http://66.94.121.10:9000`
- ✅ Tailscale access should work: `http://100.66.28.67:9000`

#### 3B. Remove n8n Direct Port (Traefik-Only Access)

**Current:** n8n accessible on port 5678 AND via Traefik
**Goal:** Remove direct port, use Traefik only

```bash
cd /root/local-ai-packaged

# Backup docker-compose.yml first
cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d)

# Edit docker-compose.yml
nano docker-compose.yml
```

**Find the n8n service** (around line 88-108) and **remove the ports section**:

**Change:**
```yaml
  n8n:
    <<: *service-n8n
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"    # <-- REMOVE THIS LINE
    expose:
      - 5678/tcp
```

**To:**
```yaml
  n8n:
    <<: *service-n8n
    container_name: n8n
    restart: unless-stopped
    expose:
      - 5678/tcp
```

**Restart:**
```bash
docker compose restart n8n
```

**Test:**
- ❌ Direct access should fail: `http://66.94.121.10:5678`
- ✅ Traefik access should work: `https://n8n.leadingai.info`

#### 3C. Secure Neo4j Ports

**Current:** Neo4j ports 7474 (browser) and 7687 (Bolt) exposed
**Goal:**
- Remove 7474 (use Traefik instead)
- Keep 7687 for internal Docker network connections only

```bash
cd /root/local-ai-packaged
nano docker-compose.yml
```

**Find the neo4j service** (around line 110-135):

**Change:**
```yaml
    ports:
      - "7474:7474"
      - "7687:7687"
```

**To:**
```yaml
    ports:
      - "127.0.0.1:7687:7687"  # Only localhost access for Bolt protocol
```

**Note:** Port 7474 is removed entirely since Traefik provides HTTPS access.

**Restart:**
```bash
docker compose restart neo4j
```

**Test:**
- ❌ Direct browser access should fail: `http://66.94.121.10:7474`
- ✅ Traefik access should work: `https://neo4j.leadingai.info`
- ✅ Bolt protocol should work for localhost/Docker: `bolt://127.0.0.1:7687`

---

### Phase 4: Verify Security Lockdown

Run these tests to confirm everything is secure:

```bash
# Test firewall rules
sudo ufw status verbose

# Test that direct IP access fails (should timeout or refuse)
curl -m 5 http://66.94.121.10
curl -m 5 http://66.94.121.10:5678
curl -m 5 http://66.94.121.10:7474
curl -m 5 http://66.94.121.10:9000

# Test that Cloudflare access works
curl -I https://n8n.leadingai.info
curl -I https://webui.leadingai.info
curl -I https://neo4j.leadingai.info
curl -I https://db.leadingai.info

# Test Tailscale access (from within Tailscale network)
# You'll need to run this from a device connected to Tailscale
curl -I http://100.66.28.67:9000  # Portainer
curl -I http://100.66.28.67:8080  # Filebrowser
curl -I https://100.66.28.67:9090 # Cockpit
```

**Expected results:**
- ✅ Direct IP access: **BLOCKED** (connection timeout or refused)
- ✅ Cloudflare URLs: **WORKING** (200 OK)
- ✅ Tailscale IPs: **WORKING** (200 OK)
- ✅ SSH: **WORKING** (from anywhere)

---

## Security Architecture After Setup

### Public Internet Access (via Cloudflare)
```
Internet → Cloudflare → ports 80/443 (Cloudflare IPs only) → Traefik → Services
```

**Services accessible via Cloudflare:**
- https://n8n.leadingai.info (n8n)
- https://webui.leadingai.info (Open WebUI)
- https://neo4j.leadingai.info (Neo4j Browser)
- https://wordpress.leadingai.info (WordPress)
- https://db.leadingai.info (Supabase Studio)
- https://traefik.leadingai.info (Traefik Dashboard)

### Tailscale VPN Access Only
```
Tailscale VPN → 100.66.28.67 → Services
```

**Services accessible via Tailscale:**
- http://100.66.28.67:9000 (Portainer)
- http://100.66.28.67:8080 (Filebrowser)
- https://100.66.28.67:9090 (Cockpit)

### Management Access
```
SSH: Port 22 (from anywhere, key-only auth)
Tailscale: Port 41641/udp (for VPN)
```

---

## Cloudflare Additional Security (Recommended)

After basic setup, consider these Cloudflare features:

### 1. Enable WAF (Web Application Firewall)
- Go to Security → WAF
- Set to "High" or create custom rules

### 2. Enable Rate Limiting
- Go to Security → Rate Limiting Rules
- Protect login endpoints (n8n, Portainer, Supabase)
- Example: Max 5 requests per minute to `/login` endpoints

### 3. Enable Bot Protection
- Go to Security → Bots
- Enable "Bot Fight Mode"

### 4. Create Access Policies (Cloudflare Zero Trust)
- Require authentication for sensitive services
- Example: Require Google login for Portainer, n8n
- Go to Zero Trust → Access → Applications

### 5. Enable DDoS Protection
- Go to Security → DDoS
- Review automatic protection settings

---

## Rollback Procedures

### If You Get Locked Out

**Option 1: Revert Firewall via Console**

Access your server via Contabo console (not SSH) and run:

```bash
# Reset UFW to defaults
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 41641/udp
ufw --force enable
```

**Option 2: Restore from Backup**

```bash
# Find your backup
ls -la /root/backups/firewall_*/

# Restore from specific backup
BACKUP_DIR="/root/backups/firewall_YYYYMMDD_HHMMSS"

# View rules to restore
cat "$BACKUP_DIR/ufw_rules_before.txt"

# Manually re-add rules or reset as above
```

### If Services Don't Work Through Cloudflare

1. Check DNS is properly configured (orange cloud)
2. Check Cloudflare SSL mode is "Full (strict)"
3. Temporarily set to "DNS only" (grey cloud) to test
4. Check Traefik logs: `docker logs traefik`

### If You Need to Revert Docker Changes

```bash
# Restore docker-compose backup
cd /root/local-ai-packaged
cp docker-compose.yml.backup-YYYYMMDD docker-compose.yml
docker compose restart

# Or restore Portainer
cd /root/portainer
# Edit docker-compose.yml back to original
docker compose up -d
```

---

## Maintenance

### Update Cloudflare IP Ranges (Monthly)

Cloudflare occasionally updates their IP ranges. Run this monthly:

```bash
/root/scripts/cloudflare_firewall_setup.sh
```

### Monitor Failed Access Attempts

```bash
# Check fail2ban
fail2ban-client status sshd

# Check UFW logs
tail -f /var/log/ufw.log

# Check for blocked HTTP requests
grep -i "UFW BLOCK" /var/log/ufw.log | grep -E "(80|443)"
```

---

## Summary Checklist

- [ ] Phase 1: Configure Cloudflare DNS with proxy enabled
- [ ] Phase 1: Set SSL/TLS to "Full (strict)"
- [ ] Phase 1: Test all domains work through Cloudflare
- [ ] Phase 2: Run cloudflare_firewall_setup.sh script
- [ ] Phase 2: Verify ports 80/443 only accept Cloudflare IPs
- [ ] Phase 3A: Bind Portainer to Tailscale IP
- [ ] Phase 3B: Remove n8n direct port exposure
- [ ] Phase 3C: Secure Neo4j ports
- [ ] Phase 4: Run verification tests
- [ ] Document any custom configurations
- [ ] Set monthly reminder to update Cloudflare IPs

---

**Prepared by:** System Administrator
**Last Updated:** November 13, 2025
**Related Documents:**
- `/root/SECURITY_INCIDENT_REPORT_20251112.md`
- `/root/NEW_SERVER_ACCESS_URLS.md`
- `/root/FILE_MANAGEMENT_TOOLS_README.md`
