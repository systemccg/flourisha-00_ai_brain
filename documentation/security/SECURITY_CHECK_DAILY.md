# Daily Security Check Script

**Location:** `/usr/local/bin/security-check.sh`
**Schedule:** Daily at 6:00 AM (via cron)
**Logs:** `/var/log/security-checks/`

---

## Overview

Automated daily security check that integrates with installed security products:
- **fail2ban** - Monitors jails and banned IPs
- **lynis** - Tracks security audit scores
- **UFW** - Firewall status and blocks
- **System logs** - Auth failures and suspicious activity
- **Docker** - Container health monitoring
- **Disk space** - Usage warnings
- **System updates** - Available updates tracking

---

## Quick Commands

```bash
# Run manual check
/usr/local/bin/security-check.sh

# View latest summary
cat /var/log/security-checks/latest-summary.txt

# View today's log
cat /var/log/security-checks/security-check-$(date +%Y-%m-%d).log

# View recent logs
ls -lht /var/log/security-checks/ | head -10

# Check cron schedule
crontab -l | grep security-check
```

---

## What It Checks

### 1. fail2ban Protection
- Service status
- Active jails
- Currently banned IPs
- Total bans count
- ⚠️ Alerts if > 10 IPs currently banned

### 2. UFW Firewall
- Firewall active status
- Blocked connections in last 24h
- ⚠️ Alerts if > 100 blocks in 24h

### 3. Authentication Attempts
- Failed SSH password attempts
- Invalid user attempts
- Top attacking IPs
- Successful root logins
- ⚠️ Alerts if > 50 failed attempts

### 4. Docker Container Health
- Docker daemon status
- Running/stopped container counts
- Unhealthy containers
- Recently restarted containers
- ❌ Critical if unhealthy containers found

### 5. Disk Space
- Usage for /, /var, /tmp
- Docker system disk usage
- ⚠️ Warning at 75% full
- ❌ Critical at 85% full

### 6. System Updates
- Available updates count
- Security updates count
- List of pending updates
- ⚠️ Alerts if security updates available

### 7. Critical Services
Checks these services are running:
- ssh
- docker
- fail2ban
- ufw
- cron
- tailscaled (if installed)

### 8. Lynis Security Audit
- Installation status
- Last audit date
- Last security score
- ⚠️ Reminds if > 30 days since last audit

---

## Output Files

### Latest Summary
**File:** `/var/log/security-checks/latest-summary.txt`

Contains quick status overview:
```
Last Check: Thu Nov 20 19:31:49 CET 2025
Status: CRITICAL | WARNING | PASS
Critical Issues: 1
Warnings: 1
Log File: /var/log/security-checks/security-check-2025-11-20.log
```

### Daily Logs
**Pattern:** `/var/log/security-checks/security-check-YYYY-MM-DD.log`

Contains full detailed output from each check.

---

## Status Levels

- **PASS** (exit 0): No issues or warnings found
- **WARNING** (exit 0): Warnings found but no critical issues
- **CRITICAL** (exit 1): One or more critical issues detected

---

## Common Issues & Solutions

### Unhealthy Docker Containers
```bash
# Check container logs
docker logs supabase-analytics

# Restart unhealthy container
docker restart supabase-analytics

# Check health status
docker inspect supabase-analytics | grep -A 10 Health
```

### High Number of Banned IPs
```bash
# View currently banned IPs
fail2ban-client status sshd

# Unban specific IP (if needed)
fail2ban-client set sshd unbanip 1.2.3.4

# View recent ban activity
tail -100 /var/log/fail2ban.log
```

### High Disk Usage
```bash
# Find large files
du -h / --max-depth=1 | sort -h

# Clean Docker
docker system prune -a --volumes

# Check Docker volume usage
docker volume ls
docker volume inspect <volume_name>
```

### Security Updates Available
```bash
# Review updates
apt list --upgradable | grep security

# Apply security updates only
apt-get install -y --only-upgrade <package-name>

# Apply all updates
apt update && apt upgrade -y
```

### Lynis Audit Overdue
```bash
# Run quick audit (5-10 min)
lynis audit system --quick

# Run full audit (15-20 min)
lynis audit system

# View last audit score
grep "Hardening index" /var/log/lynis.log | tail -1
```

---

## Cron Configuration

**Current schedule:** `0 6 * * * /usr/local/bin/security-check.sh`

### Modify Schedule
```bash
# Edit crontab
crontab -e

# Examples:
# Daily at 2 AM: 0 2 * * * /usr/local/bin/security-check.sh
# Every 12 hours: 0 */12 * * * /usr/local/bin/security-check.sh
# Weekly (Mon 6AM): 0 6 * * 1 /usr/local/bin/security-check.sh
```

### Email Notifications (Optional)
```bash
# Add to top of crontab
MAILTO=your-email@example.com

# Cron will email output on failures
0 6 * * * /usr/local/bin/security-check.sh
```

---

## Log Retention

Logs accumulate in `/var/log/security-checks/`. Consider setting up log rotation:

```bash
# Create logrotate config
cat > /etc/logrotate.d/security-checks << 'EOF'
/var/log/security-checks/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 root root
}
EOF

# Test rotation
logrotate -d /etc/logrotate.d/security-checks
```

---

## Integration with Monitoring

The summary file can be monitored by:
- Uptime Kuma (file monitor)
- Netdata (log alerts)
- Custom monitoring scripts

Example monitoring check:
```bash
#!/bin/bash
STATUS=$(grep "^Status:" /var/log/security-checks/latest-summary.txt | awk '{print $2}')
ISSUES=$(grep "^Critical Issues:" /var/log/security-checks/latest-summary.txt | awk '{print $3}')

if [ "$STATUS" == "CRITICAL" ] || [ "$ISSUES" -gt 0 ]; then
    echo "ALERT: Security check found critical issues!"
    exit 1
fi
```

---

## Maintenance

### Update Script
```bash
# Edit script
nano /usr/local/bin/security-check.sh

# Test changes
/usr/local/bin/security-check.sh

# Verify still executable
ls -l /usr/local/bin/security-check.sh
```

### Adjust Thresholds
Edit these variables in the script:
- `ALERT_THRESHOLD_DISK=85` - Disk usage % for alerts
- `ALERT_THRESHOLD_BANS=10` - Number of banned IPs to alert on

### Disable Check Temporarily
```bash
# Comment out cron job
crontab -e
# Add # before the line: # 0 6 * * * /usr/local/bin/security-check.sh

# Or remove cron entry entirely
crontab -e
# Delete the security-check line
```

---

## Troubleshooting

### Script Not Running
```bash
# Check cron service
systemctl status cron

# Check cron logs
grep security-check /var/log/syslog

# Test script manually
bash -x /usr/local/bin/security-check.sh
```

### Permission Errors
```bash
# Fix script permissions
chmod +x /usr/local/bin/security-check.sh

# Fix log directory permissions
chown -R root:root /var/log/security-checks
chmod 755 /var/log/security-checks
```

### Missing Dependencies
```bash
# Install required tools
apt install fail2ban lynis ufw -y

# Verify installations
which fail2ban-client lynis ufw
```

---

## Current Status

**Installed:** ✅ `/usr/local/bin/security-check.sh`
**Cron Job:** ✅ Daily at 6:00 AM
**Security Products:**
- ✅ fail2ban 1.0.2
- ✅ lynis 3.0.9
- ✅ UFW firewall

**Last Check:** See `/var/log/security-checks/latest-summary.txt`

---

**Created:** 2025-11-20
**Last Updated:** 2025-11-20
**Version:** 1.0
