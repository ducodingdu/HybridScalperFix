# 🚀 Quick Start - Deploy ke Oracle Cloud (5 Menit!)

Panduan singkat untuk deploy bot ke Oracle Cloud Free Tier.

## ⚡ Ringkasan

1. **Daftar Oracle Cloud** (gratis selamanya)
2. **Buat VM Ubuntu** (1 GB RAM, Always Free)
3. **Upload bot files** ke VM
4. **Run script deploy** (otomatis install semua)
5. **Bot running 24/7!** ✅

---

## 📝 Langkah Cepat

### 1️⃣ Daftar Oracle Cloud (5 menit)

🔗 https://www.oracle.com/cloud/free/

- Isi email & data diri
- Verifikasi kartu (tidak akan dicharge!)
- Login ke Console: https://cloud.oracle.com

### 2️⃣ Buat VM Instance (3 menit)

Di OCI Console:

1. **Compute → Instances → Create Instance**
2. Name: `scalper-bot`
3. Image: `Ubuntu 22.04`
4. Shape: `VM.Standard.E2.1.Micro` (Always Free)
5. **Download SSH private key** (.key file) ⚠️ SIMPAN!
6. Create → Tunggu status **RUNNING**
7. **Catat Public IP** VM

### 3️⃣ Buka Port Firewall (2 menit)

1. Klik **Subnet** → **Default Security List**
2. **Add Ingress Rules:**
   - Source: `0.0.0.0/0`
   - Port: `5000`
   - Protocol: TCP
3. Save

### 4️⃣ SSH & Deploy (5 menit)

**SSH ke VM:**
```bash
# Windows PowerShell/CMD
ssh -i C:\path\to\ssh-key.key ubuntu@YOUR_VM_IP

# Mac/Linux
chmod 400 /path/to/ssh-key.key
ssh -i /path/to/ssh-key.key ubuntu@YOUR_VM_IP
```

**Di VM, jalankan:**

```bash
# Download deployment script
curl -O https://raw.githubusercontent.com/YOUR_REPO/deploy.sh

# Atau copy manual dari Replit
mkdir -p ~/hybrid-scalper-bot
cd ~/hybrid-scalper-bot

# Copy file deploy.sh dari Replit (paste isi file)
nano deploy.sh
# Paste script, Ctrl+X, Y, Enter

# Make executable & run
chmod +x deploy.sh
bash deploy.sh
```

Script akan install semua otomatis!

### 5️⃣ Copy Files & Setup Env (3 menit)

```bash
cd ~/hybrid-scalper-bot

# Copy app.py dari Replit
nano app.py
# Paste code, Ctrl+X, Y, Enter

# Setup environment variables
nano .env
```

**⚠️ PENTING: Isi .env dengan nilai yang BENAR!**
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE
SESSION_SECRET=random123
```

Ganti dengan token Telegram asli Anda!  
Save: Ctrl+X, Y, Enter

### 6️⃣ Start Bot! (1 menit)

```bash
# Start service
sudo systemctl start scalper-bot.service

# Check status
sudo systemctl status scalper-bot.service

# View logs
sudo journalctl -u scalper-bot.service -f
```

### 7️⃣ Test di Browser

Buka: `http://YOUR_VM_IP:5000`

Anda akan lihat dashboard bot! ✅

---

## 🎉 Selesai!

Bot sekarang running 24/7 di Oracle Cloud - **GRATIS SELAMANYA!**

Bot akan:
- ✅ Auto scan top gainers pada 08:55, 10:30, 15:30 WIB
- ✅ Kirim signal ke Telegram
- ✅ Auto-restart jika crash
- ✅ Auto-start saat VM reboot

---

## 🔧 Commands Penting

```bash
# Start bot
sudo systemctl start scalper-bot.service

# Stop bot
sudo systemctl stop scalper-bot.service

# Restart bot
sudo systemctl restart scalper-bot.service

# View logs (real-time)
sudo journalctl -u scalper-bot.service -f

# View last 50 lines
sudo journalctl -u scalper-bot.service -n 50

# Edit bot code
cd ~/hybrid-scalper-bot
nano app.py
sudo systemctl restart scalper-bot.service

# Edit environment
nano ~/hybrid-scalper-bot/.env
sudo systemctl restart scalper-bot.service
```

---

## 📚 Panduan Lengkap

Lihat **ORACLE_DEPLOY.md** untuk:
- Troubleshooting guide
- TradingView webhook setup
- Advanced configuration
- Monitoring & logs

---

## ❓ Troubleshooting Cepat

**Bot tidak jalan?**
```bash
sudo systemctl status scalper-bot.service
sudo journalctl -u scalper-bot.service -n 50
```

**Port 5000 tidak bisa diakses?**
```bash
sudo ufw allow 5000
sudo ufw status
```

**Update bot code?**
```bash
cd ~/hybrid-scalper-bot
nano app.py
sudo systemctl restart scalper-bot.service
```

---

## 💰 Biaya

**100% GRATIS!** Oracle Always Free tier tidak expired.

Bot ini pakai:
- CPU: <5%
- RAM: ~200 MB
- Storage: ~500 MB
- Network: ~100 MB/bulan

Semua di bawah limit free tier! 🎉

---

**Need help?** Lihat **ORACLE_DEPLOY.md** untuk panduan lengkap.
