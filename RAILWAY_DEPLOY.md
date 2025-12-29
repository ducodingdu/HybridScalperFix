# 🚀 Deploy ke Railway.app (5 Menit!)

Panduan super cepat deploy bot ke Railway.app - **jauh lebih mudah dari Oracle Cloud!**

## ✨ Keuntungan Railway.app

- ✅ **Setup 5 menit** (vs Oracle 1-2 jam!)
- ✅ **$5 credit gratis/bulan** (cukup untuk bot scheduled)
- ✅ **Auto-deploy dari GitHub** (push code = auto deploy!)
- ✅ **Auto-restart** built-in
- ✅ **Monitoring & logs** included
- ✅ **Tidak perlu SSH, VPS setup, dll**
- ✅ **Support Python langsung** (auto-detect)

---

## 📋 Langkah Deploy (5 Menit!)

### **Step 1: Sign Up Railway (2 menit)**

1. Buka: https://railway.app
2. Klik **"Login"** → **"Login with GitHub"**
3. Authorize Railway ke GitHub Anda
4. ✅ Done! Dapat $5 credit gratis/bulan

---

### **Step 2: Deploy Project (3 menit)**

#### **Option A: Deploy dari GitHub (Recommended)**

**1. Push code ke GitHub:**
```bash
# Jika belum punya repo, buat dulu di GitHub
# Lalu di Replit/local:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git add .
git commit -m "Deploy to Railway"
git push -u origin main
```

**2. Deploy di Railway:**
1. Login ke https://railway.app
2. Klik **"New Project"**
3. Pilih **"Deploy from GitHub repo"**
4. Pilih repository bot Anda
5. Railway akan **auto-detect Python** & install dependencies!
6. ✅ Deployment started!

#### **Option B: Deploy dari CLI (Alternative)**

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

---

### **Step 3: Setup Environment Variables (2 menit)**

Di Railway Dashboard:

1. Klik project Anda
2. Klik tab **"Variables"**
3. Tambahkan variables:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
ALPHA_VANTAGE_API_KEY=your_api_key_optional
SESSION_SECRET=random_secret_123
```

4. Klik **"Save"**
5. Railway akan **auto-redeploy** dengan env variables!

---

### **Step 4: Verifikasi Deployment (1 menit)**

1. Di Railway dashboard, klik **"Deployments"**
2. Tunggu status: **"Success"** ✅
3. Klik **"View Logs"** untuk lihat bot running
4. Railway akan kasih **public URL** (untuk webhook TradingView)

---

## 🎯 Bot Sekarang Running 24/7!

Railway akan otomatis:
- ✅ Install dependencies dari `requirements.txt`
- ✅ Run `gunicorn` sesuai `Procfile`
- ✅ Restart jika crash
- ✅ Scale jika perlu
- ✅ Generate public URL

---

## 📊 Monitoring & Logs

**View Logs:**
1. Buka Railway dashboard
2. Klik project → **"Deployments"**
3. Klik deployment → **"View Logs"**
4. Lihat real-time logs bot!

**Metrics:**
- CPU, Memory usage
- Request count
- Response time
- Semua termonitor otomatis!

### 📌 **Memahami Scheduler Behavior**

Bot menggunakan scheduler otomatis dengan jadwal:
- 📊 **IDX**: 08:55, 10:30, 15:30 WIB
- 🪙 **Crypto**: 12:00, 19:00 WIB

**Cara Kerja:**
1. ✅ **Bot running 24/7** → Alert otomatis terkirim tepat waktu
2. ⚠️ **Bot di-restart/redeploy** → Jika restart setelah jadwal hari ini, next alert besok
3. ✅ **Besok normal** → Semua alert jalan otomatis sesuai jadwal

**Contoh:**
- Deploy jam 16:00 WIB:
  - ❌ Alert 08:55, 10:30, 15:30 sudah lewat → Jalan besok
  - ✅ Alert 19:00 belum lewat → Jalan hari ini
  - ✅ Besok: semua alert jalan otomatis!

**Cek Scheduler Status:**
- Buka: `https://<app-name>.up.railway.app/scheduler-status`
- Lihat next scheduled runs dan status

**Log Saat Alert Terkirim:**
```
============================================================
🔔 SCHEDULER TRIGGERED: SESI 1 (10:30 WIB)
⏰ Waktu: 15-Oct-2025 10:30:15 WIB
============================================================
✅ Alert SESI 1 (10:30 WIB) berhasil dikirim ke Telegram
============================================================
```

---

## 🔄 Auto-Deploy (CI/CD)

Setelah setup GitHub:
1. **Edit code** di Replit/local
2. **Push ke GitHub**: `git push`
3. **Railway auto-deploy!** ✅

Tidak perlu manual redeploy!

---

## 💰 Biaya & Limits

**$5 Credit Gratis/Bulan:**
- ≈ 500 jam runtime (cukup untuk bot scheduled!)
- Unlimited deployments
- Unlimited builds
- Public URL included

**Jika Butuh Lebih:**
- Upgrade ke Hobby: $5/bulan
- Unlimited usage
- Priority support

**Bot scheduled kami:** ~100 jam/bulan = **GRATIS!** ✅

---

## 🚀 Commands Penting

```bash
# View logs
railway logs

# Open project in browser
railway open

# Redeploy
railway up

# View variables
railway variables

# Delete project
railway down
```

---

## 🔧 Troubleshooting

### Bot tidak jalan?
1. Check **"Deployments"** → Status harus "Success"
2. Check **"Logs"** → Cari error messages
3. Check **"Variables"** → Pastikan TELEGRAM_BOT_TOKEN benar

### Port Error?
Railway auto-assign port via `$PORT` env variable.
Pastikan `Procfile` pakai: `--bind 0.0.0.0:$PORT`

### Dependencies Error?
Pastikan `requirements.txt` lengkap & versi compatible.

---

## 📱 Webhook TradingView

Setelah deploy, Railway kasih public URL:
```
https://your-project.up.railway.app
```

Gunakan untuk TradingView webhook:
```
https://your-project.up.railway.app/webhook/tradingview
```

---

## ✅ Selesai!

Bot Anda sekarang:
- 🚀 Running 24/7 di Railway
- 🔄 Auto-restart jika crash
- 📊 Termonitor real-time
- 💰 **GRATIS** dengan $5 credit/bulan!

**Enjoy!** 🎉

---

## 📚 Resources

- Railway Docs: https://docs.railway.app
- Railway Dashboard: https://railway.app/dashboard
- Support: https://railway.app/help
