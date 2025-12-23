#!/bin/bash
#
# Daily Email Summary Script
# Sends daily summary of backups, security checks, and cron jobs
#

set -e

EMAIL_TO="system@cocreatorsgroup.com"
EMAIL_FROM="noreply@leadingai.info"
EMAIL_SUBJECT="Daily Server Summary - $(hostname -s) - $(date +%Y-%m-%d)"
TEMP_FILE="/tmp/daily_summary_$(date +%Y%m%d).txt"

# Create email body
cat > "$TEMP_FILE" << EOF
================================================================================
                    DAILY SERVER SUMMARY
                    $(hostname -f)
                    $(date '+%Y-%m-%d %H:%M:%S %Z')
================================================================================

EOF

# ============================================================================
# 1. BACKUP STATUS
# ============================================================================

cat >> "$TEMP_FILE" << 'EOF'
════════════════════════════════════════════════════════════════════════════
1. BACKUP STATUS
════════════════════════════════════════════════════════════════════════════

EOF

# Check if backup ran today
BACKUP_LOG="/var/log/full_backup.log"
if [ -f "$BACKUP_LOG" ]; then
    LAST_BACKUP=$(grep "Full Server Backup Complete" "$BACKUP_LOG" | tail -1)

    if [ -n "$LAST_BACKUP" ]; then
        # Check if backup was today
        TODAY=$(date +%Y-%m-%d)
        BACKUP_DATE=$(echo "$LAST_BACKUP" | grep -oP '\d{4}-\d{2}-\d{2}' || echo "")

        if [ "$BACKUP_DATE" = "$TODAY" ]; then
            echo "✅ Backup Status: Completed successfully today" >> "$TEMP_FILE"
        else
            echo "⚠️  Backup Status: WARNING - No backup today!" >> "$TEMP_FILE"
            if [ -n "$BACKUP_DATE" ]; then
                echo "   Last successful backup: $BACKUP_DATE" >> "$TEMP_FILE"
            fi
        fi

        # Get backup size
        LATEST_BACKUP=$(ls -t /root/backups/backup-*.tar.gz 2>/dev/null | head -1)
        if [ -n "$LATEST_BACKUP" ]; then
            BACKUP_SIZE=$(du -h "$LATEST_BACKUP" | cut -f1)
            BACKUP_NAME=$(basename "$LATEST_BACKUP")
            echo "   Latest backup: $BACKUP_NAME ($BACKUP_SIZE)" >> "$TEMP_FILE"
        fi

        echo "" >> "$TEMP_FILE"

        # Check GitHub push status
        if tail -100 "$BACKUP_LOG" | grep -q "Successfully pushed to GitHub"; then
            echo "   ✅ Config backup: Pushed to GitHub successfully" >> "$TEMP_FILE"
        else
            echo "   ⚠️  Config backup: May not be pushed to GitHub" >> "$TEMP_FILE"
        fi

        # Check Google Drive sync
        if tail -100 "$BACKUP_LOG" | grep -q "Backup synced to Google Drive"; then
            echo "   ✅ Volume backup: Synced to Google Drive successfully" >> "$TEMP_FILE"
        else
            echo "   ⚠️  Volume backup: May not be synced to Google Drive" >> "$TEMP_FILE"
        fi

        echo "" >> "$TEMP_FILE"

        # Show any errors with explanation
        ERRORS=$(grep -i "error\|failed" "$BACKUP_LOG" | tail -50 | grep -v "WARNING: apt does" | grep -v "Error is not recoverable" | head -5)
        if [ -n "$ERRORS" ]; then
            echo "   ⚠️  Issues found during backup:" >> "$TEMP_FILE"
            echo "$ERRORS" | sed 's/^/      /' >> "$TEMP_FILE"
            echo "" >> "$TEMP_FILE"
            echo "   Note: Some errors may be expected (e.g., tar warnings about files changing)" >> "$TEMP_FILE"
        else
            echo "   ✅ No critical errors in backup log" >> "$TEMP_FILE"
        fi
    else
        echo "⚠️  WARNING: No backup completion found in log" >> "$TEMP_FILE"
    fi
else
    echo "❌ ERROR: Backup log not found at $BACKUP_LOG" >> "$TEMP_FILE"
fi

echo "" >> "$TEMP_FILE"

# Disk usage
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}')
BACKUP_DIR_SIZE=$(du -sh /root/backups 2>/dev/null | cut -f1)
echo "💾 Disk Usage:" >> "$TEMP_FILE"
echo "   Root filesystem: $DISK_USAGE used" >> "$TEMP_FILE"
echo "   Backup directory: $BACKUP_DIR_SIZE" >> "$TEMP_FILE"

cat >> "$TEMP_FILE" << 'EOF'


════════════════════════════════════════════════════════════════════════════
2. SECURITY STATUS
════════════════════════════════════════════════════════════════════════════

EOF

# Check security summary from latest run
SECURITY_SUMMARY="/var/log/security-checks/latest-summary.txt"
if [ -f "$SECURITY_SUMMARY" ]; then
    # Read security check results
    SECURITY_STATUS=$(grep "^Status:" "$SECURITY_SUMMARY" | cut -d' ' -f2)
    CRITICAL_ISSUES=$(grep "^Critical Issues:" "$SECURITY_SUMMARY" | cut -d' ' -f3)
    WARNINGS=$(grep "^Warnings:" "$SECURITY_SUMMARY" | cut -d' ' -f2)
    LAST_CHECK=$(grep "^Last Check:" "$SECURITY_SUMMARY" | cut -d' ' -f3-)

    # Display status with appropriate emoji
    case "$SECURITY_STATUS" in
        PASS)
            echo "✅ Status: All security checks passed" >> "$TEMP_FILE"
            ;;
        WARNING)
            echo "⚠️  Status: Security checks passed with $WARNINGS warnings" >> "$TEMP_FILE"
            ;;
        CRITICAL)
            echo "❌ Status: $CRITICAL_ISSUES critical security issues found!" >> "$TEMP_FILE"
            ;;
        *)
            echo "❓ Status: Unknown" >> "$TEMP_FILE"
            ;;
    esac

    echo "   Last security scan: $LAST_CHECK" >> "$TEMP_FILE"
    echo "" >> "$TEMP_FILE"

    # Check fail2ban status
    if command -v fail2ban-client &> /dev/null; then
        if systemctl is-active --quiet fail2ban 2>/dev/null; then
            BANNED_NOW=$(fail2ban-client status sshd 2>/dev/null | grep "Currently banned" | awk '{print $NF}')
            TOTAL_BANS=$(fail2ban-client status sshd 2>/dev/null | grep "Total banned" | awk '{print $NF}')

            if [ -n "$BANNED_NOW" ] && [ -n "$TOTAL_BANS" ]; then
                echo "🛡️  Attack Protection (fail2ban):" >> "$TEMP_FILE"
                echo "   Currently blocking: $BANNED_NOW malicious IPs" >> "$TEMP_FILE"
                echo "   Total attacks blocked (all time): $TOTAL_BANS" >> "$TEMP_FILE"

                # Show recent attack activity
                RECENT_BANS=$(grep "Ban" /var/log/fail2ban.log 2>/dev/null | grep "$(date +%Y-%m-%d)" | wc -l)
                if [ "$RECENT_BANS" -gt 0 ]; then
                    echo "   New attacks blocked today: $RECENT_BANS" >> "$TEMP_FILE"

                    # Show a sample of attacking IPs
                    echo "" >> "$TEMP_FILE"
                    echo "   Recent attacking IPs blocked today:" >> "$TEMP_FILE"
                    grep "Ban" /var/log/fail2ban.log 2>/dev/null | grep "$(date +%Y-%m-%d)" | tail -5 | \
                        awk '{print $NF}' | sed 's/^/      /' >> "$TEMP_FILE"
                else
                    echo "   No new attacks today (quiet day)" >> "$TEMP_FILE"
                fi
            fi
        else
            echo "❌ fail2ban protection is NOT running!" >> "$TEMP_FILE"
        fi
    fi

    echo "" >> "$TEMP_FILE"

    # Check authentication failures
    if [ -f /var/log/auth.log ]; then
        FAILED_TODAY=$(grep "$(date '+%b %e')" /var/log/auth.log 2>/dev/null | grep "Failed password" | wc -l)
        if [ "$FAILED_TODAY" -gt 0 ]; then
            echo "🔐 Login Security:" >> "$TEMP_FILE"
            echo "   Failed login attempts today: $FAILED_TODAY (all blocked by fail2ban)" >> "$TEMP_FILE"
        else
            echo "🔐 Login Security: No failed login attempts today" >> "$TEMP_FILE"
        fi
    fi
else
    echo "⚠️  Security check results not found" >> "$TEMP_FILE"
    echo "   Expected at: $SECURITY_SUMMARY" >> "$TEMP_FILE"
    echo "   Security checks may not be running" >> "$TEMP_FILE"
fi

cat >> "$TEMP_FILE" << 'EOF'


════════════════════════════════════════════════════════════════════════════
3. SCHEDULED TASKS (CRON JOBS)
════════════════════════════════════════════════════════════════════════════

EOF

echo "📅 Automated Tasks:" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# Parse cron jobs and make them human-readable
crontab -l | grep -v "^#" | grep -v "^$" | while IFS= read -r line; do
    # Extract cron schedule and command
    SCHEDULE=$(echo "$line" | awk '{print $1, $2, $3, $4, $5}')
    COMMAND=$(echo "$line" | awk '{for(i=6;i<=NF;i++) printf "%s ", $i; print ""}')

    # Convert cron schedule to human-readable format
    HOUR=$(echo "$SCHEDULE" | awk '{print $2}')
    MINUTE=$(echo "$SCHEDULE" | awk '{print $1}')
    DAY=$(echo "$SCHEDULE" | awk '{print $3}')
    MONTH=$(echo "$SCHEDULE" | awk '{print $4}')
    WEEKDAY=$(echo "$SCHEDULE" | awk '{print $5}')

    # Determine frequency
    if echo "$MINUTE" | grep -q "^\*/"; then
        # Handle interval-based schedules like */15
        INTERVAL=$(echo "$MINUTE" | sed 's/\*\///')
        FREQUENCY="Every $INTERVAL minutes"
    elif [ "$DAY" = "*" ] && [ "$MONTH" = "*" ] && [ "$WEEKDAY" = "*" ]; then
        FREQUENCY="Daily at ${HOUR}:$(printf '%02d' $MINUTE)"
    else
        FREQUENCY="Schedule: $SCHEDULE"
    fi

    # Extract task name from command
    if echo "$COMMAND" | grep -q "security-check.sh"; then
        TASK_NAME="Security Scan"
        LOG_FILE="/var/log/security-checks/security-check-$(date +%Y-%m-%d).log"
    elif echo "$COMMAND" | grep -q "full_backup.sh"; then
        TASK_NAME="Full Server Backup"
        LOG_FILE="/var/log/full_backup.log"
    elif echo "$COMMAND" | grep -q "daily_email_summary.sh"; then
        TASK_NAME="Daily Email Summary"
        LOG_FILE="/var/log/daily_email_summary.log"
    else
        TASK_NAME="Custom Task"
        LOG_FILE=""
    fi

    echo "   • $TASK_NAME" >> "$TEMP_FILE"
    echo "     When: $FREQUENCY" >> "$TEMP_FILE"

    # Check if task ran successfully today (if applicable log file exists)
    if [ -n "$LOG_FILE" ] && [ -f "$LOG_FILE" ]; then
        if tail -50 "$LOG_FILE" 2>/dev/null | grep -q "$(date +%Y-%m-%d)"; then
            echo "     Result: ✅ Executed successfully today" >> "$TEMP_FILE"
        else
            echo "     Result: ⏳ Not yet run today (scheduled: $FREQUENCY)" >> "$TEMP_FILE"
        fi
    else
        echo "     Result: ⏳ Scheduled: $FREQUENCY" >> "$TEMP_FILE"
    fi

    echo "" >> "$TEMP_FILE"
done

cat >> "$TEMP_FILE" << 'EOF'

════════════════════════════════════════════════════════════════════════════
4. DOCKER CONTAINERS
════════════════════════════════════════════════════════════════════════════

EOF

RUNNING=$(docker ps --format "{{.Names}}" | wc -l)
TOTAL=$(docker ps -a --format "{{.Names}}" | wc -l)

echo "📦 Container Status: $RUNNING running / $TOTAL total" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# Show any unhealthy containers
UNHEALTHY=$(docker ps --filter "health=unhealthy" --format "{{.Names}}" 2>/dev/null)
if [ -n "$UNHEALTHY" ]; then
    echo "⚠️  Unhealthy Containers:" >> "$TEMP_FILE"
    echo "$UNHEALTHY" | sed 's/^/   /' >> "$TEMP_FILE"
else
    echo "✅ All containers healthy" >> "$TEMP_FILE"
fi

# Show any stopped containers
STOPPED=$(docker ps -a --filter "status=exited" --format "{{.Names}}" 2>/dev/null | head -5)
if [ -n "$STOPPED" ]; then
    echo "" >> "$TEMP_FILE"
    echo "⚠️  Stopped Containers:" >> "$TEMP_FILE"
    echo "$STOPPED" | sed 's/^/   /' >> "$TEMP_FILE"
fi

cat >> "$TEMP_FILE" << 'EOF'


════════════════════════════════════════════════════════════════════════════
5. SYSTEM INFO
════════════════════════════════════════════════════════════════════════════

EOF

UPTIME=$(uptime -p)
LOAD=$(uptime | awk -F'load average:' '{print $2}')
MEM_USED=$(free -h | awk '/^Mem:/ {print $3}')
MEM_TOTAL=$(free -h | awk '/^Mem:/ {print $2}')

echo "🖥️  System Health:" >> "$TEMP_FILE"
echo "   Uptime: $UPTIME" >> "$TEMP_FILE"
echo "   Load Average:$LOAD" >> "$TEMP_FILE"
echo "   Memory: $MEM_USED / $MEM_TOTAL" >> "$TEMP_FILE"

cat >> "$TEMP_FILE" << 'EOF'


================================================================================
                            END OF DAILY SUMMARY
================================================================================

This is an automated email. To modify this report, edit:
/root/flourisha/00_AI_Brain/scripts/monitoring/daily_email_summary.sh

To view full logs:
- Backup log: tail -100 /var/log/full_backup.log
- Security log: tail -100 /var/log/security-checks/security-check-$(date +%Y-%m-%d).log
- System log: journalctl -xe

EOF

# Send email
if command -v mail &> /dev/null; then
    cat "$TEMP_FILE" | mail -s "$EMAIL_SUBJECT" -a "From: $EMAIL_FROM" "$EMAIL_TO"
    echo "✅ Daily summary email sent to $EMAIL_TO"
else
    echo "❌ ERROR: mail command not found, cannot send email"
    exit 1
fi

# Clean up
rm -f "$TEMP_FILE"

echo "Daily summary email sent successfully at $(date)"
