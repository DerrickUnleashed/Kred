"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          INDIAN MARKET ANALYZER — Core Analysis Engine                      ║
║          Real-time data fetching, technical indicators, charts              ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module provides the core market analysis functionality including:
- Fetching real-time data from Yahoo Finance
- Calculating technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Generating interactive charts with Plotly
- Managing market indices, sector performance, and stock movers
"""

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
import warnings
import threading
from typing import Optional, Dict, List, Any

warnings.filterwarnings("ignore")


class IndianMarketAnalyzer:
    """Fetches real-time Yahoo Finance data and computes technical indicators for Indian market."""

    # Indian Market Indices
    INDICES: Dict[str, str] = {
        "NIFTY 50":    "^NSEI",
        "BSE SENSEX":  "^BSESN",
        "NIFTY BANK":  "^NSEBANK",
        "NIFTY IT":    "^CNXIT",
        "NIFTY PHARMA":"^CNXPHARMA",
        "NIFTY FMCG":  "^CNXFMCG",
        "NIFTY AUTO":  "^CNXAUTO",
        "NIFTY METAL": "^CNXMETAL",
    }

    # Sector-wise stock lists for Indian market
    SECTOR_STOCKS: Dict[str, List[str]] = {
        "Banking": ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS"],
        "IT":      ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS"],
        "Pharma":  ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","DIVISLAB.NS","BIOCON.NS"],
        "FMCG":    ["HINDUNILVR.NS","ITC.NS","NESTLEIND.NS","BRITANNIA.NS","DABUR.NS"],
        "Auto":    ["MARUTI.NS","M&M.NS","TATAMOTORS.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS"],
        "Energy":  ["RELIANCE.NS","ONGC.NS","NTPC.NS","POWERGRID.NS","TATAPOWER.NS"],
        "Metal":   ["TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","VEDL.NS","NATIONALUM.NS"],
        "Infra":   ["LT.NS","ADANIPORTS.NS","SIEMENS.NS","ABB.NS"],
    }

    # Complete list of actively tracked Indian stocks
    ALL_TICKERS: List[str] = [
        "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
        "HINDUNILVR.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","ITC.NS",
        "LT.NS","AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS",
        "WIPRO.NS","HCLTECH.NS","TATAMOTORS.NS","NESTLEIND.NS","NTPC.NS",
        "ONGC.NS","TATASTEEL.NS","BAJAJ-AUTO.NS","M&M.NS","CIPLA.NS",
        "DRREDDY.NS","TECHM.NS","POWERGRID.NS","ADANIPORTS.NS","JSWSTEEL.NS",
    ]

    def __init__(self):
        """Initialize the analyzer with caching mechanism."""
        self._cache: Dict[str, Any] = {}
        self._cache_ts: Dict[str, datetime] = {}
        self._lock = threading.Lock()

    # ── Cache Helpers ──────────────────────────────────────────────────────────
    def _is_stale(self, key: str, ttl_s: int = 300) -> bool:
        """Check if cached data is stale."""
        ts = self._cache_ts.get(key)
        return ts is None or (datetime.now() - ts).total_seconds() > ttl_s

    def _set_cache(self, key: str, value: Any):
        """Store value in cache with timestamp."""
        with self._lock:
            self._cache[key] = value
            self._cache_ts[key] = datetime.now()

    def _get_cache(self, key: str) -> Any:
        """Retrieve value from cache."""
        return self._cache.get(key)

    # ── Data Fetching Methods ───────────────────────────────────────────────────
    def fetch_historical_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a given symbol.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE.NS")
            period: Time period (1mo, 3mo, 6mo, 1y, 2y)
        
        Returns:
            DataFrame with Open, High, Low, Close, Volume columns
        """
        key = f"hist_{symbol}_{period}"
        if not self._is_stale(key, 600):
            return self._get_cache(key)
        
        try:
            tk = yf.Ticker(symbol)
            df = tk.history(period=period)
            if df.empty:
                return pd.DataFrame()
            
            df.index = pd.to_datetime(df.index).tz_localize(None)
            if len(df.columns) >= 6:
                df = df.iloc[:, :6]
                df.columns = ["Open", "High", "Low", "Close", "Volume", "Dividends"]
            
            self._set_cache(key, df)
            return df
        except Exception:
            return pd.DataFrame()

    def get_company_info(self, symbol: str) -> Dict:
        """
        Get detailed company information.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE.NS")
        
        Returns:
            Dictionary with company details (name, sector, market cap, PE ratio, etc.)
        """
        key = f"info_{symbol}"
        if not self._is_stale(key, 3600):
            return self._get_cache(key)
        
        try:
            info = yf.Ticker(symbol).info
            div_yield = info.get("dividendYield") or 0
            
            result = {
                "name":          info.get("longName", symbol),
                "sector":        info.get("sector", "N/A"),
                "industry":      info.get("industry", "N/A"),
                "market_cap":    info.get("marketCap"),
                "pe_ratio":      info.get("trailingPE"),
                "eps":           info.get("trailingEps"),
                "dividend_yield": round(div_yield * 100, 2),
                "52w_high":      info.get("fiftyTwoWeekHigh"),
                "52w_low":       info.get("fiftyTwoWeekLow"),
                "avg_volume":    info.get("averageVolume"),
                "beta":          info.get("beta"),
                "description":   info.get("longBusinessSummary", ""),
            }
            self._set_cache(key, result)
            return result
        except Exception:
            return {}

    def get_market_summary(self) -> Dict:
        """
        Get current market indices summary.
        
        Returns:
            Dictionary with index names and their values, changes, percentages
        """
        key = "market_summary"
        if not self._is_stale(key, 120):
            return self._get_cache(key)
        
        summary = {}
        for name, symbol in self.INDICES.items():
            try:
                tk = yf.Ticker(symbol)
                hist = tk.history(period="2d")
                if len(hist) >= 2:
                    prev = hist["Close"].iloc[-2]
                    curr = hist["Close"].iloc[-1]
                    chg = curr - prev
                    chg_p = (chg / prev) * 100
                    summary[name] = {
                        "value": round(curr, 2),
                        "change": round(chg, 2),
                        "pct": round(chg_p, 2),
                    }
                elif len(hist) == 1:
                    curr = hist["Close"].iloc[-1]
                    summary[name] = {"value": round(curr, 2), "change": 0.0, "pct": 0.0}
            except Exception:
                continue
        
        self._set_cache(key, summary)
        return summary

    def get_movers(self) -> Dict[str, List[Dict]]:
        """
        Get top gainers and losers from tracked stocks.
        
        Returns:
            Dictionary with 'gainers' and 'losers' lists
        """
        key = "movers"
        if not self._is_stale(key, 300):
            return self._get_cache(key)
        
        movers = []
        for ticker in self.ALL_TICKERS:
            try:
                tk = yf.Ticker(ticker)
                hist = tk.history(period="2d")
                if len(hist) < 2:
                    continue
                
                prev = hist["Close"].iloc[-2]
                curr = hist["Close"].iloc[-1]
                pct = ((curr - prev) / prev) * 100
                
                movers.append({
                    "symbol": ticker.replace(".NS", ""),
                    "name": tk.info.get("shortName", ticker)[:22],
                    "price": round(curr, 2),
                    "change": round(pct, 2),
                    "volume": int(hist["Volume"].iloc[-1]),
                })
            except Exception:
                continue
        
        movers.sort(key=lambda x: x["change"], reverse=True)
        result = {"gainers": movers[:8], "losers": list(reversed(movers[-8:]))}
        self._set_cache(key, result)
        return result

    def get_sector_performance(self) -> Dict[str, float]:
        """
        Calculate sector-wise performance based on top stocks.
        
        Returns:
            Dictionary with sector names and their average percentage changes
        """
        key = "sectors"
        if not self._is_stale(key, 300):
            return self._get_cache(key)
        
        perf = {}
        for sector, tickers in self.SECTOR_STOCKS.items():
            changes = []
            for t in tickers[:4]:
                try:
                    hist = yf.Ticker(t).history(period="2d")
                    if len(hist) >= 2:
                        changes.append(((hist["Close"].iloc[-1] - hist["Close"].iloc[-2])
                                        / hist["Close"].iloc[-2]) * 100)
                except Exception:
                    continue
            
            if changes:
                perf[sector] = round(sum(changes) / len(changes), 2)
        
        self._set_cache(key, perf)
        return perf

    # ── Technical Indicators ────────────────────────────────────────────────────
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for the given DataFrame.
        
        Indicators computed:
        - SMA_20, SMA_50, SMA_200 (Simple Moving Averages)
        - EMA_12, EMA_26 (Exponential Moving Averages)
        - MACD, MACD_Signal, MACD_Histogram
        - RSI (Relative Strength Index)
        - Bollinger Bands (BB_Mid, BB_Up, BB_Lo)
        - Volatility (annualized)
        - Volume_Ratio (volume relative to average)
        - ATR (Average True Range)
        
        Returns:
            DataFrame with added indicator columns
        """
        if df.empty or len(df) < 20:
            return df
        
        df = df.copy()

        # Moving Averages
        df["SMA_20"] = df["Close"].rolling(20).mean()
        df["SMA_50"] = df["Close"].rolling(50).mean()
        df["SMA_200"] = df["Close"].rolling(200).mean()
        df["EMA_12"] = df["Close"].ewm(span=12, adjust=False).mean()
        df["EMA_26"] = df["Close"].ewm(span=26, adjust=False).mean()

        # MACD
        df["MACD"] = df["EMA_12"] - df["EMA_26"]
        df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
        df["MACD_Histogram"] = df["MACD"] - df["MACD_Signal"]

        # RSI (14-day)
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss.replace(0, 1e-9)
        df["RSI"] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        bb_mid = df["Close"].rolling(20).mean()
        bb_std = df["Close"].rolling(20).std()
        df["BB_Mid"] = bb_mid
        df["BB_Up"] = bb_mid + 2 * bb_std
        df["BB_Lo"] = bb_mid - 2 * bb_std

        # Volatility & Volume
        df["Daily_Return"] = df["Close"].pct_change()
        df["Volatility"] = df["Daily_Return"].rolling(20).std() * np.sqrt(252) * 100
        df["Volume_SMA"] = df["Volume"].rolling(20).mean()
        df["Volume_Ratio"] = df["Volume"] / df["Volume_SMA"].replace(0, 1)

        # ATR (Average True Range)
        hl = df["High"] - df["Low"]
        hcp = (df["High"] - df["Close"].shift()).abs()
        lcp = (df["Low"] - df["Close"].shift()).abs()
        df["ATR"] = pd.concat([hl, hcp, lcp], axis=1).max(axis=1).rolling(14).mean()

        return df

    # ── Charting Methods ────────────────────────────────────────────────────────
    @staticmethod
    def candlestick_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
        """
        Create interactive candlestick chart with volume and RSI.
        
        Args:
            df: DataFrame with OHLCV data and indicators
            symbol: Stock symbol for title
        
        Returns:
            Plotly figure object
        """
        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True,
            vertical_spacing=0.04, row_heights=[0.6, 0.2, 0.2],
            subplot_titles=[f"{symbol} — Price & MAs", "Volume", "RSI (14)"],
        )
        
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            increasing_line_color="#22c55e", decreasing_line_color="#ef4444",
            name="Price"), row=1, col=1)
        
        # Moving Averages and Bollinger Bands
        for col, colour, dash in [("SMA_20", "#f59e0b", "solid"),
                                  ("SMA_50", "#3b82f6", "solid"),
                                  ("BB_Up", "#6b7280", "dash"),
                                  ("BB_Lo", "#6b7280", "dash")]:
            if col in df:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df[col],
                    line=dict(color=colour, width=1, dash=dash),
                    name=col, opacity=0.8), row=1, col=1)
        
        # Volume bars (colored by price direction)
        vol_colors = ["#ef4444" if o > c else "#22c55e"
                      for o, c in zip(df["Open"], df["Close"])]
        fig.add_trace(go.Bar(
            x=df.index, y=df["Volume"],
            marker_color=vol_colors, name="Volume", opacity=0.7), row=2, col=1)
        
        # RSI
        if "RSI" in df:
            fig.add_trace(go.Scatter(
                x=df.index, y=df["RSI"],
                line=dict(color="#a78bfa", width=1.5), name="RSI"), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#ef4444",
                          line_width=1, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#22c55e",
                          line_width=1, row=3, col=1)
        
        fig.update_layout(
            template="plotly_dark", height=780,
            paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1421",
            font=dict(color="#94a3b8"), showlegend=True,
            legend=dict(orientation="h", y=1.02, x=0),
            xaxis_rangeslider_visible=False,
        )
        return fig

    @staticmethod
    def indicator_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
        """
        Create technical indicator chart with Bollinger Bands and MACD.
        
        Args:
            df: DataFrame with OHLCV data and indicators
            symbol: Stock symbol for title
        
        Returns:
            Plotly figure object
        """
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.08, row_heights=[0.55, 0.45],
            subplot_titles=[f"{symbol} — Bollinger Bands", "MACD"],
        )
        
        # Bollinger Bands
        for col, colour, dash in [("BB_Up", "#6b7280", "dash"),
                                  ("BB_Lo", "#6b7280", "dash"),
                                  ("BB_Mid", "#f59e0b", "solid"),
                                  ("Close", "#f1f5f9", "solid")]:
            if col in df:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df[col],
                    line=dict(color=colour, width=1, dash=dash),
                    name=col), row=1, col=1)
        
        # MACD
        if "MACD" in df:
            fig.add_trace(go.Scatter(
                x=df.index, y=df["MACD"],
                line=dict(color="#3b82f6", width=1.5), name="MACD"), row=2, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=df["MACD_Signal"],
                line=dict(color="#ef4444", width=1.5), name="Signal"), row=2, col=1)
            
            hist_colors = ["#22c55e" if v >= 0 else "#ef4444"
                           for v in df["MACD_Histogram"]]
            fig.add_trace(go.Bar(
                x=df.index, y=df["MACD_Histogram"],
                marker_color=hist_colors, name="Histogram", opacity=0.7), row=2, col=1)
        
        fig.update_layout(
            template="plotly_dark", height=580,
            paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1421",
            font=dict(color="#94a3b8"),
        )
        return fig

    @staticmethod
    def sector_heatmap(perf: Dict[str, float]) -> go.Figure:
        """
        Create sector performance heatmap bar chart.
        
        Args:
            perf: Dictionary with sector names and performance percentages
        
        Returns:
            Plotly figure object
        """
        if not perf:
            return go.Figure()
        
        sectors = list(perf.keys())
        values = list(perf.values())
        colors = ["#22c55e" if v >= 0 else "#ef4444" for v in values]
        
        fig = go.Figure(go.Bar(
            x=sectors, y=values,
            marker_color=colors,
            text=[f"{v:+.2f}%" for v in values],
            textposition="outside",
        ))
        
        fig.update_layout(
            title="Sector Performance", template="plotly_dark",
            height=380, paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1421",
            font=dict(color="#94a3b8"),
            yaxis_title="% Change",
            margin=dict(t=40, b=20),
        )
        return fig


# ── Quick Test / Example Usage ─────────────────────────────────────────────────
if __name__ == "__main__":
    analyzer = IndianMarketAnalyzer()
    
    print("\n" + "="*80)
    print(" INDIAN MARKET ANALYZER - Test Run")
    print("="*80)
    
    # Test market summary
    print("\n📊 MARKET SUMMARY:")
    summary = analyzer.get_market_summary()
    for idx, data in summary.items():
        print(f"  {idx}: ₹{data['value']:,} ({data['pct']:+.2f}%)")
    
    # Test movers
    print("\n🚀 TOP GAINERS:")
    movers = analyzer.get_movers()
    for g in movers.get("gainers", [])[:5]:
        print(f"  {g['symbol']}: ₹{g['price']:,} (+{g['change']:.2f}%)")
    
    print("\n📉 TOP LOSERS:")
    for l in movers.get("losers", [])[:5]:
        print(f"  {l['symbol']}: ₹{l['price']:,} ({l['change']:.2f}%)")
    
    # Test company info
    print("\n🏢 COMPANY INFO (RELIANCE):")
    info = analyzer.get_company_info("RELIANCE.NS")
    print(f"  Name: {info.get('name', 'N/A')}")
    print(f"  Sector: {info.get('sector', 'N/A')}")
    print(f"  Market Cap: {info.get('market_cap', 'N/A')}")
    print(f"  P/E Ratio: {info.get('pe_ratio', 'N/A')}")
    
    print("\n Test completed successfully!")