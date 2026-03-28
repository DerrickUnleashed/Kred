"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          KRED AI — Indian Stock Market Intelligence Platform                ║
║          Market Analyzer + AI Analytics + Streamlit Dashboard               ║
╚══════════════════════════════════════════════════════════════════════════════╝

SETUP:
    pip install streamlit yfinance pandas numpy plotly langchain-groq python-dotenv

RUN:
    streamlit run indian_market_platform.py

ENV (create .env file with):
    GROQ_API_KEY=gsk_your_actual_api_key_here
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import os
import warnings
import threading
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KRED AI — Indian Market Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base dark theme ────────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1421 50%, #0a0e1a 100%);
    color: #e0e6f0;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1421 0%, #111827 100%);
    border-right: 1px solid #1e293b;
}

/* ── Metric cards ───────────────────────────────────────────────────────── */
.metric-card {
    background: linear-gradient(135deg, #111827, #1e293b);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 6px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(59,130,246,0.15);
}
.metric-label {
    font-size: 11px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.metric-value {
    font-size: 22px;
    font-weight: 700;
    color: #f1f5f9;
}
.metric-change-positive { color: #22c55e; font-size: 14px; font-weight: 600; }
.metric-change-negative { color: #ef4444; font-size: 14px; font-weight: 600; }
.metric-change-neutral  { color: #94a3b8; font-size: 14px; font-weight: 600; }

/* ── Section headers ────────────────────────────────────────────────────── */
.section-header {
    font-size: 18px;
    font-weight: 700;
    color: #60a5fa;
    border-left: 3px solid #3b82f6;
    padding-left: 10px;
    margin: 20px 0 12px;
}

/* ── Gainers / Losers table ─────────────────────────────────────────────── */
.stock-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 4px 0;
    font-size: 13px;
}
.stock-symbol { font-weight: 700; color: #93c5fd; min-width: 80px; }
.stock-name   { color: #94a3b8; flex: 1; margin: 0 10px; }
.stock-price  { color: #f1f5f9; font-weight: 600; min-width: 70px; text-align: right; }

/* ── AI response box ────────────────────────────────────────────────────── */
.ai-response {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border: 1px solid #1e3a5f;
    border-left: 3px solid #3b82f6;
    border-radius: 10px;
    padding: 18px 22px;
    margin: 10px 0;
    line-height: 1.7;
    font-size: 14px;
}

/* ── Chat bubbles ───────────────────────────────────────────────────────── */
.chat-user {
    background: linear-gradient(135deg, #1e3a5f, #1e40af);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    margin: 8px 0 8px 60px;
    font-size: 14px;
}
.chat-ai {
    background: linear-gradient(135deg, #111827, #1e293b);
    border: 1px solid #1e293b;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 16px;
    margin: 8px 60px 8px 0;
    font-size: 14px;
}

/* ── Education card ─────────────────────────────────────────────────────── */
.edu-card {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px;
    margin: 8px 0;
}
.edu-card h4 { color: #60a5fa; margin-bottom: 8px; }

/* ── Status badge ───────────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.badge-green  { background: #052e16; color: #22c55e; border: 1px solid #166534; }
.badge-red    { background: #1f0e0e; color: #ef4444; border: 1px solid #7f1d1d; }
.badge-blue   { background: #0c1a3a; color: #60a5fa; border: 1px solid #1e3a5f; }
.badge-yellow { background: #1f1a00; color: #fbbf24; border: 1px solid #78350f; }

/* ── Sticker for risk levels ────────────────────────────────────────────── */
.risk-low    { color: #22c55e; }
.risk-medium { color: #fbbf24; }
.risk-high   { color: #ef4444; }

/* ── Tab styling ────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1421;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #6b7280;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
}
.stTabs [aria-selected="true"] {
    background: #1e3a5f !important;
    color: #60a5fa !important;
}

/* ── Input fields ───────────────────────────────────────────────────────── */
.stTextInput>div>div>input,
.stSelectbox>div>div>div,
.stTextArea>div>div>textarea {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 1 — MARKET ANALYZER ENGINE
# ═════════════════════════════════════════════════════════════════════════════
class IndianMarketAnalyzer:
    """Fetches real-time Yahoo Finance data and computes technical indicators."""

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

    ALL_TICKERS: List[str] = [
        "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
        "HINDUNILVR.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","ITC.NS",
        "LT.NS","AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS",
        "WIPRO.NS","HCLTECH.NS","TATAMOTORS.NS","NESTLEIND.NS","NTPC.NS",
        "ONGC.NS","TATASTEEL.NS","BAJAJ-AUTO.NS","M&M.NS","CIPLA.NS",
        "DRREDDY.NS","TECHM.NS","POWERGRID.NS","ADANIPORTS.NS","JSWSTEEL.NS",
    ]

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_ts: Dict[str, datetime] = {}
        self._lock = threading.Lock()

    # ── helpers ──────────────────────────────────────────────────────────────
    def _is_stale(self, key: str, ttl_s: int = 300) -> bool:
        ts = self._cache_ts.get(key)
        return ts is None or (datetime.now() - ts).total_seconds() > ttl_s

    def _set_cache(self, key: str, value: Any):
        with self._lock:
            self._cache[key] = value
            self._cache_ts[key] = datetime.now()

    def _get_cache(self, key: str) -> Any:
        return self._cache.get(key)

    # ── data fetching ─────────────────────────────────────────────────────────
    def fetch_historical_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        key = f"hist_{symbol}_{period}"
        if not self._is_stale(key, 600):
            return self._get_cache(key)
        try:
            tk = yf.Ticker(symbol)
            df = tk.history(period=period)
            if df.empty:
                return pd.DataFrame()
            df.index = pd.to_datetime(df.index).tz_localize(None)
            # normalise columns
            if len(df.columns) >= 6:
                df = df.iloc[:, :6]
                df.columns = ["Open","High","Low","Close","Volume","Dividends"]
            self._set_cache(key, df)
            return df
        except Exception:
            return pd.DataFrame()

    def get_company_info(self, symbol: str) -> Dict:
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
        key = "market_summary"
        if not self._is_stale(key, 120):
            return self._get_cache(key)
        summary = {}
        for name, symbol in self.INDICES.items():
            try:
                tk = yf.Ticker(symbol)
                hist = tk.history(period="2d")
                if len(hist) >= 2:
                    prev  = hist["Close"].iloc[-2]
                    curr  = hist["Close"].iloc[-1]
                    chg   = curr - prev
                    chg_p = (chg / prev) * 100
                    summary[name] = {
                        "value":  round(curr, 2),
                        "change": round(chg, 2),
                        "pct":    round(chg_p, 2),
                    }
                elif len(hist) == 1:
                    curr = hist["Close"].iloc[-1]
                    summary[name] = {"value": round(curr,2), "change": 0.0, "pct": 0.0}
            except Exception:
                continue
        self._set_cache(key, summary)
        return summary

    def get_movers(self) -> Dict[str, List[Dict]]:
        """Return top gainers and losers from ALL_TICKERS."""
        key = "movers"
        if not self._is_stale(key, 300):
            return self._get_cache(key)
        movers = []
        for ticker in self.ALL_TICKERS:
            try:
                tk   = yf.Ticker(ticker)
                hist = tk.history(period="2d")
                if len(hist) < 2:
                    continue
                prev  = hist["Close"].iloc[-2]
                curr  = hist["Close"].iloc[-1]
                pct   = ((curr - prev) / prev) * 100
                movers.append({
                    "symbol": ticker.replace(".NS",""),
                    "name":   tk.info.get("shortName", ticker)[:22],
                    "price":  round(curr, 2),
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

    # ── technical indicators ──────────────────────────────────────────────────
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 20:
            return df
        df = df.copy()

        # Moving averages
        df["SMA_20"]  = df["Close"].rolling(20).mean()
        df["SMA_50"]  = df["Close"].rolling(50).mean()
        df["SMA_200"] = df["Close"].rolling(200).mean()
        df["EMA_12"]  = df["Close"].ewm(span=12, adjust=False).mean()
        df["EMA_26"]  = df["Close"].ewm(span=26, adjust=False).mean()

        # MACD
        df["MACD"]           = df["EMA_12"] - df["EMA_26"]
        df["MACD_Signal"]    = df["MACD"].ewm(span=9, adjust=False).mean()
        df["MACD_Histogram"] = df["MACD"] - df["MACD_Signal"]

        # RSI
        delta = df["Close"].diff()
        gain  = delta.where(delta > 0, 0).rolling(14).mean()
        loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs    = gain / loss.replace(0, 1e-9)
        df["RSI"] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        bb_mid       = df["Close"].rolling(20).mean()
        bb_std       = df["Close"].rolling(20).std()
        df["BB_Mid"] = bb_mid
        df["BB_Up"]  = bb_mid + 2 * bb_std
        df["BB_Lo"]  = bb_mid - 2 * bb_std

        # Volatility & volume
        df["Daily_Return"]  = df["Close"].pct_change()
        df["Volatility"]    = df["Daily_Return"].rolling(20).std() * np.sqrt(252) * 100
        df["Volume_SMA"]    = df["Volume"].rolling(20).mean()
        df["Volume_Ratio"]  = df["Volume"] / df["Volume_SMA"].replace(0, 1)

        # ATR
        hl  = df["High"] - df["Low"]
        hcp = (df["High"] - df["Close"].shift()).abs()
        lcp = (df["Low"]  - df["Close"].shift()).abs()
        df["ATR"] = pd.concat([hl, hcp, lcp], axis=1).max(axis=1).rolling(14).mean()

        return df

    # ── charts ────────────────────────────────────────────────────────────────
    @staticmethod
    def candlestick_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
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
        # MAs
        for col, colour, dash in [("SMA_20","#f59e0b","solid"),
                                    ("SMA_50","#3b82f6","solid"),
                                    ("BB_Up", "#6b7280","dash"),
                                    ("BB_Lo", "#6b7280","dash")]:
            if col in df:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df[col],
                    line=dict(color=colour, width=1, dash=dash),
                    name=col, opacity=0.8), row=1, col=1)
        # Volume
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
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.08, row_heights=[0.55, 0.45],
            subplot_titles=[f"{symbol} — Bollinger Bands", "MACD"],
        )
        # Bollinger
        for col, colour, dash in [("BB_Up","#6b7280","dash"),
                                    ("BB_Lo","#6b7280","dash"),
                                    ("BB_Mid","#f59e0b","solid"),
                                    ("Close","#f1f5f9","solid")]:
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
        if not perf:
            return go.Figure()
        sectors = list(perf.keys())
        values  = list(perf.values())
        colors  = ["#22c55e" if v >= 0 else "#ef4444" for v in values]
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


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 2 — AI ANALYTICS ENGINE (Groq / LangChain) - API Key from .env only
# ═════════════════════════════════════════════════════════════════════════════
def _init_groq_llm():
    """Initialize Groq LLM using API key from .env file only."""
    try:
        from langchain_groq import ChatGroq
        
        # Get API key ONLY from environment (.env file)
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            return None, "🔑 GROQ_API_KEY not found in .env file. Please add GROQ_API_KEY=gsk_your_key to .env"
        
        if not api_key.startswith("gsk_"):
            return None, "❌ Invalid API key format. Key should start with 'gsk_'"
        
        llm = ChatGroq(
            groq_api_key=api_key,
            model_name="groq/compound-mini",
            temperature=0.4,
            max_tokens=1200,
        )
        return llm, None
    except ImportError:
        return None, "📦 `langchain-groq` not installed. Run: pip install langchain-groq"
    except Exception as e:
        return None, f"❌ Groq init failed: {e}"


_SYSTEM_PROMPT = """You are KRED AI, a friendly Indian stock market expert who explains finance 
in super simple language that even a complete beginner can understand.

CORE RULES:
1. Always use simple analogies — compare market trends to WEATHER (sunny/stormy),
   RSI to a CAR SPEEDOMETER (going too fast = overbought), volatility to ROAD CONDITIONS 
   (bumpy road = high risk), MACD to a TRAIN (momentum/direction).
2. Use ₹ for prices. Reference Indian context (NSE, BSE, SEBI, FD rates, SIP).
3. Never recommend "buy/sell" — say "worth watching", "looks interesting", "be cautious".
4. Tailor advice to the user's risk profile: conservative (FD mindset), moderate, aggressive.
5. End every market insight with one actionable suggestion.
6. Keep responses under 250 words unless asked for detail.
7. Use emojis sparingly to highlight key points. 📊  ⚠️

Risk profiles:
- Conservative: prioritise capital safety, dividends, blue chips
- Moderate: balanced growth + safety, diversified sectors  
- Aggressive: growth stocks, momentum plays, higher tolerance for dips
"""


def ai_market_insight(market_data: str, risk_profile: str) -> str:
    llm, err = _init_groq_llm()
    if err:
        return err
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        prompt = (
            f"User's risk profile: {risk_profile}\n\n"
            f"Current market snapshot:\n{market_data}\n\n"
            "Give a clear, beginner-friendly market overview using simple analogies. "
            "Highlight 2-3 sectors worth watching and end with one actionable tip."
        )
        response = llm.invoke([SystemMessage(content=_SYSTEM_PROMPT),
                               HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"❌ AI error: {e}"


def ai_stock_analysis(symbol: str, indicators: Dict, company_info: Dict,
                      risk_profile: str) -> str:
    llm, err = _init_groq_llm()
    if err:
        return err
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        prompt = (
            f"Analyse {symbol} for a {risk_profile} investor.\n\n"
            f"Company: {company_info.get('name','N/A')} | "
            f"Sector: {company_info.get('sector','N/A')}\n"
            f"PE: {company_info.get('pe_ratio','N/A')} | "
            f"Beta: {company_info.get('beta','N/A')}\n\n"
            f"Technical indicators: {indicators}\n\n"
            "Explain what these numbers mean in plain language using everyday analogies. "
            "Point out the most important signal and what it suggests."
        )
        response = llm.invoke([SystemMessage(content=_SYSTEM_PROMPT),
                               HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"❌ AI error: {e}"


def ai_chat(history: List[Dict], user_msg: str, context: str,
            risk_profile: str) -> str:
    llm, err = _init_groq_llm()
    if err:
        return err
    try:
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
        msgs = [SystemMessage(
            content=_SYSTEM_PROMPT +
            f"\n\nCurrent market context:\n{context}\n"
            f"User risk profile: {risk_profile}"
        )]
        for h in history[-6:]:          # keep last 6 turns for context
            if h["role"] == "user":
                msgs.append(HumanMessage(content=h["content"]))
            else:
                msgs.append(AIMessage(content=h["content"]))
        msgs.append(HumanMessage(content=user_msg))
        response = llm.invoke(msgs)
        return response.content
    except Exception as e:
        return f"❌ AI error: {e}"


# ═════════════════════════════════════════════════════════════════════════════
# SHARED STATE HELPERS
# ═════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def get_analyzer() -> IndianMarketAnalyzer:
    return IndianMarketAnalyzer()


def init_session_state():
    defaults = {
        "risk_profile":  "Moderate",
        "username":      "Investor",
        "chat_history":  [],
        "last_refresh":  None,
        "market_ctx":    "",
        "selected_stock":"RELIANCE.NS",
        "auto_refresh":  False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def fmt_rupee(val) -> str:
    if val is None or val == "N/A":
        return "N/A"
    try:
        v = float(val)
        if v >= 1e12:
            return f"₹{v/1e12:.2f}T"
        if v >= 1e9:
            return f"₹{v/1e9:.2f}B"
        if v >= 1e7:
            return f"₹{v/1e7:.2f}Cr"
        if v >= 1e5:
            return f"₹{v/1e5:.2f}L"
        return f"₹{v:,.2f}"
    except Exception:
        return str(val)


# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:12px 0 20px;">
          <div style="font-size:32px;">📈</div>
          <div style="font-size:20px;font-weight:800;color:#60a5fa;letter-spacing:1px;">
            KRED AI</div>
          <div style="font-size:11px;color:#6b7280;margin-top:2px;">
            Indian Market Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 👤 Your Profile")
        st.session_state["username"] = st.text_input(
            "Name", value=st.session_state["username"], key="sb_name")
        st.session_state["risk_profile"] = st.selectbox(
            "Risk Appetite", ["Conservative", "Moderate", "Aggressive"],
            index=["Conservative","Moderate","Aggressive"].index(
                st.session_state["risk_profile"]),
            key="sb_risk")

        st.markdown("---")
        
        # API Key Status (Read-only from .env)
        api_key = os.getenv("GROQ_API_KEY")
        if api_key and api_key.startswith("gsk_"):
            st.markdown('<span class="badge badge-green">✓ AI Connected (from .env)</span>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-red">✗ AI Offline — Check .env file</span>',
                        unsafe_allow_html=True)
            st.markdown("""
            <div style="background:#1f0e0e; border:1px solid #7f1d1d; border-radius:8px; padding:10px; margin-top:8px;">
              <small style="color:#ef4444;">⚠️ Add GROQ_API_KEY=gsk_your_key to .env file</small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        st.session_state["auto_refresh"] = st.toggle(
            "Auto-refresh (5 min)", value=st.session_state["auto_refresh"])

        if st.button("🔄 Refresh Now", use_container_width=True):
            get_analyzer()._cache.clear()
            st.rerun()

        st.markdown("---")
        # Risk profile guide
        risk = st.session_state["risk_profile"]
        colors = {"Conservative":"#22c55e","Moderate":"#fbbf24","Aggressive":"#ef4444"}
        descs = {
            "Conservative": "Capital safety first. Think FD + blue-chips.",
            "Moderate":     "Balanced growth & safety. Diversified.",
            "Aggressive":   "High growth potential. Comfortable with dips.",
        }
        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e293b;border-radius:8px;padding:12px;">
          <div style="font-size:11px;color:#6b7280;margin-bottom:4px;">YOUR RISK PROFILE</div>
          <div style="color:{colors[risk]};font-weight:700;font-size:15px;">{risk}</div>
          <div style="color:#94a3b8;font-size:12px;margin-top:4px;">{descs[risk]}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:11px;color:#4b5563;text-align:center;">
          Last updated: {datetime.now().strftime('%d %b %Y  %H:%M')}<br>
          Data: Yahoo Finance · NSE/BSE
        </div>
        """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — MARKET DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
def tab_market_dashboard(analyzer: IndianMarketAnalyzer):
    st.markdown(f"""
    <div style="margin-bottom:20px;">
      <h2 style="color:#f1f5f9;margin:0;">
        Good {'morning' if datetime.now().hour<12 else 'afternoon'}, 
        {st.session_state['username']}! 👋</h2>
      <p style="color:#6b7280;margin:4px 0 0;">
        Indian Stock Market · {datetime.now().strftime('%A, %d %B %Y')}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Market indices ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🏛️ Market Indices</div>',
                unsafe_allow_html=True)
    with st.spinner("Fetching live index data…"):
        summary = analyzer.get_market_summary()

    if summary:
        cols = st.columns(min(4, len(summary)))
        for i, (name, d) in enumerate(summary.items()):
            pct   = d.get("pct", 0)
            arrow = "▲" if pct >= 0 else "▼"
            cls   = "metric-change-positive" if pct >= 0 else "metric-change-negative"
            with cols[i % 4]:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="metric-label">{name}</div>
                  <div class="metric-value">
                    {"₹{:,.2f}".format(d['value'])}</div>
                  <div class="{cls}">{arrow} {abs(pct):.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Could not fetch index data. Markets may be closed.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gainers / Losers + Sector chart ───────────────────────────────────────
    col_l, col_r = st.columns([1, 1])

    with col_l:
        with st.spinner("Loading movers…"):
            movers = analyzer.get_movers()
        gainers = movers.get("gainers", [])
        losers  = movers.get("losers", [])

        st.markdown('<div class="section-header">🚀 Top Gainers</div>',
                    unsafe_allow_html=True)
        for g in gainers[:6]:
            st.markdown(f"""
            <div class="stock-row">
              <span class="stock-symbol">{g['symbol']}</span>
              <span class="stock-name">{g['name']}</span>
              <span class="stock-price">₹{g['price']:,.2f}</span>
              <span class="metric-change-positive">▲ {g['change']:.2f}%</span>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-header" style="margin-top:20px;">📉 Top Losers</div>',
                    unsafe_allow_html=True)
        for lo in losers[:6]:
            st.markdown(f"""
            <div class="stock-row">
              <span class="stock-symbol">{lo['symbol']}</span>
              <span class="stock-name">{lo['name']}</span>
              <span class="stock-price">₹{lo['price']:,.2f}</span>
              <span class="metric-change-negative">▼ {abs(lo['change']):.2f}%</span>
            </div>""", unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-header">🏭 Sector Performance</div>',
                    unsafe_allow_html=True)
        with st.spinner("Loading sector data…"):
            sectors = analyzer.get_sector_performance()
        if sectors:
            st.plotly_chart(
                IndianMarketAnalyzer.sector_heatmap(sectors),
                use_container_width=True,
            )
        else:
            st.info("Sector data unavailable.")

    # ── Market context string for AI ──────────────────────────────────────────
    ctx_parts = []
    if summary:
        ctx_parts.append("INDICES: " + "; ".join(
            f"{k}: {v['value']} ({v['pct']:+.2f}%)" for k, v in summary.items()))
    if sectors:
        ctx_parts.append("SECTORS: " + "; ".join(
            f"{k}: {v:+.2f}%" for k, v in sectors.items()))
    st.session_state["market_ctx"] = "\n".join(ctx_parts)

    # ── Auto-refresh countdown ────────────────────────────────────────────────
    if st.session_state["auto_refresh"]:
        st.markdown("""
        <div style="text-align:center;color:#4b5563;font-size:12px;margin-top:20px;">
          ⏱ Auto-refresh active · Next refresh in 5 minutes
        </div>""", unsafe_allow_html=True)
        time.sleep(300)
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — STOCK ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
def tab_stock_analysis(analyzer: IndianMarketAnalyzer):
    st.markdown('<div class="section-header">🔍 Deep Stock Analysis</div>',
                unsafe_allow_html=True)

    # Stock picker
    col_a, col_b, col_c = st.columns([3, 2, 1])
    with col_a:
        all_opts = sorted(set(
            t for lst in analyzer.SECTOR_STOCKS.values() for t in lst))
        selected = st.selectbox(
            "Select Stock", all_opts,
            index=all_opts.index("RELIANCE.NS") if "RELIANCE.NS" in all_opts else 0,
            format_func=lambda x: x.replace(".NS",""))
        st.session_state["selected_stock"] = selected
    with col_b:
        period = st.selectbox("Period", ["1mo","3mo","6mo","1y","2y"],
                               index=1)
    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)
        go_btn = st.button("📊 Analyse", use_container_width=True)

    if go_btn or True:   # always show on load
        symbol = st.session_state["selected_stock"]
        with st.spinner(f"Fetching data for {symbol.replace('.NS','')}…"):
            df   = analyzer.fetch_historical_data(symbol, period)
            info = analyzer.get_company_info(symbol)

        if df.empty:
            st.error("No data returned. Try a different stock or period.")
            return

        df = IndianMarketAnalyzer.calculate_indicators(df)
        latest = df.iloc[-1]

        # ── Company header ────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#111827,#1e293b);
                    border:1px solid #1e3a5f;border-radius:12px;padding:18px;
                    margin-bottom:20px;">
          <div style="font-size:22px;font-weight:800;color:#f1f5f9;">
            {info.get('name', symbol)}</div>
          <div style="color:#6b7280;font-size:13px;margin-top:4px;">
            {info.get('sector','N/A')} · {info.get('industry','N/A')} · NSE: {symbol.replace('.NS','')}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Key metrics row ───────────────────────────────────────────────────
        km = st.columns(6)
        metrics = [
            ("Current Price",   f"₹{latest['Close']:,.2f}", ""),
            ("Market Cap",      fmt_rupee(info.get('market_cap')), ""),
            ("P/E Ratio",       f"{info.get('pe_ratio','N/A')}", ""),
            ("52W High",        f"₹{info.get('52w_high','N/A')}", ""),
            ("52W Low",         f"₹{info.get('52w_low','N/A')}", ""),
            ("Dividend Yield",  f"{info.get('dividend_yield',0):.2f}%", ""),
        ]
        for col, (label, val, _) in zip(km, metrics):
            col.markdown(f"""
            <div class="metric-card" style="text-align:center;">
              <div class="metric-label">{label}</div>
              <div class="metric-value" style="font-size:16px;">{val}</div>
            </div>""", unsafe_allow_html=True)

        # ── Technical snapshot ────────────────────────────────────────────────
        st.markdown('<div class="section-header">📡 Technical Signals</div>',
                    unsafe_allow_html=True)
        ts = st.columns(5)
        rsi_val = latest.get("RSI", float("nan"))
        rsi_lbl = ("🔥 Overbought" if rsi_val > 70
                   else "💚 Oversold" if rsi_val < 30 else "⚖️ Neutral")
        vol_r = latest.get("Volume_Ratio", float("nan"))
        vol_lbl = "🔊 High" if vol_r > 1.5 else ("🔇 Low" if vol_r < 0.7 else "Normal")
        macd   = latest.get("MACD", float("nan"))
        signal = latest.get("MACD_Signal", float("nan"))
        macd_lbl = "📈 Bullish" if macd > signal else "📉 Bearish"
        vola   = latest.get("Volatility", float("nan"))
        vola_lbl = ("🌪 High" if vola > 30
                    else "🌤 Moderate" if vola > 15 else "😌 Low")

        for col, (label, val) in zip(ts, [
            ("RSI (14)",        f"{rsi_val:.1f}  {rsi_lbl}"),
            ("MACD",            f"{macd:.2f}  {macd_lbl}"),
            ("Volatility",      f"{vola:.1f}%  {vola_lbl}"),
            ("Volume Ratio",    f"{vol_r:.2f}x  {vol_lbl}"),
            ("ATR (14)",        f"₹{latest.get('ATR', 0):.2f}"),
        ]):
            col.markdown(f"""
            <div class="metric-card" style="text-align:center;">
              <div class="metric-label">{label}</div>
              <div style="font-size:13px;color:#f1f5f9;font-weight:600;
                          margin-top:4px;">{val}</div>
            </div>""", unsafe_allow_html=True)

        # ── Charts ────────────────────────────────────────────────────────────
        chart_tab1, chart_tab2 = st.tabs(["📊 Price + RSI", "📉 MACD + Bollinger"])
        with chart_tab1:
            st.plotly_chart(
                IndianMarketAnalyzer.candlestick_chart(df, symbol.replace(".NS","")),
                use_container_width=True)
        with chart_tab2:
            st.plotly_chart(
                IndianMarketAnalyzer.indicator_chart(df, symbol.replace(".NS","")),
                use_container_width=True)

        # ── AI analysis button ────────────────────────────────────────────────
        st.markdown('<div class="section-header">🤖 AI Interpretation</div>',
                    unsafe_allow_html=True)
        if st.button("✨ Get AI Analysis", use_container_width=False):
            indicators_dict = {
                "RSI": round(rsi_val, 1),
                "MACD": round(macd, 3),
                "Volatility_%": round(vola, 1),
                "Volume_Ratio": round(vol_r, 2),
                "Price": round(float(latest["Close"]), 2),
                "SMA_20": round(float(latest.get("SMA_20",0)), 2),
                "SMA_50": round(float(latest.get("SMA_50",0) or 0), 2),
            }
            with st.spinner("KRED AI is analysing…"):
                analysis = ai_stock_analysis(
                    symbol.replace(".NS",""),
                    indicators_dict, info,
                    st.session_state["risk_profile"])
            st.markdown(f'<div class="ai-response">{analysis}</div>',
                        unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI INSIGHTS
# ═════════════════════════════════════════════════════════════════════════════
def tab_ai_insights(analyzer: IndianMarketAnalyzer):
    st.markdown('<div class="section-header">🧠 AI Market Intelligence</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        risk  = st.session_state["risk_profile"]
        ctx   = st.session_state.get("market_ctx", "")

        if st.button("🚀 Generate Market Insight", use_container_width=True):
            if not ctx:
                with st.spinner("Fetching market data first…"):
                    summary = analyzer.get_market_summary()
                    sectors = analyzer.get_sector_performance()
                    ctx  = ("INDICES: " + "; ".join(
                        f"{k}: {v['value']} ({v['pct']:+.2f}%)"
                        for k,v in summary.items()))
                    ctx += "\nSECTORS: " + "; ".join(
                        f"{k}: {v:+.2f}%" for k,v in sectors.items())
                    st.session_state["market_ctx"] = ctx

            with st.spinner("KRED AI is thinking…"):
                insight = ai_market_insight(ctx, risk)
            st.markdown(f'<div class="ai-response">{insight}</div>',
                        unsafe_allow_html=True)

        # ── Quick analysis tiles ───────────────────────────────────────────────
        st.markdown('<div class="section-header" style="margin-top:24px;">⚡ Quick Sector AI</div>',
                    unsafe_allow_html=True)
        sectors_list = list(analyzer.SECTOR_STOCKS.keys())
        sel_sector = st.selectbox("Choose sector to analyse", sectors_list)
        if st.button(f"Analyse {sel_sector} Sector"):
            prompt = (
                f"Give a quick AI take on the {sel_sector} sector of India's stock market "
                f"for a {risk} investor. What are the key themes, risks, and one stock "
                f"to research (NOT a buy recommendation)? Use simple language."
            )
            with st.spinner(f"Analysing {sel_sector}…"):
                sector_ai = ai_chat([], prompt, st.session_state.get("market_ctx",""),
                                    risk)
            st.markdown(f'<div class="ai-response">{sector_ai}</div>',
                        unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="edu-card">
          <h4> How to use AI Insights</h4>
          <p style="color:#94a3b8;font-size:13px;">
            1. Click <b>Generate Market Insight</b> for a daily market overview.<br><br>
            2. Use <b>Quick Sector AI</b> to deep-dive any sector.<br><br>
            3. All insights are tailored to your <b>risk profile</b> set in the sidebar.<br><br>
            ⚠️ <i>This is educational content, not financial advice. Always DYOR.</i>
          </p>
        </div>
        """, unsafe_allow_html=True)

        # Live risk tip
        tips = {
            "Conservative": [
                "💎 HDFC Bank, TCS, and Infosys are classic blue-chips for low-risk portfolios.",
                "📊 Focus on companies with consistent dividend history.",
                "🛡 Sector diversification (IT + FMCG + Banking) reduces concentration risk.",
            ],
            "Moderate": [
                "⚖️ Combine blue-chips with a few mid-cap growth stories.",
                "📈 SIP into NIFTY 50 index fund = instant diversification.",
                "🔄 Rebalance portfolio every 6 months.",
            ],
            "Aggressive": [
                "🔥 Momentum stocks in IT, Pharma, or EV space for high beta.",
                "⚡ Watch for earnings beats — they move stocks 5-15% overnight.",
                "🎯 Risk only what you can afford to keep locked for 3+ years.",
            ],
        }
        import random
        tip = random.choice(tips[st.session_state["risk_profile"]])
        st.markdown(f"""
        <div class="edu-card" style="margin-top:16px;">
          <h4>🎯 Tip for You ({st.session_state['risk_profile']})</h4>
          <p style="color:#94a3b8;font-size:13px;">{tip}</p>
        </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — CHATBOT
# ═════════════════════════════════════════════════════════════════════════════
def tab_chatbot():
    st.markdown('<div class="section-header">💬 Chat with KRED AI</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div style="color:#6b7280;font-size:13px;margin-bottom:16px;">
      Ask me anything about Indian stocks, market concepts, or your investment questions.
      I'll explain everything in simple, beginner-friendly language! 🎓
    </div>""", unsafe_allow_html=True)

    # Conversation display
    chat_container = st.container()
    with chat_container:
        if not st.session_state["chat_history"]:
            st.markdown("""
            <div class="chat-ai">
              👋 Namaste! I'm <b>KRED AI</b>, your personal Indian market buddy.<br><br>
              Ask me things like:<br>
              • "What is RSI and why should I care?"<br>
              • "Is HDFC Bank a good stock for beginners?"<br>
              • "Explain MACD like I'm 10 years old"<br>
              • "How do I start investing with ₹5,000?"
            </div>""", unsafe_allow_html=True)
        else:
            for msg in st.session_state["chat_history"]:
                css_class = "chat-user" if msg["role"] == "user" else "chat-ai"
                prefix = "You" if msg["role"] == "user" else "🤖 KRED AI"
                st.markdown(f"""
                <div class="{css_class}">
                  <small style="color:#6b7280;">{prefix}</small><br>
                  {msg['content']}
                </div>""", unsafe_allow_html=True)

    # Suggested questions
    st.markdown("** Quick questions:**")
    q_cols = st.columns(3)
    suggestions = [
        "What is RSI?",
        "Explain MACD simply",
        "What are blue-chip stocks?",
        "How does SIP work?",
        "What is P/E ratio?",
        "What is Nifty 50?",
    ]
    for i, (col, q) in enumerate(zip(q_cols * 2, suggestions)):
        with col:
            if st.button(q, key=f"sug_{i}", use_container_width=True):
                st.session_state["chat_history"].append(
                    {"role": "user", "content": q})
                with st.spinner("Thinking…"):
                    reply = ai_chat(
                        st.session_state["chat_history"][:-1], q,
                        st.session_state.get("market_ctx",""),
                        st.session_state["risk_profile"])
                st.session_state["chat_history"].append(
                    {"role": "assistant", "content": reply})
                st.rerun()

    # Input
    st.markdown("<br>", unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        col_inp, col_btn = st.columns([5, 1])
        with col_inp:
            user_input = st.text_input(
                "Your question", placeholder="Ask KRED AI anything about markets…",
                label_visibility="collapsed")
        with col_btn:
            submit = st.form_submit_button("Send 🚀", use_container_width=True)

    if submit and user_input.strip():
        st.session_state["chat_history"].append(
            {"role": "user", "content": user_input})
        with st.spinner("KRED AI is typing…"):
            reply = ai_chat(
                st.session_state["chat_history"][:-1],
                user_input,
                st.session_state.get("market_ctx",""),
                st.session_state["risk_profile"])
        st.session_state["chat_history"].append(
            {"role": "assistant", "content": reply})
        st.rerun()

    # Clear chat
    if st.session_state["chat_history"]:
        if st.button("🗑 Clear conversation", key="clear_chat"):
            st.session_state["chat_history"] = []
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═════════════════════════════════════════════════════════════════════════════
def main():
    init_session_state()
    render_sidebar()
    analyzer = get_analyzer()

    # ── Header ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:10px 0 24px;">
      <span style="font-size:36px;">📈</span>
      <h1 style="display:inline;font-size:30px;font-weight:800;
                 background:linear-gradient(90deg,#60a5fa,#a78bfa);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 margin-left:10px;">KRED AI — Indian Market Intelligence</h1>
      <div style="color:#4b5563;font-size:12px;margin-top:4px;">
        Powered by Yahoo Finance · NSE · BSE · Groq LLM</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "🏛 Market Dashboard",
        "📊 Stock Analysis",
        "🧠 AI Insights",
        "💬 Chatbot",
    ])

    with tabs[0]:
        tab_market_dashboard(analyzer)
    with tabs[1]:
        tab_stock_analysis(analyzer)
    with tabs[2]:
        tab_ai_insights(analyzer)
    with tabs[3]:
        tab_chatbot()


if __name__ == "__main__":
    main()