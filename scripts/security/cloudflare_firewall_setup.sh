#!/bin/bash
#
# Cloudflare Firewall Setup Script
# Configures UFW to only allow Cloudflare IPs for ports 80/443
# Keeps SSH and Tailscale access open for management
#
# Usage: ./cloudflare_firewall_setup.sh [--dry-run]
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}DRY RUN MODE - No changes will be made${NC}\n"
fi

echo "=========================================="
echo "Cloudflare Firewall Setup Script"
echo "=========================================="
echo ""

# Create backup directory
BACKUP_DIR="/root/backups/firewall_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo -e "${GREEN}[1/6] Backing up current UFW rules...${NC}"
if [ "$DRY_RUN" = false ]; then
    ufw status numbered > "$BACKUP_DIR/ufw_rules_before.txt"
    iptables-save > "$BACKUP_DIR/iptables_before.txt"
    echo "Backup saved to: $BACKUP_DIR"
else
    echo "[DRY RUN] Would backup to: $BACKUP_DIR"
fi

echo -e "\n${GREEN}[2/6] Fetching latest Cloudflare IP ranges...${NC}"
CF_IPV4=$(curl -s https://www.cloudflare.com/ips-v4)
CF_IPV6=$(curl -s https://www.cloudflare.com/ips-v6)

echo "Cloudflare IPv4 ranges:"
echo "$CF_IPV4"
echo ""
echo "Cloudflare IPv6 ranges:"
echo "$CF_IPV6"

# Save IP ranges for reference
echo "$CF_IPV4" > "$BACKUP_DIR/cloudflare_ipv4.txt"
echo "$CF_IPV6" > "$BACKUP_DIR/cloudflare_ipv6.txt"

echo -e "\n${GREEN}[3/6] Removing old HTTP/HTTPS rules...${NC}"
if [ "$DRY_RUN" = false ]; then
    # Remove existing allow rules for 80 and 443
    ufw --force delete allow 80/tcp 2>/dev/null || true
    ufw --force delete allow 443/tcp 2>/dev/null || true
    ufw --force delete allow 80 2>/dev/null || true
    ufw --force delete allow 443 2>/dev/null || true
    echo "Old rules removed"
else
    echo "[DRY RUN] Would remove existing allow rules for ports 80/tcp and 443/tcp"
fi

echo -e "\n${GREEN}[4/6] Adding Cloudflare IPv4 ranges to UFW...${NC}"
while IFS= read -r ip; do
    if [ -n "$ip" ]; then
        echo "  Adding: $ip (port 80)"
        if [ "$DRY_RUN" = false ]; then
            ufw allow from "$ip" to any port 80 proto tcp comment 'Cloudflare IPv4'
        fi

        echo "  Adding: $ip (port 443)"
        if [ "$DRY_RUN" = false ]; then
            ufw allow from "$ip" to any port 443 proto tcp comment 'Cloudflare IPv4'
        fi
    fi
done <<< "$CF_IPV4"

echo -e "\n${GREEN}[5/6] Adding Cloudflare IPv6 ranges to UFW...${NC}"
while IFS= read -r ip; do
    if [ -n "$ip" ]; then
        echo "  Adding: $ip (port 80)"
        if [ "$DRY_RUN" = false ]; then
            ufw allow from "$ip" to any port 80 proto tcp comment 'Cloudflare IPv6'
        fi

        echo "  Adding: $ip (port 443)"
        if [ "$DRY_RUN" = false ]; then
            ufw allow from "$ip" to any port 443 proto tcp comment 'Cloudflare IPv6'
        fi
    fi
done <<< "$CF_IPV6"

echo -e "\n${GREEN}[6/6] Verifying essential access is preserved...${NC}"
echo "Checking SSH (22) and Tailscale (41641) access..."

if [ "$DRY_RUN" = false ]; then
    # Ensure SSH is allowed (should already be there from security incident)
    ufw allow 22/tcp comment 'SSH' 2>/dev/null || true

    # Ensure Tailscale is allowed
    ufw allow 41641/udp comment 'Tailscale' 2>/dev/null || true

    # Reload UFW
    ufw reload

    echo -e "\n${GREEN}Setup complete!${NC}"
    echo ""
    echo "Current UFW status:"
    ufw status numbered

    # Save final state
    ufw status numbered > "$BACKUP_DIR/ufw_rules_after.txt"
    iptables-save > "$BACKUP_DIR/iptables_after.txt"
else
    echo "[DRY RUN] Would ensure SSH (22/tcp) and Tailscale (41641/udp) are allowed"
    echo "[DRY RUN] Would reload UFW"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Cloudflare Firewall Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "What was done:"
echo "  ✅ Backed up current firewall rules"
echo "  ✅ Removed unrestricted HTTP/HTTPS access"
echo "  ✅ Added Cloudflare IP ranges for ports 80/443"
echo "  ✅ Preserved SSH (22) and Tailscale (41641) access"
echo ""
echo "Next steps:"
echo "  1. Configure Cloudflare DNS (see /root/CLOUDFLARE_SETUP_GUIDE.md)"
echo "  2. Test that your sites work through Cloudflare"
echo "  3. Close any remaining direct port exposures"
echo ""
echo -e "${YELLOW}IMPORTANT: If you get locked out, you can restore from:${NC}"
echo "  $BACKUP_DIR"
echo ""
echo "To restore UFW rules manually:"
echo "  ufw reset"
echo "  ufw allow 22/tcp"
echo "  ufw allow 41641/udp"
echo "  ufw enable"
echo ""
