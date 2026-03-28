# KRED - AI-Powered Behavioral Financial Platform

KRED is a comprehensive financial management platform that combines AI-powered behavior analysis with intelligent tools to transform financial habits. The platform features Kred Bird, your personal AI companion who guides every financial decision.

## Features

### Core Modules

#### 1. Kred Bird AI Companion
Your AI-powered financial companion that guides you through daily decisions, evolves with your discipline, and celebrates your wins. Kred Bird provides real-time guidance and emotional support for your financial journey.

#### 2. Budget Planner & Insights
- Plan, track, and manage daily, weekly, and monthly budgets
- Intelligent analysis with actionable insights
- Clear recommendations for better financial decisions
- Category-based expense tracking (Groceries, Electronics, Clothing, Utilities, Healthcare, Entertainment, Transportation, Education, Housing, Other)

#### 3. Dynamic Limit Engine
Personalized spending limits calculated based on:
- Monthly income and expected savings
- Current expenses and spending patterns
- Time-of-day and day-of-week context (detects evening/weekend spending risks)
- Behavioral factors (impulsive vs. disciplined spending)
- Savings goals and remaining budget
- Real-time adaptation as you make purchases

The engine calculates:
- `dynamic_limit`: Adaptive daily spending limit
- `safe_spend_now`: Amount you can safely spend right now
- `status`: Budget status (relaxed/moderate/tight)
- `behavior_factor`: Detects impulsive spending patterns
- `context_factor`: Time-based risk assessment
- `goal_factor`: Savings goal pressure indicator

#### 4. AI Behavior Engine
Advanced behavioral analysis that:
- Detects patterns like overspending, inconsistency, and financial risk
- Calculates behavior score (0-100)
- Identifies behavior profiles: disciplined, saver, occasional_impulsive, impulsive, no_data
- Generates corrective insights and predictive recommendations
- Monitors spending volatility and frequency
- Tracks essential vs. non-essential purchases

**AI Insights Include:**
- High impulsive spending detection
- Savings rate warnings
- Entertainment spending alerts
- Purchase frequency analysis
- 5-year financial projections
- Personalized recommendations

#### 5. Future Self Visualization
- Simulates future financial condition based on current habits
- Creates emotional connection between present actions and long-term consequences
- 5-year spending projections
- Potential savings calculations
- Progress tracking dashboards

#### 6. Stock Analysis & Insights (KRED AI)
Full-featured Indian market intelligence with:

**Market Dashboard:**
- Real-time NSE/BSE market indices (NIFTY 50, BSE SENSEX, NIFTY BANK, NIFTY IT)
- Top gainers and losers tracking
- Sector-wise performance analysis with interactive charts
- Live data from Yahoo Finance

**Stock Analysis:**
- 20 NSE stocks available (RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK, HINDUNILVR, SBIN, BHARTIARTL, KOTAKBANK, ITC, LT, AXISBANK, ASIANPAINT, MARUTI, SUNPHARMA, WIPRO, HCLTECH, TATAMOTORS, NESTLEIND, NTPC)
- Stock information: Current price, Market cap, P/E ratio, 52-week high/low, Dividend yield, Beta
- Historical price charts with volume analysis
- Technical indicators: RSI(14), MACD, Volatility, Volume ratio

**AI Chatbot:**
- Conversational interface powered by Groq LLM (Llama 3.3 70B)
- Risk profile customization (Conservative, Moderate, Aggressive)
- Market insights with beginner-friendly explanations
- Uses Indian context (NSE, BSE, SEBI, FD rates, SIP)
- Simple analogies for complex financial concepts

**AI Market Insights:**
- Daily market overview generation
- Sector analysis and recommendations
- Actionable tips for different risk profiles
- Weather/market analogies for beginners

#### 7. Automated Savings & Investment
- Automatic fund allocation toward savings goals
- Investment recommendations based on risk profile
- Reduces manual financial decisions
- Ensures consistent wealth building

#### 8. Adaptive Feedback Loop
- Continuous activity monitoring
- Real-time strategy updates
- Self-reinforcing system for disciplined financial behavior
- Continuous improvement cycle

### FSVE - Financial State Variable Engine
*(Backend module - infrastructure for financial state management)*

### User Authentication
- Supabase-powered authentication
- Secure login and registration
- Persistent session management
- Protected routes for dashboard and stocks

## Tech Stack

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router v7** - Navigation
- **Recharts** - Data visualization
- **Chart.js** - Financial charts
- **Supabase** - Authentication & database
- **Spline** - 3D elements (Kred Bird mascot)

### Backend
- **FastAPI** - API framework
- **Python** - Server logic
- **yfinance** - Yahoo Finance data
- **Groq SDK** - AI/LLM integration

## Project Structure

```
Vashist3.0/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx      # Main dashboard with 5 tabs
│   │   │   ├── Stocks.jsx         # Stock market module
│   │   │   ├── Navbar.jsx         # Navigation
│   │   │   ├── Hero.jsx           # Landing hero
│   │   │   ├── Features.jsx       # Feature showcase
│   │   │   ├── HowItWorks.jsx     # Process steps
│   │   │   ├── Pricing.jsx        # Pricing plans
│   │   │   ├── CTA.jsx            # Call to action
│   │   │   ├── Footer.jsx         # Footer
│   │   │   ├── Login.jsx          # Login page
│   │   │   ├── Register.jsx      # Registration page
│   │   │   ├── LandingPage.jsx    # Main landing page
│   │   │   └── SplineBot.jsx      # 3D Kred Bird
│   │   ├── lib/
│   │   │   └── supabase.js        # Supabase client
│   │   ├── App.jsx                # Router
│   │   └── index.css              # Global styles
│   ├── tailwind.config.js         # Tailwind configuration
│   └── package.json
├── backend/
│   ├── app.py                     # FastAPI application
│   ├── stock_service.py            # Yahoo Finance service
│   ├── fsve/                      # FSVE module (infrastructure)
│   ├── requirements.txt
│   └── .env                       # GROQ_API_KEY
└── README.md
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- Supabase account
- Groq API key (for AI features)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Create `.env` file:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_STOCKS_API_URL=http://localhost:8000
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file:
```env
GROQ_API_KEY=your_groq_api_key
```

Run the backend:
```bash
python app.py
# or
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Database Setup (Supabase)

Create tables in Supabase:

```sql
-- Income table
CREATE TABLE income (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users NOT NULL,
  monthly_income DECIMAL,
  expected_savings DECIMAL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Products/Expenses table
CREATE TABLE products (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users NOT NULL,
  name TEXT,
  quantity INTEGER,
  cost_per_unit DECIMAL,
  category TEXT,
  total_cost DECIMAL,
  is_essential BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE income ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can manage own income" ON income
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own products" ON products
  FOR ALL USING (auth.uid() = user_id);
```

## License

MIT License
