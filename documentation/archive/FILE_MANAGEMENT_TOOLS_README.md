# File Management Tools - Installation Summary

**Installation Date**: 2025-11-12 23:30 CET
**Server**: 66.94.121.10 (Tailscale IP: 100.66.28.67)

## 📦 Installed Tools

### 1. Cockpit Navigator v0.5.10
**Purpose**: Web-based file browser integrated into Cockpit system management

**Access**:
- URL: `https://100.66.28.67:9090` (Tailscale only)
- Credentials: Use root login

**Installation Details**:
- Package: `cockpit-navigator_0.5.10-1focal_all.deb`
- Source: https://github.com/45Drives/cockpit-navigator/releases/tag/v0.5.10
- Service: cockpit.socket (active)

**Configuration**:
```bash
# Installation commands
wget https://github.com/45Drives/cockpit-navigator/releases/download/v0.5.10/cockpit-navigator_0.5.10-1focal_all.deb -O /tmp/cockpit-navigator.deb
apt install -y /tmp/cockpit-navigator_0.5.10-1focal_all.deb
systemctl restart cockpit.socket
```

---

### 2. Portainer CE 2.20.2
**Purpose**: Docker container management web interface

**Access**:
- URL: `http://66.94.121.10:9000` (HTTP, public)
- URL: `https://66.94.121.10:9443` (HTTPS, public)
- Credentials:
  - Username: `admin`
  - Password: `PortainerAdmin2024`

**Version Information**:
- ⚠️ **Important**: Running v2.20.2 (not latest) due to Docker 29.0.0 compatibility
- Docker 29.0.0 requires API v1.44+
- Portainer 2.33.3 only supports API v1.41 (incompatible)
- Related Issue: https://github.com/portainer/portainer/issues/12925

**Installation Details**:
- Image: `portainer/portainer-ce:2.20.2`
- Container: portainer
- Status: Up 30 minutes
- Ports: 9000 (HTTP), 9443 (HTTPS)
- Docker socket: `/var/run/docker.sock` (read-write)
- Data volume: `portainer_portainer_data`

**Configuration File**: `/root/portainer/docker-compose.yml`
```yaml
services:
  portainer:
    image: portainer/portainer-ce:2.20.2
    container_name: portainer
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
    ports:
      - "9000:9000"
      - "9443:9443"

volumes:
  portainer_data:
```

**Known Issue - Fixed**:
- **Problem**: "Failed loading environment - The environment named local is unreachable"
- **Root Cause**: Docker 29.0 API v1.52 incompatible with Portainer 2.33.3 (API v1.41)
- **Solution**: Downgraded to Portainer 2.20.2
- **Status**: ✅ Working perfectly

**Upgrade Path**:
When Portainer releases a version supporting Docker API v1.44+:
```bash
cd /root/portainer
# Edit docker-compose.yml: change image to new version
docker compose down
docker compose pull
docker compose up -d
```

---

### 3. Filebrowser (Latest)
**Purpose**: Web-based file manager with full root filesystem access

**Access**:
- URL: `http://100.66.28.67:8080` (Tailscale only)
- Credentials:
  - Username: `systemccg`
  - Password: (user-set via web interface)

**Installation Details**:
- Image: `filebrowser/filebrowser:latest`
- Container: filebrowser
- Status: Up 3 hours (healthy)
- Port: 8080 (bound to Tailscale IP only)
- Root mount: `/` → `/srv` (full filesystem access)
- Database: `/database/filebrowser.db` (SQLite)

**Security Configuration**:
- Runs as root: `user: "0:0"` (required for full filesystem permissions)
- Bound to Tailscale IP only: `100.66.28.67:8080`
- Network: `management_network` (external)

**Configuration File**: `/root/filebrowser/docker-compose.yml`
```yaml
version: '3.8'

services:
  filebrowser:
    image: filebrowser/filebrowser:latest
    container_name: filebrowser
    restart: unless-stopped
    user: "0:0"
    volumes:
      - /:/srv
      - filebrowser_data:/database
      - filebrowser_config:/config
    environment:
      - PUID=0
      - PGID=0
    ports:
      - "100.66.28.67:8080:80"
    networks:
      - management
    command:
      - --database
      - /database/filebrowser.db
      - --root
      - /srv

volumes:
  filebrowser_data:
  filebrowser_config:

networks:
  management:
    name: management_network
    external: true
```

**User Configuration**:
- Default admin user renamed to: `systemccg`
- User scope: `/` (full root access)
- Permissions: Full admin rights

**Database Location**:
```bash
/var/lib/docker/volumes/filebrowser_filebrowser_data/_data/filebrowser.db
```

**CLI Management**:
```bash
# Update user password
docker run --rm -v filebrowser_filebrowser_data:/database \
  filebrowser/filebrowser:latest \
  users update systemccg --password "newpassword" \
  --database /database/filebrowser.db

# Add new user
docker run --rm -v filebrowser_filebrowser_data:/database \
  filebrowser/filebrowser:latest \
  users add username password \
  --scope /srv/restricted/path \
  --database /database/filebrowser.db
```

---

## 🔒 Security Configuration

### Tailscale VPN Access
- **Server Tailscale IP**: `100.66.28.67`
- **Network Name**: leadingai004
- **Services on Tailscale**:
  - Cockpit Navigator: Port 9090
  - Filebrowser: Port 8080

### Public Access
- **Portainer**: Ports 9000, 9443 (public IP: 66.94.121.10)
  - ⚠️ Consider adding authentication layer or restricting access
  - Currently uses admin password: `PortainerAdmin2024`

### Network Configuration
- Cockpit: System service (systemd)
- Portainer: `portainer_default` network
- Filebrowser: `management_network` (external)

---

## 📋 Management Commands

### Check Service Status
```bash
# Cockpit
systemctl status cockpit.socket

# Portainer
docker ps | grep portainer
docker logs portainer

# Filebrowser
docker ps | grep filebrowser
docker logs filebrowser
```

### Restart Services
```bash
# Cockpit
systemctl restart cockpit.socket

# Portainer
cd /root/portainer
docker compose restart

# Filebrowser
cd /root/filebrowser
docker compose restart
```

### Update Services
```bash
# Portainer (when compatible version available)
cd /root/portainer
docker compose pull
docker compose up -d

# Filebrowser
cd /root/filebrowser
docker compose pull
docker compose up -d
```

### Backup Configurations
```bash
# Backup Portainer data
docker run --rm -v portainer_portainer_data:/data -v /tmp:/backup \
  alpine tar czf /backup/portainer_backup_$(date +%Y%m%d).tar.gz -C /data .

# Backup Filebrowser data
docker run --rm -v filebrowser_filebrowser_data:/data -v /tmp:/backup \
  alpine tar czf /backup/filebrowser_backup_$(date +%Y%m%d).tar.gz -C /data .
```

---

## 🐛 Troubleshooting

### Portainer "Failed loading environment" Error
**Symptoms**: Cannot access local Docker environment, error message shows environment is unreachable

**Diagnosis**:
```bash
# Check Docker API version
docker version --format '{{.Server.APIVersion}}'

# Check Portainer version
docker inspect portainer --format '{{.Config.Image}}'
```

**Fix**: Already applied - downgraded to v2.20.2
- Docker 29.0+ requires Portainer with API v1.44+ support
- Currently running v2.20.2 which is compatible

### Filebrowser Permission Denied Errors
**Symptoms**: Cannot access certain directories

**Fix**: Verify container runs as root
```bash
# Check user
docker exec filebrowser id
# Should show: uid=0(root) gid=0(root)

# If not running as root, update docker-compose.yml:
user: "0:0"
```

### Cockpit Navigator Not Showing
**Symptoms**: Navigator option missing in Cockpit interface

**Fix**: Restart cockpit service
```bash
systemctl restart cockpit.socket
# Clear browser cache and reload
```

### Cannot Access via Tailscale
**Symptoms**: Connection refused or timeout

**Diagnosis**:
```bash
# Check Tailscale status
tailscale status

# Check Tailscale IP
tailscale ip -4

# Verify port binding
ss -tlnp | grep 8080  # Filebrowser
ss -tlnp | grep 9090  # Cockpit
```

---

## 📚 References

- **Cockpit Navigator**: https://github.com/45Drives/cockpit-navigator
- **Portainer Docs**: https://docs.portainer.io
- **Portainer GitHub Issue #12925**: https://github.com/portainer/portainer/issues/12925
- **Filebrowser Docs**: https://filebrowser.org
- **Tailscale Docs**: https://tailscale.com/kb

---

## 🔄 Change Log

### 2025-11-12 23:30 CET - Initial Installation
- ✅ Installed Cockpit Navigator v0.5.10
- ✅ Installed Portainer 2.20.2 (downgraded from 2.33.3)
  - Fixed Docker 29.0 API compatibility issue
  - Created admin account: admin / PortainerAdmin2024
- ✅ Installed Filebrowser with root filesystem access
  - Changed username from admin to systemccg
  - Configured to run as root (uid=0)
  - Mounted entire filesystem at /srv
- ✅ Configured Tailscale security for Cockpit and Filebrowser
- ✅ Public access configured for Portainer

---

**Installation completed successfully** ✅
All three file management tools are operational and accessible.
