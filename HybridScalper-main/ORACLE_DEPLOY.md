# 🚀 Deploy ke Oracle Cloud Free Tier (GRATIS SELAMANYA!)

Panduan lengkap deploy **Hybrid Scalper Bot** ke Oracle Cloud Free Tier untuk running 24/7 tanpa biaya.

## 📋 Yang Anda Dapatkan (100% GRATIS!)

Oracle Cloud Free Tier memberikan:
- ✅ **2 VM Compute** (AMD) - 1/8 OCPU, 1 GB RAM
- ✅ **4 VM Arm** - Total 24 GB RAM
- ✅ **200 GB Block Storage**
- ✅ **10 GB Object Storage**
- ✅ **GRATIS SELAMANYA** (bukan trial!)
- ✅ Bonus $300 credit untuk 30 hari pertama

## 🎯 Langkah 1: Setup Oracle Cloud Account

### 1.1 Daftar Oracle Cloud
1. Buka: https://www.oracle.com/cloud/free/
2. Klik **"Start for free"**
3. Isi data:
   - Email
   - Country/Territory: Indonesia
   - Cloud Account Name (pilih nama unik)
4. Verifikasi email & telepon
5. Masukkan kartu kredit/debit (untuk verifikasi, **tidak akan dicharge**)
6. Selesaikan pendaftaran

### 1.2 Login ke OCI Console
1. Login di: https://cloud.oracle.com
2. Masukkan:
   - Cloud Account Name
   - Email & Password
3. Anda akan masuk ke **OCI Console**

---

## 🖥️ Langkah 2: Buat VM Instance

### 2.1 Create Compute Instance
1. Di OCI Console, klik **☰ Menu** → **Compute** → **Instances**
2. Klik **"Create Instance"**
3. Konfigurasi:

   **Name:** `hybrid-scalper-bot`
   
   **Image:** Ubuntu 22.04 (minimal)
   
   **Shape:** 
   - Klik "Change Shape"
   - Pilih **"VM.Standard.E2.1.Micro"** (Always Free)
   - 1/8 OCPU, 1 GB Memory
   
   **Networking:**
   - Leave default (auto-create VCN)
   
   **SSH Keys:**
   - Pilih "Generate SSH key pair"
   - **DOWNLOAD** private key (`.key` file) - SIMPAN BAIK-BAIK!
   - (Atau upload public key Anda sendiri)

4. Klik **"Create"**
5. Tunggu status **"RUNNING"** (± 1-2 menit)
6. Catat **Public IP Address** VM Anda

### 2.2 Setup Firewall Rules
1. Di halaman Instance, klik **"Subnet"** link
2. Klik **"Default Security List"**
3. Klik **"Add Ingress Rules"**
4. Tambahkan rule untuk Flask:
   ```
   Source CIDR: 0.0.0.0/0
   IP Protocol: TCP
   Destination Port Range: 5000
   Description: Flask Bot
   ```
5. Klik **"Add Ingress Rules"**

---

## 💻 Langkah 3: Deploy Bot ke VM

### 3.1 SSH ke VM Anda

**Windows (PowerShell/CMD):**
```powershell
ssh -i C:\path\to\ssh-key.key ubuntu@YOUR_PUBLIC_IP
```

**Mac/Linux:**
```bash
chmod 400 /path/to/ssh-key.key
ssh -i /path/to/ssh-key.key ubuntu@YOUR_PUBLIC_IP
```

Ganti `YOUR_PUBLIC_IP` dengan IP VM Anda.

### 3.2 Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & tools
sudo apt install python3 python3-pip python3-venv git -y

# Install firewall & configure
sudo apt install ufw -y
sudo ufw allow 22    # SSH
sudo ufw allow 5000  # Flask
sudo ufw enable
```

### 3.3 Clone & Setup Bot

```bash
# Buat direktori project
mkdir -p ~/hybrid-scalper-bot
cd ~/hybrid-scalper-bot

# Download project files dari Replit
# (Copy semua file: app.py, pyproject.toml, dll)
```

**Cara termudah:** Copy file `app.py` dan `pyproject.toml` dari Replit:

```bash
# Buat file app.py
nano app.py
# Paste isi file app.py dari Replit, save (Ctrl+X, Y, Enter)

# Buat file pyproject.toml
nano pyproject.toml
# Paste isi file, save
```

### 3.4 Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask gunicorn beautifulsoup4 lxml pandas requests schedule yfinance pytz
```

### 3.5 Setup Environment Variables

```bash
# Buat file .env
nano .env
```

Isi dengan:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
ALPHA_VANTAGE_API_KEY=your_api_key_here
SESSION_SECRET=random_secret_key_123
```

Ganti dengan value yang sebenarnya, save (Ctrl+X, Y, Enter).

### 3.6 Test Bot

```bash
# Load environment variables
export $(cat .env | xargs)

# Test run
gunicorn --bind 0.0.0.0:5000 --workers=1 --threads=2 app:app
```

Buka browser: `http://YOUR_PUBLIC_IP:5000`

Jika berhasil, tekan **Ctrl+C** untuk stop.

---

## ⚙️ Langkah 4: Setup Auto-Start (Systemd)

### 4.1 Buat Service File

```bash
sudo nano /etc/systemd/system/scalper-bot.service
```

Paste konten berikut:

```ini
[Unit]
Description=Hybrid Scalper Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/hybrid-scalper-bot
Environment="PATH=/home/ubuntu/hybrid-scalper-bot/venv/bin"
EnvironmentFile=/home/ubuntu/hybrid-scalper-bot/.env
ExecStart=/home/ubuntu/hybrid-scalper-bot/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers=1 --threads=2 --timeout=120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save (Ctrl+X, Y, Enter).

### 4.2 Enable & Start Service

⚠️ **PENTING**: Pastikan file `.env` sudah diisi dengan token Telegram yang benar sebelum start service!

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable scalper-bot.service

# Start service (setelah .env dikonfigurasi!)
sudo systemctl start scalper-bot.service

# Check status
sudo systemctl status scalper-bot.service
```

**Expected output:**
```
● scalper-bot.service - Hybrid Scalper Bot
   Loaded: loaded
   Active: active (running)
```

### 4.3 Useful Commands

```bash
# Stop bot
sudo systemctl stop scalper-bot.service

# Restart bot
sudo systemctl restart scalper-bot.service

# View logs
sudo journalctl -u scalper-bot.service -f

# View last 50 lines
sudo journalctl -u scalper-bot.service -n 50
```

---

## ✅ Langkah 5: Verifikasi Deployment

### 5.1 Test Endpoints

```bash
# Test homepage
curl http://YOUR_PUBLIC_IP:5000/

# Test Telegram
curl http://YOUR_PUBLIC_IP:5000/test-telegram

# Test screening
curl http://YOUR_PUBLIC_IP:5000/test-screening
```

### 5.2 Test Telegram Notifications

Buka Telegram, Anda harus menerima pesan dari bot!

### 5.3 Monitoring

Bot akan otomatis:
- 🕐 Scan & kirim signal pada 08:55, 10:30, 15:30 WIB
- 🔄 Auto-restart jika crash
- 📊 Screening real-time dari YFinance (gratis!)

---

## 🌐 Langkah 6: Setup Webhook untuk TradingView (Optional)

Jika Anda ingin menerima alert dari TradingView:

1. Buka TradingView
2. Buat Alert
3. Webhook URL: `http://YOUR_PUBLIC_IP:5000/webhook/tradingview`
4. Message format:
   ```json
   {
     "symbol": "{{ticker}}",
     "signal": "{{strategy.order.alert_message}}"
   }
   ```

---

## 🔧 Troubleshooting

### Bot tidak jalan?
```bash
# Check service status
sudo systemctl status scalper-bot.service

# Check logs
sudo journalctl -u scalper-bot.service -n 100
```

### Port 5000 tidak bisa diakses?
```bash
# Check firewall
sudo ufw status

# Allow port 5000
sudo ufw allow 5000
```

### Restart VM?
```bash
sudo reboot
```
Bot akan auto-start setelah reboot!

### Update bot code?
```bash
cd ~/hybrid-scalper-bot
nano app.py  # Edit file
sudo systemctl restart scalper-bot.service
```

---

## 💰 Estimasi Biaya

**GRATIS SELAMANYA!** ✅

Oracle Cloud Free Tier:
- VM E2.1.Micro: **Always Free** (tidak expired)
- Storage 200 GB: **Always Free**
- Network egress: **10 TB/bulan gratis**

Bot ini menggunakan:
- CPU: < 5% average
- RAM: ~200 MB
- Storage: ~500 MB
- Network: ~100 MB/bulan

**100% dalam batas Free Tier!** 🎉

---

## 📚 Resources

- Oracle Free Tier: https://www.oracle.com/cloud/free/
- OCI Console: https://cloud.oracle.com
- OCI Docs: https://docs.oracle.com/iaas/

---

## 🎯 Next Steps

Setelah deploy sukses:

1. ✅ Verifikasi Telegram notifications (08:55, 10:30, 15:30 WIB)
2. ✅ Monitor logs: `sudo journalctl -u scalper-bot.service -f`
3. ✅ Setup TradingView webhook (optional)
4. ✅ Customize watchlist di `app.py` (optional)

**Selamat! Bot Anda sudah running 24/7 di Oracle Cloud - GRATIS!** 🚀
