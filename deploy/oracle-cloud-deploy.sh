#!/bin/bash
# Oracle Cloud Free Tier Deployment Script
# Deploys the AI Sales Assistant to a free forever AMD VM (2 vCPU, 1 GB RAM)

set -e

APP_NAME="ai-sales-assistant"
APP_DIR="/opt/$APP_NAME"
USER="ubuntu"
PYTHON_VERSION="3.11"

echo "========================================"
echo "AI Sales Assistant — Oracle Cloud Deploy"
echo "========================================"

# Update system
echo "[1/10] Updating system..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install dependencies
echo "[2/10] Installing dependencies..."
sudo apt-get install -y python3-pip python3-venv python3-dev nginx git curl ufw

# Create app directory
echo "[3/10] Creating app directory..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Create virtual environment
echo "[4/10] Setting up application..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Install requirements (you need to copy your requirements.txt first)
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Create .env file
echo "[5/10] Creating environment file..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Meta / Facebook
META_ACCESS_TOKEN=your-page-access-token
META_AD_ACCOUNT_ID=act_1234567890
META_PAGE_ID=your-page-id
META_VERIFY_TOKEN=fb_webhook_123
META_APP_SECRET=your-app-secret
META_INSTAGRAM_ID=your-instagram-business-id

# WhatsApp Cloud API
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token
WHATSAPP_VERIFY_TOKEN=wa_webhook_123

# Email
EMAIL_ADDRESS=youragency@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token

# Channels
ACTIVE_CHANNELS=facebook,whatsapp,instagram,email,telegram

# Database
DATABASE_PATH=database/sales_assistant.db

# Dashboard
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8000

# Agency Info
AGENCY_NAME=Your Dubai Web Design Agency
AGENCY_SERVICES=Web Design, Landing Pages, SEO, E-commerce
AGENCY_LOCATION=Dubai, UAE
EOF
    echo "⚠️  IMPORTANT: Edit .env and fill in your real API keys!"
fi

# Create systemd service
echo "[6/10] Creating systemd service..."
sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null << EOF
[Unit]
Description=AI Sales Assistant
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/run.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx config
echo "[7/10] Setting up Nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;  # Accept any server name (or replace with your domain)

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/webhook {
        proxy_pass http://127.0.0.1:8000;
        proxy_buffering off;
        proxy_read_timeout 86400;
    }

    client_max_body_size 10M;
}
EOF

sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# Setup firewall
echo "[8/10] Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Create backup script
echo "[9/10] Creating backup script..."
sudo tee /opt/$APP_NAME/backup.sh > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/ai-sales-assistant/backups"
DB_FILE="/opt/ai-sales-assistant/database/sales_assistant.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_FILE "$BACKUP_DIR/sales_assistant_$DATE.db"

# Keep only last 30 backups
ls -t $BACKUP_DIR/*.db | tail -n +31 | xargs -r rm

echo "Backup complete: $BACKUP_DIR/sales_assistant_$DATE.db"
EOF
sudo chmod +x /opt/$APP_NAME/backup.sh

# Add backup cron job
echo "0 3 * * * /opt/$APP_NAME/backup.sh >> /var/log/ai-sales-assistant-backup.log 2>&1" | sudo crontab -

# Enable services
echo "[10/10] Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl enable nginx

echo ""
echo "========================================"
echo "DEPLOYMENT INFRASTRUCTURE COMPLETE!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Copy your project files to /opt/$APP_NAME/"
echo "   (requirements.txt, run.py, config.py, core/, database/, dashboard/)"
echo "2. Edit /opt/$APP_NAME/.env with your real API keys"
echo "3. Install Python dependencies: cd /opt/$APP_NAME && source venv/bin/activate && pip install -r requirements.txt"
echo "4. Initialize database: python -c 'from database.db import init_db; init_db()'"
echo "5. Start the service: sudo systemctl start $APP_NAME"
echo "6. Check status: sudo systemctl status $APP_NAME"
echo "7. View logs: sudo journalctl -u $APP_NAME -f"
echo "8. Open dashboard: http://YOUR_ORACLE_IP"
echo ""
echo "For webhooks, use: http://YOUR_ORACLE_IP/api/webhook/PLATFORM"
echo ""
echo "To add SSL (recommended):"
echo "  sudo apt install certbot python3-certbot-nginx"
echo "  sudo certbot --nginx -d your-domain.com"
echo "========================================"
