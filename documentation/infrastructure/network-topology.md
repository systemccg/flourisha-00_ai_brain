# Network Topology - Flourisha PAI System

**Location:** `/root/flourisha/00_AI_Brain/documentation/infrastructure/network-topology.md`
**Purpose:** Network architecture and Tailscale integration
**Last Updated:** 2025-11-22

---

## Overview

The Flourisha PAI system runs on a Contabo VPS with **Tailscale networking** for secure remote access. **NEVER use localhost for server-based applications** - always use Tailscale IP or domain names.

---

## Server Identity

**Provider:** Contabo VPS
**OS:** Ubuntu (Linux 6.8.0-87-generic)
**Tailscale Hostname:** `leadingai004`
**Tailscale IP:** `100.66.28.67`
**Tailscale DNS:** `leadingai004.tail8b1922.ts.net`

**Verification:**
```bash
# Check Tailscale status
tailscale status

# Get Tailscale IP
tailscale ip -4
```

---

## Network Architecture Principles

### 🚫 NEVER Use Localhost on Server

**WRONG:**
```bash
# ❌ Don't do this on a server
VITE_API_URL=http://localhost:8001
```

**CORRECT:**
```bash
# ✅ Use Tailscale IP or domain
VITE_API_URL=http://100.66.28.67:8001
# or
VITE_API_URL=https://api.leadingai.info
```

**Why?**
- Server is not your local machine
- Services need to be accessible across network
- Localhost only works within the same machine
- Tailscale provides secure mesh networking

---

## Tailscale Network Devices

Current network topology:

| Device | Tailscale IP | Hostname | Type | Purpose |
|--------|--------------|----------|------|---------|
| Contabo VPS | `100.66.28.67` | `leadingai004` | Linux server | Main PAI infrastructure |
| Windows PC | `100.105.187.91` | `accelerate` | Windows | Development machine |
| Android Phone | `100.77.219.32` | `google-pixel-8-pro` | Android | Mobile access |

**Check network status:**
```bash
tailscale status
```

---

## Service Port Allocation

### Docker Services (via Traefik)

**Public HTTPS Endpoints (via Traefik):**
- **n8n:** https://n8n.leadingai.info → n8n:5678
- **Supabase Studio:** https://db.leadingai.info → supabase-studio:3000
- **Neo4j Browser:** https://neo4j.leadingai.info → neo4j:7474
- **Open WebUI:** https://webui.leadingai.info → open-webui:8080

**Direct Port Mappings:**
- **Traefik:** 80 (HTTP), 443 (HTTPS)
- **Supabase Kong:** 8000 (REST API), 8443 (HTTPS)
- **Supabase Analytics:** 4000
- **Neo4j (local):** 127.0.0.1:7687 (Bolt protocol)
- **Graphiti MCP:** 8030 (exposed to 0.0.0.0)

### Tailscale Access Patterns

**From Windows PC (accelerate) to server:**
```bash
# SSH via Tailscale
ssh root@100.66.28.67

# Access service directly
curl http://100.66.28.67:8000/health
```

**From mobile device:**
- Access via Tailscale IP when on network
- Or use public domains (*.leadingai.info)

---

## Flourisha App Configuration

**Backend API:**
- **Development:** `http://100.66.28.67:8001`
- **Production (future):** `https://flourisha-api.leadingai.info`

**Frontend:**
- **Development:** Access via Tailscale - `http://100.66.28.67:5173`
- **Production (future):** `https://flourisha.leadingai.info`

**Configuration file:**
```bash
# /root/flourisha/01f_Flourisha_Projects/flourisha-app/web/.env.local
VITE_API_URL=http://100.66.28.67:8001
```

---

## Domain Routing (*.leadingai.info)

**DNS Setup:**
- All `*.leadingai.info` domains point to Contabo public IP
- Cloudflare manages DNS and SSL
- Traefik reverse proxy routes by hostname

**SSL/TLS:**
- Traefik + Let's Encrypt for automatic HTTPS
- Certificates auto-renewed

**Adding new subdomain:**
1. Add Traefik labels to docker-compose.yml
2. DNS automatically resolves via wildcard
3. Traefik issues certificate automatically

---

## Service Communication Patterns

### Internal Docker Network

Services in same docker-compose stack communicate via service names:

```yaml
# Example: Backend connecting to Supabase
DATABASE_URL=postgresql://postgres:postgres@supabase-db:5432/postgres
```

**Good:**
- `http://supabase-db:5432` (within Docker network)
- `http://neo4j:7474` (within Docker network)

**Bad:**
- `http://localhost:5432` ❌
- `http://127.0.0.1:7474` ❌

### External Access to Services

**From outside Docker (e.g., flourisha-app backend):**

```python
# Connect to Neo4j
NEO4J_URI = "bolt://127.0.0.1:7687"  # Localhost OK because mapped
# or
NEO4J_URI = "bolt://100.66.28.67:7687"  # Tailscale IP

# Connect to Supabase
SUPABASE_URL = "http://100.66.28.67:8000"  # Via Kong gateway
# or
SUPABASE_URL = "https://db.leadingai.info"  # Via domain
```

### Frontend to Backend Communication

**Browser-based frontend (React) needs network-accessible backend:**

```typescript
// ❌ WRONG - localhost only works on the server itself
const API_URL = "http://localhost:8001"

// ✅ CORRECT - Tailscale IP accessible from any Tailscale device
const API_URL = "http://100.66.28.67:8001"

// ✅ BEST - Public domain for production
const API_URL = "https://flourisha-api.leadingai.info"
```

---

## Security Considerations

### Firewall (UFW)

```bash
# Check firewall status
ufw status

# Typical rules
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw allow 41641/udp   # Tailscale
```

### Tailscale Security

- **Mesh networking:** Direct encrypted connections between devices
- **ACLs:** Control which devices can access which services
- **MagicDNS:** Automatic DNS resolution for Tailscale devices
- **No public exposure:** Services only accessible via Tailscale or reverse proxy

### Best Practices

1. **Use Tailscale for development access** - Secure mesh network
2. **Use public domains for production** - SSL/TLS via Traefik
3. **Never expose database ports publicly** - 0.0.0.0 bindings only when necessary
4. **Use Docker networks for inter-service communication** - Isolated by default

---

## Common Access Patterns

### Accessing Services from Different Locations

**From Contabo server itself:**
```bash
# Via Docker service name (if in same network)
curl http://n8n:5678

# Via localhost (if port mapped)
curl http://localhost:8000

# Via Tailscale IP
curl http://100.66.28.67:8000

# Via public domain
curl https://n8n.leadingai.info
```

**From Windows PC (via Tailscale):**
```bash
# Via Tailscale IP
curl http://100.66.28.67:8000

# Via Tailscale DNS
curl http://leadingai004.tail8b1922.ts.net:8000

# Via public domain
curl https://n8n.leadingai.info
```

**From mobile app (React Native):**
```typescript
// Development (on Tailscale network)
const API_URL = "http://100.66.28.67:8001"

// Production (public internet)
const API_URL = "https://flourisha-api.leadingai.info"
```

---

## Troubleshooting

### Service Not Accessible

**Check if service is running:**
```bash
docker ps | grep <service-name>
```

**Check port binding:**
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep <service-name>
```

**Check from server:**
```bash
curl http://localhost:<port>
```

**Check via Tailscale:**
```bash
curl http://100.66.28.67:<port>
```

**Check firewall:**
```bash
ufw status | grep <port>
```

### Tailscale Connection Issues

**Restart Tailscale:**
```bash
systemctl restart tailscaled
```

**Check Tailscale status:**
```bash
tailscale status
```

**Verify connectivity:**
```bash
ping 100.66.28.67
```

---

## Port Planning

### Reserved Ports

| Port Range | Purpose | Example |
|------------|---------|---------|
| 80, 443 | Traefik (HTTP/HTTPS) | Public web traffic |
| 8000-8099 | Application APIs | Supabase Kong (8000), Flourisha API (8001) |
| 5000-5999 | Web frontends | n8n (5678), Flourisha web (5173) |
| 7000-7999 | Databases | Neo4j (7474, 7687) |
| 3000-3999 | Admin panels | Supabase Studio (3000) |
| 4000-4999 | Analytics/Monitoring | Supabase Analytics (4000) |

### Allocation Strategy

1. **Check existing allocations:**
   ```bash
   docker ps --format "table {{.Names}}\t{{.Ports}}"
   ```

2. **Choose port from appropriate range**

3. **Update docker-compose.yml:**
   ```yaml
   ports:
     - "8001:8000"  # host:container
   ```

4. **Document in this file**

---

## Quick Reference

**Get Tailscale IP:**
```bash
tailscale ip -4
```

**List all services and ports:**
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

**Test service accessibility:**
```bash
# From server
curl http://localhost:<port>

# Via Tailscale
curl http://100.66.28.67:<port>

# Via domain
curl https://<subdomain>.leadingai.info
```

**Check what's listening on a port:**
```bash
ss -tlnp | grep :<port>
```

---

## Future Considerations

### Scaling

- Multiple servers: Add to Tailscale network
- Load balancing: Via Traefik or external LB
- Database replication: PostgreSQL streaming replication

### Monitoring

- Network metrics via Netdata
- Service health via Uptime Kuma
- Tailscale connectivity monitoring

---

**Version:** 1.0
**Created:** 2025-11-22
**Maintainer:** Flourisha AI System
