# Server Migration Plan - Comprehensive Guide

**Date Created**: 2025-11-10
**Current Server**: leadingai.info
**Target**: New server location

## Overview

This server runs a Docker-based AI infrastructure with multiple services. Migration requires handling:
- Configuration files (→ GitHub)
- Application data (→ Database exports + volume backups)
- Secrets/credentials (→ Secure transfer, NOT GitHub)

---

## Current System Inventory

### Services Running
- **Supabase** (PostgreSQL, Auth, Storage, Realtime, Studio)
- **n8n** (Workflow automation + SQLite database)
- **Neo4j** (Graph database)
- **Langfuse** (LLM observability + ClickHouse + MinIO + Postgres)
- **Qdrant** (Vector database)
- **Coolify** (Deployment platform)
- **MCP Server** (n8n-mcp)

### Key Directories
```
/root/local-ai-packaged/         # Main application (3.1GB)
├── docker-compose.yml           # Main orchestration
├── .env                         # ⚠️ SECRETS - do NOT commit
├── supabase/                    # Supabase setup
├── n8n/                         # n8n workflows & docs
├── backups/                     # Existing backups
└── CLAUDE.md                    # AI assistant guidance

/root/mcp/                       # MCP server configs
/root/graphiti/                  # Graphiti configs
```

### Docker Volumes (39 total)
Critical data volumes:
- `supabase_db-config` - Supabase database
- `n8n_storage` - n8n data & SQLite DB
- `graphiti_neo4j_data` - Neo4j graph data
- `local-ai-packaged_qdrant_storage` - Vector embeddings
- `local-ai-packaged_langfuse_*` - Langfuse data (Postgres, ClickHouse, MinIO)

---

## Migration Strategy

### Phase 1: Configuration & Code (GitHub)

**What goes to GitHub:**
```
✅ docker-compose.yml
✅ docker-compose.override.yml
✅ Caddyfile
✅ All scripts (*.sh)
✅ Documentation (*.md)
✅ n8n workflow JSONs (from backups)
✅ Application configs (non-secret)
✅ .env.example (template without secrets)
```

**What NEVER goes to GitHub:**
```
❌ .env (actual secrets)
❌ Database dumps
❌ API keys, tokens, passwords
❌ SSL certificates
❌ Docker volume data
```

### Phase 2: Data Export

**1. n8n Workflows**
```bash
# Export all workflows
docker exec n8n n8n export:workflow --all --output=/data/workflow_export.json
docker cp n8n:/data/workflow_export.json /root/migration/n8n_workflows.json

# Export credentials (encrypted)
docker exec n8n n8n export:credentials --all --output=/data/credentials_export.json
docker cp n8n:/data/credentials_export.json /root/migration/n8n_credentials.json
```

**2. Supabase (PostgreSQL)**
```bash
# Full database dump
docker exec supabase-db pg_dumpall -U postgres > /root/migration/supabase_full_dump.sql

# Or specific database
docker exec supabase-db pg_dump -U postgres postgres > /root/migration/supabase_postgres_dump.sql
```

**3. n8n SQLite Database**
```bash
# Export n8n's internal database
docker exec n8n sqlite3 /home/node/.n8n/database.sqlite ".dump" > /root/migration/n8n_database.sql

# Or copy the file directly
docker cp n8n:/home/node/.n8n/database.sqlite /root/migration/n8n_database.sqlite
```

**4. Neo4j Graph Database**
```bash
# Stop Neo4j first
docker stop localai-neo4j-1

# Export Neo4j data
docker run --rm \
  -v graphiti_neo4j_data:/data \
  -v /root/migration:/backup \
  neo4j:latest \
  neo4j-admin database dump neo4j --to-path=/backup

# Restart Neo4j
docker start localai-neo4j-1
```

**5. Qdrant Vector Database**
```bash
# Backup Qdrant storage
docker run --rm \
  -v local-ai-packaged_qdrant_storage:/source \
  -v /root/migration:/backup \
  alpine tar czf /backup/qdrant_backup.tar.gz -C /source .
```

**6. Langfuse Data**
```bash
# Postgres backup
docker exec local-ai-packaged-langfuse-postgres-1 \
  pg_dump -U postgres langfuse > /root/migration/langfuse_postgres.sql

# ClickHouse backup (if needed)
# MinIO backup (object storage - can sync with mc/rclone)
```

### Phase 3: Secrets & Environment Files

**Securely transfer (DO NOT use GitHub):**
```bash
# Copy all .env files
cp /root/local-ai-packaged/.env /root/migration/env_main
cp /root/local-ai-packaged/supabase/docker/.env /root/migration/env_supabase

# Copy any SSL certificates
cp -r /root/ssl_certs /root/migration/ssl_certs 2>/dev/null

# Compress for secure transfer
cd /root/migration
tar czf secrets_$(date +%Y%m%d).tar.gz env_* ssl_certs
```

**Transfer methods (choose one):**
- `scp` to new server directly
- Encrypted USB drive
- Secure file transfer service (with encryption)
- Cloud storage with encryption (temporary)

### Phase 4: Docker Volume Backup (Full Safety Net)

```bash
#!/bin/bash
# Backup all Docker volumes

BACKUP_DIR="/root/migration/docker_volumes"
mkdir -p $BACKUP_DIR

# Get list of volumes
VOLUMES=$(docker volume ls -q | grep -E "supabase|n8n|neo4j|langfuse|qdrant")

for VOLUME in $VOLUMES; do
  echo "Backing up $VOLUME..."
  docker run --rm \
    -v $VOLUME:/source \
    -v $BACKUP_DIR:/backup \
    alpine tar czf /backup/${VOLUME}.tar.gz -C /source .
done

echo "✅ All volumes backed up to $BACKUP_DIR"
```

---

## New Server Restoration Process

### Step 1: Fresh Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Install git
sudo apt install git -y
```

### Step 2: Clone Repository

```bash
# Clone from GitHub
cd /root
git clone https://github.com/YOUR_USERNAME/local-ai-packaged.git

cd local-ai-packaged
```

### Step 3: Restore Secrets

```bash
# Transfer secrets archive to new server (via scp or other secure method)
# Then extract:
cd /root
tar xzf secrets_YYYYMMDD.tar.gz

# Restore .env files
cp env_main /root/local-ai-packaged/.env
cp env_supabase /root/local-ai-packaged/supabase/docker/.env
```

### Step 4: Restore Data

**Option A: Database-Only Restore (Recommended)**

```bash
# Start services first
cd /root/local-ai-packaged
docker-compose up -d

# Wait for services to initialize
sleep 30

# Restore Supabase
cat /root/migration/supabase_postgres_dump.sql | \
  docker exec -i supabase-db psql -U postgres postgres

# Restore n8n SQLite
docker cp /root/migration/n8n_database.sqlite n8n:/home/node/.n8n/database.sqlite
docker restart n8n

# Restore n8n workflows (if not using SQLite restore)
docker exec -i n8n n8n import:workflow --input=/dev/stdin < /root/migration/n8n_workflows.json

# Restore Neo4j
docker stop localai-neo4j-1
docker run --rm \
  -v graphiti_neo4j_data:/data \
  -v /root/migration:/backup \
  neo4j:latest \
  neo4j-admin database load neo4j --from-path=/backup
docker start localai-neo4j-1

# Restore Qdrant
docker run --rm \
  -v local-ai-packaged_qdrant_storage:/target \
  -v /root/migration:/backup \
  alpine tar xzf /backup/qdrant_backup.tar.gz -C /target
```

**Option B: Full Volume Restore (Complete Safety)**

```bash
# Stop all services
docker-compose down

# Restore each volume
cd /root/migration/docker_volumes
for ARCHIVE in *.tar.gz; do
  VOLUME_NAME=$(basename $ARCHIVE .tar.gz)
  echo "Restoring $VOLUME_NAME..."

  # Create volume if doesn't exist
  docker volume create $VOLUME_NAME

  # Restore data
  docker run --rm \
    -v $VOLUME_NAME:/target \
    -v $(pwd):/backup \
    alpine tar xzf /backup/$ARCHIVE -C /target
done

# Start services
docker-compose up -d
```

### Step 5: Verification

```bash
# Check all containers are running
docker ps

# Check n8n
curl https://n8n.leadingai.info
docker logs n8n --tail 50

# Check Supabase
curl https://db.leadingai.info
docker exec supabase-db psql -U postgres -c "SELECT count(*) FROM auth.users;"

# Check Neo4j
docker logs localai-neo4j-1 --tail 50

# Verify workflows in n8n
docker exec n8n n8n list:workflow
```

---

## Migration Checklist

### Pre-Migration
- [ ] Document all running services
- [ ] Note all custom configurations
- [ ] Test current system functionality
- [ ] Create full backup of current server
- [ ] Verify backup integrity

### Export Phase
- [ ] Export all n8n workflows
- [ ] Export all n8n credentials
- [ ] Dump Supabase PostgreSQL
- [ ] Backup n8n SQLite database
- [ ] Export Neo4j graph data
- [ ] Backup Qdrant vectors
- [ ] Backup Langfuse data
- [ ] Backup all Docker volumes (safety net)
- [ ] Copy all .env files securely
- [ ] Copy SSL certificates

### GitHub Phase
- [ ] Create private GitHub repository
- [ ] Add all configuration files
- [ ] Add documentation
- [ ] Add restoration scripts
- [ ] Add .env.example (template)
- [ ] Verify .gitignore excludes secrets

### Transfer Phase
- [ ] Securely transfer secrets archive
- [ ] Securely transfer database dumps
- [ ] Securely transfer volume backups
- [ ] Verify file integrity (checksums)

### New Server Phase
- [ ] Setup new server (Docker, compose, git)
- [ ] Clone repository
- [ ] Restore secrets
- [ ] Restore data/databases
- [ ] Start services
- [ ] Verify all services running
- [ ] Test all workflows
- [ ] Verify data integrity
- [ ] Update DNS (if changing domains)
- [ ] Test SSL certificates

### Post-Migration
- [ ] Monitor logs for errors
- [ ] Test all integrations
- [ ] Verify backups on new server
- [ ] Document any issues
- [ ] Keep old server running for 1-2 weeks

---

## Estimated Sizes & Time

```
Configuration files:    ~50 MB     (5 minutes)
n8n workflows:         ~5 MB      (2 minutes)
Supabase DB:           ~500 MB    (10 minutes)
n8n SQLite:            ~100 MB    (2 minutes)
Neo4j:                 ~200 MB    (5 minutes)
Qdrant:                ~1 GB      (15 minutes)
Langfuse:              ~500 MB    (10 minutes)
Other volumes:         ~500 MB    (10 minutes)
Total:                 ~3-4 GB    (1-2 hours)
```

---

## Quick Start Command

```bash
# Run the automated migration script (to be created)
cd /root
curl -O https://raw.githubusercontent.com/YOUR_REPO/main/scripts/migrate_server.sh
chmod +x migrate_server.sh
./migrate_server.sh --export
```

---

## Support & Recovery

If migration fails:
1. Old server is still intact
2. All backups are preserved
3. Can restore to old server
4. Can retry migration

**Critical files location:**
- Backups: `/root/migration/`
- Documentation: This file
- Scripts: `/root/local-ai-packaged/scripts/`

---

## Next Steps

1. Review this plan
2. Create GitHub repository
3. Run export scripts
4. Test restoration on a test server (optional but recommended)
5. Execute actual migration
