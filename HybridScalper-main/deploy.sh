#!/bin/bash

# Hybrid Scalper Bot - Oracle Cloud Deployment Script
# Usage: bash deploy.sh

set -e

echo "🚀 Hybrid Scalper Bot - Oracle Cloud Deployment"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on Ubuntu
if [ ! -f /etc/lsb-release ]; then
    echo -e "${RED}❌ Error: This script is designed for Ubuntu${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Step 1: Update system packages...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${YELLOW}🐍 Step 2: Install Python and dependencies...${NC}"
sudo apt install -y python3 python3-pip python3-venv git ufw

echo -e "${YELLOW}🔥 Step 3: Configure firewall...${NC}"
sudo ufw --force enable
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 5000/tcp comment 'Flask Bot'
echo -e "${GREEN}✅ Firewall configured${NC}"

echo -e "${YELLOW}📂 Step 4: Setup project directory...${NC}"
PROJECT_DIR="$HOME/hybrid-scalper-bot"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo -e "${YELLOW}🌐 Step 5: Create Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}📥 Step 6: Install Python packages...${NC}"
pip install --upgrade pip
pip install flask gunicorn beautifulsoup4 lxml pandas requests schedule yfinance pytz

echo -e "${YELLOW}🔐 Step 7: Setup environment variables...${NC}"
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Telegram Configuration (WAJIB!)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Optional API Keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# Session Secret
SESSION_SECRET=random_secret_key_change_this
EOF
    echo -e "${YELLOW}⚠️  Created .env file - PLEASE EDIT IT WITH YOUR ACTUAL VALUES!${NC}"
    echo -e "${YELLOW}   Edit with: nano $PROJECT_DIR/.env${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

echo -e "${YELLOW}⚙️  Step 8: Setup systemd service...${NC}"
sudo tee /etc/systemd/system/scalper-bot.service > /dev/null << EOF
[Unit]
Description=Hybrid Scalper Bot - Indonesian Stock Trading Signal Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers=1 --threads=2 --timeout=120 --reuse-port app:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}🔄 Step 9: Enable systemd service...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable scalper-bot.service

echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Before starting the service:${NC}"
echo -e "${YELLOW}   1. Copy app.py to: $PROJECT_DIR${NC}"
echo -e "${YELLOW}   2. Edit .env with your actual Telegram credentials${NC}"
echo -e "${YELLOW}   3. Then start: sudo systemctl start scalper-bot.service${NC}"
echo ""

# Check if app.py exists
if [ -f "$PROJECT_DIR/app.py" ]; then
    echo -e "${GREEN}✅ app.py found${NC}"
    echo -e "${YELLOW}⚠️  Make sure .env is configured with real values before starting!${NC}"
    read -p "Start service now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo systemctl start scalper-bot.service
        sleep 2
        
        if sudo systemctl is-active --quiet scalper-bot.service; then
            echo -e "${GREEN}✅ Service started successfully!${NC}"
        else
            echo -e "${RED}❌ Service failed to start. Check logs with: sudo journalctl -u scalper-bot.service -n 50${NC}"
        fi
    else
        echo -e "${YELLOW}Service not started. Start manually after configuring .env:${NC}"
        echo -e "${YELLOW}   sudo systemctl start scalper-bot.service${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  app.py not found. Please copy your bot files to: $PROJECT_DIR${NC}"
fi

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Edit environment variables:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2. Copy your bot files (app.py) to:"
echo "   $PROJECT_DIR"
echo ""
echo "3. Start the bot:"
echo "   sudo systemctl start scalper-bot.service"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status scalper-bot.service"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u scalper-bot.service -f"
echo ""
echo "6. Get your server IP:"
echo "   curl ifconfig.me"
echo ""
echo "7. Test bot in browser:"
echo "   http://YOUR_SERVER_IP:5000"
echo ""
echo -e "${GREEN}✅ Bot will auto-start on system reboot!${NC}"
echo ""
