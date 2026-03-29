# app.py - Streamlit with exact input format from main.py
import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="KRED - Future Life Simulator",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
    }
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFD700, #FFA500, #FF6347);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 30px;
    }
    .score-card {
        background: linear-gradient(135deg, rgba(255,215,0,0.15), rgba(255,100,0,0.05));
        border-radius: 15px;
        padding: 20px;
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
    .metric-box {
        background: rgba(0,0,0,0.5);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 3px solid #FFD700;
    }
    .risk-low { color: #00ff88; font-weight: bold; }
    .risk-moderate { color: #ffaa00; font-weight: bold; }
    .risk-high { color: #ff4444; font-weight: bold; }
    .insight-box {
        background: rgba(255,215,0,0.1);
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
        border-left: 3px solid #FFD700;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">🔮 KRED - FUTURE LIFE SIMULATOR</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Financial Behavior Intelligence System</p>', unsafe_allow_html=True)

# Initialize session state for default values
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        "Full Name": "Default Student",
        "Age": 21,
        "Gender": "Male",
        "Country": "India",
        "Education Level": "Undergraduate",
        "Field of Study": "Computer Science",
        "Institution Tier": 2,
        "CGPA": 7.5,
        "Study Hours": 20,
        "Target Career": "Software Developer",
        "Skill Level": "Intermediate",
        "Internships": 1,
        "Consistency": 5,
        "Monthly Income": 15000,
        "Fixed Expenses": 8000,
        "Variable Expenses": 4000,
        "Weekly Spending": 2000,
        "Current Savings": 25000,
        "Savings Target": 50000,
        "Savings Duration": 12,
        "Family Income": 60000,
        "Earning Members": 2,
        "Dependents": 3,
        "Father Occupation": "Private Job",
        "Mother Occupation": "Homemaker",
        "Family Support": 5000,
        "Family Responsibility": 2000,
        "Screen Time": 6,
        "Sleep Duration": 6.5,
        "Sleep Quality": 6,
        "Health Score": 6,
        "Sick Days": 2,
        "Medical Expenses": 1000
    }

# Sidebar for inputs
with st.sidebar:
    st.markdown("## 📝 Student Profile")
    
    with st.expander("👤 Personal Info", expanded=True):
        name = st.text_input("Full Name", st.session_state.user_data["Full Name"])
        age = st.number_input("Age", 18, 80, st.session_state.user_data["Age"])
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                              index=["Male", "Female", "Other"].index(st.session_state.user_data["Gender"]))
        country = st.text_input("Country", st.session_state.user_data["Country"])
    
    with st.expander("🎓 Academic Info", expanded=True):
        edu_level = st.selectbox("Education Level", 
                                 ["Undergraduate", "High School", "Postgraduate", "PhD"],
                                 index=["Undergraduate", "High School", "Postgraduate", "PhD"].index(st.session_state.user_data["Education Level"]))
        field = st.text_input("Field of Study", st.session_state.user_data["Field of Study"])
        institution_tier = st.selectbox("Institution Tier", [1, 2, 3], 
                                        index=[1, 2, 3].index(st.session_state.user_data["Institution Tier"]))
        cgpa = st.slider("CGPA", 0.0, 10.0, st.session_state.user_data["CGPA"], 0.1)
        study_hours = st.slider("Study Hours/Week", 0, 60, st.session_state.user_data["Study Hours"])
        target_career = st.text_input("Target Career", st.session_state.user_data["Target Career"])
        skill_level = st.select_slider("Skill Level", ["Beginner", "Intermediate", "Advanced"], value=st.session_state.user_data["Skill Level"])
        internships = st.number_input("Internships", 0, 5, st.session_state.user_data["Internships"])
        consistency = st.slider("Consistency (0-10)", 0, 10, st.session_state.user_data["Consistency"])
    
    with st.expander("💰 Financial Data", expanded=True):
        monthly_income = st.number_input("Monthly Income (₹)", 0, 200000, st.session_state.user_data["Monthly Income"])
        fixed_expenses = st.number_input("Fixed Expenses (₹)", 0, 100000, st.session_state.user_data["Fixed Expenses"])
        variable_expenses = st.number_input("Variable Expenses (₹)", 0, 100000, st.session_state.user_data["Variable Expenses"])
        weekly_spending = st.number_input("Weekly Spending (₹)", 0, 50000, st.session_state.user_data["Weekly Spending"])
        current_savings = st.number_input("Current Savings (₹)", 0, 1000000, st.session_state.user_data["Current Savings"])
        savings_target = st.number_input("Savings Target (₹)", 0, 1000000, st.session_state.user_data["Savings Target"])
        savings_duration = st.number_input("Savings Duration (Months)", 1, 60, st.session_state.user_data["Savings Duration"])
    
    with st.expander("👨‍👩‍👧 Family Background", expanded=True):
        family_income = st.number_input("Family Income (₹)", 0, 500000, st.session_state.user_data["Family Income"])
        earning_members = st.number_input("Earning Members", 0, 10, st.session_state.user_data["Earning Members"])
        dependents = st.number_input("Dependents", 0, 10, st.session_state.user_data["Dependents"])
        father_occ = st.text_input("Father Occupation", st.session_state.user_data["Father Occupation"])
        mother_occ = st.text_input("Mother Occupation", st.session_state.user_data["Mother Occupation"])
        family_support = st.number_input("Family Support (₹)", 0, 50000, st.session_state.user_data["Family Support"])
        family_responsibility = st.number_input("Family Responsibility (₹)", 0, 50000, st.session_state.user_data["Family Responsibility"])
    
    with st.expander("❤️ Lifestyle & Health", expanded=True):
        screen_time = st.slider("Screen Time (Hours)", 0.0, 24.0, st.session_state.user_data["Screen Time"], 0.5)
        sleep_duration = st.slider("Sleep Duration (Hours)", 0.0, 12.0, st.session_state.user_data["Sleep Duration"], 0.5)
        sleep_quality = st.slider("Sleep Quality (0-10)", 0, 10, st.session_state.user_data["Sleep Quality"])
        health_score = st.slider("Health Score (0-10)", 0, 10, st.session_state.user_data["Health Score"])
        sick_days = st.number_input("Sick Days (per month)", 0, 30, st.session_state.user_data["Sick Days"])
        medical_expenses = st.number_input("Medical Expenses (₹)", 0, 50000, st.session_state.user_data["Medical Expenses"])
    
    analyze_btn = st.button("🚀 ANALYZE MY FUTURE", use_container_width=True)

# Main content area
if analyze_btn:
    with st.spinner("🔮 AI is analyzing your financial future..."):
        try:
            # Prepare payload in the exact format
            payload = {
                "Full Name": name,
                "Age": age,
                "Gender": gender,
                "Country": country,
                "Education Level": edu_level,
                "Field of Study": field,
                "Institution Tier": institution_tier,
                "CGPA": cgpa,
                "Study Hours": study_hours,
                "Target Career": target_career,
                "Skill Level": skill_level,
                "Internships": internships,
                "Consistency": consistency,
                "Monthly Income": monthly_income,
                "Fixed Expenses": fixed_expenses,
                "Variable Expenses": variable_expenses,
                "Weekly Spending": weekly_spending,
                "Current Savings": current_savings,
                "Savings Target": savings_target,
                "Savings Duration": savings_duration,
                "Family Income": family_income,
                "Earning Members": earning_members,
                "Dependents": dependents,
                "Father Occupation": father_occ,
                "Mother Occupation": mother_occ,
                "Family Support": family_support,
                "Family Responsibility": family_responsibility,
                "Screen Time": screen_time,
                "Sleep Duration": sleep_duration,
                "Sleep Quality": sleep_quality,
                "Health Score": health_score,
                "Sick Days": sick_days,
                "Medical Expenses": medical_expenses
            }
            
            # Call the API
            response = requests.post("http://localhost:8000/analyze", json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Display results
                st.success("✅ Analysis Complete!")
                
                # ============================================================
                # SECTION 1: SUMMARY
                # ============================================================
                st.markdown("## 📋 Executive Summary")
                st.markdown(f"""
                <div class="metric-box">
                    {result.get('summary', 'No summary available')}
                </div>
                """, unsafe_allow_html=True)
                
                # ============================================================
                # SECTION 2: KEY METRICS (4x4 Grid)
                # ============================================================
                st.markdown("## 📊 Key Metrics Dashboard")
                
                scores = result.get('scores', {})
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    rr = scores.get('retirement_readiness', {})
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-value">{rr.get('value', 0)}</div>
                        <div>Retirement Readiness</div>
                        <small style="color:#888;">{rr.get('reason', '')[:40]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    sd = scores.get('savings_discipline_score', {})
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-value">{sd.get('value', 0)}</div>
                        <div>Savings Discipline</div>
                        <small style="color:#888;">{sd.get('reason', '')[:40]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    fb = scores.get('financial_burn_rate_indicator', {})
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-value">{fb.get('value', 0)}</div>
                        <div>Burn Rate Indicator</div>
                        <small style="color:#888;">{fb.get('reason', '')[:40]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    lr = scores.get('lifestyle_risk_index', {})
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-value">{lr.get('value', 0)}</div>
                        <div>Lifestyle Risk Index</div>
                        <small style="color:#888;">{lr.get('reason', '')[:40]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Second row of metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    cg = scores.get('career_growth_potential_score', {})
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-value">{cg.get('value', 0)}</div>
                        <div>Career Growth</div>
                        <small style="color:#888;">{cg.get('reason', '')[:40]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    fd = scores.get('financial_dependency_ratio', {})
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-value">{fd.get('value', 0)}</div>
                        <div>Dependency Ratio</div>
                        <small style="color:#888;">{fd.get('reason', '')[:40]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    wa = scores.get('wealth_acceleration_potential', {})
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-value">{wa.get('value', 0)}</div>
                        <div>Wealth Acceleration</div>
                        <small style="color:#888;">{wa.get('reason', '')[:40]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    iu = scores.get('intervention_urgency_level', {})
                    urgency_color = "🔴" if iu.get('value', 0) > 70 else "🟡" if iu.get('value', 0) > 40 else "🟢"
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-value">{urgency_color} {iu.get('value', 0)}</div>
                        <div>Intervention Urgency</div>
                        <small style="color:#888;">{iu.get('reason', '')[:40]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                # ============================================================
                # SECTION 3: FUTURE PROJECTIONS
                # ============================================================
                st.markdown("## 🔮 Future Projections")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fp = result.get('future_projection', {})
                    st.markdown(f"""
                    <div class="metric-box">
                        <strong>📈 Qualitative:</strong> {fp.get('qualitative', 'N/A')}<br>
                        <strong>💰 Numeric:</strong> {fp.get('numeric', 'N/A')}<br>
                        <strong>⚠️ Retirement Delay Risk:</strong> <span class="risk-high">{result.get('retirement_delay_risk', 'N/A')}</span><br>
                        <strong>🏠 Future Lifestyle:</strong> <span class="risk-{result.get('future_lifestyle_tier', 'At Risk').lower().replace(' ', '-')}">{result.get('future_lifestyle_tier', 'N/A')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Create a gauge chart for retirement readiness
                    rr_value = scores.get('retirement_readiness', {}).get('value', 0)
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=rr_value,
                        title={'text': "Retirement Readiness", 'font': {'color': 'white'}},
                        gauge={
                            'axis': {'range': [0, 100], 'tickcolor': 'white'},
                            'bar': {'color': "#FFD700"},
                            'steps': [
                                {'range': [0, 33], 'color': "#ff4444"},
                                {'range': [33, 66], 'color': "#ffaa00"},
                                {'range': [66, 100], 'color': "#00ff88"}
                            ],
                            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': rr_value}
                        },
                        number={'font': {'color': 'white', 'size': 50}}
                    ))
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=250)
                    st.plotly_chart(fig, use_container_width=True)
                
                # ============================================================
                # SECTION 4: LIFEPATH ANALYSIS (Current vs Optimized)
                # ============================================================
                st.markdown("## 🛤️ LifePath Analysis")
                
                lp = result.get('lifepath_analysis', {})
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📉 Current Behavior Path")
                    current = lp.get('current_behavior', {})
                    st.markdown(f"""
                    <div class="metric-box">
                        <strong>💰 Wealth:</strong> {current.get('wealth', 'N/A')}<br>
                        <strong>📈 Career Growth:</strong> {current.get('career_growth', 'N/A')}<br>
                        <strong>🏦 Financial Stability:</strong> {current.get('financial_stability', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### 📈 Optimized Behavior Path")
                    optimized = lp.get('optimized_behavior', {})
                    st.markdown(f"""
                    <div class="metric-box" style="border-left-color: #00ff88;">
                        <strong>💰 Wealth:</strong> {optimized.get('wealth', 'N/A')}<br>
                        <strong>📈 Career Growth:</strong> {optimized.get('career_growth', 'N/A')}<br>
                        <strong>🏦 Financial Stability:</strong> {optimized.get('financial_stability', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                
                # ============================================================
                # SECTION 5: MICRO-REGRET INSIGHTS
                # ============================================================
                st.markdown("## 😰 Micro-Regret Insights")
                
                micro_regrets = result.get('micro_regret', [])
                for regret in micro_regrets:
                    st.markdown(f"""
                    <div class="insight-box">
                        ⚠️ {regret}
                    </div>
                    """, unsafe_allow_html=True)
                
                # ============================================================
                # SECTION 6: OPPORTUNITY COST & BEHAVIORAL PROFILE
                # ============================================================
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 💸 Opportunity Cost Analysis")
                    opp_costs = result.get('opportunity_cost', [])
                    for cost in opp_costs:
                        st.markdown(f"""
                        <div class="metric-box">
                            📉 {cost}
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### 🧠 Behavioral Profile")
                    profile = result.get('behavior_profile', 'Unknown')
                    profile_color = "🔴" if profile == "Impulsive" else "🟡" if profile == "Moderate" else "🟢"
                    st.markdown(f"""
                    <div class="metric-box">
                        <strong>{profile_color} {profile}</strong><br>
                        <small>{'Needs immediate intervention' if profile == 'Impulsive' else 'Balanced approach needed' if profile == 'Moderate' else 'Good habits, maintain momentum'}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 🏥 Health → Wealth Impact")
                    health_impact = result.get('health_impact', 'N/A')
                    st.markdown(f"""
                    <div class="metric-box">
                        {health_impact}
                    </div>
                    """, unsafe_allow_html=True)
                
                # ============================================================
                # SECTION 7: PEER COMPARISON
                # ============================================================
                st.markdown("## 👥 Peer Comparison (Gen Z Context)")
                peer = result.get('peer_comparison', 'Average')
                peer_icon = "🏆" if peer == "Above Average" else "📊" if peer == "Average" else "⚠️"
                st.markdown(f"""
                <div class="metric-box" style="text-align: center;">
                    <h2>{peer_icon} {peer}</h2>
                    <small>Compared to similar Gen Z students</small>
                </div>
                """, unsafe_allow_html=True)
                
                # ============================================================
                # SECTION 8: RECOMMENDATIONS
                # ============================================================
                st.markdown("## 🎯 Actionable Recommendations")
                
                recommendations = result.get('recommendations', [])
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"""
                    <div class="insight-box">
                        <strong>{i}.</strong> {rec}
                    </div>
                    """, unsafe_allow_html=True)
                
                # ============================================================
                # SECTION 9: FINAL INSIGHT
                # ============================================================
                st.markdown("## 💡 Final Insight")
                st.markdown(f"""
                <div class="metric-box" style="background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(255,100,0,0.1)); text-align: center;">
                    <em>“{result.get('final_statement', 'No final statement available')}”</em>
                </div>
                """, unsafe_allow_html=True)
                
                # ============================================================
                # EXPORT OPTION
                # ============================================================
                st.markdown("---")
                col1, col2, col3 = st.columns([1,2,1])
                with col2:
                    if st.button("📥 Download Full Report (JSON)", use_container_width=True):
                        report_data = {
                            "user_input": payload,
                            "analysis_results": result,
                            "generated_at": datetime.now().isoformat()
                        }
                        st.download_button(
                            label="Click to Download",
                            data=json.dumps(report_data, indent=2),
                            file_name=f"kred_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Please run: python working_api.py")
        except Exception as e:
            st.error(f"Error: {str(e)}")

else:
    # Welcome screen
    st.markdown("""
    <div style="text-align: center; padding: 60px;">
        <h2 style="color: #FFD700;">✨ Welcome to KRED</h2>
        <p style="color: #aaa; font-size: 1.1rem;">Your AI-powered financial behavior intelligence system</p>
        <p style="color: #666;">Fill in your details in the sidebar and click "ANALYZE MY FUTURE"</p>
        <br>
        <div style="background: rgba(255,215,0,0.1); border-radius: 15px; padding: 20px; margin-top: 20px;">
            <h3 style="color: #FFD700;">🔍 What KRED Analyzes</h3>
            <table style="width: 100%; color: #aaa;">
                <tr><td>📊 Retirement Readiness</td><td>💰 Savings Discipline</td></tr>
                <tr><td>📈 Career Growth Potential</td><td>🏥 Health → Wealth Impact</td></tr>
                <tr><td>😰 Future Regret Projections</td><td>🎯 Personalized Recommendations</td></tr>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px; margin-top: 30px; border-top: 1px solid rgba(255,215,0,0.1);">
    <p>⚡ Powered by GROQ (Qwen-32B) | KRED — AI-Powered Financial Behavior Intelligence System</p>
    <p style="font-size: 0.8rem;">Solving "Retirement Blindness" among Gen Z students</p>
</div>
""", unsafe_allow_html=True)
