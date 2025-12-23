# New Server (66.94.121.10) - Access URLs and Status

**Date**: 2025-11-13 (Updated after Cloudflare security implementation)
**Server**: leadingai004.contaboserver.net (66.94.121.10)

---

## 🔒 SECURITY STATUS

**✅ All services now secured behind Cloudflare proxy**
- DDoS protection enabled
- WAF (Web Application Firewall) active
- Ports 80/443 restricted to Cloudflare IPs only
- Direct IP access blocked for web services
- Management tools restricted to Tailscale VPN only

---

## ✅ PUBLIC SERVICES (via Cloudflare HTTPS)

All public services are accessible via HTTPS through Cloudflare proxy:

| Service | Access URL | Status | Credentials |
|---------|-----------|--------|-------------|
| **n8n** | `https://n8n.leadingai.info` | ✅ Running | (Set up on first access) |
| **Open WebUI** | `https://webui.leadingai.info` | ✅ Running | AI Chat Interface |
| **Neo4j Browser** | `https://neo4j.leadingai.info` | ✅ Running | Username: `neo4j`<br>Password: `riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj` |
| **Supabase Studio** | `https://db.leadingai.info` | ✅ Running | Username: `systemai`<br>Password: `riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Ew6` |
| **WordPress** | `https://wordpress.leadingai.info` | ✅ Running | WordPress Site |
| **Traefik Dashboard** | `https://traefik.leadingai.info` | ✅ Running | Username: `systemccg`<br>Password: `7lly3bwA$HA*Z4Q` |

**Security Notes:**
- All traffic routed through Cloudflare (DDoS protection, WAF, caching)
- Let's Encrypt SSL certificates managed by Traefik
- HTTP automatically redirects to HTTPS
- Direct IP access blocked (firewall restricted to Cloudflare IPs only)

---

## 🔒 MANAGEMENT SERVICES (Tailscale VPN Only)

**Tailscale Network**: Connected and authenticated
**Server Tailscale IP**: `100.66.28.67`
**Tailscale Network Name**: leadingai004

| Service | Tailscale Access URL | Port | Credentials | Notes |
|---------|---------------------|------|-------------|-------|
| **Portainer** | `http://100.66.28.67:9000`<br>`https://100.66.28.67:9443` | 9000, 9443 | Username: `admin`<br>Password: `PortainerAdmin2024` | Docker container management (v2.20.2 for Docker 29.0 compatibility) |
| **Filebrowser** | `http://100.66.28.67:8080` | 8080 | Username: `systemccg`<br>Password: (user-set) | Web-based file manager with full root filesystem access |
| **Cockpit** | `https://100.66.28.67:9090` | 9090 | Username: `root`<br>Password: (server root password) | System administration panel with Navigator file browser |
| **Netdata** | `http://100.66.28.67:19999` | 19999 | No authentication required | Real-time system monitoring with Docker container metrics |
| **Uptime Kuma** | `http://100.66.28.67:3001` | 3001 | Username: `systemccg`<br>Password: `7lly3bwA$HA*Z4Q` | Uptime monitoring and status pages |

**Monitoring & Alerts:**
- **Email**: All alerts sent to `gwasmuth@gmail.com`
- **SMTP**: Gmail (smtp.gmail.com:587) via msmtp
- **Netdata**: System monitoring (CPU, RAM, Disk, Docker containers)
  - Alert Types: WARNING, CRITICAL, CLEAR
  - Configuration: `/etc/netdata/health_alarm_notify.conf` (in container)
  - Logs: `docker exec netdata cat /var/log/msmtp.log`
- **Uptime Kuma**: Service uptime monitoring (6 services configured)
  - Monitors: n8n, Open WebUI, Neo4j, Supabase, WordPress, Traefik
  - Check Interval: 60 seconds
  - Email alerts on service down/recovery
- **Lynis**: Security auditing tool (command line)
  - Version: 3.0.9
  - Last audit: 2025-11-14
  - Security score: 66/100
  - Usage: `lynis audit system --quick`

**Important Security Notes:**
- ⚠️ These services are ONLY accessible via Tailscale VPN (IP: 100.66.28.67)
- You MUST be connected to Tailscale VPN to access these services
- Services are NOT exposed on the public internet
- Portainer now restricted to Tailscale after Cloudflare security implementation
- Filebrowser has full root filesystem access (/) - use with caution

**To Access:**
1. Connect to your Tailscale VPN
2. Navigate to the Tailscale URLs listed above (100.66.28.67)
3. Your Tailscale client will route traffic through the secure VPN tunnel

---

## 📊 MONITORING & ALERTING

### Uptime Kuma - Service Monitoring

**6 Services Actively Monitored** (checked every 60 seconds):

| Service | URL | Status Codes | Email Alert |
|---------|-----|--------------|-------------|
| n8n | https://n8n.leadingai.info | 200-299 | ✅ |
| Open WebUI | https://webui.leadingai.info | 200-299 | ✅ |
| Neo4j Browser | https://neo4j.leadingai.info | 200-299 | ✅ |
| Supabase Studio | https://db.leadingai.info | 200-299, 401 | ✅ |
| WordPress | https://wordpress.leadingai.info | 200-299 | ✅ |
| Traefik Dashboard | https://traefik.leadingai.info | 200-299, 401 | ✅ |

**Alert Behavior**:
- Service down after 3 consecutive failed checks → Email sent
- Service recovery → Email sent
- Retry interval: 60 seconds
- Max retries: 3

**Database**:
- SQLite database: `/app/data/kuma.db` (in container)
- Backup: `docker cp uptime-kuma:/app/data /root/backups/uptime-kuma-$(date +%Y%m%d)`

### Netdata - System Monitoring

**Monitors**:
- System: CPU, RAM, Disk, Network, Load average
- Docker: All containers (CPU, RAM, Network, I/O)
- Services: systemd services, processes
- Storage: Disk usage, I/O latency

**Alert Thresholds** (default):
- CPU > 80% (WARNING), > 95% (CRITICAL)
- RAM > 80% (WARNING), > 95% (CRITICAL)
- Disk > 80% (WARNING), > 95% (CRITICAL)
- Docker container stopped (CRITICAL)

**Data Retention**: 3 hours (default, configurable)

### Lynis - Security Auditing

**Last Audit**: 2025-11-14 01:41:59
**Security Score**: 66/100 (Good hardening, room for improvement)
**Status**: System hardened beyond defaults

**Key Findings**:
- ✅ SSH hardening in place
- ✅ Firewall active (UFW)
- ✅ fail2ban protecting SSH
- ⚠️ Additional password policies recommended
- ⚠️ GRUB password not set
- ⚠️ Some systemd services could be hardened

**Run Audits**:
```bash
# Quick audit (5 minutes)
lynis audit system --quick

# Full audit (15 minutes)
lynis audit system

# View last results
cat /var/log/lynis.log | grep "Hardening index"
```

**Detailed Report**: `/root/monitoring/LYNIS_SECURITY_AUDIT.md`

---

## 📝 CREDENTIALS & PASSWORDS

### Neo4j
- **Username**: `neo4j`
- **Password**: `riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj`
- **Access**: https://neo4j.leadingai.info
- **Bolt Protocol**: `bolt://localhost:7687` (localhost only, for internal Docker connections)

### Supabase
- **Username**: `systemai`
- **Password**: `riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Ew6`
- **Access**: https://db.leadingai.info
- **Database Password**: `CPO3POCFCM3BC7g8QbUmdCPSqR7CDp4Z`
- **Postgres Host**: `db` (internal Docker hostname)
- **Postgres Port**: `5432`
- **Postgres DB**: `postgres`

### Portainer
- **Username**: `admin`
- **Password**: `PortainerAdmin2024`
- **Access**: http://100.66.28.67:9000 (Tailscale VPN only)
- **Version**: v2.20.2 (for Docker 29.0 API compatibility)

### Filebrowser
- **Username**: `systemccg`
- **Password**: (user-set during first login)
- **Access**: http://100.66.28.67:8080 (Tailscale VPN only)
- **Root Path**: `/` (full filesystem access)

### Traefik Dashboard
- **Username**: `systemccg`
- **Password**: `7lly3bwA$HA*Z4Q`
- **Access**: https://traefik.leadingai.info

### Uptime Kuma
- **Username**: `systemccg`
- **Password**: `7lly3bwA$HA*Z4Q`
- **Access**: http://100.66.28.67:3001 (Tailscale VPN only)
- **Email Notifications**: Configured to gwasmuth@gmail.com
- **Monitors**: 6 active (all public services)

### MySQL/WordPress
- **Root Password**: `changeme123` (⚠️ change this!)
- **WordPress DB User**: `wordpress`
- **WordPress DB Password**: `wordpress123` (⚠️ change this!)
- **Database Name**: `wordpress`

### Coolify
- **Access**: http://66.94.121.10:8888 (if still needed)
- **Setup**: First-time access creates admin user

---

## 🤖 MCP SERVERS (Model Context Protocol)

### n8n-mcp
- **Status**: ✅ Running and Healthy
- **Container**: `n8n-mcp`
- **Port**: 3000 (internal only, not exposed)
- **Database**: SQLite (`/app/data/nodes.db`)
- **Purpose**: MCP server providing n8n workflow automation documentation and tools
- **Configuration**:
  - AUTH_TOKEN: `e6a7170ce4491f1ae2a9b27179d07f06ffee1300ea144424ec5534e03e142ecd`
  - N8N_API_URL: `https://n8n.leadingai.info`
  - Tools: 39 tools (includes n8n API management)
- **Docker Compose**: `/root/mcp/n8n-mcp/docker-compose.yml`
- **Usage**: Connect via MCP client (stdio mode only)

### graphiti-mcp-neo4j
- **Status**: ✅ Running (Neo4j connected)
- **Container**: `graphiti-mcp-neo4j`
- **Port**: 8030 (external) → 8002 (internal)
- **Database**: Neo4j (connected to `local-ai-packaged-neo4j-1`)
- **Purpose**: Knowledge graph MCP server using Graphiti with Neo4j backend
- **Configuration**:
  - NEO4J_URI: `bolt://local-ai-packaged-neo4j-1:7687`
  - NEO4J_USER: `neo4j`
  - NEO4J_PASSWORD: `riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj`
  - OPENAI_API_KEY: Configured in .env
  - MODEL_NAME: `gpt-4.1-mini`
  - Transport: SSE (Server-Sent Events)
- **Docker Compose**: `/root/mcp/graphiti/docker-compose.yml`
- **MCP Endpoint**: `http://66.94.121.10:8030/sse`
- **Usage**: Connect via MCP client with SSE transport

**Important Notes:**
- MCP servers are NOT web interfaces - they require MCP clients (like Claude Desktop, Cline, etc.)
- Access at `http://66.94.121.10:8030` will return 404 - this is expected
- Use the `/sse` endpoint for MCP client connections

**Claude Desktop Configuration Example:**
```json
{
  "mcpServers": {
    "graphiti": {
      "url": "http://66.94.121.10:8030/sse",
      "transport": "sse"
    }
  }
}
```

---

## 🗑️ REMOVED SERVICES

The following services were removed:
- ❌ BT-Panel (aaPanel) - Removed for security (potential vulnerability vector)
- ❌ Flowise (port 3001)
- ❌ Qdrant (port 6333)
- ❌ Caddy (ports 80/443 - replaced by Traefik)
- ❌ nginx (not present)

---

## 🔧 CONFIGURATION FILES

### Docker Compose Locations
- **Local AI Stack**: `/root/local-ai-packaged/docker-compose.yml`
- **Traefik**: `/root/traefik/docker-compose.yml`
- **Supabase**: `/root/local-ai-packaged/supabase/docker/docker-compose.yml`
- **Coolify**: `/data/coolify/source/docker-compose.yml` + `docker-compose.prod.yml`
- **WordPress**: `/root/wordpress/docker-compose.yml`
- **n8n-mcp**: `/root/mcp/n8n-mcp/docker-compose.yml`
- **graphiti-mcp**: `/root/mcp/graphiti/docker-compose.yml`
- **Portainer**: `/root/portainer/docker-compose.yml` (Tailscale-only)
- **Filebrowser**: `/root/filebrowser/docker-compose.yml` (Tailscale-secured)
- **Netdata**: `/root/monitoring/docker-compose.yml` (Tailscale-only)
- **Uptime Kuma**: `/root/monitoring/docker-compose.yml` (Tailscale-only)

### Environment Files
- **Local AI**: `/root/local-ai-packaged/.env`
- **Supabase**: `/root/local-ai-packaged/supabase/docker/.env`
- **Traefik**: `/root/traefik/traefik.yml`
- **Traefik Dynamic**: `/root/traefik/dynamic-conf.yml` (file-based routing config)
- **Coolify**: `/data/coolify/source/.env`
- **n8n-mcp**: `/root/mcp/n8n-mcp/.env`
- **graphiti-mcp**: `/root/mcp/graphiti/.env`

### Tailscale Configuration
- **Status**: Active and authenticated
- **Server IP**: `100.66.28.67`
- **Network Name**: leadingai004
- **Tailscale State**: `/var/lib/tailscale/tailscaled.state`

---

## 🚀 QUICK START COMMANDS

### Check All Services
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Restart Services
```bash
# Local AI Stack (includes n8n, Neo4j, Open WebUI)
cd /root/local-ai-packaged && docker compose restart

# Supabase Stack
cd /root/local-ai-packaged/supabase/docker && docker compose restart

# Traefik
cd /root/traefik && docker compose restart

# Portainer
cd /root/portainer && docker compose restart

# WordPress
cd /root/wordpress && docker compose restart
```

### View Logs
```bash
# Core services
docker logs n8n
docker logs local-ai-packaged-neo4j-1
docker logs open-webui
docker logs traefik

# Supabase services
docker logs supabase-kong
docker logs supabase-studio
docker logs supabase-meta
docker logs supabase-db

# Management
docker logs portainer
```

### Start Stopped Supabase Services
```bash
# If supabase-meta or supabase-studio are stopped
docker start supabase-meta
docker start supabase-studio
docker restart supabase-kong
```

---

## 📊 SYSTEM STATUS

### Core Services
- **Traefik**: ✅ Running (v3.6.0, file-based provider)
- **Neo4j**: ✅ Running (Browser via HTTPS, Bolt on localhost:7687)
- **Open WebUI**: ✅ Running (HTTPS via Cloudflare)
- **n8n**: ✅ Running (HTTPS via Cloudflare)
- **WordPress**: ✅ Running (HTTPS via Cloudflare)

### Supabase Services
- **supabase-db**: ✅ Running (Postgres 15.8)
- **supabase-kong**: ✅ Running (API Gateway)
- **supabase-studio**: ✅ Running (Web UI)
- **supabase-meta**: ✅ Running (Database metadata service)
- **supabase-rest**: ✅ Running (PostgREST API)
- **supabase-realtime**: ✅ Running
- **supabase-auth**: Running (if started)
- **supabase-storage**: Running (if started)

### Management & Monitoring Tools
- **Portainer**: ✅ Running (Tailscale-only, v2.20.2)
- **Filebrowser**: ✅ Running (Tailscale-only)
- **Cockpit**: ✅ Running (Tailscale-only)
- **Netdata**: ✅ Running (Tailscale-only, v2.7.0) - System monitoring with email alerts
- **Uptime Kuma**: ✅ Running (Tailscale-only, v1.x) - Service uptime monitoring with email alerts
- **Lynis**: ✅ Installed (v3.0.9) - Security auditing (command line)

---

## 🔐 SECURITY NOTES

### Implemented Security Measures

1. **Cloudflare Protection** (Implemented 2025-11-13):
   - All public services behind Cloudflare proxy
   - DDoS protection active
   - WAF (Web Application Firewall) enabled
   - Ports 80/443 restricted to Cloudflare IPs only
   - Direct IP access blocked

2. **Firewall (UFW)**:
   - SSH: Port 22 (key-only authentication + fail2ban)
   - HTTP/HTTPS: Ports 80/443 (Cloudflare IPs only)
   - Tailscale: Port 41641 (VPN tunnel)
   - All other ports: DENIED

3. **SSH Hardening**:
   - Password authentication disabled (key-only)
   - Fail2ban active with 3-attempt threshold, 24-hour bans
   - Root login: prohibit-password mode

4. **Service Isolation**:
   - Management tools (Portainer, Filebrowser, Cockpit): Tailscale VPN only
   - Public services: HTTPS via Cloudflare only
   - No direct port exposure for n8n, Neo4j browser

5. **SSL/TLS**:
   - Let's Encrypt certificates managed by Traefik
   - Automatic HTTP to HTTPS redirection
   - Certificate auto-renewal

### Security Recommendations

1. **Change default passwords**:
   - ⚠️ MySQL root password (currently: changeme123)
   - ⚠️ WordPress database password (currently: wordpress123)
   - Consider rotating Neo4j password if used in production

2. **Regular Maintenance**:
   - Update Cloudflare IP ranges monthly: `/root/scripts/cloudflare_firewall_setup.sh`
   - Review fail2ban logs: `fail2ban-client status sshd`
   - Check UFW logs: `tail -f /var/log/ufw.log`

3. **Optional Enhancements**:
   - Configure Cloudflare WAF rules for specific threats
   - Set up rate limiting for login endpoints
   - Enable Cloudflare Bot Fight Mode
   - Configure Zero Trust Access for sensitive services

---

## 🆘 TROUBLESHOOTING

### Supabase Studio Shows No Tables

**Issue**: Table editor is empty or shows "An unexpected error occurred"

**Solution**:
```bash
# Check if supabase-meta is running
docker ps | grep supabase-meta

# If not running or unhealthy, start it
docker start supabase-meta

# Wait 10 seconds, then restart studio
sleep 10
docker restart supabase-studio

# If still not working, check PG_META_CRYPTO_KEY exists in .env
grep PG_META_CRYPTO_KEY /root/local-ai-packaged/supabase/docker/.env
```

### Service Won't Start
```bash
# Check logs
docker logs <container-name>

# Restart specific service
docker restart <container-name>

# Check if port is in use
ss -tlnp | grep <port>
```

### Neo4j Connection Issues
- Verify username is `neo4j` (not systemai)
- Check password in `/root/local-ai-packaged/.env` (NEO4J_AUTH)
- Access via https://neo4j.leadingai.info (not direct IP)

### Traefik Not Working
- Check Traefik logs: `docker logs traefik`
- Verify DNS points to Cloudflare IPs: `dig n8n.leadingai.info`
- Check dynamic config: `cat /root/traefik/dynamic-conf.yml`
- Ensure services are on traefik network: `docker inspect <container> | grep Networks`

### Can't Access Services via Cloudflare
- Verify DNS is proxied (orange cloud) in Cloudflare dashboard
- Check Cloudflare SSL/TLS mode is "Full (strict)"
- Wait 5-10 minutes for DNS propagation
- Test from external network (not localhost)

### Portainer Shows "Failed loading environment" Error
- **Issue**: Docker 29.0+ requires API v1.44+, but Portainer 2.33.3 uses v1.41
- **Solution**: Already using Portainer 2.20.2 (compatible version)
- **Reference**: https://github.com/portainer/portainer/issues/12925

---

## 📝 CHANGELOG

### 2025-11-14 - System Monitoring & Security Tools
- ✅ Installed Netdata v2.7.0 for real-time system monitoring
  - Configured for Tailscale-only access (100.66.28.67:19999)
  - Auto-discovery of all Docker containers and system metrics
  - Configured email alerts via Gmail (gwasmuth@gmail.com)
  - Test emails sent successfully for WARNING, CRITICAL, and CLEAR alerts
  - Documentation: `/root/monitoring/NETDATA_ALERTS_REFERENCE.md`
- ✅ Installed Uptime Kuma v1.x for uptime monitoring
  - Access: http://100.66.28.67:3001 (Tailscale VPN only)
  - Created user: systemccg with password 7lly3bwA$HA*Z4Q
  - Configured 6 monitors: n8n, Open WebUI, Neo4j, Supabase, WordPress, Traefik
  - Set up email notifications to gwasmuth@gmail.com via Gmail SMTP
  - Monitors check every 60 seconds, email on down/recovery
  - Database: SQLite at `/app/data/kuma.db` (in container)
  - Documentation: `/root/monitoring/UPTIME_KUMA_SETUP_COMPLETE.md`
- ✅ Installed Lynis v3.0.9 for security auditing
  - Completed initial security audit
  - Security score: 66/100 (good hardening, room for improvement)
  - Identified key improvements: password policies, GRUB password, service hardening
  - Audit logs: `/var/log/lynis.log`
  - Documentation: `/root/monitoring/LYNIS_SECURITY_AUDIT.md`
- ✅ Changed Traefik credentials to username: systemccg, password: 7lly3bwA$HA*Z4Q
- ✅ Created comprehensive monitoring documentation in `/root/monitoring/`

### 2025-11-13 - Cloudflare Security Implementation
- ✅ Implemented Cloudflare proxy for all public services
- ✅ Locked down ports 80/443 to Cloudflare IPs only (15 IPv4 + 7 IPv6 ranges)
- ✅ Upgraded Traefik from v2.11 to v3.6.0
- ✅ Switched Traefik to file-based provider (fixes Docker API compatibility)
- ✅ Restricted Portainer to Tailscale VPN only (was public before)
- ✅ Removed n8n direct port exposure (Traefik-only access)
- ✅ Secured Neo4j ports (browser via Traefik, Bolt on localhost only)
- ✅ Fixed Supabase Studio table editor (added PG_META_CRYPTO_KEY, started supabase-meta)
- ✅ Created firewall automation script: `/root/scripts/cloudflare_firewall_setup.sh`
- ✅ Documentation: `/root/CLOUDFLARE_SETUP_GUIDE.md`, `/root/CLOUDFLARE_IMPLEMENTATION_SUMMARY.md`
- ✅ Security incident documented: `/root/SECURITY_INCIDENT_REPORT_20251112.md`

### 2025-11-12 - File Management Tools Installation
- ✅ Installed Cockpit Navigator v0.5.10 for web-based file browsing
- ✅ Installed Portainer 2.20.2 (downgraded from 2.33.3 for Docker 29.0 compatibility)
- ✅ Installed Filebrowser with full root filesystem access
- ✅ All management services configured behind Tailscale VPN (100.66.28.67)

---

---

## 📚 MONITORING DOCUMENTATION

Complete guides available in `/root/monitoring/`:

| Document | Description |
|----------|-------------|
| `MONITORING_TOOLS_GUIDE.md` | Overview of all monitoring tools (Netdata, Uptime Kuma, Lynis) |
| `NETDATA_ALERTS_REFERENCE.md` | Netdata email alerts configuration and commands |
| `NETDATA_UI_GUIDE.md` | How to navigate Netdata dashboard |
| `EMAIL_ALERTS_SETUP.md` | Complete email alert setup guide (Gmail/SendGrid) |
| `UPTIME_KUMA_SETUP_COMPLETE.md` | Uptime Kuma configuration and usage guide |
| `LYNIS_SECURITY_AUDIT.md` | Security audit results and improvement recommendations |

**Quick Access**:
```bash
# View all monitoring documentation
ls -lah /root/monitoring/*.md

# View specific guides
cat /root/monitoring/MONITORING_TOOLS_GUIDE.md
cat /root/monitoring/UPTIME_KUMA_SETUP_COMPLETE.md
cat /root/monitoring/LYNIS_SECURITY_AUDIT.md
```

---

**Migration Status**: ✅ Complete and secured
**Last Updated**: 2025-11-14 01:51 CET
**Security Level**: ✅ Enhanced with Cloudflare protection + VPN-only management access + Comprehensive monitoring
**Monitoring Status**: ✅ System monitoring (Netdata) + Service uptime (Uptime Kuma) + Security auditing (Lynis)
