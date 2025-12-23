# Monitoring & Security Tools - Quick Reference

**Last Updated**: 2025-11-14
**Server**: leadingai004.contaboserver.net (66.94.121.10)

---

## 📊 Installed Tools Overview

| Tool | Purpose | Access | Status |
|------|---------|--------|--------|
| **Netdata** | Real-time system monitoring | http://100.66.28.67:19999 | ✅ Running |
| **Uptime Kuma** | Uptime monitoring & status pages | http://100.66.28.67:3001 | ✅ Running |
| **Lynis** | Security auditing | Command line only | ✅ Installed |

**All tools accessible via Tailscale VPN only (100.66.28.67)**

---

## 🔍 Netdata - Real-Time Monitoring

### What It Does
- Real-time system metrics (CPU, RAM, Disk, Network)
- Docker container monitoring
- Automatic alert detection
- Email notifications for critical issues

### Access
```
URL: http://100.66.28.67:19999
Authentication: None (Tailscale VPN required)
```

### Key Features
- **1-second granularity** - See metrics update in real-time
- **Auto-discovery** - Automatically detects all services and containers
- **Built-in alerts** - Pre-configured for common issues
- **Email notifications** - Sends alerts to gwasmuth@gmail.com

### Quick Commands
```bash
# Check Netdata status
docker ps --filter "name=netdata"

# View Netdata logs
docker logs netdata --tail 50

# Send test email alert
docker exec netdata /usr/libexec/netdata/plugins.d/alarm-notify.sh test

# Restart Netdata
docker restart netdata
```

### What It Monitors
- System: CPU, RAM, Load, Swap, Entropy
- Disks: Usage, I/O, Latency
- Network: Traffic, Connections, Errors
- Docker: All containers (CPU, RAM, Network per container)
- Services: systemd services, processes

### Email Alerts
- **Configured**: gwasmuth@gmail.com
- **SMTP**: Gmail (smtp.gmail.com:587)
- **Alert Types**: WARNING, CRITICAL, CLEAR
- **Configuration**: See `/root/monitoring/NETDATA_ALERTS_REFERENCE.md`

---

## ⏱️ Uptime Kuma - Uptime Monitoring

### What It Does
- Monitor uptime of websites, APIs, and services
- Create public status pages
- Alert when services go down
- Track historical uptime statistics

### Access
```
URL: http://100.66.28.67:3001
First-time access: Create admin account
```

### First-Time Setup
1. **Connect to Tailscale VPN**
2. **Open**: http://100.66.28.67:3001
3. **Create admin account**:
   - Username: systemccg (recommended)
   - Password: Choose a strong password
   - Email: gwasmuth@gmail.com

4. **Add monitors** for your services:
   - https://n8n.leadingai.info
   - https://webui.leadingai.info
   - https://neo4j.leadingai.info
   - https://db.leadingai.info
   - https://wordpress.leadingai.info
   - https://traefik.leadingai.info

### Monitor Types Available
- **HTTP(s)** - Monitor websites and APIs
- **TCP Port** - Check if a port is open
- **Ping** - ICMP ping monitoring
- **DNS** - Monitor DNS resolution
- **Docker Container** - Check container status
- **Push** - Receive heartbeat from services

### Notification Options
Can send alerts via:
- Email (SMTP)
- Slack
- Discord
- Telegram
- Webhook
- Many more...

### Quick Commands
```bash
# Check Uptime Kuma status
docker ps --filter "name=uptime-kuma"

# View Uptime Kuma logs
docker logs uptime-kuma --tail 50

# Restart Uptime Kuma
docker restart uptime-kuma

# Backup Uptime Kuma data
docker cp uptime-kuma:/app/data /root/backups/uptime-kuma-$(date +%Y%m%d)
```

### Recommended Monitors to Add

**Public Services** (Monitor every 60 seconds):
- n8n: https://n8n.leadingai.info
- Open WebUI: https://webui.leadingai.info
- Neo4j: https://neo4j.leadingai.info
- Supabase: https://db.leadingai.info
- WordPress: https://wordpress.leadingai.info
- Traefik: https://traefik.leadingai.info

**Docker Containers** (Monitor every 60 seconds):
- n8n container
- supabase-db container
- traefik container
- open-webui container

---

## 🔒 Lynis - Security Auditing

### What It Does
- Comprehensive security audit of Linux systems
- Scans for vulnerabilities and misconfigurations
- Provides hardening recommendations
- Generates security score and report

### Access
```
Command line only (no web interface)
Run via SSH or terminal
```

### Quick Security Audit
```bash
# Run quick audit (5 minutes)
lynis audit system --quick

# Run full audit (10-15 minutes)
lynis audit system

# Save audit to file
lynis audit system --quick > /root/security-audit-$(date +%Y%m%d).txt
```

### Understanding Lynis Output

**Security Score**:
- 90-100: Excellent security
- 80-89: Good security
- 70-79: Needs improvement
- <70: Serious issues

**Severity Levels**:
- 🔴 **High**: Critical security issue (fix immediately)
- 🟡 **Medium**: Important recommendation
- 🟢 **Low**: Minor suggestion

### Common Lynis Checks
- System updates and patches
- User accounts and passwords
- File permissions
- SSH configuration
- Firewall rules
- Running services
- Kernel hardening
- File integrity
- Malware scanning

### Schedule Regular Audits
```bash
# Run weekly audit (every Sunday at 2 AM)
echo "0 2 * * 0 /usr/bin/lynis audit system --cronjob > /var/log/lynis/audit-\$(date +\%Y\%m\%d).log" | crontab -

# Create log directory
mkdir -p /var/log/lynis
```

### View Last Audit Results
```bash
# View last audit log
cat /var/log/lynis.log

# View audit report
cat /var/log/lynis-report.dat

# View suggestions
grep Suggestion /var/log/lynis.log
```

### Quick Fixes for Common Issues

**Update system packages**:
```bash
apt update && apt upgrade -y
```

**Enable automatic security updates**:
```bash
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades
```

**Check for compromised files**:
```bash
# Install AIDE (file integrity)
apt install aide -y
aideinit
```

---

## 📈 Monitoring Strategy

### Daily Monitoring
1. **Glance at Netdata** dashboard - Quick health check
2. **Check email** for any alerts from Netdata
3. **Review Uptime Kuma** status page - All services up?

### Weekly Monitoring
1. **Review Netdata** historical trends
2. **Check Uptime Kuma** uptime statistics
3. **Review container resource usage** in Netdata
4. **Adjust alerts** if getting too many false positives

### Monthly Monitoring
1. **Run Lynis security audit**
2. **Review security recommendations**
3. **Update system packages**
4. **Review Netdata alert thresholds**
5. **Backup Uptime Kuma configuration**

---

## 🔔 Alert Configuration

### Netdata Email Alerts
Already configured for:
- Email: gwasmuth@gmail.com
- Severity: WARNING, CRITICAL, CLEAR
- Configuration: `/root/monitoring/NETDATA_ALERTS_REFERENCE.md`

### Uptime Kuma Alerts
**To configure**:
1. Open Uptime Kuma: http://100.66.28.67:3001
2. Go to Settings → Notifications
3. Add Email notification:
   - SMTP Server: smtp.gmail.com
   - Port: 587
   - Username: gwasmuth@gmail.com
   - Password: [Gmail App Password]
   - From: uptime-kuma@leadingai004
   - To: gwasmuth@gmail.com

---

## 🔧 Maintenance Commands

### Restart All Monitoring Tools
```bash
cd /root/monitoring
docker compose restart
```

### View All Monitoring Containers
```bash
docker ps --filter "label=monitoring" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Backup Monitoring Data
```bash
# Backup Uptime Kuma
docker cp uptime-kuma:/app/data /root/backups/uptime-kuma-$(date +%Y%m%d)

# Netdata data is in volumes (backed up with Docker volume backups)
```

### Update Monitoring Tools
```bash
cd /root/monitoring
docker compose pull
docker compose up -d
```

---

## 📚 Documentation Files

- **Netdata Alerts Reference**: `/root/monitoring/NETDATA_ALERTS_REFERENCE.md`
- **Email Alerts Setup**: `/root/monitoring/EMAIL_ALERTS_SETUP.md`
- **Netdata UI Guide**: `/root/monitoring/NETDATA_UI_GUIDE.md`
- **This File**: `/root/monitoring/MONITORING_TOOLS_GUIDE.md`

---

## 🎯 Quick Access Summary

**Netdata Dashboard**:
```
URL: http://100.66.28.67:19999
Login: None required
Access: Tailscale VPN
Purpose: Real-time system monitoring
```

**Uptime Kuma Dashboard**:
```
URL: http://100.66.28.67:3001
Login: Create on first access (systemccg recommended)
Access: Tailscale VPN
Purpose: Uptime monitoring & status pages
```

**Lynis Security Audit**:
```
Command: lynis audit system --quick
Access: SSH/Terminal
Purpose: Security auditing and hardening
```

---

## 🆘 Troubleshooting

### Netdata Not Loading
```bash
docker restart netdata
docker logs netdata --tail 50
```

### Uptime Kuma Not Loading
```bash
docker restart uptime-kuma
docker logs uptime-kuma --tail 50
```

### Email Alerts Not Working
```bash
# Check email logs
docker exec netdata cat /var/log/msmtp.log | tail -20

# Send test email
docker exec netdata /usr/libexec/netdata/plugins.d/alarm-notify.sh test
```

### Lynis Errors
```bash
# Reinstall Lynis
apt remove lynis -y
apt install lynis -y

# Run with verbose output
lynis audit system --verbose
```

---

**Need Help?**
All monitoring tools are documented in `/root/monitoring/` directory.
Check individual documentation files for detailed guides.
