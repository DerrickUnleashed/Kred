import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict, List, Any
from functools import lru_cache
import threading

INDICES = {
    "NIFTY 50": "^NSEI",
    "BSE SENSEX": "^BSESN",
    "NIFTY BANK": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY AUTO": "^CNXAUTO",
    "NIFTY METAL": "^CNXMETAL",
}

SECTOR_STOCKS = {
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "IT": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
    "Pharma": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "BIOCON.NS"],
    "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS"],
    "Auto": ["MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS"],
    "Energy": ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "TATAPOWER.NS"],
    "Metal": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "NATIONALUM.NS"],
    "Infra": ["LT.NS", "ADANIPORTS.NS", "SIEMENS.NS", "ABB.NS"],
}

ALL_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "ITC.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "WIPRO.NS", "HCLTECH.NS", "TATAMOTORS.NS", "NESTLEIND.NS", "NTPC.NS",
    "ONGC.NS", "TATASTEEL.NS", "BAJAJ-AUTO.NS", "M&M.NS", "CIPLA.NS",
    "DRREDDY.NS", "TECHM.NS", "POWERGRID.NS", "ADANIPORTS.NS", "JSWSTEEL.NS",
]


class StockCache:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_ts: Dict[str, datetime] = {}
        self._lock = threading.Lock()

    def is_stale(self, key: str, ttl_s: int = 300) -> bool:
        ts = self._cache_ts.get(key)
        return ts is None or (datetime.now() - ts).total_seconds() > ttl_s

    def set(self, key: str, value: Any):
        with self._lock:
            self._cache[key] = value
            self._cache_ts[key] = datetime.now()

    def get(self, key: str) -> Any:
        return self._cache.get(key)

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._cache_ts.clear()


cache = StockCache()


def get_market_summary() -> Dict[str, Any]:
    key = "market_summary"
    if not cache.is_stale(key, 120):
        return cache.get(key)
    
    summary = {}
    for name, symbol in INDICES.items():
        try:
            tk = yf.Ticker(symbol)
            hist = tk.history(period="2d")
            if len(hist) >= 2:
                prev = hist["Close"].iloc[-2]
                curr = hist["Close"].iloc[-1]
                chg = curr - prev
                chg_p = (chg / prev) * 100
                summary[name] = {"value": round(curr, 2), "change": round(chg, 2), "pct": round(chg_p, 2)}
            elif len(hist) == 1:
                summary[name] = {"value": round(hist["Close"].iloc[-1], 2), "change": 0.0, "pct": 0.0}
        except Exception:
            continue
    
    cache.set(key, summary)
    return summary


def get_movers() -> Dict[str, List[Dict]]:
    key = "movers"
    if not cache.is_stale(key, 300):
        return cache.get(key)
    
    movers = []
    for ticker in ALL_STOCKS:
        try:
            tk = yf.Ticker(ticker)
            hist = tk.history(period="2d")
            if len(hist) < 2:
                continue
            prev = hist["Close"].iloc[-2]
            curr = hist["Close"].iloc[-1]
            pct = ((curr - prev) / prev) * 100
            info = tk.info
            movers.append({
                "symbol": ticker.replace(".NS", ""),
                "name": info.get("shortName", ticker)[:22],
                "price": round(curr, 2),
                "change": round(pct, 2),
                "volume": int(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0,
            })
        except Exception:
            continue
    
    movers.sort(key=lambda x: x["change"], reverse=True)
    result = {"gainers": movers[:8], "losers": list(reversed(movers[-8:]))}
    cache.set(key, result)
    return result


def get_sector_performance() -> Dict[str, float]:
    key = "sectors"
    if not cache.is_stale(key, 300):
        return cache.get(key)
    
    perf = {}
    for sector, tickers in SECTOR_STOCKS.items():
        changes = []
        for t in tickers[:4]:
            try:
                hist = yf.Ticker(t).history(period="2d")
                if len(hist) >= 2:
                    changes.append(((hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2]) * 100)
            except Exception:
                continue
        if changes:
            perf[sector] = round(sum(changes) / len(changes), 2)
    
    cache.set(key, perf)
    return perf


def get_stock_info(symbol: str) -> Dict[str, Any]:
    key = f"info_{symbol}"
    if not cache.is_stale(key, 3600):
        return cache.get(key)
    
    try:
        tk = yf.Ticker(symbol)
        info = tk.info
        div_yield = info.get("dividendYield") or 0
        
        result = {
            "name": info.get("longName", symbol),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "change": info.get("regularMarketChange", 0),
            "pct": info.get("regularMarketChangePercent", 0),
            "market_cap": info.get("marketCap"),
            "pe": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "div_yield": round(div_yield * 100, 2) if div_yield else 0,
            "high52": info.get("fiftyTwoWeekHigh"),
            "low52": info.get("fiftyTwoWeekLow"),
            "volume": info.get("averageVolume"),
            "beta": info.get("beta"),
            "description": info.get("longBusinessSummary", "")[:500],
        }
        cache.set(key, result)
        return result
    except Exception as e:
        return {"error": str(e)}


def get_historical_data(symbol: str, period: str = "1mo") -> List[Dict]:
    key = f"hist_{symbol}_{period}"
    if not cache.is_stale(key, 600):
        return cache.get(key)
    
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period=period)
        if df.empty:
            return []
        
        df.index = pd.to_datetime(df.index).tz_localize(None)
        result = []
        for idx, row in df.iterrows():
            result.append({
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"]) if "Volume" in row else 0,
            })
        
        cache.set(key, result)
        return result
    except Exception as e:
        return []


def calculate_indicators(symbol: str) -> Dict[str, Any]:
    key = f"indicators_{symbol}"
    if not cache.is_stale(key, 600):
        return cache.get(key)
    
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period="3mo")
        if df.empty or len(df) < 20:
            return {}
        
        close = df["Close"]
        
        sma_20 = close.rolling(20).mean().iloc[-1]
        sma_50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else None
        
        ema_12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema_26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        macd = ema_12 - ema_26
        macd_signal = pd.Series([ema_12 - ema_26]).ewm(span=9, adjust=False).mean().iloc[-1]
        macd_hist = macd - macd_signal
        
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
        rs = gain / loss if loss != 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        bb_mid = close.rolling(20).mean().iloc[-1]
        bb_std = close.rolling(20).std().iloc[-1]
        bb_up = bb_mid + 2 * bb_std
        bb_lo = bb_mid - 2 * bb_std
        
        daily_returns = close.pct_change()
        volatility = daily_returns.rolling(20).std().iloc[-1] * np.sqrt(252) * 100
        
        volume_sma = df["Volume"].rolling(20).mean().iloc[-1]
        volume_ratio = df["Volume"].iloc[-1] / volume_sma if volume_sma > 0 else 1
        
        result = {
            "rsi": round(rsi, 1),
            "macd": round(macd, 2),
            "macd_signal": round(macd_signal, 2),
            "macd_hist": round(macd_hist, 2),
            "sma_20": round(sma_20, 2),
            "sma_50": round(sma_50, 2) if sma_50 else None,
            "bb_up": round(bb_up, 2),
            "bb_mid": round(bb_mid, 2),
            "bb_lo": round(bb_lo, 2),
            "volatility": round(volatility, 1),
            "volume_ratio": round(volume_ratio, 2),
        }
        cache.set(key, result)
        return result
    except Exception as e:
        return {"error": str(e)}
