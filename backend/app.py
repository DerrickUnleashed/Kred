import os
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from stock_service import (
    get_market_summary,
    get_movers,
    get_sector_performance,
    get_stock_info,
    get_historical_data,
    calculate_indicators,
    cache,
)

load_dotenv()

app = FastAPI(title="KRED Stocks API", version="1.0.0")

origins = [
    "https://kred-git-main-derrickunleasheds-projects.vercel.app/",
    "http://localhost:3000", # For local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    risk_profile: str = "Moderate"


SYSTEM_PROMPT = """You are KRED AI, a friendly Indian stock market expert who explains finance 
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
7. Use emojis sparingly to highlight key points.

Risk profiles:
- Conservative: prioritise capital safety, dividends, blue chips
- Moderate: balanced growth + safety, diversified sectors  
- Aggressive: growth stocks, momentum plays, higher tolerance for dips"""


def get_groq_llm():
    try:
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None
        return Groq(api_key=api_key)
    except ImportError:
        return None


@app.get("/")
def root():
    return {"status": "ok", "message": "KRED Stocks API is running"}


@app.get("/api/market/summary")
def market_summary():
    return get_market_summary()


@app.get("/api/market/movers")
def market_movers():
    return get_movers()


@app.get("/api/market/sectors")
def sector_performance():
    return get_sector_performance()


@app.get("/api/stock/{symbol}")
def stock_info(symbol: str):
    if not symbol.endswith(".NS"):
        symbol = f"{symbol}.NS"
    info = get_stock_info(symbol)
    if not info:
        raise HTTPException(status_code=404, detail="Stock not found")
    return info


@app.get("/api/stock/{symbol}/history")
def stock_history(symbol: str, period: str = "1mo"):
    if not symbol.endswith(".NS"):
        symbol = f"{symbol}.NS"
    return get_historical_data(symbol, period)


@app.get("/api/stock/{symbol}/indicators")
def stock_indicators(symbol: str):
    if not symbol.endswith(".NS"):
        symbol = f"{symbol}.NS"
    return calculate_indicators(symbol)


@app.post("/api/chat")
def chat(request: ChatRequest):
    client = get_groq_llm()
    
    if not client:
        return {
            "response": "AI chat is currently unavailable. Please ensure GROQ_API_KEY is configured in the backend environment.",
            "error": "API_KEY_MISSING"
        }
    
    try:
        market_summary_data = get_market_summary()
        sector_data = get_sector_performance()
        movers_data = get_movers()
        
        market_context = f"""
Current Market Data:
- NIFTY 50: {market_summary_data.get('NIFTY 50', {}).get('value', 'N/A')} ({market_summary_data.get('NIFTY 50', {}).get('pct', 0):+.2f}%)
- BSE SENSEX: {market_summary_data.get('BSE SENSEX', {}).get('value', 'N/A')} ({market_summary_data.get('BSE SENSEX', {}).get('pct', 0):+.2f}%)
- NIFTY BANK: {market_summary_data.get('NIFTY BANK', {}).get('value', 'N/A')} ({market_summary_data.get('NIFTY BANK', {}).get('pct', 0):+.2f}%)

Sector Performance: {', '.join([f'{k}: {v:+.2f}%' for k, v in sector_data.items()])}

Top Gainers: {', '.join([f"{g['symbol']}: +{g['change']}%" for g in movers_data.get('gainers', [])[:3]])}
Top Losers: {', '.join([f"{l['symbol']}: {l['change']}%" for l in movers_data.get('losers', [])[:3]])}
"""
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + f"\n\nCurrent market context:\n{market_context}\nUser risk profile: {request.risk_profile}"}
        ]
        
        for msg in request.history[-6:]:
            messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": request.message})
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
            max_tokens=500,
        )
        
        return {"response": response.choices[0].message.content}
    
    except Exception as e:
        return {"response": f"I encountered an error: {str(e)}", "error": "CHAT_ERROR"}


@app.post("/api/chat/insight")
def market_insight(risk_profile: str = "Moderate"):
    client = get_groq_llm()
    
    if not client:
        return {
            "response": "AI insights are currently unavailable. Please ensure GROQ_API_KEY is configured.",
            "error": "API_KEY_MISSING"
        }
    
    try:
        market_summary_data = get_market_summary()
        sector_data = get_sector_performance()
        movers_data = get_movers()
        
        market_context = f"""
Current Market Data:
- NIFTY 50: {market_summary_data.get('NIFTY 50', {}).get('value', 'N/A')} ({market_summary_data.get('NIFTY 50', {}).get('pct', 0):+.2f}%)
- BSE SENSEX: {market_summary_data.get('BSE SENSEX', {}).get('value', 'N/A')} ({market_summary_data.get('BSE SENSEX', {}).get('pct', 0):+.2f}%)
- NIFTY BANK: {market_summary_data.get('NIFTY BANK', {}).get('value', 'N/A')} ({market_summary_data.get('NIFTY BANK', {}).get('pct', 0):+.2f}%)
- NIFTY IT: {market_summary_data.get('NIFTY IT', {}).get('value', 'N/A')} ({market_summary_data.get('NIFTY IT', {}).get('pct', 0):+.2f}%)

Sector Performance: {', '.join([f'{k}: {v:+.2f}%' for k, v in sector_data.items()])}

Top Gainers: {', '.join([f"{g['symbol']}: +{g['change']}%" for g in movers_data.get('gainers', [])[:5]])}
Top Losers: {', '.join([f"{l['symbol']}: {l['change']}%" for l in movers_data.get('losers', [])[:5]])}
"""
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"User's risk profile: {risk_profile}\n\nCurrent market snapshot:\n{market_context}\n\nGive a clear, beginner-friendly market overview using simple analogies. Highlight 2-3 sectors worth watching and end with one actionable tip."}
        ]
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
            max_tokens=600,
        )
        
        return {"response": response.choices[0].message.content}
    
    except Exception as e:
        return {"response": f"I encountered an error: {str(e)}", "error": "INSIGHT_ERROR"}


@app.post("/api/cache/clear")
def clear_cache():
    cache.clear()
    return {"message": "Cache cleared successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
