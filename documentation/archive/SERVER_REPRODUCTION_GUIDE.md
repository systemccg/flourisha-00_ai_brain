# Server Reproduction Guide

This guide will help you safely reproduce this entire server on a new machine without losing your custom configurations.

## Problem Statement

Your server contains:
- **Public GitHub repos** (local-ai-packaged, graphiti) that you've customized
- **Custom configurations** (.env files, docker-compose.yml modifications)
- **Persistent data** (databases, uploaded files, credentials)

If you simply clone the upstream repos, your customizations would be lost.

## Solution: Three-Layer Backup Strategy

### Layer 1: Configuration Backup (Your Customizations)

Create a **private Git repository** for your custom configurations only:

```bash
# Create a new directory for your custom configs
mkdir -p /root/server-config-backup
cd /root/server-config-backup

# Initialize git
git init
git config user.email "your-email@example.com"
git config user.name "Your Name"

# Copy ONLY your custom configurations (not upstream repo content)
# See backup_configs.sh script below
```

### Layer 2: Docker Volume Backup (Your Data)

Backup all Docker volumes containing persistent data:
- Database content
- Uploaded files
- Application state
- Credentials

### Layer 3: Documentation (How to Rebuild)

Document the exact steps to reproduce the server from scratch.

---

## Step-by-Step Reproduction Process

### Phase 1: Prepare New Server

1. **Install base requirements**:
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
mkdir -p /usr/local/lib/docker/cli-plugins
ln -s /usr/local/bin/docker-compose /usr/local/lib/docker/cli-plugins/docker-compose

# Install other utilities
apt install -y git curl wget rsync python3 python3-pip ufw
```

2. **Setup firewall** (optional):
```bash
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

### Phase 2: Clone Upstream Repos

Clone the original public repos to get the base setup:

```bash
cd /root

# Clone local-ai-packaged (main AI stack)
git clone -b stable https://github.com/coleam00/local-ai-packaged.git

# Clone graphiti (if you use it)
git clone https://github.com/getzep/graphiti.git

# Don't track these as git repos anymore (to avoid conflicts with your changes)
# We'll handle updates manually when needed
```

### Phase 3: Restore Your Custom Configurations

Now overlay YOUR customizations on top of the upstream repos:

```bash
# If you created a server-config-backup repo (from backup script):
cd /root
git clone <your-private-repo-url> server-config-restore

# Run the restore script (created by backup_configs.sh)
cd server-config-restore
./restore_configs.sh
```

OR manually restore key files:

```bash
# Restore .env files (CRITICAL - contains all secrets)
cp /path/to/backup/local-ai-packaged/.env /root/local-ai-packaged/.env

# Restore modified docker-compose files
cp /path/to/backup/wordpress/docker-compose.yml /root/wordpress/docker-compose.yml
cp /path/to/backup/traefik/docker-compose.yml /root/traefik/docker-compose.yml
# ... etc for other services

# Restore scripts
cp -r /path/to/backup/scripts /root/scripts

# Restore custom service configs
cp -r /path/to/backup/filebrowser /root/filebrowser
cp -r /path/to/backup/portainer /root/portainer
cp -r /path/to/backup/monitoring /root/monitoring
```

### Phase 4: Restore Docker Volumes

```bash
# Restore volumes from backup (created by backup_volumes.sh)
cd /root
tar -xzf /path/to/backup/docker-volumes-YYYY-MM-DD.tar.gz

# Import each volume
docker volume create wordpress_mysql_data
docker run --rm -v wordpress_mysql_data:/data -v /root/volume-backups:/backup alpine sh -c "cd /data && tar xzf /backup/wordpress_mysql_data.tar.gz"

docker volume create wordpress_wordpress_data
docker run --rm -v wordpress_wordpress_data:/data -v /root/volume-backups:/backup alpine sh -c "cd /data && tar xzf /backup/wordpress_wordpress_data.tar.gz"

# Repeat for all critical volumes...
# See restore_volumes.sh script for automated version
```

### Phase 5: Start Services

```bash
# Start Traefik first (reverse proxy)
cd /root/traefik
docker compose up -d

# Start WordPress
cd /root/wordpress
docker compose up -d

# Start local-ai-packaged stack
cd /root/local-ai-packaged
python3 start_services.py --profile cpu --environment public

# Start other services
cd /root/portainer && docker compose up -d
cd /root/filebrowser && docker compose up -d
cd /root/monitoring && docker compose up -d
```

### Phase 6: Verify Services

```bash
# Check all containers are running
docker ps

# Test each service endpoint
curl -I https://wordpress.leadingai.info
curl -I https://n8n.leadingai.info
curl -I https://db.leadingai.info
# etc...
```

---

## Managing Updates from Upstream Repos

**Problem**: You've customized local-ai-packaged. How do you get updates without losing your changes?

**Solution**: Manual selective merge

1. **Check for updates**:
```bash
cd /root/local-ai-packaged
git remote add upstream https://github.com/coleam00/local-ai-packaged.git
git fetch upstream
git log HEAD..upstream/stable --oneline  # See what's new
```

2. **Review changes before merging**:
```bash
git diff HEAD..upstream/stable  # See all changes
```

3. **Selectively merge**:
```bash
# Option A: Cherry-pick specific commits
git cherry-pick <commit-hash>

# Option B: Merge but keep your .env and custom files
git merge upstream/stable --no-commit
git checkout HEAD .env  # Keep your .env
git checkout HEAD docker-compose.yml  # Keep your compose file if customized
git commit -m "Merge upstream updates, keeping local customizations"
```

4. **Test in dev first**:
```bash
# Always test major updates on a dev server first!
# Clone to a test directory and try the update there
```

---

## What to Backup Regularly

### Critical (Must Backup):
- `/root/local-ai-packaged/.env` - All secrets and configuration
- `/root/wordpress/docker-compose.yml` - WordPress config
- `/root/traefik/` - Reverse proxy config
- `/root/scripts/` - Custom scripts
- Docker volumes: `wordpress_*`, `portainer_*`, `local-ai-packaged_*`, `supabase_*`
- n8n workflows and credentials backups

### Nice to Have:
- `/root/monitoring/` - Can be recreated
- `/root/filebrowser/` - Can be recreated
- System config: `/etc/ufw/`, crontabs, systemd services

### Don't Need to Backup:
- Docker images (can be re-pulled)
- Upstream repo code (can be re-cloned)
- `/root/graphiti/` if you haven't customized it
- `/root/.nvm/` (can be reinstalled)

---

## Automation Scripts

See the following scripts in `/root/backups/`:
- `backup_configs.sh` - Backs up all configuration files
- `backup_volumes.sh` - Backs up all Docker volumes
- `restore_configs.sh` - Restores configuration files
- `restore_volumes.sh` - Restores Docker volumes
- `full_backup.sh` - Runs both config and volume backups

Run daily via cron:
```bash
0 2 * * * /root/backups/full_backup.sh >> /var/log/server_backup.log 2>&1
```

---

## Emergency Recovery

If the server crashes and you need to recover:

1. Spin up a new server
2. Install Docker/Docker Compose
3. Restore configs from your private Git repo
4. Restore volumes from latest backup tarball
5. Start services in order: Traefik → Individual services → Local AI stack

**Recovery Time Estimate**: 1-2 hours with good backups

---

## Best Practices

1. **Keep a private Git repo** for your configs (NOT public repos content)
2. **Backup volumes weekly** (contains your data)
3. **Document every customization** you make to upstream repos
4. **Test restoration process** on a dev server periodically
5. **Version your .env files** (encrypted or in private repo)
6. **Keep backup scripts updated** as you add new services
7. **Store backups off-server** (S3, Backblaze, another server)

---

## File Structure for Backups

```
/root/
├── server-config-backup/          # Your private Git repo
│   ├── .env.encrypted              # Encrypted environment files
│   ├── docker-compose/             # Modified docker-compose files
│   │   ├── wordpress.yml
│   │   ├── traefik.yml
│   │   └── ...
│   ├── scripts/                    # Custom scripts
│   ├── configs/                    # Service configs (nginx, etc)
│   ├── backup_configs.sh           # Config backup script
│   ├── restore_configs.sh          # Config restore script
│   └── README.md                   # Your customization notes
│
└── backups/                        # Local backups (also copy off-server)
    ├── volumes/                    # Docker volume backups
    │   └── docker-volumes-2025-11-13.tar.gz
    ├── backup_volumes.sh
    ├── restore_volumes.sh
    └── full_backup.sh
```

---

## Next Steps

Run the backup scripts provided to:
1. Create your first configuration backup
2. Create your first volume backup
3. Test the restoration process on a dev server
4. Set up automated daily backups
5. Push config backups to a private Git repository
