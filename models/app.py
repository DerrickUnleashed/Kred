# app.py - Place in C:\Users\Asus\Documents\GitHub\Kred\models\
import streamlit as st
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from PIL import Image
import io
import base64

# Page configuration
st.set_page_config(
    page_title="KRED - Future Life Simulator",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for the exact style from the image
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
    }
    
    /* Title styling */
    .main-title {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF6347 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 40px;
    }
    
    /* Card styling */
    .card {
        background: rgba(20, 20, 40, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 215, 0, 0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    /* Score cards */
    .score-card {
        background: linear-gradient(135deg, rgba(255,215,0,0.1) 0%, rgba(255,100,0,0.05) 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255,215,0,0.3);
        transition: transform 0.3s;
    }
    
    .score-card:hover {
        transform: translateY(-5px);
    }
    
    .score-value {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .score-label {
        color: #aaa;
        font-size: 0.85rem;
        margin-top: 5px;
    }
    
    /* Metric boxes */
    .metric-box {
        background: rgba(0,0,0,0.5);
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
        border-left: 3px solid #FFD700;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #000;
        font-weight: bold;
        font-size: 1.1rem;
        padding: 12px 30px;
        border-radius: 30px;
        border: none;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(255,215,0,0.3);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(30,30,50,0.8);
        border-radius: 10px;
        padding: 10px 20px;
        color: #ccc;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #000;
    }
    
    /* Header styling */
    .header-logo {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Risk indicators */
    .risk-low {
        color: #00ff88;
        font-weight: bold;
    }
    .risk-moderate {
        color: #ffaa00;
        font-weight: bold;
    }
    .risk-high {
        color: #ff4444;
        font-weight: bold;
    }
    
    /* Divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #FFD700, transparent);
        margin: 30px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.8rem;
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid rgba(255,215,0,0.1);
    }
    
    /* Input fields */
    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background-color: rgba(30,30,50,0.8);
        border-color: rgba(255,215,0,0.3);
        color: white;
    }
    
    .stSelectbox > div > div {
        background-color: rgba(30,30,50,0.8);
        color: white;
    }
    
    label {
        color: #FFD700 !important;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'results' not in st.session_state:
    st.session_state.results = None

# Header
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown('<h1 class="main-title">🔮 FUTURE LIFE SIMULATOR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Powered Life Trajectory Engine · FLUX + GROQ</p>', unsafe_allow_html=True)

st.markdown("""
<p style="text-align: center; color: #888; font-size: 0.9rem; margin-bottom: 40px;">
    Your academic, financial, career, and lifestyle inputs are scored and projected 5, 10, and 25 years ahead.<br>
    AI generates photorealistic visualizations of exactly what your lifestyle environment will look like.
</p>
""", unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Main input form
with st.container():
    st.markdown("### 📊 ENTER YOUR PROFILE")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Personal & Academic")
        age = st.number_input("Age", min_value=18, max_value=80, value=21, step=1)
        country = st.selectbox("Country", ["India", "USA", "UK", "Canada", "Australia", "Other"])
        edu_level = st.selectbox("Education Level", ["Undergraduate", "High School", "Postgraduate", "PhD"])
        field = st.selectbox("Field of Study", [
            "Engineering / Technology", "Computer Science", "Medicine / Healthcare",
            "Commerce / Business", "Arts / Humanities", "Law", "Science", "Other"
        ])
        college_tier = st.selectbox("College Tier", ["Tier 1", "Tier 2", "Tier 3"])
        cgpa = st.slider("CGPA/GPA", 0.0, 10.0, 7.5, 0.1)
        study_hours = st.slider("Study Hours per Week", 0, 60, 20)
        
    with col2:
        st.markdown("#### 💰 Financial & Lifestyle")
        monthly_spend = st.number_input("Monthly Spend (₹)", min_value=0, value=18000, step=1000)
        skill = st.select_slider("Skill Level", options=["Beginner", "Intermediate", "Advanced"], value="Intermediate")
        consistency = st.select_slider("Consistency", options=["Low", "Medium", "High"], value="Medium")
        discipline = st.select_slider("Spending Discipline", options=["Impulsive", "Balanced", "Disciplined"], value="Balanced")
        savings = st.select_slider("Savings Habit", options=["Low", "Medium", "High"], value="Medium")
        health = st.select_slider("Health Status", options=["Poor", "Average", "Good"], value="Average")
        sleep = st.select_slider("Sleep Quality", options=["Poor", "Average", "Good"], value="Average")
        
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            screen_time = st.selectbox("Screen Time", ["Low (<2 hrs)", "Medium (4-6 hrs)", "High (>8 hrs)"], index=1)
            experience = st.checkbox("Has Internship/Work Experience")
        with col2:
            family_bg = st.selectbox("Family Background", ["Low", "Middle", "High"], index=1)
            target_career = st.text_input("Target Career", "Software Engineer")
    
    # Analyze button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        analyze_clicked = st.button("🚀 ANALYZE MY FUTURE", use_container_width=True)

# API call and analysis
if analyze_clicked:
    with st.spinner("🔮 Analyzing your future trajectory..."):
        try:
            # Prepare payload
            payload = {
                "age": age,
                "country": country,
                "edu_level": edu_level,
                "field": field,
                "college_tier": college_tier,
                "cgpa": cgpa,
                "study_hours": study_hours,
                "target_career": target_career,
                "skill": skill,
                "experience": experience,
                "consistency": consistency,
                "monthly_spend": monthly_spend,
                "savings": savings,
                "family_bg": family_bg,
                "discipline": discipline,
                "screen_time": screen_time,
                "health": health,
                "sleep": sleep,
                "generate_images": False
            }
            
            # Call API
            response = requests.post(
                "http://localhost:8000/analyze",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                st.session_state.results = response.json()
                st.session_state.analyzed = True
                st.rerun()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Please run: python server.py")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Display results
if st.session_state.analyzed and st.session_state.results:
    results = st.session_state.results
    
    if results.get("status") == "success":
        
        # Hero Score Section
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        composite = results.get("composite_score", 0)
        risk = results.get("risk_level", "unknown")
        risk_class = f"risk-{risk}" if risk in ["low", "moderate", "high"] else ""
        
        with col1:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-value">{composite:.0f}</div>
                <div class="score-label">COMPOSITE SCORE</div>
                <div class="score-label" style="font-size:0.7rem">/100</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-value">{results.get("behavior_score", 0)}</div>
                <div class="score-label">BEHAVIOR SCORE</div>
                <div class="score-label" style="font-size:0.7rem">Financial Discipline</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-value">{results.get("regret_score", 0)}</div>
                <div class="score-label">REGRET SCORE</div>
                <div class="score-label" style="font-size:0.7rem">Future Impact</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            urgency = results.get("urgency_level", "Low")
            urgency_color = {"Critical": "#ff4444", "High": "#ffaa00", "Moderate": "#ffdd00", "Low": "#00ff88"}.get(urgency, "#fff")
            st.markdown(f"""
            <div class="score-card">
                <div class="score-value" style="color:{urgency_color}">{urgency}</div>
                <div class="score-label">URGENCY LEVEL</div>
                <div class="score-label" style="font-size:0.7rem">Action Required</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Risk indicator
        risk_display = {"low": "🟢 LOW RISK", "moderate": "🟡 MODERATE RISK", "high": "🔴 HIGH RISK"}.get(risk, "⚪ UNKNOWN")
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <span style="font-size: 1.2rem;">Risk Assessment: </span>
            <span class="risk-{risk}" style="font-size: 1.2rem;">{risk_display}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for detailed analysis
        tab1, tab2, tab3, tab4 = st.tabs(["📈 FUTURE PROJECTION", "💡 INSIGHTS", "📊 DETAILED SCORES", "🔮 REGRET ANALYSIS"])
        
        with tab1:
            st.markdown("### 🚀 Your Life Trajectory")
            
            # Create radar chart for future scores
            if results.get("details", {}).get("future_scores"):
                scores_data = results["details"]["future_scores"]
                categories = list(scores_data.keys())
                values = list(scores_data.values())
                
                fig = go.Figure(data=go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    line_color='#FFD700',
                    fillcolor='rgba(255,215,0,0.2)'
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], color='#888'),
                        angularaxis=dict(color='#888')
                    ),
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            st.markdown("### 🎯 Priority Actions")
            recommendations = results.get("details", {}).get("recommendations", [])
            if recommendations:
                for i, rec in enumerate(recommendations[:5], 1):
                    st.markdown(f"""
                    <div class="metric-box">
                        <strong>{i}.</strong> {rec}
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### 💡 AI-Generated Insights")
            insights = results.get("details", {}).get("insights", [])
            if insights:
                for insight in insights:
                    st.info(f"💭 {insight}")
            
            st.markdown("### 🛡️ Redemption Path")
            redemption = results.get("details", {}).get("redemption_path", "")
            if redemption:
                st.success(f"🌟 {redemption}")
        
        with tab3:
            st.markdown("### 📊 Domain Scores")
            
            col1, col2 = st.columns(2)
            scores_data = results.get("details", {}).get("future_scores", {})
            
            if scores_data:
                df = pd.DataFrame({
                    "Domain": list(scores_data.keys()),
                    "Score": list(scores_data.values())
                })
                
                fig = px.bar(df, x="Domain", y="Score", color="Score",
                            color_continuous_scale=["#ff4444", "#ffaa00", "#00ff88"],
                            range_color=[0, 100])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#fff',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 📋 Profile Summary")
            st.markdown(f"""
            <div class="metric-box">
                <strong>Behavior Profile:</strong> {results.get('behavior_profile', 'N/A')}<br>
                <strong>Risk Level:</strong> <span class="risk-{risk}">{risk.upper()}</span><br>
                <strong>Composite Score:</strong> {composite:.1f}/100
            </div>
            """, unsafe_allow_html=True)
        
        with tab4:
            st.markdown("### 😰 Regret Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="card">
                    <h4>5-Year Projection</h4>
                    <p>{results.get('details', {}).get('five_year_regret', 'No data')[:200]}...</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="card">
                    <h4>10-Year Projection</h4>
                    <p>{results.get('details', {}).get('ten_year_regret', 'No data')[:200]}...</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 🔮 Trajectory Metaphor")
            metaphor = results.get("details", {}).get("trajectory_metaphor", "")
            if metaphor:
                st.markdown(f"""
                <div class="card" style="background: linear-gradient(135deg, rgba(255,215,0,0.15), rgba(255,100,0,0.05));">
                    <p style="font-size: 1.1rem; font-style: italic;">“{metaphor}”</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Footer
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="footer">
            <p>⚡ Powered by GROQ (Qwen-32B) + FLUX.1-schnell</p>
            <p>KRED — AI-Powered Financial Behavior Intelligence System</p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.error(f"Analysis failed: {results.get('error', 'Unknown error')}")

# Instructions if no API running
elif not analyze_clicked:
    st.markdown("""
    <div style="text-align: center; padding: 40px; background: rgba(20,20,40,0.5); border-radius: 20px; margin-top: 30px;">
        <h3 style="color: #FFD700;">✨ Ready to See Your Future?</h3>
        <p style="color: #aaa;">Fill in your details above and click "ANALYZE MY FUTURE"</p>
        <p style="color: #666; font-size: 0.85rem;">Make sure the API server is running: <code>python server.py</code></p>
    </div>
    """, unsafe_allow_html=True)