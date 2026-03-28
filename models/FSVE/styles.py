"""
ui/styles.py
──────────────
Global CSS injection for SFIE Streamlit app.
Aesthetic: Dark editorial / data-intel / futurist terminal
Fonts: Epilogue (display) + JetBrains Mono (data) + DM Sans (body)
"""

import streamlit as st


def inject_styles():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Epilogue:wght@300;400;600;700;800;900&family=JetBrains+Mono:wght@300;400;600&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & Base ──────────────────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #06070f; color: #d4d0e8; }
h1,h2,h3,h4 { font-family: 'Epilogue', sans-serif; }

/* ── Sidebar ─────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #080910 !important;
    border-right: 1px solid rgba(100,80,200,0.2);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
.sb-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 600;
    color: #7c6fff;
    letter-spacing: .08em;
    margin-bottom: .2rem;
}
.sb-tagline {
    font-size: .72rem;
    color: rgba(180,170,220,.5);
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: .8rem;
}

/* ── Streamlit widget overrides ──────────────────────────────────────── */
.stSelectbox > div > div,
.stNumberInput > div,
.stSlider > div {
    background: rgba(255,255,255,.03) !important;
    border-color: rgba(100,80,200,.25) !important;
    border-radius: 6px !important;
    color: #d4d0e8 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #3d2fa0, #1a3080) !important;
    color: #e0dcff !important;
    border: 1px solid rgba(124,111,255,.4) !important;
    border-radius: 8px !important;
    font-family: 'Epilogue', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: .06em !important;
    padding: .65rem 1.4rem !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #5040c0, #2040a0) !important;
    box-shadow: 0 0 20px rgba(124,111,255,.3) !important;
}
.stProgress > div > div {
    background: linear-gradient(90deg, #7c6fff, #38b2f0) !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: .5rem;
    background: transparent !important;
    border-bottom: 1px solid rgba(124,111,255,.2);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: .78rem !important;
    letter-spacing: .08em !important;
    color: rgba(180,170,220,.6) !important;
    border: none !important;
    background: transparent !important;
    padding: .6rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    color: #7c6fff !important;
    border-bottom: 2px solid #7c6fff !important;
}

/* ── Header ──────────────────────────────────────────────────────────── */
.sfie-header {
    background: linear-gradient(135deg, #0a0b18 0%, #0e0b22 40%, #0b1222 100%);
    border: 1px solid rgba(100,80,200,.25);
    border-radius: 16px;
    padding: 2.2rem 2rem 2rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.sfie-header::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(80,60,200,.14) 0%, transparent 65%);
    border-radius: 50%;
}
.sfie-header::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(30,120,200,.10) 0%, transparent 65%);
    border-radius: 50%;
}
.sfie-title {
    font-family: 'Epilogue', sans-serif;
    font-weight: 900;
    font-size: 2.4rem;
    letter-spacing: -.04em;
    color: #e8e4ff;
    position: relative; z-index:1;
}
.sfie-title span { color: #7c6fff; }
.sfie-sub {
    font-size: .9rem;
    color: rgba(200,195,230,.5);
    margin-top: .4rem;
    font-weight: 300;
    position: relative; z-index:1;
    letter-spacing: .02em;
}

/* ── Generic Cards ───────────────────────────────────────────────────── */
.card {
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
}
.card-accent {
    background: rgba(124,111,255,.06);
    border: 1px solid rgba(124,111,255,.2);
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
}

/* ── Score Gauge ─────────────────────────────────────────────────────── */
.score-gauge {
    background: rgba(10,10,22,.6);
    border: 1px solid rgba(124,111,255,.2);
    border-radius: 12px;
    padding: 1.1rem;
    text-align: center;
}
.gauge-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: .68rem;
    letter-spacing: .15em;
    text-transform: uppercase;
    color: rgba(180,170,220,.55);
    margin-bottom: .5rem;
}
.gauge-value {
    font-family: 'Epilogue', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
}
.gauge-bar-track {
    background: rgba(255,255,255,.08);
    border-radius: 99px;
    height: 5px;
    margin-top: .5rem;
    overflow: hidden;
}
.gauge-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width .6s ease;
}

/* ── Timeline cards ──────────────────────────────────────────────────── */
.timeline-card {
    background: linear-gradient(145deg, rgba(14,12,30,.9), rgba(10,14,28,.9));
    border: 1px solid rgba(124,111,255,.22);
    border-radius: 14px;
    padding: 1.2rem;
    position: relative;
    overflow: hidden;
}
.timeline-card::after {
    content: attr(data-years);
    position: absolute;
    top: -12px; right: 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: .65rem;
    letter-spacing: .2em;
    color: rgba(124,111,255,.6);
    background: #06070f;
    padding: 2px 8px;
    border: 1px solid rgba(124,111,255,.2);
    border-radius: 99px;
}
.tl-income {
    font-family: 'Epilogue', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: #7c6fff;
}
.tl-stat {
    font-family: 'JetBrains Mono', monospace;
    font-size: .75rem;
    color: rgba(200,195,230,.65);
    margin-top: .3rem;
}

/* ── Risk / Profile badges ───────────────────────────────────────────── */
.badge-low      { background:#0d2416; border:1px solid #22c55e; color:#22c55e; padding:.25rem .85rem; border-radius:999px; font-size:.8rem; font-weight:700; display:inline-block; font-family:'JetBrains Mono',monospace; }
.badge-moderate { background:#221a08; border:1px solid #f59e0b; color:#f59e0b; padding:.25rem .85rem; border-radius:999px; font-size:.8rem; font-weight:700; display:inline-block; font-family:'JetBrains Mono',monospace; }
.badge-high     { background:#200c0c; border:1px solid #ef4444; color:#ef4444; padding:.25rem .85rem; border-radius:999px; font-size:.8rem; font-weight:700; display:inline-block; font-family:'JetBrains Mono',monospace; }

/* ── Narrative box ───────────────────────────────────────────────────── */
.narrative-box {
    background: rgba(124,111,255,.07);
    border-left: 3px solid #7c6fff;
    border-radius: 0 10px 10px 0;
    padding: 1.1rem 1.3rem;
    font-size: .92rem;
    line-height: 1.75;
    color: rgba(220,215,240,.9);
    margin: .8rem 0;
}

/* ── Insight row ─────────────────────────────────────────────────────── */
.insight-row {
    display: flex;
    gap: .8rem;
    align-items: flex-start;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 10px;
    padding: .8rem 1rem;
    margin: .4rem 0;
    font-size: .88rem;
    line-height: 1.6;
}
.insight-icon { flex-shrink: 0; font-size: 1rem; }

/* ── Rec card ────────────────────────────────────────────────────────── */
.rec-card {
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: .5rem 0;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}
.rec-area {
    font-family: 'JetBrains Mono', monospace;
    font-size: .68rem;
    letter-spacing: .14em;
    color: #7c6fff;
    text-transform: uppercase;
    flex-shrink: 0;
    width: 80px;
    padding-top: .15rem;
}
.rec-action { font-size: .9rem; line-height: 1.6; }
.impact-high   { color: #22c55e; }
.impact-medium { color: #f59e0b; }
.impact-low    { color: #64748b; }

/* ── Welcome panel ───────────────────────────────────────────────────── */
.welcome-panel {
    border: 1px solid rgba(124,111,255,.2);
    border-radius: 20px;
    padding: 4rem 2rem;
    text-align: center;
    background: linear-gradient(145deg, rgba(14,12,30,.6), rgba(8,10,22,.8));
    margin-top: 1rem;
}
.welcome-icon { font-size: 4rem; margin-bottom: 1rem; }
.welcome-title {
    font-family: 'Epilogue', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #e8e4ff;
    margin-bottom: .7rem;
}
.welcome-sub {
    color: rgba(200,195,230,.55);
    max-width: 480px;
    margin: 0 auto 1.5rem;
    line-height: 1.8;
    font-size: .95rem;
}
.welcome-chips { display: flex; flex-wrap: wrap; gap: .5rem; justify-content: center; }
.chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: .72rem;
    padding: .3rem .8rem;
    border: 1px solid rgba(124,111,255,.3);
    border-radius: 99px;
    color: rgba(180,170,240,.7);
    background: rgba(124,111,255,.07);
}

/* ── Analysis grid ───────────────────────────────────────────────────── */
.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: .68rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: rgba(180,170,220,.5);
    margin-bottom: .2rem;
}
.metric-value {
    font-family: 'Epilogue', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
}

/* ── Dividers ────────────────────────────────────────────────────────── */
hr { border-color: rgba(255,255,255,.07) !important; }

/* ── Download button ─────────────────────────────────────────────────── */
.stDownloadButton > button {
    background: rgba(124,111,255,.12) !important;
    color: #7c6fff !important;
    border: 1px solid rgba(124,111,255,.3) !important;
    border-radius: 6px !important;
    font-size: .8rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    padding: .4rem .9rem !important;
}
</style>
""", unsafe_allow_html=True)
