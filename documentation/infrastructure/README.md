# Infrastructure Documentation

This directory contains documentation about server setup, networking, DNS, and core infrastructure configuration.

## Files in This Category

- **[SERVER_CONFIG.md](./SERVER_CONFIG.md)** - Server specifications and configuration details
- **[DNS_CONFIGURATION_FIX.md](./DNS_CONFIGURATION_FIX.md)** - DNS setup and troubleshooting
- **[TRAEFIK_SETUP.md](./TRAEFIK_SETUP.md)** - Reverse proxy and SSL automation
- **[DOCKER_DAEMON_CONFIG.md](./DOCKER_DAEMON_CONFIG.md)** - Docker daemon configuration

## Quick Facts

**Server Location:** Contabo (Primary VPS)
**Server IP:** 66.94.121.10
**Hostname:** leadingai.info
**Public URL:** https://leadingai.info

**Key Infrastructure:**
- Docker 29.0.0 (25+ production containers)
- Traefik reverse proxy with SSL (*.leadingai.info)
- Tailscale VPN for secure access
- 4 GB RAM available
- 34 GB disk space

## Getting Started

1. **New to infrastructure?** Start with [SERVER_CONFIG.md](./SERVER_CONFIG.md)
2. **DNS issues?** See [DNS_CONFIGURATION_FIX.md](./DNS_CONFIGURATION_FIX.md)
3. **Traefik setup?** Read [TRAEFIK_SETUP.md](./TRAEFIK_SETUP.md)
4. **Docker config?** Check [DOCKER_DAEMON_CONFIG.md](./DOCKER_DAEMON_CONFIG.md)

## Important Commands

```bash
# View server IP and hostname
grep "SERVER_IP\|SERVER_HOSTNAME" /root/flourisha/00_AI_Brain/.flourisha-config

# Check Traefik config
cat /root/traefik/traefik.yml
cat /root/traefik/dynamic-conf.yml

# View Docker daemon config
cat /etc/docker/daemon.json

# Test DNS
dig leadingai.info @8.8.8.8
```

## CRITICAL REMINDER

⚠️ **Be EXTREMELY CAUTIOUS when modifying:**
- Contabo server configuration
- Traefik routing rules
- DNS settings
- Docker daemon configuration

Always:
1. Backup current configuration
2. Test changes in staging first
3. Have a rollback plan
4. Verify changes work as expected

## Related Documentation

- **Phase 2:** [../phase2/](../phase2/) - Docker sandbox deployment
- **Startup:** [../startup/](../startup/) - System startup procedures
- **Monitoring:** [../monitoring/](../monitoring/) - Infrastructure monitoring
- **Troubleshooting:** [../troubleshooting/](../troubleshooting/) - Common issues

---

**Last Updated:** 2025-12-05
**Maintainer:** Flourisha AI System
**Responsibility:** Greg Wasmuth
