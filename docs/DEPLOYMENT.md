# Production Deployment Architecture

## Deployment Options

### Option A: Oracle Cloud Free Tier (RECOMMENDED — Free Forever)
**Cost:** $0/month
**Specs:** 2 vCPU AMD, 1 GB RAM, 10 GB boot volume, 200 GB block volume
**Uptime:** 24/7 (always-on)
**SSL:** Let's Encrypt (free, with a domain)
**Backup:** Daily SQLite copy to Object Storage (free 10 GB)

```
Internet
    │
    ▼
┌─────────────────────────────────────────┐
│  Oracle Cloud Free Tier (AMD VM)        │
│  Ubuntu 22.04, 2 vCPU, 1 GB RAM         │
│                                         │
│  ┌─────────┐   ┌─────────┐   ┌──────┐ │
│  │ Nginx   │──→│ FastAPI │──→│ AI   │ │
│  │ (80/443)│   │ (8000)  │   │ App  │ │
│  └─────────┘   └─────────┘   └──────┘ │
│                     │                    │
│                     ▼                    │
│              ┌────────────┐              │
│              │ SQLite DB  │              │
│              │ + backups  │              │
│              └────────────┘              │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │ Systemd (auto-restart on crash)  │   │
│  │ Cron (daily backup at 3 AM)      │   │
│  │ UFW firewall (only 80/443/22)     │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Option B: Your Laptop (Development / Testing)
**Cost:** $0/month
**Uptime:** Only when laptop is on
**SSL:** ngrok (free, temporary URLs)
**Best for:** Development, testing before deploy

```
Your Laptop
├── Python 3.11 + venv
├── SQLite file
├── ngrok http 8000 → https://abc123.ngrok.io
├── .env with API keys
└── http://localhost:8000
```

### Option C: Railway / Render (Easiest, Paid)
**Cost:** $5-10/month
**Uptime:** 24/7
**SSL:** Automatic
**Best for:** Zero server management, just push code

```
GitHub Repo → Railway/Render → Docker container → Auto-deploy
                                    │
                                    ▼
                              Environment vars
                              SQLite (ephemeral, use Render disk or Railway volume)
```

**WARNING:** Railway/Render free tier has sleep mode. For 24/7, you need paid ($5/mo).

---

## Oracle Cloud Free Tier Step-by-Step

### Step 1: Create Oracle Cloud Account
1. Go to https://www.oracle.com/cloud/free/
2. Sign up with your email
3. Verify identity (credit card required for verification, but NOT charged)
4. Wait for account activation (usually instant, sometimes 24 hours)

### Step 2: Create a VM Instance
1. Go to Oracle Cloud Console → Compute → Instances
2. Click "Create Instance"
3. Name: `ai-sales-assistant`
4. Image: Ubuntu 22.04 (Canonical)
5. Shape: VM.Standard.E2.1.Micro (Always Free: 2 vCPU, 1 GB RAM)
6. Networking: Create new VCN (default is fine)
7. Add SSH key: Generate new or upload your public key
8. Boot volume: 50 GB (always free limit)
9. Click "Create"

### Step 3: Open Firewall Ports
1. Go to Networking → Virtual Cloud Networks → Your VCN
2. Click Security Lists → Default Security List
3. Add Ingress Rules:
   - Port 22 (SSH) — Source: 0.0.0.0/0
   - Port 80 (HTTP) — Source: 0.0.0.0/0
   - Port 443 (HTTPS) — Source: 0.0.0.0/0
4. Click "Add Ingress Rules"

### Step 4: Connect and Deploy
1. Get your VM's public IP from the Instance page
2. SSH into the VM:
   ```bash
   ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_VM_IP
   ```
3. Copy the deployment script to the VM:
   ```bash
   scp -i ~/.ssh/your-key.pem oracle-cloud-deploy.sh ubuntu@YOUR_VM_IP:/tmp/
   ```
4. Run the deployment script:
   ```bash
   chmod +x /tmp/oracle-cloud-deploy.sh
   sudo /tmp/oracle-cloud-deploy.sh
   ```
5. Edit the .env file with your real API keys:
   ```bash
   sudo nano /opt/ai-sales-assistant/.env
   ```
6. Start the service:
   ```bash
   sudo systemctl start ai-sales-assistant
   sudo systemctl start nginx
   ```

### Step 5: Set Up Webhooks
Now that your server is on the internet, update your webhook URLs:

| Platform | Webhook URL | Where to Set |
|----------|-------------|--------------|
| Facebook | `http://YOUR_VM_IP/api/webhook/facebook` | Meta Developers > Messenger > Webhooks |
| WhatsApp | `http://YOUR_VM_IP/api/webhook/whatsapp` | Meta Developers > WhatsApp > Configuration |
| Instagram | `http://YOUR_VM_IP/api/webhook/instagram` | Meta Developers > Instagram > Webhooks |
| Telegram | `http://YOUR_VM_IP/api/webhook/telegram` | `https://api.telegram.org/botTOKEN/setWebhook?url=...` |

### Step 6: Add a Domain (Optional but Recommended)
1. Buy a domain (Namecheap, GoDaddy, Cloudflare) — ~$10/year
2. Point A record to your Oracle VM IP
3. Update Nginx config: `server_name your-domain.com;`
4. Set up SSL with Let's Encrypt:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```
5. Now all webhooks use HTTPS (required for production)

---

## Daily Backup Script

Create `/opt/ai-sales-assistant/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/ai-sales-assistant/backups"
DB_FILE="/opt/ai-sales-assistant/database/sales_assistant.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_FILE "$BACKUP_DIR/sales_assistant_$DATE.db"

# Keep only last 30 backups
ls -t $BACKUP_DIR/*.db | tail -n +31 | xargs -r rm

echo "Backup complete: $BACKUP_DIR/sales_assistant_$DATE.db"
```

Add to crontab:
```bash
sudo crontab -e
# Add this line:
0 3 * * * /opt/ai-sales-assistant/backup.sh >> /var/log/ai-sales-assistant-backup.log 2>&1
```

This runs daily at 3 AM and keeps the last 30 backups.

---

## Monitoring & Health Checks

### Check if the app is running
```bash
sudo systemctl status ai-sales-assistant
sudo journalctl -u ai-sales-assistant -f  # Live logs
```

### Check if Nginx is serving
```bash
curl http://localhost/api/leads  # Should return JSON
curl -I http://localhost         # Should return 200
```

### Check disk space
```bash
df -h
```

### Check memory usage
```bash
free -h
```

### Auto-restart on crash (already in systemd service)
The systemd service has `Restart=always`, so if the app crashes, it restarts in 5 seconds.

---

## SSL / HTTPS Setup (Required for Production)

Meta webhooks REQUIRE HTTPS in production. Here's the full setup:

```bash
# 1. Install Certbot
sudo apt install certbot python3-certbot-nginx

# 2. Get SSL certificate
sudo certbot --nginx -d your-domain.com --non-interactive --agree-tos -m your-email@example.com

# 3. Auto-renew (Certbot sets this up automatically)
sudo certbot renew --dry-run  # Test auto-renewal

# 4. Update webhook URLs to HTTPS:
# https://your-domain.com/api/webhook/facebook
# https://your-domain.com/api/webhook/whatsapp
# https://your-domain.com/api/webhook/instagram
# https://your-domain.com/api/webhook/telegram
```

---

## Complete Production Checklist

- [ ] Oracle Cloud VM created (Always Free tier)
- [ ] Firewall ports 22, 80, 443 open
- [ ] SSH key working
- [ ] Deployment script ran successfully
- [ ] `.env` file filled with real API keys
- [ ] Database initialized (`init_db()`)
- [ ] Service running (`systemctl status ai-sales-assistant`)
- [ ] Nginx serving (`curl http://localhost`)
- [ ] Domain pointed to VM IP (optional but recommended)
- [ ] SSL certificate installed (Let's Encrypt)
- [ ] Webhooks updated to HTTPS URLs
- [ ] Facebook webhook verified
- [ ] WhatsApp webhook verified
- [ ] Instagram webhook verified
- [ ] Telegram webhook set
- [ ] Gmail app password configured
- [ ] Daily backup cron job running
- [ ] Test message sent to WhatsApp → AI replies
- [ ] Test email sent → AI detects and drafts reply
- [ ] Dashboard accessible at `https://your-domain.com`

---

## Troubleshooting

### Service won't start
```bash
sudo journalctl -u ai-sales-assistant -n 50
# Check for: missing .env, wrong Python path, port already in use
```

### Nginx 502 Bad Gateway
```bash
sudo nginx -t
sudo systemctl status ai-sales-assistant
# Check if FastAPI is actually running on port 8000
```

### Webhook verification fails
```bash
# Check logs
sudo journalctl -u ai-sales-assistant -f
# Common issue: verify_token mismatch between .env and Meta app
```

### Database locked / corrupted
```bash
# Restore from latest backup
cp /opt/ai-sales-assistant/backups/sales_assistant_YYYYMMDD.db \
   /opt/ai-sales-assistant/database/sales_assistant.db
sudo systemctl restart ai-sales-assistant
```

### Out of memory (1 GB RAM is tight)
```bash
# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## Architecture Summary

```
┌──────────────┐     ┌─────────────────────────────────────────────────────┐
│   Internet   │────→│  Oracle Cloud Free Tier (AMD VM, Ubuntu 22.04)     │
│              │     │                                                     │
│  WhatsApp    │────→│  Nginx (80/443) → FastAPI (8000) → AI App         │
│  Instagram   │────→│                     │                              │
│  Facebook    │────→│                     ▼                              │
│  Email       │────→│              SQLite (leads, messages, ads)           │
│  Telegram    │────→│                     │                              │
│              │     │                     ▼                              │
│  Dashboard   │←────│  Hot Leads · Meetings · Ad Reports · Call Lists    │
│  (Browser)   │     │                                                     │
└──────────────┘     │  Systemd · Cron · UFW · Let's Encrypt · Backups     │
                     └─────────────────────────────────────────────────────┘
```
