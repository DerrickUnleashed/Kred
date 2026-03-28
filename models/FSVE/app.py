"""
Student Future Intelligence Engine (SFIE)
==========================================
AI-powered lifestyle simulation & prediction system.
LLM: ChatGroq + Qwen model via LangChain
Image Gen: HuggingFace Inference API (with rich placeholder fallback)

Run:
    streamlit run app.py
"""

import streamlit as st
from pathlib import Path

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="SFIE · Student Future Intelligence Engine",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

import io, json, datetime, random, math, os, base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from dotenv import load_dotenv

load_dotenv()

# ── Internal modules ──────────────────────────────────────────────────────────
from scoring   import process_inputs, compute_scores, analyze_behavior, simulate_future
from llm       import run_llm_analysis, generate_lifestyle_prompt
from imaging   import generate_images, save_outputs
from insights  import build_insights_and_recommendations
from styles        import inject_styles
from components    import (
    render_header, render_score_gauges, render_timeline_cards,
    render_insights_panel, render_recommendations_panel,
    render_analysis_dashboard, render_image_panel,
)

# ─────────────────────────────────────────────────────────────────────────────
inject_styles()
render_header()

# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — GROUPED INPUTS
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown('<div class="sb-logo">⬡ SFIE</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-tagline">Student Future Intelligence Engine</div>', unsafe_allow_html=True)
    st.markdown("---")

    # ── A. Basic ──────────────────────────────────────────────────────────────
    with st.expander("👤  Basic Profile", expanded=True):
        age    = st.slider("Age", 15, 35, 20)
        gender = st.selectbox("Gender (optional)", ["Prefer not to say", "Male", "Female", "Non-binary"])
        location = st.selectbox("Location Tier", ["Metro City", "Tier-2 City", "Small Town / Rural"])

    # ── B. Academic ───────────────────────────────────────────────────────────
    with st.expander("🎓  Academic Profile", expanded=True):
        cgpa           = st.slider("CGPA / GPA (out of 10)", 0.0, 10.0, 7.5, 0.1)
        edu_level      = st.selectbox("Education Level", ["School", "Undergraduate", "Postgraduate"])
        field_of_study = st.selectbox("Field of Study", [
            "Engineering / Technology", "Science", "Commerce / Business",
            "Arts / Humanities", "Medicine / Healthcare", "Law", "Other"
        ])
        college_tier   = st.selectbox("College Tier", ["Tier 1 (Premier)", "Tier 2", "Tier 3"])
        study_hours    = st.slider("Weekly Study Hours", 0, 80, 20)

    # ── C. Career ─────────────────────────────────────────────────────────────
    with st.expander("💼  Career Profile", expanded=True):
        target_career  = st.text_input("Target Career / Role", placeholder="e.g. Software Engineer, IAS Officer…")
        skill_level    = st.selectbox("Skill Level", ["Beginner", "Intermediate", "Advanced"])
        has_experience = st.selectbox("Internships / Work Experience", ["No", "Yes (< 6 months)", "Yes (6 months+)"])
        consistency    = st.selectbox("Work Consistency", ["Low", "Medium", "High"])

    # ── D. Financial ──────────────────────────────────────────────────────────
    with st.expander("💰  Financial Profile", expanded=True):
        monthly_spend   = st.number_input("Monthly Spending (₹)", 0, 100000, 8000, 500)
        savings_habit   = st.selectbox("Savings Habit", ["Low", "Medium", "High"])
        family_income   = st.selectbox("Family Income Background", ["Low", "Middle", "High"])
        fin_discipline  = st.selectbox("Financial Discipline", ["Impulsive", "Balanced", "Disciplined"])

    # ── E. Lifestyle ──────────────────────────────────────────────────────────
    with st.expander("🌱  Lifestyle & Habits", expanded=True):
        screen_time    = st.selectbox("Daily Screen Time", ["Low (< 3 h)", "Medium (3–6 h)", "High (> 6 h)"])
        health_habits  = st.selectbox("Health Habits", ["Poor", "Average", "Good"])
        sleep_quality  = st.selectbox("Sleep Quality", ["Poor", "Average", "Good"])

    st.markdown("---")
    run_btn = st.button("🔭  Run Future Simulation", use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  COLLECT INPUTS
# ═══════════════════════════════════════════════════════════════════════════════

raw_inputs = {
    "age": age, "gender": gender, "location": location,
    "cgpa": cgpa, "edu_level": edu_level, "field_of_study": field_of_study,
    "college_tier": college_tier, "study_hours": study_hours,
    "target_career": target_career or "Not specified",
    "skill_level": skill_level, "has_experience": has_experience,
    "consistency": consistency,
    "monthly_spend": monthly_spend, "savings_habit": savings_habit,
    "family_income": family_income, "fin_discipline": fin_discipline,
    "screen_time": screen_time, "health_habits": health_habits,
    "sleep_quality": sleep_quality,
}

# ═══════════════════════════════════════════════════════════════════════════════
#  WELCOME / IDLE STATE
# ═══════════════════════════════════════════════════════════════════════════════

if not run_btn:
    st.markdown("""
    <div class="welcome-panel">
      <div class="welcome-icon">🔭</div>
      <div class="welcome-title">Map Your Future</div>
      <div class="welcome-sub">
        Fill in your profile on the left and hit <strong>Run Future Simulation</strong>.<br/>
        The engine will project your lifestyle 5, 10, and 25 years ahead —
        using behavioral science, financial modelling, and AI reasoning.
      </div>
      <div class="welcome-chips">
        <span class="chip">📊 Behavioral Scoring</span>
        <span class="chip">🤖 Qwen AI Analysis</span>
        <span class="chip">🖼 Lifestyle Visualizations</span>
        <span class="chip">📈 Career Trajectory</span>
        <span class="chip">💡 Actionable Insights</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
#  RUN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

with st.status("⚙  Running analysis pipeline…", expanded=True) as status_box:

    st.write("📐 Processing & normalising inputs…")
    processed = process_inputs(raw_inputs)

    st.write("📊 Computing behavioral scores…")
    scores = compute_scores(processed)

    st.write("🧠 Analysing behavioral profile…")
    behavior = analyze_behavior(scores)

    st.write("📈 Simulating future trajectories…")
    simulation = simulate_future(processed, scores, behavior)

    st.write("🤖 Running Qwen LLM reasoning engine…")
    llm_output = run_llm_analysis(processed, scores, behavior, simulation)

    st.write("🖼  Generating lifestyle environment prompts…")
    image_prompts = {
        horizon: generate_lifestyle_prompt(processed, scores, behavior, simulation, llm_output, horizon)
        for horizon in ["5_year", "10_year", "25_year"]
    }

    st.write("🎨 Generating lifestyle environment images…")
    images = generate_images(image_prompts, processed, scores, behavior)

    st.write("💾 Saving outputs…")
    saved_paths = save_outputs(images, username="user")

    st.write("💡 Building insights & recommendations…")
    insights_data = build_insights_and_recommendations(processed, scores, behavior, simulation, llm_output)

    status_box.update(label="✅  Simulation complete!", state="complete", expanded=False)

# ═══════════════════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "🖼  Visual Future",
    "📊  Analysis Dashboard",
    "🤖  AI Insights",
    "💡  Recommendations",
])

with tab1:
    render_image_panel(images, scores, behavior, simulation)

with tab2:
    render_analysis_dashboard(processed, scores, behavior, simulation)

with tab3:
    render_insights_panel(llm_output, insights_data, scores, behavior)

with tab4:
    render_recommendations_panel(insights_data, scores, behavior, processed)
