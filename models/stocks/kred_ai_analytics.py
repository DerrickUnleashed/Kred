"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          KRED AI ANALYTICS — Intelligent Market Insights                    ║
║          LLM-powered analysis, chatbot, and market intelligence            ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module provides AI-powered market analytics including:
- Market insights generation using Groq LLM
- Stock-specific technical analysis with simple explanations
- Interactive chatbot for user queries
- Beginner-friendly explanations with analogies
"""

import os
from typing import Dict, List, Any
from datetime import datetime

# LLM Libraries
try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️ langchain-groq not installed. Run: pip install langchain-groq")


class KredAIAnalytics:
    """
    AI-powered market analytics engine using Groq LLM.
    Provides beginner-friendly explanations with analogies.
    """
    
    # System prompt for all AI interactions
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
7. Use emojis sparingly to highlight key points. 📊 💡 ⚠️

Risk profiles:
- Conservative: prioritise capital safety, dividends, blue chips
- Moderate: balanced growth + safety, diversified sectors  
- Aggressive: growth stocks, momentum plays, higher tolerance for dips
"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the AI analytics engine.
        
        Args:
            api_key: Groq API key (optional, will use GROQ_API_KEY env var if not provided)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.llm = None
        self.market_context = {}
        self.conversation_history = []
        
        if self.api_key and self.api_key.startswith("gsk_") and LLM_AVAILABLE:
            try:
                self.llm = ChatGroq(
                    groq_api_key=self.api_key,
                    model_name="llama3-70b-8192",
                    temperature=0.4,
                    max_tokens=1200,
                )
            except Exception as e:
                print(f"Failed to initialize LLM: {e}")
    
    def is_available(self) -> bool:
        """Check if AI engine is properly configured."""
        return self.llm is not None and LLM_AVAILABLE
    
    def update_market_context(self, context: Dict):
        """
        Update the market context for AI analysis.
        
        Args:
            context: Dictionary containing market data (indices, sectors, movers, etc.)
        """
        self.market_context = context
    
    def _format_market_data(self) -> str:
        """Format market data for inclusion in prompts."""
        if not self.market_context:
            return "Market data not available."
        
        formatted = []
        
        # Indices
        indices = self.market_context.get('indices', {})
        if indices:
            formatted.append("INDICES: " + "; ".join(
                f"{k}: {v['value']} ({v['pct']:+.2f}%)" 
                for k, v in indices.items()
            ))
        
        # Sectors
        sectors = self.market_context.get('sectors', {})
        if sectors:
            formatted.append("SECTORS: " + "; ".join(
                f"{k}: {v:+.2f}%" for k, v in sectors.items()
            ))
        
        # Gainers
        gainers = self.market_context.get('gainers', [])
        if gainers:
            formatted.append("TOP GAINERS: " + "; ".join(
                f"{g['symbol']}: +{g['change']}%" for g in gainers[:3]
            ))
        
        # Losers
        losers = self.market_context.get('losers', [])
        if losers:
            formatted.append("TOP LOSERS: " + "; ".join(
                f"{l['symbol']}: {l['change']}%" for l in losers[:3]
            ))
        
        # Summary
        summary = self.market_context.get('summary', {})
        if summary:
            formatted.append(f"MARKET SENTIMENT: {summary.get('market_sentiment', 'Neutral')}")
            formatted.append(f"AVERAGE CHANGE: {summary.get('avg_change', 0):+.2f}%")
        
        return "\n".join(formatted) if formatted else "Market data available."
    
    def generate_market_insight(self, risk_profile: str = "Moderate") -> str:
        """
        Generate comprehensive market insight based on current data.
        
        Args:
            risk_profile: User's risk appetite (Conservative/Moderate/Aggressive)
        
        Returns:
            AI-generated market analysis
        """
        if not self.is_available():
            return self._mock_market_insight(risk_profile)
        
        try:
            market_data = self._format_market_data()
            prompt = (
                f"User's risk profile: {risk_profile}\n\n"
                f"Current market snapshot:\n{market_data}\n\n"
                "Give a clear, beginner-friendly market overview using simple analogies. "
                "Highlight 2-3 sectors worth watching and end with one actionable tip."
            )
            
            response = self.llm.invoke([
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ])
            return response.content
        except Exception as e:
            return f"❌ AI error: {e}\n\n{self._mock_market_insight(risk_profile)}"
    
    def analyze_stock(self, symbol: str, technical: Dict, fundamental: Dict, 
                      risk_profile: str = "Moderate") -> str:
        """
        Generate stock-specific analysis with technical and fundamental data.
        
        Args:
            symbol: Stock symbol
            technical: Technical indicators (RSI, MACD, volatility, etc.)
            fundamental: Fundamental data (PE ratio, market cap, sector, etc.)
            risk_profile: User's risk appetite
        
        Returns:
            AI-generated stock analysis
        """
        if not self.is_available():
            return self._mock_stock_analysis(symbol, technical, fundamental, risk_profile)
        
        try:
            prompt = (
                f"Analyse {symbol} for a {risk_profile} investor.\n\n"
                f"Company: {fundamental.get('name', 'N/A')} | "
                f"Sector: {fundamental.get('sector', 'N/A')}\n"
                f"PE: {fundamental.get('pe_ratio', 'N/A')} | "
                f"Beta: {fundamental.get('beta', 'N/A')}\n\n"
                f"Technical indicators: {technical}\n\n"
                "Explain what these numbers mean in plain language using everyday analogies. "
                "Point out the most important signal and what it suggests."
            )
            
            response = self.llm.invoke([
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ])
            return response.content
        except Exception as e:
            return f"❌ AI error: {e}\n\n{self._mock_stock_analysis(symbol, technical, fundamental, risk_profile)}"
    
    def chat(self, user_query: str, risk_profile: str = "Moderate") -> str:
        """
        Interactive chatbot for user queries.
        
        Args:
            user_query: User's question
            risk_profile: User's risk appetite
        
        Returns:
            AI-generated response
        """
        if not self.is_available():
            return self._mock_chat_response(user_query, risk_profile)
        
        try:
            market_data = self._format_market_data()
            
            # Build messages with conversation history
            messages = [SystemMessage(
                content=self.SYSTEM_PROMPT +
                f"\n\nCurrent market context:\n{market_data}\n"
                f"User risk profile: {risk_profile}"
            )]
            
            # Add recent conversation history (last 6 turns)
            for h in self.conversation_history[-6:]:
                if h["role"] == "user":
                    messages.append(HumanMessage(content=h["content"]))
                else:
                    messages.append(AIMessage(content=h["content"]))
            
            messages.append(HumanMessage(content=user_query))
            
            response = self.llm.invoke(messages)
            
            # Store in conversation history
            self.conversation_history.append({"role": "user", "content": user_query})
            self.conversation_history.append({"role": "assistant", "content": response.content})
            
            return response.content
        except Exception as e:
            return f"❌ AI error: {e}\n\n{self._mock_chat_response(user_query, risk_profile)}"
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    # ── Mock Responses (for when LLM is unavailable) ──────────────────────────────
    def _mock_market_insight(self, risk_profile: str) -> str:
        """Mock market insight for demo/offline mode."""
        sentiment = self.market_context.get('summary', {}).get('market_sentiment', 'Neutral')
        avg_change = self.market_context.get('summary', {}).get('avg_change', 0)
        
        return f"""
📊 MARKET OVERVIEW
The Indian market is currently showing {sentiment.lower()} sentiment with average movement of {avg_change:+.2f}%. 
There are {self.market_context.get('summary', {}).get('total_gainers', 0)} gainers vs {self.market_context.get('summary', {}).get('total_losers', 0)} losers.

🏭 SECTOR INSIGHTS
The {self.market_context.get('top_sector', 'Banking')} sector is showing strength today. IT and Pharma sectors are worth watching for momentum.

💡 FOR YOUR {risk_profile.upper()} RISK PROFILE
Consider focusing on quality large-caps with consistent earnings. Maintain a diversified portfolio across 4-5 sectors.

🎯 ACTIONABLE TIP
Set price alerts for your watched stocks and review portfolio monthly.
"""
    
    def _mock_stock_analysis(self, symbol: str, technical: Dict, fundamental: Dict, risk_profile: str) -> str:
        """Mock stock analysis for demo/offline mode."""
        rsi = technical.get('RSI', 50)
        volatility = technical.get('Volatility_%', 20)
        price = technical.get('Price', 0)
        
        if rsi > 70:
            signal = "The RSI is above 70 — like a car going too fast. It might need to cool down soon."
            outlook = "Be cautious about buying at current levels."
        elif rsi < 30:
            signal = "The RSI is below 30 — like a car that's barely moving. It might be oversold."
            outlook = "Worth watching for potential bounce back."
        else:
            signal = "The RSI is in neutral zone (30-70) — healthy momentum."
            outlook = "Current price action looks balanced."
        
        return f"""
📊 {symbol} ANALYSIS

💰 PRICE ACTION: ₹{price:,}
{signal}
Volatility is {volatility:.1f}% — {'bumpy road' if volatility > 30 else 'smooth ride' if volatility < 15 else 'moderate conditions'}

💡 KEY INSIGHT
{outlook} For a {risk_profile.lower()} investor, this stock shows {'interesting potential' if rsi < 70 else 'cautionary signals'}.

📈 SUGGESTED ACTION
Watch key levels: Support at ₹{price * 0.95:.0f}, Resistance at ₹{price * 1.05:.0f}
"""
    
    def _mock_chat_response(self, query: str, risk_profile: str) -> str:
        """Mock chatbot response for demo/offline mode."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['gainer', 'top', 'best']):
            gainers = self.market_context.get('gainers', [])
            if gainers:
                return f"Today's top gainer is {gainers[0]['symbol']} with +{gainers[0]['change']}% gain. For your {risk_profile.lower()} risk profile, consider researching fundamentally strong stocks in gaining sectors."
            return "No significant gainers at the moment. Market appears to be consolidating."
        
        elif any(word in query_lower for word in ['risk', 'safe', 'volatile']):
            volatility = self.market_context.get('summary', {}).get('avg_volatility', 18)
            return f"Current market volatility is {volatility:.1f}%. For a {risk_profile.lower()}-risk investor, focus on large-cap stocks with consistent earnings and maintain position sizes under 5% of portfolio."
        
        elif any(word in query_lower for word in ['sector', 'industry']):
            top_sector = self.market_context.get('top_sector', 'Banking')
            return f"The {top_sector} sector is currently showing strength. This is driven by positive earnings expectations and sector-specific tailwinds. Worth researching top stocks in this space."
        
        elif 'rsi' in query_lower:
            return "RSI (Relative Strength Index) is like a car's speedometer. Above 70 means too fast (overbought) — may need to slow down. Below 30 means too slow (oversold) — might speed up soon. Healthy range is 40-60."
        
        elif 'macd' in query_lower:
            return "MACD is like a train's speed indicator. When the MACD line crosses above the signal line, it's like a train gaining speed (bullish). Crossing below means slowing down (bearish). The histogram shows how strong the momentum is."
        
        else:
            sentiment = self.market_context.get('summary', {}).get('market_sentiment', 'Neutral')
            return f"Current market sentiment is {sentiment.lower()}. I can help you understand market concepts, analyze specific stocks, or explain technical indicators. What would you like to know?"


# ── Quick Test / Example Usage ─────────────────────────────────────────────────
if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n" + "="*80)
    print(" KRED AI ANALYTICS - Test Run")
    print("="*80)
    
    # Initialize AI engine
    ai = KredAIAnalytics()
    
    if ai.is_available():
        print("\n✅ AI Engine initialized successfully with Groq LLM")
        
        # Test with mock market context
        test_context = {
            'indices': {
                'NIFTY 50': {'value': 22500, 'pct': 0.85},
                'BSE SENSEX': {'value': 74000, 'pct': 0.75}
            },
            'sectors': {'Banking': 1.2, 'IT': -0.3, 'Pharma': 0.5},
            'gainers': [{'symbol': 'RELIANCE', 'change': 2.5}],
            'summary': {'market_sentiment': 'Bullish', 'avg_change': 0.6}
        }
        ai.update_market_context(test_context)
        
        # Generate market insight
        print("\n📊 Market Insight:")
        print(ai.generate_market_insight("Moderate"))
        
        # Test chat
        print("\n💬 Chat Test:")
        print(ai.chat("What is RSI?", "Moderate"))
        
    else:
        print("\n⚠️ AI Engine in mock mode (LLM not configured)")
        print("   Set GROQ_API_KEY in .env file for real AI insights")
        
        # Mock mode test
        test_context = {
            'indices': {'NIFTY 50': {'value': 22500, 'pct': 0.85}},
            'gainers': [{'symbol': 'RELIANCE', 'change': 2.5}],
            'summary': {'market_sentiment': 'Bullish', 'avg_volatility': 18}
        }
        ai.update_market_context(test_context)
        
        print("\n📊 Market Insight (Mock):")
        print(ai.generate_market_insight("Moderate"))
    
    print("\n✅ Test completed successfully!")