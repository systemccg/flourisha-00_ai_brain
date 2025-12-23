# Tor Proxy Setup

Configuration guide for Tor SOCKS5 proxy used by transcript services.

## Purpose

YouTube blocks transcript API requests from cloud provider IPs. Tor routes requests through residential exit nodes to bypass this restriction.

## Quick Start

```bash
# Install Tor
apt update && apt install -y tor

# Start and enable
systemctl start tor
systemctl enable tor

# Verify running
systemctl status tor
ss -tlnp | grep 9050
```

## Installation

### Ubuntu/Debian

```bash
apt update
apt install -y tor
```

### Verify Installation

```bash
which tor
tor --version
```

## Configuration

### Default Configuration

Tor runs with sensible defaults. The SOCKS5 proxy listens on:
- **Address:** `127.0.0.1`
- **Port:** `9050`

### Custom Configuration (Optional)

Edit `/etc/tor/torrc`:

```bash
# Allow connections from specific IPs (default is localhost only)
SocksPort 127.0.0.1:9050

# Use specific exit nodes (optional, for geo-targeting)
# ExitNodes {us},{de},{nl}

# Disable strict exit node selection
# StrictNodes 0
```

After changes:
```bash
systemctl restart tor
```

## Service Management

### Start/Stop/Restart

```bash
systemctl start tor
systemctl stop tor
systemctl restart tor
```

### Enable on Boot

```bash
systemctl enable tor
```

### Check Status

```bash
systemctl status tor
```

### View Logs

```bash
journalctl -u tor -f
```

## Verification

### Check Port 9050

```bash
ss -tlnp | grep 9050
# Expected output:
# LISTEN 0 4096 127.0.0.1:9050 0.0.0.0:* users:(("tor",pid=XXXX,fd=6))
```

### Test Tor Connection

```bash
# Install curl with SOCKS support
apt install -y curl

# Test via Tor
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip

# Should return JSON with "IsTor": true
```

### Test from Python

```python
import requests

proxies = {
    "http": "socks5://127.0.0.1:9050",
    "https": "socks5://127.0.0.1:9050"
}

response = requests.get(
    "https://check.torproject.org/api/ip",
    proxies=proxies
)
print(response.json())
# {'IsTor': True, 'IP': 'xxx.xxx.xxx.xxx'}
```

## Integration with Services

### transcript_service.py

The transcript service uses Tor automatically:

```python
# GenericProxyConfig for youtube-transcript-api
proxy_config = GenericProxyConfig(
    http_url="socks5://127.0.0.1:9050",
    https_url="socks5://127.0.0.1:9050"
)

# yt-dlp command line
cmd = ["yt-dlp", "--proxy", "socks5://127.0.0.1:9050", ...]
```

### Python Dependencies

```bash
pip install pysocks requests[socks]
```

## Troubleshooting

### "Connection refused" on port 9050

```bash
# Check if Tor is running
systemctl status tor

# If not running, start it
systemctl start tor

# Check logs for errors
journalctl -u tor -n 50
```

### "SOCKS support not available"

```bash
pip install pysocks
```

### Tor Starts but Port Not Listening

Check `/etc/tor/torrc` for:
```
SocksPort 127.0.0.1:9050
```

Restart after changes:
```bash
systemctl restart tor
```

### Slow Connections

Tor routes through multiple relays. Expect 2-10 second latency.

To get a new circuit (new exit IP):
```bash
systemctl reload tor
```

### Exit Node Blocked by YouTube

Rare, but possible. Get a new circuit:
```bash
systemctl reload tor
```

Or wait ~10 minutes for automatic circuit rotation.

## Security Considerations

### Localhost Only

Default configuration only accepts connections from `127.0.0.1`. Do NOT expose port 9050 to the network.

### No Authentication Needed

SOCKS5 proxy runs without authentication on localhost. This is safe for single-server setups.

### Log Minimal Data

Tor does not log traffic content. Only connection metadata is logged.

## Performance

| Metric | Value |
|--------|-------|
| Connection latency | 2-10 seconds |
| Bandwidth | Limited by Tor network |
| Circuit rotation | Every 10 minutes |
| Concurrent connections | ~100 (default) |

## Monitoring

### Check Circuit Status

```bash
# Install netcat
apt install -y netcat-openbsd

# Connect to control port (if enabled)
echo -e 'AUTHENTICATE ""\r\nGETINFO circuit-status\r\nQUIT' | nc 127.0.0.1 9051
```

### Health Check Script

```bash
#!/bin/bash
# /root/scripts/check-tor.sh

if curl -s --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip | grep -q '"IsTor":true'; then
    echo "Tor OK"
    exit 0
else
    echo "Tor FAILED"
    systemctl restart tor
    exit 1
fi
```

## Uninstallation

```bash
systemctl stop tor
systemctl disable tor
apt remove -y tor
```

## Related Documentation

- [Transcript Service](../services/TRANSCRIPT_SERVICE.md) - Uses Tor for YouTube API
- [YouTube Ingestion](../services/KNOWLEDGE_INGESTION.md) - Document processing pipeline

---

*Last updated: 2025-12-14*
