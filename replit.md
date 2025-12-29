# Hybrid Scalper Bot

## Overview
Bot trading **Saham Indonesia (IDX) & Cryptocurrency** yang mengirimkan sinyal otomatis ke Telegram dengan jadwal pre-market, sesi 1, dan closing. Bot ini juga memiliki webhook untuk menerima alert dari TradingView.

## Tanggal Dibuat
13 Oktober 2025

## Fitur Utama

### 📈 Saham Indonesia (IDX)
- ✅ Notifikasi otomatis ke Telegram pada jadwal:
  - PRE-MARKET: 08:55 WIB
  - SESI 1: 10:30 WIB
  - CLOSING: 15:30 WIB
- 🚀 **Multi-Source Screening System (100% GRATIS!)** - 6-tier fallback dengan prioritas:
  1. 🚀 **YFinance Screener** - Scan 50 saham IDX top gainers (PRIMARY - FREE!)
  2. 📊 **IDX Official Scraper** - Backup dari data IDX resmi (BACKUP - FREE!)
  3. 🎯 **Sectors.app API** - Top gainers premium (PAID - optional)
  4. 📺 **TradingView Screener** - Scan IDX via TradingView API (FREE - unofficial)
  5. 📋 **Watchlist Manual** - Alpha Vantage watchlist (FREE dengan API key)
  6. 🔬 **Demo Data** - Fallback untuk testing

### 🪙 Cryptocurrency & Altcoin - PROFESSIONAL TRADING PARAMETERS
- ✅ **Alert Otomatis ke Telegram** pada jadwal:
  - SIANG: 12:00 WIB
  - SORE: 16:30 WIB
- ✅ **Crypto Screening System (100% GRATIS!)** - 3-tier fallback dengan prioritas:
  1. 🪙 **Coinlore API** - Top 100 crypto gainers (PRIMARY - FREE, NO API KEY!)
  2. 🦎 **CoinGecko API** - Top gainers crypto (FREE TIER - 30 calls/min)
  3. 📊 **YFinance Crypto** - Major crypto pairs (FALLBACK - FREE!)

- 📊 **Professional Filters (Updated 15 Okt 2025)**:
  - Volume 24h: **≥ $500k** (ideal ≥ $1M untuk likuiditas optimal)
  - Market Cap: **> $50M** (mid to large cap, menghindari shitcoin)
  - Price Change: **3% - 15%** (momentum sehat, tidak overextended)

- 📈 **Technical Indicators (Manual Calculation via Pandas/Numpy)**:
  - **EMA 20/50**: Exponential Moving Average untuk trend detection
  - **RSI (14)**: Relative Strength Index untuk overbought/oversold
  - **MACD**: Moving Average Convergence Divergence untuk momentum
  - **Bollinger Bands**: Volatilitas dan support/resistance levels

- 💹 **Sentiment & Market Data (100% FREE APIs)**:
  - **Fear & Greed Index**: Alternative.me API (market sentiment)
  - **Funding Rate**: Binance Futures API (long/short bias)
  - **Open Interest**: Binance API (derivative market activity)

- 🎯 **TP/SL Calculation**:
  - TP1: +5%, TP2: +10%, SL: -5% (disesuaikan untuk crypto volatilitas)
  - Entry berdasarkan kombinasi minimal 2 bullish indicators

- 💱 **Konversi Harga ke IDR (Rupiah)**:
  - Semua harga crypto ditampilkan dalam Rupiah (IDR)
  - Kurs: 1 USD = Rp 15,800 (configurable)
  - Format: Rp 16,432 (dengan pemisah ribuan)
  - Entry, TP1, TP2, SL otomatis terkonversi ke IDR

### 🔧 Fitur Umum
- ✅ Analisis sinyal trading dengan indikator teknikal (entry, TP1, TP2, SL)
- ✅ Real-time data dari Yahoo Finance (100% gratis, no API key!)
- ✅ Market cap & volume filtering untuk sinyal akurat
- ✅ Webhook endpoint untuk TradingView alerts
- ✅ Dashboard web untuk monitoring status bot

## Tech Stack
- **Backend**: Flask (Python 3.11)
- **Scheduler**: schedule library
- **Data Sources (Saham IDX)**: 
  - YFinance (Yahoo Finance) - Primary screener
  - IDX Official API - Backup scraper
  - Sectors.app API (optional)
  - TradingView Screener - Unofficial API screener
  - Alpha Vantage API (optional)
- **Data Sources (Crypto)**: 
  - Coinlore API - Primary crypto screener (100% free, no key)
  - CoinGecko API - Backup crypto screener (free tier)
  - YFinance Crypto - Major pairs fallback
- **Notifikasi**: Telegram Bot API
- **Dependencies**: yfinance, beautifulsoup4, lxml, pandas, numpy, tradingview-screener, requests
- **Technical Analysis**: Manual indicator calculation dengan pandas/numpy (EMA, RSI, MACD, Bollinger Bands)

## Struktur Proyek
```
.
├── app.py                  # Main application file
├── pyproject.toml          # Python dependencies (uv)
├── requirements.txt        # Python dependencies (pip/Railway)
├── Procfile                # Railway/Heroku start command
├── railway.toml            # Railway configuration
├── .gitignore              # Git ignore file
├── replit.md               # Documentation (Replit)
├── RAILWAY_DEPLOY.md       # Railway.app deployment guide (TERMUDAH!)
├── ORACLE_DEPLOY.md        # Oracle Cloud deployment guide (GRATIS!)
├── deploy.sh               # Auto deployment script untuk Oracle Cloud
└── scalper-bot.service     # Systemd service file untuk auto-start
```

## Konfigurasi Environment Variables
Diperlukan untuk bot berfungsi dengan baik:

### Wajib:
- `TELEGRAM_BOT_TOKEN`: Token dari @BotFather di Telegram
- `TELEGRAM_CHAT_ID`: Chat ID untuk menerima notifikasi

### Optional:
- `ALPHA_VANTAGE_API_KEY`: API key dari Alpha Vantage (jika tidak diset, akan menggunakan data demo)

## Cara Setup

1. **Telegram Bot Token**:
   - Buka Telegram, cari @BotFather
   - Kirim `/newbot` dan ikuti instruksi
   - Copy token yang diberikan
   - Set sebagai environment variable `TELEGRAM_BOT_TOKEN`

2. **Telegram Chat ID**:
   - Cari @userinfobot di Telegram
   - Kirim pesan apapun
   - Copy ID yang diberikan
   - Set sebagai environment variable `TELEGRAM_CHAT_ID`

3. **Alpha Vantage API Key** (Optional):
   - Daftar gratis di https://www.alphavantage.co/support/#api-key
   - Copy API key
   - Set sebagai environment variable `ALPHA_VANTAGE_API_KEY`

## Watchlist Saham
Saham yang dimonitor (dapat diubah di `app.py`):
- BBCA (Bank Central Asia)
- BMRI (Bank Mandiri)
- TLKM (Telkom Indonesia)
- ASII (Astra International)
- BBNI (Bank Negara Indonesia)

## Endpoints

### GET /
Dashboard utama dengan status bot dan konfigurasi

### POST /webhook/tradingview
Webhook untuk menerima alert dari TradingView

Format payload:
```json
{
  "symbol": "BBCA",
  "signal": "Breakout resistance 9700"
}
```

### GET /test-telegram
Test endpoint untuk mengirim pesan ke Telegram

### GET /test-screening
Test endpoint untuk multi-source screening system (YFinance + IDX + TradingView)

### GET /test-tradingview
Test endpoint khusus untuk TradingView screener

### GET /test-crypto
Test endpoint untuk crypto screening system (Coinlore + CoinGecko + YFinance)

### GET /test-idx-alert
Test endpoint untuk trigger IDX alert manual ke Telegram

### GET /test-crypto-alert
Test endpoint untuk trigger crypto alert manual ke Telegram

### GET /scheduler-status
Debug endpoint untuk cek status scheduler, next run times, dan current time (UTC & WIB)

## Cara Kerja

1. Bot berjalan di background dengan scheduler yang menjalankan analisis pada jadwal tertentu
2. Pada setiap jadwal, bot akan:
   - Mengambil data saham dari watchlist
   - Menganalisis sinyal trading (entry, TP, SL)
   - Mengirim notifikasi ke Telegram dengan format HTML
3. Bot juga menerima webhook dari TradingView untuk alert manual

## Analisis Trading
Bot menganalisis berdasarkan:
- Perubahan harga (momentum)
- Volume trading (akumulasi)
- Perhitungan TP1 (3%), TP2 (6%), SL (2%)

## Deployment Options

Bot mendukung 3 opsi deployment:

### 1. Railway.app (TERMUDAH & GRATIS!) ⭐⭐ HIGHLY RECOMMENDED
- **Setup**: 5-10 menit (super mudah!)
- **Biaya**: $5 credit gratis/bulan (cukup untuk bot scheduled)
- **Server**: Gunicorn dengan auto-restart built-in
- **Deploy**: Langsung dari GitHub (auto-deploy)
- **Monitoring**: Built-in logs & metrics
- **Panduan**: Lihat file **`RAILWAY_DEPLOY.md`** untuk tutorial lengkap
- **Kelebihan**: 
  - ✅ Setup tercepat & termudah
  - ✅ Auto-deploy dari GitHub
  - ✅ Built-in monitoring & logs
  - ✅ No SSH, VPS setup needed
  - ✅ Gratis untuk bot scheduled

### 2. Oracle Cloud Free Tier (GRATIS SELAMANYA!)
- **Type**: VM.Standard.E2.1.Micro (Always Free)
- **Server**: Gunicorn WSGI dengan systemd auto-start
- **Biaya**: **100% GRATIS** (tidak ada biaya bulanan!)
- **Panduan**: Lihat file **`ORACLE_DEPLOY.md`** untuk tutorial lengkap
- **Script**: Gunakan `deploy.sh` untuk instalasi otomatis
- **File**: `scalper-bot.service` untuk systemd configuration
- **Catatan**: Sering "out of capacity", perlu patience

### 3. Replit VM Deployment (Berbayar)
- **Type**: VM (always running untuk scheduler)
- **Server**: Gunicorn WSGI (production-grade)
- **Workers**: 1 worker, 2 threads
- **Port**: 5000 (bind to 0.0.0.0)
- **Timeout**: 120 seconds
- **Cara**: Klik tombol **"Publish"** di pojok kanan atas Replit
- **Biaya**: ~$20/bulan

## User Preferences
- Bahasa: Indonesia
- Fokus: Bot background untuk trading saham Indonesia
- Notifikasi: Telegram only (no dashboard)
- Data: Real-time dari YFinance API (100% gratis!)

## Status Deployment
- ✅ **Bot 100% Siap Deploy!** (15 Oktober 2025)
- ✅ Testing lengkap sukses (IDX + Crypto alerts)
- ✅ Scheduler running sempurna (5 jadwal/hari)
- ✅ Multi-tier screening berfungsi optimal
- ✅ Konversi harga crypto ke IDR aktif
- ✅ Technical indicators & sentiment analysis terintegrasi
- ✅ Logging detail untuk monitoring production
- 🚀 **Ready for Railway.app atau Oracle Cloud deployment!**

## Recent Changes
- 13 Okt 2025: Initial setup dengan Flask, Telegram integration, dan scheduler
- Implementasi Alpha Vantage API untuk data saham Indonesia real-time
- Tambahkan analisis sinyal trading otomatis (entry, TP1, TP2, SL)
- Setup webhook untuk TradingView alerts
- Improved error handling dengan proper HTTP status codes dan helpful messages
- Tambahkan endpoint /get-chat-id untuk memudahkan setup Chat ID
- Deployment configuration untuk production-ready VM deployment
- **🚀 Dynamic Screening Implementation:**
  - Integrasi Sectors.app API untuk screening top gainers otomatis
  - 3-tier fallback system: Dynamic → Watchlist → Demo
  - Market cap dan volume analysis  untuk sinyal lebih akurat
  - Format pesan Telegram yang lebih informatif dengan screening method indicator
- **🚀 Dual Screening Implementation (100% FREE!):**
  - Implementasi YFinance screener untuk scan 50 saham IDX top gainers
  - Implementasi IDX Official scraper sebagai backup
  - 5-tier fallback system: YFinance → IDX → Sectors → Alpha Vantage → Demo
  - Scan otomatis dengan filter market cap & volume
  - **Tidak perlu API key** untuk screening utama (YFinance gratis!)
  - Test endpoint /test-screening untuk verifikasi dual screening
- **☁️ Oracle Cloud Free Tier Deployment (100% GRATIS!):**
  - Deployment guide lengkap untuk Oracle Cloud Always Free tier
  - Auto-deployment script (`deploy.sh`) untuk setup otomatis
  - Systemd service file untuk auto-start dan auto-restart
  - Bot bisa running 24/7 **GRATIS SELAMANYA** di Oracle Cloud
  - Panduan lengkap di `ORACLE_DEPLOY.md` dengan troubleshooting guide
- **🚂 Railway.app Deployment (TERMUDAH & GRATIS!):**
  - Deployment guide super mudah untuk Railway.app
  - Deploy dalam 5-10 menit langsung dari GitHub
  - $5 credit gratis/bulan (cukup untuk bot scheduled)
  - Auto-deploy, monitoring, dan logs built-in
  - Tidak perlu SSH atau VPS setup
  - Fixed scheduler issue: bot akan kirim alert otomatis 24/7
  - Panduan lengkap di `RAILWAY_DEPLOY.md`
- **📺 TradingView Screener Integration (14 Okt 2025):**
  - Implementasi TradingView API screener untuk IDX stocks
  - Unofficial API menggunakan library `tradingview-screener`
  - Filter otomatis untuk Indonesian Stock Exchange (IDX)
  - Integrated sebagai Tier 4 di fallback system
  - Test endpoint `/test-tradingview` untuk verifikasi
  - 100% GRATIS, tidak perlu API key
  - Note: Unofficial API, mungkin tidak selalu return hasil
- **🪙 Cryptocurrency & Altcoin Screening (15 Okt 2025):**
  - Implementasi multi-tier crypto screening system (100% GRATIS!)
  - 3-tier fallback: Coinlore → CoinGecko → YFinance
  - **Coinlore API** (Tier 1): Top 100 crypto gainers, no API key needed
  - **CoinGecko API** (Tier 2): Free tier backup, 30 calls/min
  - **YFinance Crypto** (Tier 3): Major crypto pairs fallback
  - Filter basic: Volume > $100k, Market Cap > $10M
  - TP/SL disesuaikan untuk volatilitas crypto: TP1 +5%, TP2 +10%, SL -5%
  - Test endpoint `/test-crypto` untuk verifikasi
  - Bot sekarang support IDX stocks & cryptocurrency!
- **📊 Professional Crypto Parameters (15 Okt 2025 - Updated):**
  - **Filter Profesional**: Volume ≥$500k, MCap >$50M, Change 3-15%
  - **Technical Indicators** (manual calculation via numpy/pandas):
    - EMA 20/50 untuk trend detection
    - RSI (14) untuk overbought/oversold
    - MACD untuk momentum confirmation
    - Bollinger Bands untuk volatilitas analysis
  - **Sentiment & Market Data** (100% FREE APIs):
    - Fear & Greed Index (Alternative.me API)
    - Funding Rate (Binance Futures API)
    - Open Interest (Binance API)
  - **Signal Analysis**: Entry berdasarkan minimal 2 bullish indicators
  - **Telegram Format**: Enhanced dengan technical indicators display
  - Test results: 5 crypto signals (LDO, MKR, CRV, XMR, ENA) with full indicators
- **🔔 Crypto Alert Automation (15 Okt 2025 - Auto Scheduler):**
  - Implementasi alert otomatis crypto ke Telegram
  - Jadwal: 12:00 WIB (SIANG) dan 19:00 WIB (MALAM)
  - Gunakan format_crypto_alert dengan indikator teknikal lengkap
  - Parallel dengan saham IDX alerts (5 jadwal total per hari)
  - Bot sekarang kirim IDX + Crypto signals otomatis 24/7!
- **💱 Konversi Harga Crypto ke IDR (15 Okt 2025):**
  - Semua harga crypto (Entry, TP1, TP2, SL) ditampilkan dalam Rupiah
  - Kurs USD to IDR: Rp 15,800 (configurable di app.py)
  - Format dengan pemisah ribuan untuk readability
  - Contoh: Entry: Rp 16,432 | TP1: Rp 17,254 (dari $1.04 USD)
  - Volume & Market Cap tetap dalam USD untuk kemudahan
