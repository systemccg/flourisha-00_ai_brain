# Server Status Summary - leadingai004

**Last Updated**: 2025-11-14 01:51 CET
**Server**: leadingai004.contaboserver.net (66.94.121.10)
**Status**: ✅ Fully Operational & Secured

---

## 🎯 Quick Access Dashboard

### Public Services (via Cloudflare HTTPS)
All accessible from anywhere via Cloudflare proxy:

- **n8n**: https://n8n.leadingai.info
- **Open WebUI**: https://webui.leadingai.info
- **Neo4j Browser**: https://neo4j.leadingai.info (Username: `neo4j`)
- **Supabase Studio**: https://db.leadingai.info (Username: `systemai`)
- **WordPress**: https://wordpress.leadingai.info
- **Traefik Dashboard**: https://traefik.leadingai.info (Username: `systemccg`)

### Management Tools (Tailscale VPN Only)
Accessible only via Tailscale IP: 100.66.28.67

- **Portainer**: http://100.66.28.67:9000 (Username: `admin`)
- **Filebrowser**: http://100.66.28.67:8080 (Username: `systemccg`)
- **Cockpit**: https://100.66.28.67:9090 (Username: `root`)
- **Netdata**: http://100.66.28.67:19999 (No auth required)
- **Uptime Kuma**: http://100.66.28.67:3001 (Username: `systemccg`)

---

## 🔔 Monitoring & Alerts

### Email Alerts Configuration
**All alerts sent to**: gwasmuth@gmail.com
**SMTP**: Gmail (smtp.gmail.com:587)

### Active Monitoring

**Netdata** - System Monitoring:
- CPU, RAM, Disk, Network monitoring
- Docker container monitoring
- Alert on: High CPU/RAM, Low disk space, Container stopped
- Email on: WARNING (>80%), CRITICAL (>95%), CLEAR

**Uptime Kuma** - Service Uptime:
- 6 services monitored (every 60 seconds)
  - n8n, Open WebUI, Neo4j, Supabase, WordPress, Traefik
- Email on: Service down (3 failed checks), Service recovery

**Lynis** - Security Auditing:
- Last audit: 2025-11-14
- Security score: 66/100
- Status: Good hardening, room for improvement

---

## 🔒 Security Status

### ✅ Implemented Security Measures

1. **Network Security**:
   - Cloudflare DDoS protection & WAF
   - UFW firewall (ports 80/443 restricted to Cloudflare IPs)
   - fail2ban (SSH brute-force protection)
   - Tailscale VPN for management access

2. **Access Control**:
   - SSH key-only authentication (password auth disabled)
   - Management tools behind Tailscale VPN
   - Public services behind Cloudflare proxy
   - BasicAuth on sensitive endpoints

3. **Monitoring**:
   - Real-time system monitoring (Netdata)
   - Service uptime monitoring (Uptime Kuma)
   - Email alerts for all critical issues
   - Security auditing (Lynis)

4. **Service Isolation**:
   - Docker containerization
   - Traefik reverse proxy
   - Service-specific networks
   - Minimal port exposure

### Security Score: 66/100
- ✅ SSH hardening complete
- ✅ Firewall configured correctly
- ✅ fail2ban active
- ⚠️ Password policies could be stricter
- ⚠️ GRUB password not set
- ⚠️ Some systemd services could be hardened

**Improvement Guide**: `/root/monitoring/LYNIS_SECURITY_AUDIT.md`

---

## 📊 System Health

### Current Status (as of last check)
- **CPU**: Normal
- **RAM**: Normal
- **Disk**: Normal
- **Docker Containers**: All running
- **Public Services**: All UP (monitored by Uptime Kuma)
- **Email Alerts**: ✅ Configured and tested

### Services Running: 30+
**Core Services**: n8n, Supabase (6 containers), Neo4j, Open WebUI, WordPress, Traefik
**Management**: Portainer, Filebrowser, Cockpit, Netdata, Uptime Kuma
**Support**: Redis, Postgres, ClickHouse, MinIO, Langfuse
**Monitoring**: Netdata, Uptime Kuma, fail2ban

---

## 🔑 Credentials Quick Reference

### Primary Credentials
- **Traefik Dashboard**: systemccg / 7lly3bwA$HA*Z4Q
- **Uptime Kuma**: systemccg / 7lly3bwA$HA*Z4Q
- **Portainer**: admin / PortainerAdmin2024
- **Filebrowser**: systemccg / (user-set)
- **Supabase Studio**: systemai / riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Ew6
- **Neo4j**: neo4j / riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj

**Complete credential list**: `/root/NEW_SERVER_ACCESS_URLS.md`

---

## 📚 Documentation Index

### Main Documentation
- **Complete Access Guide**: `/root/NEW_SERVER_ACCESS_URLS.md`
- **Security Implementation**: `/root/CLOUDFLARE_IMPLEMENTATION_SUMMARY.md`
- **Security Setup Guide**: `/root/CLOUDFLARE_SETUP_GUIDE.md`
- **Security Incident Report**: `/root/SECURITY_INCIDENT_REPORT_20251112.md`

### Monitoring Documentation
All in `/root/monitoring/`:
- `MONITORING_TOOLS_GUIDE.md` - Overview of all monitoring tools
- `NETDATA_ALERTS_REFERENCE.md` - Netdata alerts configuration
- `NETDATA_UI_GUIDE.md` - Netdata dashboard guide
- `EMAIL_ALERTS_SETUP.md` - Email alerts setup
- `UPTIME_KUMA_SETUP_COMPLETE.md` - Uptime Kuma guide
- `LYNIS_SECURITY_AUDIT.md` - Security audit report

### Configuration Files
- Traefik: `/root/traefik/docker-compose.yml`
- Monitoring: `/root/monitoring/docker-compose.yml`
- Local AI Stack: `/root/local-ai-packaged/docker-compose.yml`
- Supabase: `/root/local-ai-packaged/supabase/docker/docker-compose.yml`

---

## 🚀 Common Tasks

### Check All Services
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### View Monitoring Dashboards
```bash
# Connect to Tailscale, then:
# Netdata: http://100.66.28.67:19999
# Uptime Kuma: http://100.66.28.67:3001
```

### Run Security Audit
```bash
lynis audit system --quick
cat /var/log/lynis.log | grep "Hardening index"
```

### Check Email Alerts
```bash
# Netdata email logs
docker exec netdata cat /var/log/msmtp.log | tail -20

# Send test email
docker exec netdata /usr/libexec/netdata/plugins.d/alarm-notify.sh test
```

### Restart All Monitoring
```bash
cd /root/monitoring
docker compose restart
```

### View Service Logs
```bash
docker logs <service-name> --tail 50
```

### Backup Critical Data
```bash
# Uptime Kuma
docker cp uptime-kuma:/app/data /root/backups/uptime-kuma-$(date +%Y%m%d)

# Netdata (data in volumes, backed up with Docker)
docker run --rm -v netdata_config:/data -v /root/backups:/backup alpine tar czf /backup/netdata-$(date +%Y%m%d).tar.gz -C /data .
```

---

## 🆘 Troubleshooting

### Service Down
1. Check Uptime Kuma dashboard
2. Check Netdata for resource issues
3. View service logs: `docker logs <service>`
4. Restart service: `docker restart <service>`

### Email Alerts Not Working
1. Check SMTP logs: `docker exec netdata cat /var/log/msmtp.log`
2. Send test: `docker exec netdata /usr/libexec/netdata/plugins.d/alarm-notify.sh test`
3. Verify Gmail App Password still valid

### Can't Access Management Tools
1. Verify Tailscale connection: `tailscale status`
2. Check service is running: `docker ps | grep <service>`
3. Check firewall: `ufw status`

### High Resource Usage
1. Check Netdata dashboard: http://100.66.28.67:19999
2. Identify container: Docker section in Netdata
3. View container stats: `docker stats`
4. Check container logs: `docker logs <container>`

---

## 📞 Support Resources

**Claude Code Documentation**: https://docs.claude.com/en/docs/claude-code
**Netdata Docs**: https://learn.netdata.cloud
**Uptime Kuma**: https://github.com/louislam/uptime-kuma
**Lynis**: https://cisofy.com/lynis/
**Traefik**: https://doc.traefik.io/traefik/

---

## 📈 Next Steps

### Immediate (Optional)
- [ ] Login to Uptime Kuma and explore dashboard
- [ ] Review Lynis security audit recommendations
- [ ] Test email notifications

### Short Term (This Week)
- [ ] Review all service status in Uptime Kuma
- [ ] Apply top Lynis security improvements
- [ ] Set up automated backups for Uptime Kuma data

### Long Term (This Month)
- [ ] Run monthly Lynis security audit
- [ ] Review and adjust monitoring thresholds
- [ ] Implement additional Lynis recommendations
- [ ] Consider enabling Cloudflare WAF rules

---

## 🎯 System Overview

**Purpose**: AI/ML workflow automation and development platform
**Security**: Multi-layered (Cloudflare → Firewall → Traefik → Services)
**Monitoring**: Comprehensive (System + Services + Security)
**Backup**: Manual + automated options available
**Access**: Public (via Cloudflare) + Private (via Tailscale VPN)

**Overall Status**: ✅ Production-ready, well-secured, actively monitored

---

**For detailed information, see**: `/root/NEW_SERVER_ACCESS_URLS.md`
