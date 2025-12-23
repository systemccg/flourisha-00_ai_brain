#!/bin/bash
#
# Backup Verification Script
# Checks that all backup systems are functioning properly
#

set -e

echo "=================================="
echo "=== Backup Verification Check ==="
echo "=================================="
echo ""

ERRORS=0
WARNINGS=0

# Function to check with visual feedback
check_pass() {
    echo "  ✅ $1"
}

check_warn() {
    echo "  ⚠️  $1"
    ((WARNINGS++))
}

check_fail() {
    echo "  ❌ $1"
    ((ERRORS++))
}

# 1. Check local backups
echo "1. Checking local backup files..."
if [ -f /root/backups/backup-latest.tar.gz ]; then
    latest_backup=$(readlink -f /root/backups/backup-latest.tar.gz)
    backup_age=$(find "$latest_backup" -mtime -1 2>/dev/null)

    if [ -n "$backup_age" ]; then
        size=$(du -h "$latest_backup" | cut -f1)
        check_pass "Latest backup exists and is recent ($size)"
    else
        check_warn "Latest backup exists but is older than 24 hours"
    fi
else
    check_fail "No backup-latest.tar.gz found"
fi

# Count backups
daily_count=$(find /root/backups -name "backup-daily-*.tar.gz" | wc -l)
weekly_count=$(find /root/backups -name "backup-weekly-*.tar.gz" | wc -l)
echo "  📊 Found $daily_count daily backups, $weekly_count weekly backups"

# 2. Check Google Drive sync
echo ""
echo "2. Checking Google Drive sync..."
if command -v rclone &> /dev/null; then
    if rclone listremotes | grep -q "flourisha"; then
        check_pass "rclone is configured"

        # Check if backup exists in Google Drive
        gdrive_backups=$(rclone lsl flourisha:/05_Backups/server-backups 2>/dev/null | wc -l)
        if [ "$gdrive_backups" -gt 0 ]; then
            check_pass "Backups found in Google Drive ($gdrive_backups files)"

            # Check if latest backup was synced recently
            latest_gdrive=$(rclone lsl flourisha:/05_Backups/server-backups 2>/dev/null | tail -1)
            echo "    Latest in GDrive: $(echo $latest_gdrive | awk '{print $4}')"
        else
            check_fail "No backups found in Google Drive"
        fi
    else
        check_fail "Google Drive remote 'flourisha' not configured"
    fi
else
    check_fail "rclone not installed"
fi

# 3. Check server-config-backup git repo
echo ""
echo "3. Checking server config backup (git)..."
if [ -d /root/backups/server-config-backup/.git ]; then
    cd /root/backups/server-config-backup

    # Check if there are uncommitted changes
    if git diff-index --quiet HEAD --; then
        check_pass "Server configs are committed to git"
    else
        check_warn "Server configs have uncommitted changes"
        echo "    Run: cd /root/backups/server-config-backup && git add . && git commit -m 'Config update'"
    fi

    # Check if remote is configured
    if git remote -v | grep -q origin; then
        remote_url=$(git remote get-url origin)
        check_pass "Git remote configured: $remote_url"

        # Check if pushed
        if git status | grep -q "Your branch is ahead"; then
            check_warn "Commits not pushed to remote"
            echo "    Run: cd /root/backups/server-config-backup && git push"
        else
            check_pass "Git repo is synced with remote"
        fi
    else
        check_fail "No git remote configured"
    fi

    cd - > /dev/null
else
    check_fail "/root/backups/server-config-backup is not a git repository"
fi

# 4. Check Flourisha sync
echo ""
echo "4. Checking Flourisha directory sync..."
if [ -d /root/flourisha ]; then
    flourisha_size=$(du -sh /root/flourisha | cut -f1)
    check_pass "Flourisha directory exists ($flourisha_size)"

    # Check if scripts are in place
    if [ -f /root/flourisha/00_AI_Brain/scripts/backups/backup_volumes_optimized.sh ]; then
        check_pass "Backup scripts are in Flourisha structure"
    else
        check_fail "Backup scripts not found in Flourisha"
    fi
else
    check_fail "Flourisha directory not found"
fi

# 5. Check critical /root files
echo ""
echo "5. Checking critical /root files..."
if [ -d /root/.ssh ]; then
    ssh_key_count=$(find /root/.ssh -type f -name "id_*" ! -name "*.pub" | wc -l)
    if [ "$ssh_key_count" -gt 0 ]; then
        check_warn "SSH keys found ($ssh_key_count) - ensure backed up manually"
    else
        echo "  ℹ️  No SSH private keys found"
    fi
else
    echo "  ℹ️  No .ssh directory"
fi

if [ -f /root/.claude.json ]; then
    check_warn "Claude config found - ensure backed up manually"
else
    echo "  ℹ️  No .claude.json file"
fi

# 6. Check cron job
echo ""
echo "6. Checking automated backup schedule..."
if crontab -l | grep -q "full_backup.sh"; then
    cron_schedule=$(crontab -l | grep "full_backup.sh" | awk '{print $1, $2, $3, $4, $5}')
    check_pass "Cron job configured: $cron_schedule"
else
    check_fail "No cron job found for automated backups"
fi

# 7. Check backup logs
echo ""
echo "7. Checking backup logs..."
if [ -f /var/log/full_backup.log ]; then
    last_backup=$(grep "Backup Complete" /var/log/full_backup.log | tail -1)
    if [ -n "$last_backup" ]; then
        check_pass "Backup log found"
        echo "    Last backup: $last_backup"
    else
        check_warn "Backup log exists but no successful backups logged"
    fi

    # Check for errors
    recent_errors=$(tail -100 /var/log/full_backup.log | grep -i error | wc -l)
    if [ "$recent_errors" -gt 0 ]; then
        check_warn "Found $recent_errors errors in recent backup logs"
        echo "    Check: tail -50 /var/log/full_backup.log"
    fi
else
    check_warn "No backup log file found at /var/log/full_backup.log"
fi

# 8. Check disk space
echo ""
echo "8. Checking disk space..."
disk_usage=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    check_pass "Disk usage is healthy (${disk_usage}%)"
else
    check_warn "Disk usage is high (${disk_usage}%)"
fi

backup_size=$(du -sh /root/backups | cut -f1)
echo "  📦 Backup directory size: $backup_size"

# 9. Test backup script existence and permissions
echo ""
echo "9. Checking backup scripts..."
scripts=(
    "/root/backups/backup_volumes_optimized.sh"
    "/root/backups/full_backup.sh"
    "/root/backups/backup_configs.sh"
    "/root/backups/restore_volumes.sh"
)

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            check_pass "$(basename $script) exists and is executable"
        else
            check_warn "$(basename $script) exists but is not executable"
        fi
    else
        check_fail "$(basename $script) not found"
    fi
done

# Summary
echo ""
echo "=================================="
echo "=== Verification Summary ==="
echo "=================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED"
    echo ""
    echo "Your backup system is healthy!"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  CHECKS PASSED WITH WARNINGS"
    echo ""
    echo "Found $WARNINGS warnings (see above)"
    echo "Backup system is functional but needs attention"
    exit 1
else
    echo "❌ CHECKS FAILED"
    echo ""
    echo "Found $ERRORS errors and $WARNINGS warnings"
    echo "Backup system needs immediate attention!"
    exit 2
fi
