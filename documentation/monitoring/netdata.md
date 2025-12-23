# Netdata Dashboard Navigation Guide

## Where to Find Alert Information

### 1. Active Alarms (Bell Icon 🔔)

**Location**: Top right corner of dashboard

**What it shows**:
- Currently active alarms (WARNING/CRITICAL)
- Recently cleared alarms
- Alarm status and values
- When the alarm was triggered

**How to access**:
1. Open http://100.66.28.67:19999 (via Tailscale)
2. Look for 🔔 icon in top-right corner
3. Click it to see alarm panel

**What you'll see**:
- 🔴 Red badge = Active critical alarms
- 🟡 Yellow badge = Active warning alarms
- ✅ Green = All clear
- Number shows count of active alarms

---

### 2. Alarms Tab (Detailed View)

**Location**: Main menu → "Alarms" (or "Alerts")

**What it shows**:
- Complete list of ALL configured alarms
- Current status of each alarm
- Alarm thresholds and conditions
- Historical alarm transitions
- Which alarms are enabled/disabled

**How to access**:
1. Open Netdata dashboard
2. Click hamburger menu (☰) or look for "Alarms" in the menu
3. Browse all alarm definitions

**Useful features**:
- Filter by alarm type (CPU, memory, disk, etc.)
- See what thresholds trigger each alarm
- View alarm history

---

### 3. Chart Alarm Indicators

**Location**: On each metric chart

**What it shows**:
- Visual indicators when a metric crosses alarm threshold
- Red/yellow lines on charts showing threshold levels
- Alarm status directly on the chart

**How to see it**:
1. Navigate to any metric (e.g., System → CPU)
2. Look for colored horizontal lines on charts
3. These lines represent WARNING and CRITICAL thresholds

---

### 4. Netdata Configuration Section

**Location**: Not available in UI by default

**Note**: Netdata's web UI does NOT have a configuration editor for:
- Email settings
- SMTP configuration
- Notification recipients
- Alert routing rules

These must be configured via command line (already done for you).

---

## ❌ What You CANNOT See in Netdata UI

The following are configured via files only (not visible in dashboard):

### Email Configuration
- Email address (gwasmuth@gmail.com)
- SMTP server settings (Gmail)
- SMTP credentials
- Email notification preferences

### Notification Routing
- Which alerts go to which emails
- Role-based recipients
- Quiet hours settings

### To view these settings, use command line:
```bash
# View email configuration
docker exec netdata cat /etc/netdata/health_alarm_notify.conf

# View SMTP settings (passwords hidden)
docker exec netdata cat /etc/msmtprc
```

---

## 🎯 Quick Navigation Cheat Sheet

| Want to see... | Go to... |
|----------------|----------|
| **Active alarms right now** | 🔔 Bell icon (top right) |
| **All alarm definitions** | Menu → Alarms tab |
| **CPU/Memory/Disk usage** | Menu → System Overview |
| **Docker containers** | Menu → Applications → Docker |
| **Network traffic** | Menu → Network |
| **Disk I/O** | Menu → Disks |
| **Email settings** | Command line only (see below) |

---

## 📧 Verify Email Is Configured (Command Line)

Since email config isn't in the UI, verify via terminal:

### Check Email Configuration
```bash
docker exec netdata cat /etc/netdata/health_alarm_notify.conf | grep -E "SEND_EMAIL|DEFAULT_RECIPIENT"
```

**Expected output**:
```
SEND_EMAIL="YES"
DEFAULT_RECIPIENT_EMAIL="gwasmuth@gmail.com"
```

### Check Recent Email Activity
```bash
docker exec netdata cat /var/log/msmtp.log | tail -5
```

### Send Test Email
```bash
docker exec netdata /usr/libexec/netdata/plugins.d/alarm-notify.sh test
```

---

## 🔍 Exploring Netdata Dashboard

Here's how to navigate effectively:

### Main Menu Structure

**☰ Hamburger Menu (left side)**:
1. **Overview** - High-level system status
2. **System** - CPU, RAM, Load, Entropy
3. **Applications** - Docker, systemd services, processes
4. **Disks** - Disk usage, I/O performance
5. **Network** - Network interfaces, traffic
6. **Alarms** - All configured alarms
7. **Nodes** - If monitoring multiple servers

### Top Bar

**🔔 Alarms** - Active alarm indicator (top right)
**⚙️ Settings** - Dashboard preferences
**📊 Metrics** - Search for specific metrics
**🕐 Time Range** - Adjust historical data view

---

## 📊 Useful Dashboard Views

### System Overview Dashboard

**Shows**:
- CPU usage (per core)
- RAM usage
- Disk space
- Network traffic
- System load

**How to access**: Main menu → Overview (usually default view)

### Docker Containers Dashboard

**Shows**:
- CPU per container
- Memory per container
- Network per container
- Disk I/O per container

**How to access**:
1. Main menu → Applications
2. Scroll to "Docker containers" section
3. Or use search: type "docker" in metrics search

### Alarms Dashboard

**Shows**:
- All alarm configurations
- Current alarm states
- Alarm thresholds
- Historical alarm log

**How to access**: Main menu → Alarms

---

## 🎨 Dashboard Customization

### Change Time Range
- Click time selector (top right)
- Choose: 1 min, 5 min, 15 min, 1 hour, etc.
- Or drag on any chart to zoom in

### Search Metrics
- Use search box (top bar)
- Type metric name (e.g., "cpu", "memory", "docker")
- Instantly filter to relevant charts

### Pin Charts
- Click 📌 icon on any chart
- Pinned charts appear in custom dashboard
- Useful for monitoring specific metrics

---

## 🔧 What If You Want a UI for Email Config?

Netdata doesn't have a built-in UI for email settings, but alternatives:

### Option 1: Use Netdata Cloud (Optional)
- Sign up at https://app.netdata.cloud
- Web-based UI for alert configuration
- Can manage email notifications there
- **Trade-off**: Data goes to Netdata's cloud

### Option 2: Create Custom Config UI (Advanced)
- Use Portainer or Filebrowser to edit config files via web
- Access `/etc/netdata/health_alarm_notify.conf` in Netdata container
- Manual but works

### Option 3: Command Line (Current Setup)
- Edit via SSH/terminal (most common)
- I can help you make changes anytime
- Most flexible and secure

---

## 🎯 Recommended Workflow

### Daily Monitoring
1. Open Netdata dashboard: http://100.66.28.67:19999
2. Glance at Overview for quick health check
3. Check 🔔 icon for any active alarms
4. Receive email if anything critical happens

### When Alert Email Received
1. Open Netdata dashboard
2. Click 🔔 to see active alarms
3. Navigate to relevant metric (CPU/Memory/Disk)
4. Investigate the spike or issue
5. Check Docker container metrics if container-related

### Managing Alerts
1. Use command line to adjust thresholds
2. Or ask me to help modify settings
3. Test changes with: `docker exec netdata /usr/libexec/netdata/plugins.d/alarm-notify.sh test`

---

## 📚 Key Takeaways

✅ **In Netdata UI**: View alarms, metrics, charts, alarm status
❌ **Not in UI**: Email configuration, SMTP settings, notification routing

**For email config changes**, you need to:
- Edit config files via command line, OR
- Ask me to help you modify settings

The UI is excellent for monitoring and viewing alarms, but configuration is file-based.

---

## 🔗 Quick Links

- **Netdata Dashboard**: http://100.66.28.67:19999 (Tailscale required)
- **Email Config Reference**: `/root/monitoring/NETDATA_ALERTS_REFERENCE.md`
- **Full Setup Guide**: `/root/monitoring/EMAIL_ALERTS_SETUP.md`

---

**Questions?**
Just ask! I can help you:
- Navigate to specific metrics
- Adjust alarm thresholds
- Change email settings
- Disable noisy alerts
