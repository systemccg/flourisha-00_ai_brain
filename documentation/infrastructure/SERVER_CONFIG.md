# Server Configuration - CRITICAL

**Last Updated:** 2025-12-04

## Server Information (DO NOT FORGET)

- **Server IP (IPv4):** `66.94.121.10`
- **Server Hostname:** `leadingai.info`
- **Public URL:** `https://leadingai.info`

This information is hardcoded in `/root/flourisha/00_AI_Brain/.flourisha-config` and sourced by all scripts.

## Testing Commands

### Always use SERVER_IP, never localhost!

```bash
# WRONG - this won't work on a server
curl http://localhost:8000/api/health

# RIGHT - use the actual server IP
curl https://66.94.121.10/api/health

# RIGHT - or use the domain name
curl https://leadingai.info/api/health
```

### Test a Sandbox

```bash
# Get the sandbox short ID (first 12 chars of full container ID)
SHORT_ID=$(echo $SANDBOX_ID | cut -c1-12)

# Test via server IP with Host header
curl -k -s -H "Host: qa-${SHORT_ID}.leadingai.info" https://66.94.121.10/api/health

# Or test via domain name directly (if DNS is configured)
curl -k -s https://qa-${SHORT_ID}.leadingai.info/api/health
```

## Configuration Files

1. **Central Config** (source this in all scripts):
   - Path: `/root/flourisha/00_AI_Brain/.flourisha-config`
   - Contains: SERVER_IP, SERVER_HOSTNAME, all critical settings
   - Auto-sourced by: `docker-sandbox-cli.sh`

2. **Docker Sandbox CLI**:
   - Path: `/root/flourisha/00_AI_Brain/scripts/docker-sandbox-cli.sh`
   - Sources: `.flourisha-config`

3. **Traefik Dynamic Config**:
   - Path: `/root/traefik/dynamic-conf.yml`
   - Updated dynamically when sandboxes are created

## Key Files to Update if Server Changes

If you ever move to a different server IP or hostname, update these files:

1. `/root/flourisha/00_AI_Brain/.flourisha-config` - SERVER_IP and SERVER_HOSTNAME
2. `/root/traefik/dynamic-conf.yml` - Update any hardcoded URLs
3. DNS records - Update A/AAAA records to point to new IP

## Sandbox URL Pattern

- **Format:** `https://qa-{short-id}.leadingai.info`
- **Example:** `https://qa-2012258b4403.leadingai.info`
- **Access:** `curl https://qa-2012258b4403.leadingai.info/api/health`
