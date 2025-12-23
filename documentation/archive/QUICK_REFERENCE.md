# Server Backup & Reproduction - Quick Reference

## Daily Operations

### Run Manual Backup
```bash
# Full backup (configs + volumes)
/root/backups/full_backup.sh

# Just configurations
/root/backups/backup_configs.sh

# Just Docker volumes
/root/backups/backup_volumes.sh
```

### Check Backup Status
```bash
# View backup logs
tail -f /var/log/full_backup.log

# List recent backups
ls -lh /root/backups/docker-volumes-*.tar.gz
ls -lh /root/backups/volumes/

# Check config backup git status
cd /root/server-config-backup && git status
```

### Push Config Backup to Remote
```bash
cd /root/server-config-backup
git add .
git commit -m "Backup $(date +%Y-%m-%d)"
git push
```

## Reproduction on New Server

### Step 1: Install Base System
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Step 2: Clone Upstream Repos
```bash
cd /root
git clone -b stable https://github.com/coleam00/local-ai-packaged.git
git clone https://github.com/getzep/graphiti.git
```

### Step 3: Restore Your Customizations
```bash
# Clone your config backup repo
git clone <your-private-repo-url> /root/server-config-backup

# Run restoration
cd /root/server-config-backup
./restore_configs.sh
```

### Step 4: Restore Docker Volumes
```bash
# Upload and extract volume backup
scp docker-volumes-*.tar.gz root@new-server:/root/backups/
ssh root@new-server "tar -xzf /root/backups/docker-volumes-*.tar.gz -C /root/backups/"

# Restore volumes interactively
/root/backups/restore_volumes.sh --interactive

# Or restore all at once
/root/backups/restore_volumes.sh --all
```

### Step 5: Start Services
```bash
# Traefik first
cd /root/traefik && docker compose up -d

# WordPress
cd /root/wordpress && docker compose up -d

# Local AI stack
cd /root/local-ai-packaged && python3 start_services.py --profile cpu

# Other services
cd /root/portainer && docker compose up -d
cd /root/filebrowser && docker compose up -d
```

## Updating from Upstream Repos

### Safe Update Process
```bash
# Navigate to repo directory
cd /root/local-ai-packaged

# Run update script
/root/backups/update_from_upstream.sh
# Or specify custom repo:
# /root/backups/update_from_upstream.sh /root/graphiti https://github.com/getzep/graphiti.git main
```

### Manual Update
```bash
cd /root/local-ai-packaged

# Initialize as git repo if needed
git init
git add .
git commit -m "Current state"

# Add upstream
git remote add upstream https://github.com/coleam00/local-ai-packaged.git

# Fetch and review changes
git fetch upstream
git log HEAD..upstream/stable --oneline
git diff HEAD..upstream/stable

# Merge (keeping your .env)
git merge upstream/stable --no-commit
git checkout HEAD .env  # Keep your .env
git commit -m "Merge upstream updates"
```

## Automated Backups

### Setup Daily Backups
```bash
/root/backups/setup_automated_backups.sh
```

### Manual Cron Setup
```bash
# Add to crontab
crontab -e

# Add this line for daily 2 AM backups:
0 2 * * * /root/backups/full_backup.sh >> /var/log/full_backup.log 2>&1
```

## File Locations

| Item | Location |
|------|----------|
| Backup scripts | `/root/backups/` |
| Config backup (git repo) | `/root/server-config-backup/` |
| Volume backups | `/root/backups/volumes/` |
| Combined archives | `/root/backups/docker-volumes-*.tar.gz` |
| Logs | `/var/log/*backup.log` |
| Main docs | `/root/SERVER_REPRODUCTION_GUIDE.md` |

## Restoration Commands

### Restore Specific Volume
```bash
/root/backups/restore_volumes.sh wordpress_mysql_data
```

### Restore Interactively
```bash
/root/backups/restore_volumes.sh --interactive
```

### List Available Backups
```bash
ls -1 /root/backups/volumes/*_latest.tar.gz | sed 's/.*\///' | sed 's/_latest\.tar\.gz$//'
```

## Troubleshooting

### Backup Failed
```bash
# Check logs
tail -50 /var/log/full_backup.log

# Check disk space
df -h

# Test individual scripts
/root/backups/backup_configs.sh
/root/backups/backup_volumes.sh
```

### Restore Failed
```bash
# Check restore logs
tail -50 /var/log/volume_restore.log

# Verify backup file exists
ls -lh /root/backups/volumes/*_latest.tar.gz

# Check Docker is running
docker ps

# Manually restore a volume
docker volume create test_volume
docker run --rm -v test_volume:/data -v /root/backups/volumes:/backup alpine tar xzf /backup/wordpress_mysql_data_latest.tar.gz -C /data
```

### Git Push Fails
```bash
cd /root/server-config-backup

# Check remote
git remote -v

# Add remote if missing
git remote add origin <your-private-repo-url>

# Push
git push -u origin main
```

## Security Notes

1. The config backup contains `.env` files with secrets
2. Only push to PRIVATE Git repositories
3. Consider encrypting `.env` files before committing
4. Store volume backups off-server (S3, another server, etc.)
5. Restrict access to backup files (they contain sensitive data)

## Backup Size Estimates

- Config backup: < 10 MB (mostly text files)
- Docker volumes: Varies widely
  - WordPress: ~100-500 MB
  - Supabase DB: Depends on data
  - n8n: ~50-200 MB
  - Total: Typically 1-5 GB

## Important Files to NEVER Lose

1. `/root/local-ai-packaged/.env` - **CRITICAL** (all secrets)
2. `/root/server-config-backup/` - Your customizations
3. Docker volumes: `wordpress_*`, `portainer_*`, `local-ai-packaged_*`
4. `/root/scripts/` - Custom automation
5. `/root/traefik/` - Reverse proxy config

## Recovery Time Estimates

- Install base system: 15-30 min
- Clone repos: 5 min
- Restore configs: 2 min
- Restore volumes: 15-60 min (depends on size)
- Start services: 5-10 min
- Verify/debug: 15-30 min
- **Total: 1-2 hours**
