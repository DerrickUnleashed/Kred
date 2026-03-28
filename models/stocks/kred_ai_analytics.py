"""
============================================================
  INDIAN MARKET ANALYZER — Complete Stock Analysis Engine
  Replica of Yahoo Finance with India-focused features
============================================================
"""

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time

warnings.filterwarnings("ignore")

class IndianMarketAnalyzer:
    """Complete Indian stock market analysis engine."""
    
    # Indian Market Indices
    INDICES = {
        'NIFTY 50': '^NSEI',
        'BSE SENSEX': '^BSESN',
        'NIFTY BANK': '^NSEBANK',
        'NIFTY IT': '^CNXIT',
        'NIFTY PHARMA': '^CNXPHARMA',
        'NIFTY FMCG': '^CNXFMCG',
        'NIFTY AUTO': '^CNXAUTO',
        'NIFTY METAL': '^CNXMETAL'
    }
    
    # Sector-wise top stocks
    SECTOR_STOCKS = {
        'Banking': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'AXISBANK.NS'],
        'IT': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS'],
        'Pharma': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'BIOCON.NS'],
        'FMCG': ['HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS', 'DABUR.NS'],
        'Auto': ['MARUTI.NS', 'M&M.NS', 'TATAMOTORS.NS', 'BAJAJ-AUTO.NS', 'HEROMOTOCO.NS'],
        'Energy': ['RELIANCE.NS', 'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS', 'TATAPOWER.NS'],
        'Metal': ['TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'VEDL.NS', 'NATIONALUM.NS'],
        'Infra': ['LT.NS', 'ADANIPORTS.NS', 'SIEMENS.NS', 'ABB.NS', 'L&T.NS']
    }
    
    def __init__(self):
        self.cache = {}
        self.last_update = None
        
    def fetch_live_data(self, symbol):
        """Fetch live data for any symbol."""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d", interval="1m")
            if not data.empty:
                latest = data.iloc[-1]
                return {
                    'price': round(latest['Close'], 2),
                    'open': round(latest['Open'], 2),
                    'high': round(latest['High'], 2),
                    'low': round(latest['Low'], 2),
                    'volume': int(latest['Volume']),
                    'timestamp': datetime.now()
                }
            return None
        except:
            return None
    
    def fetch_historical_data(self, symbol, period="1mo"):
        """Fetch historical OHLCV data."""
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
            df.index = pd.to_datetime(df.index)
            return df
        except:
            return pd.DataFrame()
    
    def get_company_info(self, symbol):
        """Get detailed company information."""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'eps': info.get('trailingEps', 'N/A'),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                'avg_volume': info.get('averageVolume', 'N/A'),
                'beta': info.get('beta', 'N/A')
            }
        except:
            return {}
    
    def calculate_indicators(self, df):
        """Calculate all technical indicators."""
        if df.empty:
            return df
            
        df = df.copy()
        
        # Moving Averages
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['SMA_200'] = df['Close'].rolling(200).mean()
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Volatility
        df['Daily_Return'] = df['Close'].pct_change()
        df['Volatility'] = df['Daily_Return'].rolling(20).std() * np.sqrt(252) * 100
        
        # Volume Indicators
        df['Volume_SMA'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # ATR
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(14).mean()
        
        return df
    
    def get_top_gainers(self):
        """Get top gainers from NIFTY 50."""
        gainers = []
        tickers = self.SECTOR_STOCKS['Banking'][:5] + self.SECTOR_STOCKS['IT'][:5] + self.SECTOR_STOCKS['FMCG'][:5]
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev_close = stock.info.get('previousClose', current)
                    change_pct = ((current - prev_close) / prev_close) * 100
                    
                    gainers.append({
                        'symbol': ticker.replace('.NS', ''),
                        'name': stock.info.get('longName', ticker)[:25],
                        'price': round(current, 2),
                        'change': round(change_pct, 2),
                        'volume': int(hist['Volume'].iloc[-1])
                    })
            except:
                continue
        
        return sorted(gainers, key=lambda x: x['change'], reverse=True)[:10]
    
    def get_top_losers(self):
        """Get top losers from NIFTY 50."""
        losers = []
        tickers = self.SECTOR_STOCKS['Banking'][:5] + self.SECTOR_STOCKS['IT'][:5] + self.SECTOR_STOCKS['FMCG'][:5]
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev_close = stock.info.get('previousClose', current)
                    change_pct = ((current - prev_close) / prev_close) * 100
                    
                    losers.append({
                        'symbol': ticker.replace('.NS', ''),
                        'name': stock.info.get('longName', ticker)[:25],
                        'price': round(current, 2),
                        'change': round(change_pct, 2),
                        'volume': int(hist['Volume'].iloc[-1])
                    })
            except:
                continue
        
        return sorted(losers, key=lambda x: x['change'])[:10]
    
    def get_market_summary(self):
        """Get overall market summary."""
        summary = {}
        
        for name, symbol in self.INDICES.items():
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev_close = stock.info.get('previousClose', current)
                    change_pct = ((current - prev_close) / prev_close) * 100
                    
                    summary[name] = {
                        'value': round(current, 2),
                        'change': round(change_pct, 2)
                    }
            except:
                continue
        
        return summary
    
    def get_sector_performance(self):
        """Get sector-wise performance."""
        sector_performance = {}
        
        for sector, stocks in self.SECTOR_STOCKS.items():
            sector_changes = []
            for ticker in stocks[:3]:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="1d")
                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        prev_close = stock.info.get('previousClose', current)
                        change_pct = ((current - prev_close) / prev_close) * 100
                        sector_changes.append(change_pct)
                except:
                    continue
            
            if sector_changes:
                sector_performance[sector] = round(sum(sector_changes) / len(sector_changes), 2)
        
        return sector_performance
    
    def create_candlestick_chart(self, df, symbol):
        """Create interactive candlestick chart."""
        fig = make_subplots(rows=3, cols=1, 
                           shared_xaxes=True,
                           vertical_spacing=0.05,
                           row_heights=[0.6, 0.2, 0.2])
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(x=df.index,
                                     open=df['Open'],
                                     high=df['High'],
                                     low=df['Low'],
                                     close=df['Close'],
                                     name='Price'),
                     row=1, col=1)
        
        # Add moving averages
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'],
                                line=dict(color='orange', width=1),
                                name='SMA 20'),
                     row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'],
                                line=dict(color='blue', width=1),
                                name='SMA 50'),
                     row=1, col=1)
        
        # Volume chart
        colors = ['red' if row['Open'] > row['Close'] else 'green' for _, row in df.iterrows()]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors),
                     row=2, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'],
                                line=dict(color='purple', width=1),
                                name='RSI'),
                     row=3, col=1)
        
        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        fig.update_layout(title=f'{symbol} - Price Analysis',
                         xaxis_title='Date',
                         yaxis_title='Price (₹)',
                         template='plotly_dark',
                         height=800)
        
        fig.update_xaxes(rangeslider_visible=False)
        
        return fig
    
    def create_indicator_chart(self, df, symbol):
        """Create MACD and Bollinger Bands chart."""
        fig = make_subplots(rows=2, cols=1,
                           shared_xaxes=True,
                           vertical_spacing=0.1,
                           row_heights=[0.5, 0.5])
        
        # Bollinger Bands
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'],
                                line=dict(color='white', width=1),
                                name='Close'),
                     row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'],
                                line=dict(color='gray', width=1, dash='dash'),
                                name='Upper BB'),
                     row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'],
                                line=dict(color='gray', width=1, dash='dash'),
                                name='Lower BB',
                                fill='tonexty',
                                fillcolor='rgba(128,128,128,0.2)'),
                     row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Middle'],
                                line=dict(color='orange', width=1),
                                name='Middle BB'),
                     row=1, col=1)
        
        # MACD
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'],
                                line=dict(color='blue', width=1),
                                name='MACD'),
                     row=2, col=1)
        
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'],
                                line=dict(color='red', width=1),
                                name='Signal'),
                     row=2, col=1)
        
        # MACD Histogram
        colors = ['red' if val < 0 else 'green' for val in df['MACD_Histogram']]
        fig.add_trace(go.Bar(x=df.index, y=df['MACD_Histogram'],
                            name='Histogram', marker_color=colors),
                     row=2, col=1)
        
        fig.update_layout(title=f'{symbol} - Technical Indicators',
                         xaxis_title='Date',
                         template='plotly_dark',
                         height=600)
        
        return fig
    
    def create_heatmap(self, sector_performance):
        """Create sector performance heatmap."""
        sectors = list(sector_performance.keys())
        values = list(sector_performance.values())
        
        colors = ['green' if v > 0 else 'red' for v in values]
        
        fig = go.Figure(data=go.Bar(x=sectors, y=values,
                                    marker_color=colors,
                                    text=[f'{v:+.2f}%' for v in values],
                                    textposition='auto'))
        
        fig.update_layout(title='Sector Performance Heatmap',
                         xaxis_title='Sector',
                         yaxis_title='Change (%)',
                         template='plotly_dark',
                         height=500)
        
        return fig
    
    def search_stocks(self, query):
        """Search for stocks by name or symbol."""
        results = []
        all_tickers = []
        
        for stocks in self.SECTOR_STOCKS.values():
            all_tickers.extend(stocks)
        
        for ticker in set(all_tickers):
            try:
                stock = yf.Ticker(ticker)
                name = stock.info.get('longName', '')
                symbol = ticker.replace('.NS', '')
                
                if query.lower() in name.lower() or query.lower() in symbol.lower():
                    results.append({
                        'symbol': symbol,
                        'name': name[:40],
                        'sector': stock.info.get('sector', 'N/A')
                    })
            except:
                continue
        
        return results[:20]


# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    analyzer = IndianMarketAnalyzer()
    
    print("\n" + "="*80)
    print(" INDIAN MARKET ANALYZER - Testing")
    print("="*80)
    
    # Get market summary
    print("\n📊 MARKET SUMMARY:")
    summary = analyzer.get_market_summary()
    for index, data in summary.items():
        print(f"  {index}: ₹{data['value']:,} ({data['change']:+.2f}%)")
    
    # Get top gainers
    print("\n🚀 TOP GAINERS:")
    gainers = analyzer.get_top_gainers()
    for g in gainers[:5]:
        print(f"  {g['symbol']}: ₹{g['price']:,} (+{g['change']:.2f}%)")
    
    # Get sector performance
    print("\n🏭 SECTOR PERFORMANCE:")
    sectors = analyzer.get_sector_performance()
    for sector, change in sectors.items():
        print(f"  {sector}: {change:+.2f}%")
    
    # Analyze a specific stock
    print("\n📈 ANALYZING RELIANCE:")
    df = analyzer.fetch_historical_data("RELIANCE.NS", "3mo")
    df = analyzer.calculate_indicators(df)
    
    if not df.empty:
        latest = df.iloc[-1]
        print(f"  Current Price: ₹{latest['Close']:.2f}")
        print(f"  RSI: {latest['RSI']:.1f}")
        print(f"  Volatility: {latest['Volatility']:.1f}%")
        print(f"  Volume Ratio: {latest['Volume_Ratio']:.2f}x")