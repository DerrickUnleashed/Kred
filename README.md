<div align="center">

<!-- Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=2,2,3,30&height=300&section=header&text=KRED&fontSize=90&animation=fadeIn&fontAlignY=38&desc=AI-Powered%20Life%20&amp;%20Financial%20Intelligence%20Engine&descAlignY=55&descAlign=50" width="100%" />

<!-- Typing Animation -->
<p align="center">
  <a href="https://git.io/typing-svg">
    <img 
      src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=22&pause=100&color=FFA500&center=true&vCenter=true&multiline=true&height=100&width=900&lines=See+your+future.;Quantify+your+decisions.;Change+your+trajectory." 
      alt="Typing SVG" 
    />
  </a>
</p>

</div>

# Problem Statement

## Retirement Blindness Among Gen Z

Today’s generation is highly focused on short-term financial needs, lifestyle upgrades, and immediate gratification — often at the cost of long-term financial security.
Retirement, being distant and abstract, is largely ignored or postponed. Most individuals lack the financial literacy and awareness required to understand the importance of early investing and compounding.
As a result, there exists a critical gap between **knowing** and **acting**.

This leads to:
- Delayed investment decisions  
- Weak financial habits  
- Loss of compounding advantages  
- Increased risk of financial insecurity in later life  

---

# Solution

> The problem isn’t that people don’t care about their future —  
> it’s that they **can’t see it clearly enough to act today.**

KRED is an AI-driven platform that transforms how individuals understand money, behavior, and long-term life outcomes.

Instead of simply tracking expenses, KRED analyzes **how you think, spend, learn, and live** — and converts those patterns into **future wealth, career growth, and lifestyle projections**.

---


# Presentation, Demo & Deployment

Explore the complete project, live demo, and pitch:

🔗 **Live Deployment**: [Click Here](kred-steel.vercel.app)

🔗 **PPT**: [Click Here](https://docs.google.com/presentation/d/160gLE1GIUt3D2saIO7HdB4uaYYA1cxga/edit?usp=sharing&ouid=112083637467050535240&rtpof=true&sd=true)  

🎥 **Demo Video**: [Click Here](https://your-demo-video-link.com)

> This includes the live application, full walkthrough, and presentation covering the problem, solution, core features, innovations, and system design of KRED.

---

# Project Setup Instructions

## 1. Clone the Project

```bash
git clone https://github.com/DerrickUnleashed/Kred.git
cd Kred
```

## 2. Backend Setup

```bash
cd backend
```

* Create a `.env` file based on `.env.example`

### Create Virtual Environment**

**Linux / macOS**

```bash
python3 -m venv venv
```

**Windows**

```bash
python -m venv venv
```

### Activate Virtual Environment

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Backend

```bash
uvicorn app:app
```

## 3. Frontend Setup

```bash
cd ../frontend
```

* Create a `.env` file based on `.env.example`

### Install Dependencies

```bash
npm install
```

### Run Frontend

```bash
npm run dev
```

---

# Core Features

## 1. AI Behavioral Analysis Engine

Analyzes your academic, financial, and lifestyle patterns to understand how you make decisions.  
Transforms raw behavior into a clear psychological-financial profile that predicts future stability and risk.

---

## 2. Life Regret Intelligence Engine *(Novel)*

Calculates the hidden long-term cost of your everyday habits using compounding models.  
Turns small present decisions into tangible lifetime financial impact, making consequences impossible to ignore.

---

## 3. Micro Life Simulation Engine *(Novel)*

Simulates alternate versions of your life based on behavioral changes in real time.  
Shows how small improvements today can drastically reshape your future wealth and career trajectory.

---

## 4. KRED Reels — Financial Intelligence Feed *(Novel)*

Delivers personalized, high-value financial and career insights in a short-form content format.  
Redesigns scrolling into a productive experience that improves decision-making instead of distracting you.

---

## 5. PF & Retirement Intelligence Engine *(Novel)*

Projects your long-term financial security by analyzing savings, contributions, and inflation.  
Helps you understand how today’s habits affect your retirement readiness and future independence.

---

## 6. Dynamic Spending Limit Engine

Continuously adapts your spending limits based on income, behavior, and financial goals.  
Acts as a real-time guardrail that prevents overspending before it happens.

---

## 7. Future Life Projection Engine

Builds a long-term simulation of your financial and career trajectory.  
Compares your current path with optimized scenarios to highlight where change creates the most impact.

---

## 8. Stock Intelligence Module

Provides real-time market insights with simplified explanations of complex indicators.  
Helps beginners make informed decisions without needing deep financial expertise.

---

## 9. AI Financial Assistant

Acts as a conversational guide for all financial and behavioral insights.  
Breaks down complex data into simple, actionable recommendations tailored to you.

---

## 10. Adaptive Feedback System

Continuously learns from your actions, habits, and decisions over time.  
Refines predictions and recommendations to become more accurate and personalized.

---

# Novel Contributions

KRED introduces a new class of intelligent systems:

-  **Life Regret Quantification (Novel)**  
-  **Behavioral Future Simulation (Novel)**  
-  **Educational Reels Engine (Novel)**  
-  **Retirement Intelligence for Gen Z (Novel)**  
-  **Life Intelligence Layer (Novel)**  

---

# User Authentication

- Supabase-powered authentication  
- Secure login & registration  
- Row-Level Security (RLS)  
- Persistent sessions  

---

# Tech Stack

## Frontend
- React 19  
- Vite  
- Tailwind CSS  
- React Router v7  
- Recharts / Chart.js  
- Supabase (Auth + DB)  
- Spline (3D AI Assistant)  

## Backend
- FastAPI (Python)  

### AI Engines:
- Scoring Engine  
- Regret Engine  
- Projection Engine  
- Behavioural Engine  

## AI Layer
- LangChain + Groq  
- Models: LLaMA / Qwen  
- Structured reasoning (JSON outputs)  

## Data Sources
- yFinance (market data)  
- Supabase (user data)  

---

# Project Structure

```
.
├── LICENSE
├── README.md
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── output
│   ├── requirements.txt
│   └── stock_service.py
└── frontend
    ├── README.md
    ├── dist
    ├── eslint.config.js
    ├── index.html
    ├── node_modules
    ├── package-lock.json
    ├── package.json
    ├── postcss.config.js
    ├── public
    ├── src
    ├── tailwind.config.js
    ├── vercel.json
    └── vite.config.js

8 directories, 15 files
```
