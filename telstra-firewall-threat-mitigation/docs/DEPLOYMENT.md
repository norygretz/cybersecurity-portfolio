# Deployment & Hardening Guide

## Production Deployment Strategy

This guide provides comprehensive instructions for deploying the Log4j2 RCE Firewall in production environments.

## Pre-Deployment Checklist

### System Requirements

- **OS**: Linux (Ubuntu 20.04 LTS or CentOS 8+)
- **Python**: 3.8 or higher
- **RAM**: Minimum 2GB (recommended 4GB+)
- **CPU**: 2 cores minimum (4+ recommended)
- **Network**: Dedicated security zone
- **Disk**: 10GB minimum (for logs and future expansion)

### Prerequisites

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install Python and dependencies
sudo apt-get install -y python3 python3-pip git

# Install monitoring tools (optional)
sudo apt-get install -y htop netstat tcpdump

# Create non-root user for firewall
sudo useradd -m -s /bin/bash firewall
sudo usermod -aG sudo firewall
```

## Installation

### Step 1: Clone Repository

```bash
sudo su - firewall
cd /opt
git clone https://github.com/yourusername/telstra-firewall-threat-mitigation.git
cd telstra-firewall-threat-mitigation
```

### Step 2: Setup Virtual Environment

```bash
# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Firewall

Edit `src/firewall_server.py` to customize for your environment:

```python
# Change default host/port
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 8443       # Use HTTPS port

# Add additional attack signatures as needed
ATTACK_SIGNATURES = {
    # Existing signatures...
}
```

### Step 4: Create Systemd Service

Create `/etc/systemd/system/log4j2-firewall.service`:

```ini
[Unit]
Description=Log4j2 RCE Firewall
After=network.target

[Service]
Type=simple
User=firewall
WorkingDirectory=/opt/telstra-firewall-threat-mitigation
ExecStart=/opt/telstra-firewall-threat-mitigation/venv/bin/python src/firewall_server.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable log4j2-firewall
sudo systemctl start log4j2-firewall
sudo systemctl status log4j2-firewall
```

## Network Configuration

### Reverse Proxy Setup (Nginx)

```nginx
upstream firewall_backend {
    server localhost:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name firewall.company.com;

    ssl_certificate /etc/ssl/certs/firewall.crt;
    ssl_certificate_key /etc/ssl/private/firewall.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://firewall_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 10s;
    }
}
```

### Firewall Rules (UFW)

```bash
# Allow SSH (change port if needed)
sudo ufw allow 22/tcp

# Allow HTTPS traffic
sudo ufw allow 443/tcp

# Allow internal traffic from application servers
sudo ufw allow from 10.0.0.0/8 to any port 8000

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

### Load Balancing (HAProxy)

```
global
    maxconn 4096
    daemon
    
defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend firewall_http
    bind *:80
    redirect scheme https code 301

frontend firewall_https
    bind *:443 ssl crt /etc/ssl/firewall.pem
    default_backend firewall_backends

backend firewall_backends
    balance roundrobin
    server firewall1 10.0.1.10:8000 check
    server firewall2 10.0.1.11:8000 check
    server firewall3 10.0.1.12:8000 check
```

## Logging & Monitoring

### Configure Log Rotation

Create `/etc/logrotate.d/log4j2-firewall`:

```
/var/log/log4j2-firewall.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 firewall firewall
    sharedscripts
    postrotate
        systemctl reload log4j2-firewall > /dev/null 2>&1 || true
    endscript
}
```

### Real-Time Monitoring

```bash
# Monitor firewall status
sudo systemctl status log4j2-firewall

# View live logs
sudo journalctl -u log4j2-firewall -f

# Count attacks detected
sudo journalctl -u log4j2-firewall | grep "BLOCKED" | wc -l

# View unique attack IPs
sudo journalctl -u log4j2-firewall | grep "BLOCKED" | cut -d' ' -f3 | sort | uniq
```

### Prometheus Metrics (Optional)

Add metrics collection to `firewall_server.py`:

```python
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
requests_total = Counter(
    'firewall_requests_total',
    'Total requests processed',
    ['status']
)

request_duration = Histogram(
    'firewall_request_duration_seconds',
    'Request processing duration'
)

# In request handler
with request_duration.time():
    # Process request
    requests_total.labels(status='blocked').inc()
    # or
    requests_total.labels(status='allowed').inc()

# Expose metrics on port 9000
if __name__ == '__main__':
    start_http_server(9000)
```

## Security Hardening

### OS-Level Security

```bash
# Disable IPv6 if not needed
echo "net.ipv6.conf.all.disable_ipv6 = 1" | sudo tee -a /etc/sysctl.conf

# Kernel hardening
echo "net.ipv4.conf.all.rp_filter = 1" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.icmp_echo_ignore_broadcasts = 1" | sudo tee -a /etc/sysctl.conf

# Apply settings
sudo sysctl -p

# Enable auditd for security monitoring
sudo apt-get install -y auditd
sudo systemctl enable auditd
sudo systemctl start auditd
```

### Access Control

```bash
# Restrict file permissions
sudo chmod 755 /opt/telstra-firewall-threat-mitigation
sudo chmod 644 /opt/telstra-firewall-threat-mitigation/src/firewall_server.py
sudo chown -R firewall:firewall /opt/telstra-firewall-threat-mitigation

# Restrict log access
sudo chmod 640 /var/log/log4j2-firewall.log
sudo chown firewall:firewall /var/log/log4j2-firewall.log

# SSH key-based authentication
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### Fail2Ban Integration

Install and configure Fail2Ban to block attacking IPs:

```bash
sudo apt-get install -y fail2ban

# Create filter: /etc/fail2ban/filter.d/log4j2-firewall.conf
[Definition]
failregex = Incoming request from IP: <HOST>.*Attack blocked
ignoreregex =

# Create jail: /etc/fail2ban/jail.d/log4j2-firewall.conf
[log4j2-firewall]
enabled = true
port = http,https
filter = log4j2-firewall
logpath = /var/log/log4j2-firewall.log
maxretry = 3
findtime = 3600
bantime = 86400
```

### SSL/TLS Hardening

```bash
# Generate strong certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
  -keyout /etc/ssl/private/firewall.key \
  -out /etc/ssl/certs/firewall.crt

# Configure strong ciphers in nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
```

## Performance Tuning

### Connection Pooling

Modify `firewall_server.py` for production:

```python
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    max_thread_count = 100

# Use ThreadedHTTPServer instead of HTTPServer
server = ThreadedHTTPServer((HOST, PORT), FirewallHandler)
```

### Kernel Parameters

```bash
# Increase file descriptors
sudo ulimit -n 65535

# Persistent setting in /etc/security/limits.conf
firewall soft nofile 65535
firewall hard nofile 65535

# Increase backlog
echo "net.core.somaxconn = 65535" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## Disaster Recovery

### Backup Strategy

```bash
# Daily backup
0 2 * * * tar -czf /backup/firewall-$(date +\%Y\%m\%d).tar.gz /opt/telstra-firewall-threat-mitigation

# Store backups
sudo mkdir -p /backup
sudo chown firewall:firewall /backup

# Test restore
tar -tzf /backup/firewall-20260519.tar.gz | head -20
```

### High Availability Setup

```
        ┌──────────────────┐
        │  Load Balancer   │
        └──────┬───────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
Firewall1   Firewall2   Firewall3
(Active)    (Standby)   (Standby)
    │          │          │
    └──────────┴──────────┘
               │
        ┌──────▼──────┐
        │   Database  │
        │  (Shared    │
        │   Logs)     │
        └─────────────┘
```

## Maintenance Schedule

| Task | Frequency | Owner |
|------|-----------|-------|
| Log review | Daily | Security Team |
| Security patches | As released | DevOps |
| Full backup | Weekly | DevOps |
| Disaster recovery test | Monthly | DevOps |
| Performance review | Monthly | DevOps |
| Signature updates | Quarterly | Security Team |

## Troubleshooting

### Firewall Not Starting

```bash
# Check service status
sudo systemctl status log4j2-firewall

# View detailed logs
sudo journalctl -u log4j2-firewall -n 100

# Test Python execution
python3 /opt/telstra-firewall-threat-mitigation/src/firewall_server.py

# Check port availability
sudo netstat -tuln | grep 8000
```

### High CPU Usage

```bash
# Monitor real-time
top -p $(pgrep -f firewall_server.py)

# Check for hang requests
sudo netstat -tan | grep ESTABLISHED | wc -l

# Restart service
sudo systemctl restart log4j2-firewall
```

### Memory Leaks

```bash
# Monitor memory growth
watch -n 5 'ps aux | grep firewall_server.py'

# Check process memory usage
ps -o pid,vsz,rss,comm= $(pgrep -f firewall_server.py)

# Restart periodically via cron
0 */6 * * * systemctl restart log4j2-firewall
```

## Success Criteria

- Firewall starts without errors  
- Accepts incoming requests  
- Blocks attack signatures correctly  
- Logs all events properly  
- Stays within resource limits  
- Handles 100+ concurrent connections  
- Response time <10ms average  

---

**Document Version**: 1.0  
**Last Updated**: May 2026  
**Status**: Ready for Production
