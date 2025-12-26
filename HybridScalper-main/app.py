from flask import Flask, request, jsonify
import os
import requests
import schedule
import time
import threading
from datetime import datetime
import pytz
import yfinance as yf
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tradingview_screener.query import Query
from tradingview_screener.column import Column

app = Flask(__name__)

# Scheduler initialization flag (untuk pastikan hanya jalan sekali)
_scheduler_started = False

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
SECTORS_API_KEY = os.getenv("SECTORS_API_KEY", "")

WIB = pytz.timezone("Asia/Jakarta")

# Konstanta untuk konversi USD ke IDR (update manual atau gunakan API)
USD_TO_IDR = 15800  # Rata-rata kurs USD ke IDR

def send_telegram_message(text):
    """Mengirim pesan ke Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        error_msg = "TELEGRAM_BOT_TOKEN atau TELEGRAM_CHAT_ID belum diset!"
        print(f"⚠️ {error_msg}")
        return False, error_msg
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ Pesan terkirim ke Telegram")
            return True, "Pesan berhasil dikirim"
        else:
            error_msg = response.json().get("description", response.text)
            print(f"❌ Gagal kirim Telegram: {error_msg}")
            return False, error_msg
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error kirim Telegram: {error_msg}")
        return False, error_msg

def get_dynamic_top_movers():
    """Mendapatkan top movers dinamis dari Sectors.app API"""
    if not SECTORS_API_KEY:
        print("⚠️ SECTORS_API_KEY belum diset, skip dynamic screening")
        return []
    
    try:
        url = "https://api.sectors.app/v1/ranking/top-changes"
        headers = {"Authorization": SECTORS_API_KEY}
        params = {
            "classification": "top_gainers",
            "period": "1d",
            "n_stock": 10,
            "min_market_cap": 1
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stocks = []
            
            for stock in data:
                symbol = stock.get("symbol", "")
                price = stock.get("close_price", 0)
                change_percent = stock.get("change_1d", 0)
                volume = stock.get("volume", 0)
                market_cap = stock.get("market_cap", 0)
                
                if price > 0:
                    stocks.append({
                        "symbol": symbol,
                        "price": price,
                        "change_percent": f"{change_percent}%",
                        "volume": volume,
                        "market_cap": market_cap
                    })
            
            print(f"✅ Berhasil mendapatkan {len(stocks)} top movers dari Sectors.app")
            return stocks
        else:
            print(f"❌ Error Sectors.app API: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error get_dynamic_top_movers: {e}")
        return []

def get_idx_top_gainers_yfinance():
    """Mendapatkan top gainers dari IDX menggunakan YFinance (100% GRATIS)"""
    try:
        print("🔍 Scanning IDX top gainers via YFinance...")
        
        # Daftar 100 saham IDX terpopuler
        idx_tickers = [
            'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK',
            'BBNI.JK', 'UNVR.JK', 'GOTO.JK', 'AMMN.JK', 'ADRO.JK',
            'ANTM.JK', 'INDF.JK', 'ICBP.JK', 'KLBF.JK', 'SMGR.JK',
            'CPIN.JK', 'PTBA.JK', 'INCO.JK', 'ITMG.JK', 'PGAS.JK',
            'MDKA.JK', 'MEDC.JK', 'GGRM.JK', 'TOWR.JK', 'EMTK.JK',
            'EXCL.JK', 'TBIG.JK', 'BRPT.JK', 'BYAN.JK', 'ESSA.JK',
            'INKP.JK', 'TPIA.JK', 'BRIS.JK', 'TKIM.JK', 'BUKA.JK',
            'PGEO.JK', 'SIDO.JK', 'MNCN.JK', 'ERAA.JK', 'SRTG.JK',
            'DMAS.JK', 'TINS.JK', 'AKRA.JK', 'UNTR.JK', 'MAPI.JK',
            'PWON.JK', 'SMSM.JK', 'JPFA.JK', 'ACES.JK', 'MYOR.JK'
        ]
        
        gainers = []
        
        for ticker in idx_tickers[:50]:  # Limit 50 untuk speed
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='2d')
                info = stock.info
                
                if len(hist) >= 2:
                    latest_close = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    volume = hist['Volume'].iloc[-1]
                    
                    pct_change = ((latest_close - prev_close) / prev_close) * 100
                    
                    # Filter: minimal gain 0.5% dan volume > 100k
                    if pct_change > 0.5 and volume > 100000:
                        symbol = ticker.replace('.JK', '')
                        market_cap = info.get('marketCap', 0) / 1_000_000_000  # Dalam Miliar
                        
                        gainers.append({
                            "symbol": symbol,
                            "price": latest_close,
                            "change_percent": f"{pct_change:.2f}%",
                            "volume": int(volume),
                            "market_cap": market_cap
                        })
            except Exception as e:
                continue
        
        # Sort by change percentage
        gainers.sort(key=lambda x: float(x['change_percent'].replace('%', '')), reverse=True)
        
        if gainers:
            print(f"✅ YFinance: Ditemukan {len(gainers)} top gainers")
            return gainers[:10]  # Return top 10
        
        print("⚠️ YFinance: Tidak ada gainers ditemukan")
        return []
        
    except Exception as e:
        print(f"❌ Error YFinance screener: {e}")
        return []

def get_idx_top_gainers_scraper():
    """Mendapatkan top gainers dari IDX official website (100% GRATIS)"""
    try:
        print("🔍 Scraping IDX official top gainers...")
        
        # IDX official endpoint (internal API)
        url = "https://www.idx.co.id/umbraco/Surface/ListedCompany/GetStockGainerLoser"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            gainers = []
            
            # Parse gainer data dari response
            gainer_list = data.get('Gainer', [])
            
            for item in gainer_list[:10]:
                try:
                    symbol = item.get('StockCode', '').strip()
                    price = float(item.get('Price', 0))
                    change_val = float(item.get('Change', 0))
                    prev_price = price - change_val
                    change_percent = (change_val / prev_price * 100) if prev_price > 0 else 0
                    volume = int(item.get('Volume', 0))
                    market_cap = float(item.get('MarketCap', 0)) / 1_000_000_000  # Dalam Miliar
                    
                    if symbol and price > 0:
                        gainers.append({
                            "symbol": symbol,
                            "price": price,
                            "change_percent": f"{change_percent:.2f}%",
                            "volume": volume,
                            "market_cap": market_cap
                        })
                except:
                    continue
            
            if gainers:
                print(f"✅ IDX Scraper: Ditemukan {len(gainers)} top gainers")
                return gainers
        
        print(f"⚠️ IDX Scraper: Response status {response.status_code}")
        return []
        
    except Exception as e:
        print(f"❌ Error IDX scraper: {e}")
        return []

def get_idx_top_gainers_tradingview():
    """
    Mendapatkan top gainers dari TradingView screener (100% GRATIS)
    
    NOTE: TradingView menggunakan unofficial API yang mungkin tidak selalu return hasil
    untuk Indonesian Stock Exchange (IDX). Function ini di-designed sebagai fallback
    tier ke-4 setelah YFinance, IDX Scraper, dan Sectors.app.
    """
    try:
        print("🔍 Scanning IDX top gainers via TradingView...")
        
        # Try with filters first
        # Note: 'ticker' is auto-returned, don't explicitly select it
        try:
            total_count, df = (Query()
                .select('name', 'close', 'change', 'volume', 'market_cap_basic', 'exchange')
                .where(
                    Column('exchange') == 'IDX',  # Indonesian Stock Exchange
                    Column('change') > 0.5,  # Minimal gain 0.5%
                    Column('volume') > 100000  # Volume > 100k
                )
                .order_by('change', ascending=False)
                .limit(10)
                .get_scanner_data())
        except Exception as e:
            # Fallback: Try without strict filters (IDX might not work)
            print(f"⚠️ TradingView: Filter IDX gagal ({str(e)}), coba global search...")
            total_count, df = (Query()
                .select('name', 'close', 'change', 'volume', 'market_cap_basic')
                .where(Column('change') > 0)
                .order_by('change', ascending=False)
                .limit(20)
                .get_scanner_data())
        
        if not df.empty:
            gainers = []
            
            for _, row in df.iterrows():
                try:
                    # Extract symbol dari ticker (format: IDX:BBCA or just BBCA)
                    ticker = str(row.get('ticker', ''))
                    symbol = ticker.split(':')[-1] if ticker and ':' in ticker else ticker
                    
                    # Skip jika bukan IDX
                    if not symbol or (ticker and 'IDX:' not in ticker and ':' in ticker):
                        continue
                    
                    price = float(row.get('close', 0) or 0)
                    change_percent = float(row.get('change', 0) or 0)
                    volume = int(row.get('volume', 0) or 0)
                    market_cap_val = row.get('market_cap_basic', 0)
                    market_cap = float(market_cap_val or 0) / 1_000_000_000  # Dalam Miliar
                    
                    if symbol and price > 0 and change_percent > 0.5:
                        gainers.append({
                            "symbol": symbol,
                            "price": price,
                            "change_percent": f"{change_percent:.2f}%",
                            "volume": volume,
                            "market_cap": market_cap
                        })
                except Exception as e:
                    print(f"⚠️ Error parsing TradingView row: {e}")
                    continue
            
            if gainers:
                print(f"✅ TradingView: Ditemukan {len(gainers)} top gainers dari {total_count} saham")
                return gainers[:10]  # Limit to top 10
        
        print("⚠️ TradingView: Tidak ada gainers ditemukan (market tutup atau API issue)")
        return []
        
    except Exception as e:
        print(f"❌ Error TradingView screener: {e}")
        return []

def get_crypto_top_gainers_coinlore():
    """
    Mendapatkan top gainers crypto dari Coinlore API (100% GRATIS, NO API KEY)
    
    Filter Profesional:
    - Volume 24h ≥ $500k (ideal ≥ $1M)
    - Market Cap > $50M (mid to large cap)
    - Price Change 24h: 3% s/d 15% (momentum tanpa overextended)
    """
    try:
        print("🔍 Scanning crypto top gainers via Coinlore...")
        
        url = "https://api.coinlore.net/api/tickers/"
        params = {"start": 0, "limit": 100}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            coins = data.get("data", [])
            
            # Filter dengan parameter profesional
            gainers = []
            for coin in coins:
                try:
                    symbol = coin.get("symbol", "")
                    name = coin.get("name", "")
                    price = float(coin.get("price_usd", 0))
                    change_24h = float(coin.get("percent_change_24h", 0))
                    volume_24h = float(coin.get("volume24", 0))
                    market_cap = float(coin.get("market_cap_usd", 0))
                    
                    # FILTER PROFESIONAL:
                    # A. Likuiditas & Aktivitas
                    if volume_24h < 500000:  # Min $500k volume
                        continue
                    if market_cap < 50000000:  # Min $50M market cap (mid cap+)
                        continue
                    
                    # B. Momentum range (3-15%)
                    if change_24h < 3.0 or change_24h > 15.0:
                        continue
                    
                    gainers.append({
                        "symbol": symbol,
                        "name": name,
                        "price": price,
                        "change_percent": f"{change_24h:.2f}%",
                        "volume": volume_24h,
                        "market_cap": market_cap / 1_000_000  # Convert to millions
                    })
                except Exception as e:
                    continue
            
            # Sort by change_percent descending
            gainers_sorted = sorted(gainers, key=lambda x: float(x["change_percent"].replace("%", "")), reverse=True)
            
            if gainers_sorted:
                print(f"✅ Coinlore: Ditemukan {len(gainers_sorted)} crypto gainers (filtered)")
                return gainers_sorted[:10]  # Top 10
        
        print("⚠️ Coinlore: Tidak ada gainers yang memenuhi kriteria profesional")
        return []
        
    except Exception as e:
        print(f"❌ Error Coinlore API: {e}")
        return []

def get_crypto_top_gainers_coingecko():
    """
    Mendapatkan top gainers crypto dari CoinGecko API (FREE TIER, 30 calls/min)
    
    Filter Profesional: Volume ≥$500k, MCap >$50M, Change 3-15%
    """
    try:
        print("🔍 Scanning crypto top gainers via CoinGecko...")
        
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "percent_change_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            coins = response.json()
            
            gainers = []
            for coin in coins:
                try:
                    symbol = coin.get("symbol", "").upper()
                    name = coin.get("name", "")
                    price = float(coin.get("current_price", 0))
                    change_24h = float(coin.get("price_change_percentage_24h", 0))
                    volume_24h = float(coin.get("total_volume", 0))
                    market_cap = float(coin.get("market_cap", 0))
                    
                    # FILTER PROFESIONAL
                    if volume_24h < 500000:  # Min $500k volume
                        continue
                    if market_cap < 50000000:  # Min $50M market cap
                        continue
                    if change_24h < 3.0 or change_24h > 15.0:  # 3-15% range
                        continue
                    
                    gainers.append({
                        "symbol": symbol,
                        "name": name,
                        "price": price,
                        "change_percent": f"{change_24h:.2f}%",
                        "volume": volume_24h,
                        "market_cap": market_cap / 1_000_000
                    })
                except Exception as e:
                    continue
            
            if gainers:
                print(f"✅ CoinGecko: Ditemukan {len(gainers)} crypto gainers (filtered)")
                return gainers[:10]
        
        print("⚠️ CoinGecko: Tidak ada gainers yang memenuhi kriteria")
        return []
        
    except Exception as e:
        print(f"❌ Error CoinGecko API: {e}")
        return []

def get_crypto_top_gainers_yfinance():
    """Mendapatkan top gainers crypto dari YFinance (FALLBACK)"""
    try:
        print("🔍 Scanning crypto top gainers via YFinance...")
        
        # Major crypto pairs
        crypto_pairs = [
            'BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD',
            'SOL-USD', 'DOT-USD', 'DOGE-USD', 'AVAX-USD', 'MATIC-USD',
            'LINK-USD', 'UNI-USD', 'ATOM-USD', 'LTC-USD', 'ETC-USD',
            'XLM-USD', 'ALGO-USD', 'VET-USD', 'ICP-USD', 'FIL-USD'
        ]
        
        gainers = []
        
        for pair in crypto_pairs:
            try:
                ticker = yf.Ticker(pair)
                info = ticker.info
                
                symbol = pair.replace('-USD', '')
                price = info.get('regularMarketPrice', 0)
                change_24h = info.get('regularMarketChangePercent', 0)
                volume = info.get('regularMarketVolume', 0)
                market_cap = info.get('marketCap', 0)
                
                if price > 0 and change_24h > 0 and volume > 100000:
                    gainers.append({
                        "symbol": symbol,
                        "name": info.get('shortName', symbol),
                        "price": price,
                        "change_percent": f"{change_24h:.2f}%",
                        "volume": volume,
                        "market_cap": market_cap / 1_000_000 if market_cap else 0
                    })
            except:
                continue
        
        # Sort by change_percent
        gainers_sorted = sorted(gainers, key=lambda x: float(x["change_percent"].replace("%", "")), reverse=True)
        
        if gainers_sorted:
            print(f"✅ YFinance: Ditemukan {len(gainers_sorted)} crypto gainers")
            return gainers_sorted[:10]
        
        print("⚠️ YFinance Crypto: Tidak ada gainers ditemukan")
        return []
        
    except Exception as e:
        print(f"❌ Error YFinance Crypto: {e}")
        return []

def analyze_crypto_signal(crypto_data):
    """
    Analisis sinyal trading untuk cryptocurrency dengan indikator teknikal lengkap
    
    Parameter: Volume ≥$500k, MCap >$50M, Change 3-15%
    Indicators: EMA 20/50, RSI, MACD, Bollinger Bands, Fear & Greed, Funding Rate, OI
    """
    if not crypto_data or crypto_data["price"] == 0:
        return None
    
    symbol = crypto_data["symbol"]
    name = crypto_data.get("name", symbol)
    price = crypto_data["price"]
    change_24h = float(crypto_data["change_percent"].replace("%", ""))
    volume = crypto_data.get("volume", 0)
    market_cap = crypto_data.get("market_cap", 0)
    
    # Crypto TP/SL disesuaikan volatilitas
    entry = round(price, 8)
    tp1 = round(price * 1.05, 8)  # 5% TP1
    tp2 = round(price * 1.10, 8)  # 10% TP2
    sl = round(price * 0.95, 8)   # 5% SL
    
    # Get technical indicators & signals
    indicators, tech_signals = analyze_crypto_with_indicators(
        symbol, name, price, change_24h, volume, market_cap
    )
    
    # Build main signal based on indicators
    main_signal = ""
    
    # Priority signal dari indikator
    if tech_signals:
        # Cek kombinasi bullish
        bullish_count = sum(1 for s in tech_signals if any(x in s for x in ['Bullish', 'Oversold', 'EMA20 > EMA50']))
        bearish_count = sum(1 for s in tech_signals if any(x in s for x in ['Bearish', 'Overbought', 'EMA20 < EMA50']))
        
        if bullish_count >= 2:
            main_signal = f"🚀 {bullish_count} Bullish Signals"
        elif bearish_count >= 2:
            main_signal = f"⚠️ {bearish_count} Bearish Signals"
        else:
            main_signal = "📊 Mixed Signals"
    else:
        # Fallback ke basic signal
        if change_24h > 5:
            main_signal = "🚀 Momentum sangat kuat!"
        elif change_24h > 2:
            main_signal = "📈 Breakout positif"
        else:
            main_signal = "✅ Potensi entry"
    
    # Compile complete signal data
    signal_data = {
        "symbol": symbol,
        "name": name,
        "sinyal": main_signal,
        "entry": entry,
        "tp1": tp1,
        "tp2": tp2,
        "sl": sl,
        "volume": volume,
        "market_cap": market_cap,
        "change_24h": change_24h
    }
    
    # Add technical indicators if available
    if indicators:
        signal_data["indicators"] = indicators
        signal_data["tech_signals"] = tech_signals
    
    return signal_data

def get_crypto_trading_signals():
    """Mendapatkan sinyal trading crypto dengan multi-tier fallback system"""
    signals = []
    screening_method = "❓ Unknown"
    
    print("🔍 Memulai crypto screening...")
    
    # TIER 1: Coinlore API (100% GRATIS, NO API KEY)
    top_gainers = get_crypto_top_gainers_coinlore()
    
    if top_gainers:
        screening_method = "🪙 Coinlore API (Top Gainers Crypto)"
        print(f"✅ Menggunakan Coinlore, ditemukan {len(top_gainers)} crypto")
        
        for crypto in top_gainers[:5]:
            signal = analyze_crypto_signal(crypto)
            if signal:
                signals.append(signal)
    
    # TIER 2: CoinGecko Free Tier
    if not signals:
        print("⚠️ Coinlore tidak ada hasil, fallback ke CoinGecko...")
        top_gainers = get_crypto_top_gainers_coingecko()
        
        if top_gainers:
            screening_method = "🦎 CoinGecko API (Top Gainers Crypto)"
            print(f"✅ Menggunakan CoinGecko, ditemukan {len(top_gainers)} crypto")
            
            for crypto in top_gainers[:5]:
                signal = analyze_crypto_signal(crypto)
                if signal:
                    signals.append(signal)
    
    # TIER 3: YFinance Crypto (FALLBACK)
    if not signals:
        print("⚠️ CoinGecko tidak ada hasil, fallback ke YFinance...")
        top_gainers = get_crypto_top_gainers_yfinance()
        
        if top_gainers:
            screening_method = "📊 YFinance (Major Crypto Pairs)"
            print(f"✅ Menggunakan YFinance, ditemukan {len(top_gainers)} crypto")
            
            for crypto in top_gainers[:5]:
                signal = analyze_crypto_signal(crypto)
                if signal:
                    signals.append(signal)
    
    # DEMO DATA (last resort)
    if not signals:
        print("⚠️ Semua crypto screening gagal, gunakan demo data")
        screening_method = "🔬 Demo Data (Crypto)"
        signals = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "sinyal": "🔬 Demo - Momentum kuat",
                "entry": 45000.0,
                "tp1": 47250.0,
                "tp2": 49500.0,
                "sl": 42750.0,
                "volume": 25000000000,
                "market_cap": 850000
            }
        ]
    
    return signals, screening_method

# ================== TECHNICAL INDICATORS CALCULATIONS ==================

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return None
    
    df = pd.DataFrame({'price': prices})
    ema = df['price'].ewm(span=period, adjust=False).mean()
    return ema.iloc[-1] if len(ema) > 0 else None

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    if len(prices) < period + 1:
        return None
    
    df = pd.DataFrame({'price': prices})
    delta = df['price'].diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1] if len(rsi) > 0 else None

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    if len(prices) < slow:
        return None, None, None
    
    df = pd.DataFrame({'price': prices})
    
    ema_fast = df['price'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['price'].ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return (macd_line.iloc[-1] if len(macd_line) > 0 else None,
            signal_line.iloc[-1] if len(signal_line) > 0 else None,
            histogram.iloc[-1] if len(histogram) > 0 else None)

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    if len(prices) < period:
        return None, None, None
    
    df = pd.DataFrame({'price': prices})
    
    sma = df['price'].rolling(window=period).mean()
    std = df['price'].rolling(window=period).std()
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    return (upper_band.iloc[-1] if len(upper_band) > 0 else None,
            sma.iloc[-1] if len(sma) > 0 else None,
            lower_band.iloc[-1] if len(lower_band) > 0 else None)

# ================== EXTERNAL DATA APIs ==================

def get_fear_greed_index():
    """Get Crypto Fear & Greed Index from Alternative.me"""
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                value = int(data['data'][0]['value'])
                classification = data['data'][0]['value_classification']
                return value, classification
        
        return None, None
    except Exception as e:
        print(f"❌ Error Fear & Greed Index: {e}")
        return None, None

def get_binance_funding_rate(symbol):
    """Get funding rate from Binance Futures"""
    try:
        # Convert symbol format (BTC -> BTCUSDT)
        binance_symbol = f"{symbol}USDT"
        url = "https://fapi.binance.com/fapi/v1/premiumIndex"
        params = {"symbol": binance_symbol}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            funding_rate = float(data.get('lastFundingRate', 0)) * 100  # Convert to percentage
            return funding_rate
        
        return None
    except Exception as e:
        print(f"⚠️ Funding rate error for {symbol}: {e}")
        return None

def get_binance_open_interest(symbol):
    """Get open interest from Binance Futures"""
    try:
        binance_symbol = f"{symbol}USDT"
        url = "https://fapi.binance.com/fapi/v1/openInterest"
        params = {"symbol": binance_symbol}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            open_interest = float(data.get('openInterest', 0))
            return open_interest
        
        return None
    except Exception as e:
        print(f"⚠️ Open interest error for {symbol}: {e}")
        return None

def get_crypto_historical_data(symbol, period="1mo", interval="1h"):
    """Get historical OHLCV data for technical analysis"""
    try:
        # Convert to YFinance format
        ticker_symbol = f"{symbol}-USD"
        ticker = yf.Ticker(ticker_symbol)
        
        # Get historical data
        hist = ticker.history(period=period, interval=interval)
        
        if not hist.empty:
            return {
                'close': hist['Close'].tolist(),
                'high': hist['High'].tolist(),
                'low': hist['Low'].tolist(),
                'volume': hist['Volume'].tolist(),
                'open': hist['Open'].tolist()
            }
        
        return None
    except Exception as e:
        print(f"⚠️ Historical data error for {symbol}: {e}")
        return None

def analyze_crypto_with_indicators(symbol, name, price, change_24h, volume, market_cap):
    """
    Analisis crypto dengan indikator teknikal lengkap
    Mengembalikan dict dengan signals dan indicators
    """
    # Get historical data for technical analysis
    hist_data = get_crypto_historical_data(symbol)
    
    indicators = {}
    signals = []
    
    if hist_data and len(hist_data['close']) > 50:
        close_prices = hist_data['close']
        
        # Calculate EMA 20 & 50
        ema_20 = calculate_ema(close_prices, 20)
        ema_50 = calculate_ema(close_prices, 50)
        
        if ema_20 and ema_50:
            indicators['ema_20'] = round(ema_20, 8)
            indicators['ema_50'] = round(ema_50, 8)
            
            # EMA Crossover Signal
            if ema_20 > ema_50:
                signals.append("EMA20 &gt; EMA50 (Bullish)")
            else:
                signals.append("EMA20 &lt; EMA50 (Bearish)")
        
        # Calculate RSI
        rsi = calculate_rsi(close_prices, 14)
        if rsi:
            indicators['rsi'] = round(rsi, 2)
            
            if rsi < 30:
                signals.append(f"RSI {rsi:.1f} (Oversold)")
            elif rsi > 70:
                signals.append(f"RSI {rsi:.1f} (Overbought)")
            else:
                signals.append(f"RSI {rsi:.1f} (Neutral)")
        
        # Calculate MACD
        macd, signal_line, histogram = calculate_macd(close_prices)
        if macd and signal_line:
            indicators['macd'] = round(macd, 8)
            indicators['macd_signal'] = round(signal_line, 8)
            
            if macd > signal_line:
                signals.append("MACD Bullish")
            else:
                signals.append("MACD Bearish")
        
        # Calculate Bollinger Bands
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close_prices)
        if bb_upper and bb_lower:
            indicators['bb_upper'] = round(bb_upper, 8)
            indicators['bb_lower'] = round(bb_lower, 8)
            
            current_price = close_prices[-1]
            if current_price > bb_upper:
                signals.append("Price &gt; Upper BB (Overbought)")
            elif current_price < bb_lower:
                signals.append("Price &lt; Lower BB (Oversold)")
    
    # Get Fear & Greed Index
    fg_value, fg_class = get_fear_greed_index()
    if fg_value:
        indicators['fear_greed'] = fg_value
        indicators['fear_greed_class'] = fg_class
        signals.append(f"F&G: {fg_value} ({fg_class})")
    
    # Get Funding Rate (only for major coins on Binance)
    funding_rate = get_binance_funding_rate(symbol)
    if funding_rate is not None:
        indicators['funding_rate'] = round(funding_rate, 4)
        if funding_rate > 0.01:
            signals.append(f"Funding: +{funding_rate:.3f}% (Bullish sentiment)")
        elif funding_rate < -0.01:
            signals.append(f"Funding: {funding_rate:.3f}% (Bearish sentiment)")
    
    # Get Open Interest
    open_interest = get_binance_open_interest(symbol)
    if open_interest:
        indicators['open_interest'] = open_interest
    
    return indicators, signals

def get_stock_data(symbol):
    """Mendapatkan data saham dari Alpha Vantage API"""
    if not ALPHA_VANTAGE_API_KEY:
        print("⚠️ ALPHA_VANTAGE_API_KEY belum diset, menggunakan data demo")
        return None
    
    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": f"{symbol}.JK",
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            return {
                "symbol": symbol,
                "price": float(quote.get("05. price", 0)),
                "change_percent": quote.get("10. change percent", "0%"),
                "volume": int(float(quote.get("06. volume", 0)))
            }
        return None
    except Exception as e:
        print(f"❌ Error mengambil data {symbol}: {e}")
        return None

def analyze_stock_signal(stock_data):
    """Analisis sinyal trading berdasarkan data saham"""
    if not stock_data or stock_data["price"] == 0:
        return None
    
    price = stock_data["price"]
    
    entry = price
    tp1 = round(price * 1.03, 2)
    tp2 = round(price * 1.06, 2)
    sl = round(price * 0.98, 2)
    
    change = float(stock_data["change_percent"].replace("%", ""))
    
    if change > 2:
        signal = "Momentum kuat naik 🚀"
    elif change > 0.5:
        signal = "Breakout positif"
    elif stock_data["volume"] > 1000000:
        signal = "Volume tinggi, akumulasi bandar"
    else:
        signal = "Potensi entry"
    
    return {
        "kode": stock_data["symbol"],
        "sinyal": signal,
        "entry": entry,
        "tp1": tp1,
        "tp2": tp2,
        "sl": sl,
        "volume": stock_data["volume"]
    }

def get_trading_signals(session):
    """Mendapatkan sinyal trading dengan dual screening system (YFinance + IDX Scraper)"""
    signals = []
    screening_method = "❓ Unknown"
    
    print(f"🔍 Memulai screening untuk {session}...")
    
    # TIER 1: YFinance Dynamic Screener (100% GRATIS, PRIMARY)
    top_gainers = get_idx_top_gainers_yfinance()
    
    if top_gainers:
        screening_method = "🚀 YFinance Screener (Top Gainers IDX)"
        print(f"✅ Menggunakan YFinance screener, ditemukan {len(top_gainers)} saham")
        
        for stock in top_gainers[:5]:
            signal = analyze_stock_signal(stock)
            if signal:
                signal["market_cap"] = stock.get("market_cap", 0)
                signals.append(signal)
    
    # TIER 2: IDX Official Scraper (100% GRATIS, BACKUP)
    if not signals:
        print("⚠️ YFinance tidak ada hasil, fallback ke IDX Scraper...")
        top_gainers = get_idx_top_gainers_scraper()
        
        if top_gainers:
            screening_method = "📊 IDX Official Scraper (Top Gainers)"
            print(f"✅ Menggunakan IDX scraper, ditemukan {len(top_gainers)} saham")
            
            for stock in top_gainers[:5]:
                signal = analyze_stock_signal(stock)
                if signal:
                    signal["market_cap"] = stock.get("market_cap", 0)
                    signals.append(signal)
    
    # TIER 3: Sectors.app API (PAID, optional)
    if not signals:
        print("⚠️ Free screening tidak ada hasil, coba Sectors.app...")
        top_movers = get_dynamic_top_movers()
        
        if top_movers:
            screening_method = "🎯 Sectors.app (Top Gainers)"
            print(f"✅ Menggunakan Sectors.app, ditemukan {len(top_movers)} saham")
            
            for stock in top_movers[:5]:
                signal = analyze_stock_signal(stock)
                if signal:
                    signal["market_cap"] = stock.get("market_cap", 0)
                    signals.append(signal)
    
    # TIER 4: TradingView Screener (100% GRATIS)
    if not signals:
        print("⚠️ Sectors.app tidak ada hasil, coba TradingView screener...")
        top_gainers = get_idx_top_gainers_tradingview()
        
        if top_gainers:
            screening_method = "📺 TradingView Screener (Top Gainers IDX)"
            print(f"✅ Menggunakan TradingView screener, ditemukan {len(top_gainers)} saham")
            
            for stock in top_gainers[:5]:
                signal = analyze_stock_signal(stock)
                if signal:
                    signal["market_cap"] = stock.get("market_cap", 0)
                    signals.append(signal)
    
    # TIER 5: Alpha Vantage Watchlist (GRATIS dengan API key)
    if not signals and ALPHA_VANTAGE_API_KEY:
        print("⚠️ Dynamic screening tidak ada hasil, fallback ke watchlist manual...")
        screening_method = "📋 Watchlist Manual (Alpha Vantage)"
        watchlist = ["BBCA", "BMRI", "TLKM", "ASII", "BBNI"]
        
        for symbol in watchlist:
            stock_data = get_stock_data(symbol)
            if stock_data:
                signal = analyze_stock_signal(stock_data)
                if signal:
                    signals.append(signal)
                time.sleep(12)
    
    # TIER 6: Demo Data (Final Fallback)
    if not signals:
        screening_method = "🔬 Demo Data"
        print("⚠️ Semua screening gagal, menggunakan demo data")
        demo_signals = [
            {"kode": "BBCA", "sinyal": "Breakout level resistance", "entry": 9710, "tp1": 9900, "tp2": 10100, "sl": 9550, "volume": 5000000, "market_cap": 584000},
            {"kode": "BMRI", "sinyal": "Volume spike, momentum kuat", "entry": 7650, "tp1": 7900, "tp2": 8200, "sl": 7500, "volume": 8500000, "market_cap": 452000},
            {"kode": "TLKM", "sinyal": "Support kuat di 3500", "entry": 3550, "tp1": 3650, "tp2": 3800, "sl": 3480, "volume": 12000000, "market_cap": 356000}
        ]
        return demo_signals, screening_method
    
    return signals, screening_method

def format_alert(session):
    """Format pesan alert untuk Telegram"""
    signals, screening_method = get_trading_signals(session)
    now = datetime.now(WIB).strftime("%d-%b-%Y %H:%M WIB")
    
    if not signals:
        return f"📊 <b>Update {session}</b>\n🕐 {now}\n\nTidak ada saham yang memenuhi kriteria hari ini."
    
    message = f"📊 <b>Update {session}</b>\n"
    message += f"🕐 {now}\n"
    message += f"{screening_method}\n\n"
    
    for s in signals:
        message += f"💡 <b>{s['kode']}</b>\n"
        message += f"📈 {s['sinyal']}\n"
        message += f"🎯 Entry: {s['entry']} | TP1: {s['tp1']} | TP2: {s['tp2']} | SL: {s['sl']}\n"
        message += f"📊 Volume: {s['volume']:,}"
        
        if s.get('market_cap'):
            mcap_text = f"{s['market_cap']:,.0f}B" if s['market_cap'] < 1000 else f"{s['market_cap']/1000:.1f}T"
            message += f" | MCap: {mcap_text}"
        
        message += "\n\n"
    
    message += "#FollowTheWhale 🐋 #HybridScalper"
    return message

def format_crypto_alert(session="CRYPTO"):
    """Format pesan crypto alert untuk Telegram dengan indikator teknikal (harga dalam IDR)"""
    signals, screening_method = get_crypto_trading_signals()
    now = datetime.now(WIB).strftime("%d-%b-%Y %H:%M WIB")
    
    if not signals:
        return f"🪙 <b>Crypto Update {session}</b>\n🕐 {now}\n\nTidak ada crypto yang memenuhi kriteria profesional hari ini."
    
    message = f"🪙 <b>Crypto Update {session}</b>\n"
    message += f"🕐 {now}\n"
    message += f"{screening_method}\n"
    message += f"💱 Kurs: 1 USD = Rp {USD_TO_IDR:,}\n\n"
    
    for s in signals:
        # Konversi harga ke IDR
        entry_idr = s['entry'] * USD_TO_IDR
        tp1_idr = s['tp1'] * USD_TO_IDR
        tp2_idr = s['tp2'] * USD_TO_IDR
        sl_idr = s['sl'] * USD_TO_IDR
        
        # Basic Info
        message += f"💎 <b>{s['symbol']}</b> - {s.get('name', s['symbol'])}\n"
        message += f"📈 {s['sinyal']}\n"
        message += f"🎯 Entry: Rp {entry_idr:,.0f} | TP1: Rp {tp1_idr:,.0f} | TP2: Rp {tp2_idr:,.0f} | SL: Rp {sl_idr:,.0f}\n"
        
        # Volume & Market Cap (tetap USD untuk mudah dibaca)
        vol_text = f"${s['volume']/1e6:.1f}M" if s['volume'] < 1e9 else f"${s['volume']/1e9:.2f}B"
        mcap_text = f"${s['market_cap']:.0f}M"
        message += f"📊 Vol: {vol_text} | MCap: {mcap_text}"
        
        if s.get('change_24h'):
            message += f" | 24h: +{s['change_24h']:.1f}%"
        
        message += "\n"
        
        # Technical Indicators (if available)
        if s.get('indicators'):
            ind = s['indicators']
            message += "🔍 Indicators: "
            
            # RSI
            if ind.get('rsi'):
                message += f"RSI {ind['rsi']:.0f} "
            
            # EMA
            if ind.get('ema_20') and ind.get('ema_50'):
                ema_status = "✅" if ind['ema_20'] > ind['ema_50'] else "⚠️"
                message += f"| EMA {ema_status} "
            
            # MACD
            if ind.get('macd') and ind.get('macd_signal'):
                macd_status = "✅" if ind['macd'] > ind['macd_signal'] else "⚠️"
                message += f"| MACD {macd_status} "
            
            # Fear & Greed
            if ind.get('fear_greed'):
                fg_class = ind.get('fear_greed_class', 'N/A')
                message += f"| FG: {ind['fear_greed']} ({fg_class})"
            
            message += "\n"
        
        # Technical Signals summary (if available)
        if s.get('tech_signals'):
            message += f"📉 {', '.join(s['tech_signals'][:3])}\n"
        
        message += "\n"
    
    message += "💡 Filter: Vol≥$500k, MCap>$50M, Change 3-15%\n"
    message += "#CryptoScalper 🪙 #HybridBot"
    return message

def job_alert(session):
    """Job scheduler untuk mengirim alert saham IDX"""
    now = datetime.now(WIB).strftime("%d-%b-%Y %H:%M:%S WIB")
    print(f"\n{'='*60}")
    print(f"🔔 SCHEDULER TRIGGERED: {session}")
    print(f"⏰ Waktu: {now}")
    print(f"{'='*60}")
    text = format_alert(session)
    send_telegram_message(text)
    print(f"✅ Alert {session} berhasil dikirim ke Telegram")
    print(f"{'='*60}\n")

def job_crypto_alert(session):
    """Job scheduler untuk mengirim alert crypto"""
    now = datetime.now(WIB).strftime("%d-%b-%Y %H:%M:%S WIB")
    print(f"\n{'='*60}")
    print(f"🪙 SCHEDULER TRIGGERED: {session}")
    print(f"⏰ Waktu: {now}")
    print(f"{'='*60}")
    text = format_crypto_alert(session)
    send_telegram_message(text)
    print(f"✅ Crypto alert {session} berhasil dikirim ke Telegram")
    print(f"{'='*60}\n")

def scheduler_thread():
    """Thread untuk menjalankan scheduler"""
    import pytz
    now_wib = datetime.now(WIB)
    now_utc = datetime.now(pytz.UTC)
    
    print("⏰ Scheduler dimulai...")
    print(f"🕐 Waktu sekarang: {now_wib.strftime('%d-%b-%Y %H:%M WIB')} ({now_utc.strftime('%H:%M UTC')})")
    
    # Jadwal Saham IDX
    schedule.every().day.at("01:55").do(job_alert, session="PRE-MARKET (08:55 WIB)")
    schedule.every().day.at("03:30").do(job_alert, session="SESI 1 (10:30 WIB)")
    schedule.every().day.at("08:30").do(job_alert, session="CLOSING (15:30 WIB)")
    
    # Jadwal Cryptocurrency
    schedule.every().day.at("05:00").do(job_crypto_alert, session="SIANG (12:00 WIB)")
    schedule.every().day.at("09:30").do(job_crypto_alert, session="SORE (16:30 WIB)")
    
    print("\n📅 Jadwal notifikasi IDX:")
    print("   - PRE-MARKET: 08:55 WIB (01:55 UTC)")
    print("   - SESI 1: 10:30 WIB (03:30 UTC)")
    print("   - CLOSING: 15:30 WIB (08:30 UTC)")
    print("\n🪙 Jadwal notifikasi CRYPTO:")
    print("   - SIANG: 12:00 WIB (05:00 UTC)")
    print("   - SORE: 16:30 WIB (09:30 UTC)")
    
    # Display next run times
    jobs = schedule.get_jobs()
    print("\n⏭️  Next scheduled runs:")
    for job in jobs:
        func_name = job.job_func.__name__.replace("job_", "").replace("_alert", "").upper()
        next_run = job.next_run.strftime("%d-%b %H:%M UTC")
        print(f"   - {func_name}: {next_run}")
    
    print("\n📌 NOTE: Jika bot di-restart setelah jadwal hari ini, alert akan jalan besok.")
    print("📌 Di production (Railway), bot running 24/7, alert otomatis sesuai jadwal!\n")
    
    while True:
        schedule.run_pending()
        time.sleep(30)

@app.route("/webhook/tradingview", methods=["POST"])
def webhook():
    """Webhook untuk menerima alert dari TradingView"""
    try:
        data = request.get_json(force=True)
        symbol = data.get("symbol", "Unknown")
        signal = data.get("signal", "No signal info")
        
        msg = f"⚡ <b>TradingView Alert</b>\n\n"
        msg += f"📊 {symbol}\n"
        msg += f"📈 {signal}\n\n"
        msg += f"🕐 {datetime.now(WIB).strftime('%d-%b-%Y %H:%M WIB')}"
        
        success, message = send_telegram_message(msg)
        
        if success:
            return jsonify({"status": "ok", "message": "Alert diterima dan dikirim ke Telegram"})
        else:
            return jsonify({
                "status": "partial", 
                "message": "Alert diterima tapi gagal kirim ke Telegram",
                "error": message
            }), 500
    except Exception as e:
        print(f"❌ Error webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/")
def home():
    """Halaman utama"""
    status = "✅ Aktif" if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else "⚠️ Konfigurasi belum lengkap"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hybrid Scalper Bot</title>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .card {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #2c3e50; }}
            .status {{ 
                padding: 10px;
                border-radius: 5px;
                background: #e8f5e9;
                margin: 20px 0;
            }}
            .info {{ color: #555; margin: 10px 0; }}
            .endpoint {{
                background: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🐋 Hybrid Scalper Bot</h1>
            <div class="status">
                <strong>Status:</strong> {status}
            </div>
            
            <h3>📅 Jadwal Notifikasi:</h3>
            <div class="info">
                <strong>📈 Saham IDX:</strong><br>
                • PRE-MARKET: 08:55 WIB<br>
                • SESI 1: 10:30 WIB<br>
                • CLOSING: 15:30 WIB<br><br>
                
                <strong>🪙 Cryptocurrency:</strong><br>
                • SIANG: 12:00 WIB<br>
                • SORE: 16:30 WIB
            </div>
            
            <h3>🔗 Endpoints:</h3>
            <div class="info">
                • <a href="/test-telegram">GET /test-telegram</a> - Test kirim pesan ke Telegram<br>
                • <a href="/test-screening">GET /test-screening</a> - Test dual screening system (YFinance + IDX)<br>
                • <a href="/test-crypto">GET /test-crypto</a> - Test crypto screening dengan indikator teknikal<br>
                • <a href="/test-crypto-alert">GET /test-crypto-alert</a> - 🆕 Test kirim crypto alert ke Telegram<br>
                • <a href="/get-chat-id">GET /get-chat-id</a> - Dapatkan Chat ID Telegram Anda<br>
                • POST /webhook/tradingview - Webhook untuk TradingView alerts
            </div>
            
            <h3>⚙️ Konfigurasi yang diperlukan:</h3>
            <div class="info">
                <strong>Wajib:</strong><br>
                • TELEGRAM_BOT_TOKEN: {'✅ Tersedia' if TELEGRAM_BOT_TOKEN else '❌ Belum diset'}<br>
                • TELEGRAM_CHAT_ID: {'✅ Tersedia' if TELEGRAM_CHAT_ID else '❌ Belum diset'}<br><br>
                
                <strong>Dual Screening System (100% GRATIS!):</strong><br>
                • 🚀 YFinance Screener: ✅ Aktif (Top Gainers IDX - FREE!)<br>
                • 📊 IDX Official Scraper: ✅ Standby (Backup - FREE!)<br><br>
                
                <strong>Optional (Additional Screening):</strong><br>
                • SECTORS_API_KEY: {'✅ Tersedia' if SECTORS_API_KEY else '⚠️ Belum diset (PAID - optional)'}<br>
                • ALPHA_VANTAGE_API_KEY: {'✅ Tersedia' if ALPHA_VANTAGE_API_KEY else '⚠️ Belum diset (watchlist fallback)'}
            </div>
            
            <h3>🎯 Screening Method:</h3>
            <div class="info">
                {'🚀 <strong>Dynamic Screening</strong> - Bot akan scan top gainers dari seluruh saham IDX secara otomatis!' if SECTORS_API_KEY else '📋 <strong>Manual Watchlist</strong> - Bot hanya scan saham di watchlist (BBCA, BMRI, TLKM, ASII, BBNI)'}
            </div>
            
            <h3>📝 Cara Setup TELEGRAM_CHAT_ID:</h3>
            <div class="info">
                1. Buka Telegram dan cari bot Anda (dari @BotFather)<br>
                2. Kirim pesan '/start' ke bot Anda<br>
                3. Klik <a href="/get-chat-id" target="_blank">disini</a> untuk mendapatkan Chat ID<br>
                4. Tambahkan Chat ID ke Secrets dengan nama TELEGRAM_CHAT_ID
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route("/get-chat-id")
def get_chat_id():
    """Mendapatkan Chat ID dari Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        return jsonify({"error": "TELEGRAM_BOT_TOKEN belum diset"}), 400
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("ok") and data.get("result"):
            chats = []
            for update in data["result"]:
                if "message" in update:
                    chat = update["message"]["chat"]
                    chats.append({
                        "chat_id": chat["id"],
                        "type": chat["type"],
                        "name": chat.get("first_name", "") + " " + chat.get("last_name", ""),
                        "username": chat.get("username", "")
                    })
            
            if chats:
                return jsonify({
                    "status": "ok",
                    "message": "Ditemukan chat. Gunakan chat_id di bawah untuk TELEGRAM_CHAT_ID",
                    "chats": chats
                })
            else:
                return jsonify({
                    "status": "no_messages",
                    "message": "Tidak ada pesan. Kirim pesan '/start' ke bot Anda di Telegram dulu, lalu refresh halaman ini."
                })
        
        return jsonify({"error": "Gagal mengambil updates", "details": data}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/test-screening")
def test_screening():
    """Test screening dinamis"""
    try:
        signals, method = get_trading_signals("TEST SCREENING")
        
        return jsonify({
            "status": "ok",
            "screening_method": method,
            "total_signals": len(signals),
            "signals": signals,
            "message": f"Berhasil mendapatkan {len(signals)} sinyal dengan metode: {method}"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/test-tradingview")
def test_tradingview():
    """Test TradingView screener"""
    try:
        print("🧪 Testing TradingView screener...")
        gainers = get_idx_top_gainers_tradingview()
        
        if gainers:
            return jsonify({
                "status": "ok",
                "source": "TradingView Screener",
                "total_gainers": len(gainers),
                "gainers": gainers,
                "message": f"✅ TradingView: Ditemukan {len(gainers)} top gainers"
            })
        else:
            return jsonify({
                "status": "no_results",
                "source": "TradingView Screener",
                "total_gainers": 0,
                "gainers": [],
                "message": "⚠️ TradingView: Tidak ada gainers ditemukan"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "source": "TradingView Screener",
            "message": str(e),
            "error_type": type(e).__name__
        }), 500

@app.route("/test-crypto")
def test_crypto():
    """Test crypto screening system dengan indikator teknikal lengkap"""
    try:
        print("🧪 Testing crypto screening dengan professional parameters...")
        signals, method = get_crypto_trading_signals()
        
        # Format telegram message untuk preview
        telegram_preview = format_crypto_alert("TEST")
        
        return jsonify({
            "status": "ok",
            "screening_method": method,
            "total_signals": len(signals),
            "signals": signals,
            "telegram_preview": telegram_preview,
            "filters_applied": {
                "volume_min": "$500k",
                "market_cap_min": "$50M",
                "price_change_range": "3% - 15%"
            },
            "indicators": {
                "technical": ["EMA 20/50", "RSI", "MACD", "Bollinger Bands"],
                "sentiment": ["Fear & Greed Index", "Funding Rate", "Open Interest"]
            },
            "message": f"✅ {len(signals)} crypto signals found with professional filters\n📊 Method: {method}"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }), 500

@app.route("/test-telegram")
def test_telegram():
    """Test pengiriman pesan ke Telegram"""
    msg = f"🧪 <b>Test Pesan</b>\n\nBot Hybrid Scalper berjalan dengan baik!\n\n🕐 {datetime.now(WIB).strftime('%d-%b-%Y %H:%M WIB')}"
    success, message = send_telegram_message(msg)
    
    if success:
        return jsonify({"status": "ok", "message": "✅ " + message})
    else:
        return jsonify({
            "status": "error", 
            "message": "❌ Gagal mengirim pesan ke Telegram",
            "error": message,
            "help": "Pastikan TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID sudah benar. Cek /get-chat-id untuk mendapatkan Chat ID yang benar."
        }), 400

@app.route("/test-crypto-alert")
def test_crypto_alert():
    """Test kirim crypto alert ke Telegram (manual trigger)"""
    try:
        print("🧪 Testing crypto alert to Telegram...")
        job_crypto_alert("TEST MANUAL")
        
        return jsonify({
            "status": "ok",
            "message": "✅ Crypto alert berhasil dikirim ke Telegram!",
            "info": "Cek Telegram Anda untuk melihat pesan crypto alert dengan indikator teknikal lengkap"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"❌ Gagal mengirim crypto alert: {str(e)}",
            "error_type": type(e).__name__
        }), 500

@app.route("/test-idx-alert")
def test_idx_alert():
    """Test kirim IDX alert ke Telegram (manual trigger)"""
    try:
        print("🧪 Testing IDX alert to Telegram...")
        job_alert("TEST MANUAL")
        
        return jsonify({
            "status": "ok",
            "message": "✅ IDX alert berhasil dikirim ke Telegram!",
            "info": "Cek Telegram Anda untuk melihat pesan IDX alert"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"❌ Gagal mengirim IDX alert: {str(e)}",
            "error_type": type(e).__name__
        }), 500

@app.route("/scheduler-status")
def scheduler_status():
    """Debug endpoint untuk cek status scheduler"""
    import pytz
    utc_now = datetime.now(pytz.UTC)
    wib_now = datetime.now(WIB)
    
    jobs = schedule.get_jobs()
    jobs_info = []
    
    for job in jobs:
        jobs_info.append({
            "next_run": str(job.next_run),
            "job_func": job.job_func.__name__,
            "interval": str(job.unit),
            "at_time": str(job.at_time) if hasattr(job, 'at_time') else None
        })
    
    return jsonify({
        "status": "ok",
        "scheduler_started": _scheduler_started,
        "total_jobs": len(jobs),
        "current_time_utc": utc_now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "current_time_wib": wib_now.strftime("%Y-%m-%d %H:%M:%S WIB"),
        "scheduled_jobs": jobs_info,
        "expected_schedule": {
            "idx": [
                "01:55 UTC (08:55 WIB) - PRE-MARKET",
                "03:30 UTC (10:30 WIB) - SESI 1",
                "08:30 UTC (15:30 WIB) - CLOSING"
            ],
            "crypto": [
                "05:00 UTC (12:00 WIB) - SIANG",
                "09:30 UTC (16:30 WIB) - SORE"
            ]
        }
    })

# Start scheduler thread saat module di-import (untuk production dengan Gunicorn)
def init_scheduler():
    """Initialize scheduler thread (jalan sekali saat app startup)"""
    global _scheduler_started
    if not _scheduler_started:
        _scheduler_started = True
        print("\n" + "="*50)
        print("🚀 HYBRID SCALPER BOT STARTING...")
        print("="*50 + "\n")
        threading.Thread(target=scheduler_thread, daemon=True).start()

# Auto-start scheduler saat module di-import (production mode)
init_scheduler()

if __name__ == "__main__":
    # Development mode - Flask dev server
    app.run(host="0.0.0.0", port=5000, debug=False)
