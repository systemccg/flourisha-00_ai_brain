# Google Drive Backup Setup Guide

Since rclone requires browser authentication and this is a headless server, you have two options:

## Option 1: SSH Port Forwarding (Recommended)

This allows you to use the browser on your local machine to authenticate:

```bash
# On your local machine, create an SSH tunnel:
ssh -L 53682:localhost:53682 root@64.23.180.200

# Then on the server, run:
rclone config reconnect gdrive:

# The browser on your local machine will open and you can authenticate
```

## Option 2: Authorize on Your Computer (Easier)

1. **Install rclone on your local computer**:
   - Mac: `brew install rclone`
   - Windows: Download from https://rclone.org/downloads/
   - Linux: `curl https://rclone.org/install.sh | sudo bash`

2. **Configure Google Drive on your computer**:
   ```bash
   rclone config
   # Choose: n (new remote)
   # Name: gdrive
   # Storage: Google Drive
   # Follow the prompts and authenticate in your browser
   ```

3. **Extract the token from your computer**:
   ```bash
   # On your computer:
   cat ~/.config/rclone/rclone.conf
   ```

4. **Copy the config to the server**:
   ```bash
   # Copy the entire [gdrive] section from your computer's rclone.conf
   # and paste it into /root/.config/rclone/rclone.conf on the server

   # On server:
   mkdir -p /root/.config/rclone
   nano /root/.config/rclone/rclone.conf
   # Paste the [gdrive] section and save
   ```

5. **Test the connection**:
   ```bash
   # On server:
   rclone lsd gdrive:
   # Should list your Google Drive folders
   ```

## Option 3: Use Service Account (For Advanced Users)

If you want fully automated backups without user interaction:

1. Create a Google Cloud Project
2. Enable Google Drive API
3. Create a Service Account
4. Download the JSON key
5. Configure rclone with the service account

See: https://rclone.org/drive/#service-account-support

## After Setup

Once Google Drive is configured, run:

```bash
# Create sync script
cat > /root/backups/sync_to_gdrive.sh << 'EOF'
#!/bin/bash
BACKUP_LOG="/var/log/gdrive_sync.log"

echo "=== Google Drive Sync Started: $(date) ===" | tee -a "$BACKUP_LOG"

# Sync combined volume backups
rclone copy /root/backups/docker-volumes-*.tar.gz gdrive:ServerBackups/VolumeBackups/ \
    --progress --log-file="$BACKUP_LOG" --log-level INFO

# Sync config backup
rclone sync /root/server-config-backup gdrive:ServerBackups/ConfigBackup/ \
    --exclude ".git/**" --progress --log-file="$BACKUP_LOG" --log-level INFO

# Clean old backups (keep last 7 days)
rclone delete gdrive:ServerBackups/VolumeBackups/ \
    --min-age 7d --log-file="$BACKUP_LOG" --log-level INFO

echo "=== Sync Complete: $(date) ===" | tee -a "$BACKUP_LOG"
EOF

chmod +x /root/backups/sync_to_gdrive.sh

# Test it
/root/backups/sync_to_gdrive.sh
```

## Add to Daily Backups

Once working, add Google Drive sync to automated backups:

```bash
# Edit the cron job
crontab -e

# Change the line to:
0 2 * * * /root/backups/full_backup.sh && /root/backups/sync_to_gdrive.sh >> /var/log/full_backup.log 2>&1
```

This will:
1. Run backup at 2 AM daily
2. Then automatically sync to Google Drive

## Current Status

Your server is already set up with:
- ✅ Configuration backup in Git: https://github.com/systemccg/server-config-backup.git
- ✅ Docker volume backup: /root/backups/docker-volumes-20251114_012843.tar.gz (2.3GB)
- ✅ Automated daily backups at 2:00 AM

The only remaining step is Google Drive authentication, which you can do when convenient.
