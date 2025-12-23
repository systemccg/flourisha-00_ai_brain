# New Server Migration Steps
**New Server**: root@66.94.121.10
**Migration File**: migration_20251110.tar.gz (in local Downloads folder)

---

## Step 1: Upload Migration to New Server

**From your local machine:**

### Mac/Linux:
```bash
cd ~/Downloads
scp migration_20251110.tar.gz root@66.94.121.10:/root/
```

### Windows (PowerShell):
```powershell
cd ~\Downloads
scp migration_20251110.tar.gz root@66.94.121.10:/root/
```

### Alternative: If scp not available on Windows
Use WinSCP or:
```powershell
# Or use Windows Terminal/WSL
wsl scp ~/Downloads/migration_20251110.tar.gz root@66.94.121.10:/root/
```

---

## Step 2: Extract Migration on New Server

**SSH into new server:**
```bash
ssh root@66.94.121.10
```

**Extract migration:**
```bash
cd /root
tar xzf migration_20251110.tar.gz
ls -lh migration_20251110_214735/
```

---

## Step 3: Setup New Server

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install git
apt install git -y

# Verify installations
docker --version
git --version
```

---

## Step 4: Clone Your Repository

```bash
cd /root
git clone https://github.com/systemccg/leadingai.info.git local-ai-packaged
cd local-ai-packaged
```

---

## Step 5: Restore Secrets

```bash
# Extract secrets from migration
cd /root
tar xzf migration_20251110_214735/secrets_20251110_215015.tar.gz -C /tmp/

# Copy to project
cp /tmp/env_main /root/local-ai-packaged/.env
cp /tmp/env_supabase /root/local-ai-packaged/supabase/docker/.env

# Verify
ls -la /root/local-ai-packaged/.env
cat /root/local-ai-packaged/.env | head -5
```

---

## Step 6: Run Restoration Script

```bash
cd /root/local-ai-packaged
chmod +x scripts/restore_from_migration.sh
./scripts/restore_from_migration.sh /root/migration_20251110_214735
```

**This will:**
- Verify checksums ✓
- Start Docker containers ✓
- Restore all databases ✓
- Import workflows ✓
- Verify everything ✓

**Time**: ~20-30 minutes

---

## Step 7: Verify Everything Works

```bash
# Check containers
docker ps

# Check n8n
docker logs n8n --tail 50
docker exec n8n n8n list:workflow

# Check Supabase
docker exec supabase-db psql -U postgres -c "SELECT count(*) FROM auth.users;"
```

---

## Step 8: Update DNS (if needed)

If you're keeping the same domain (leadingai.info), update DNS:
- Point `n8n.leadingai.info` to `66.94.121.10`
- Point `db.leadingai.info` to `66.94.121.10`

---

## Troubleshooting

### If upload is slow:
```bash
# Check file size
ls -lh ~/Downloads/migration_20251110.tar.gz

# Monitor transfer progress (on new server)
watch -n 1 du -h /root/migration_20251110.tar.gz
```

### If restore fails:
```bash
# Check logs
docker-compose logs -f

# Restart specific service
docker-compose restart n8n

# Full restart
docker-compose down && docker-compose up -d
```

---

## Quick Reference

**Upload**: `scp migration_20251110.tar.gz root@66.94.121.10:/root/`
**SSH**: `ssh root@66.94.121.10`
**Restore**: `./scripts/restore_from_migration.sh /root/migration_20251110_214735`
