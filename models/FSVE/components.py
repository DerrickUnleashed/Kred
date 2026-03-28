from __future__ import annotations
import io
import streamlit as st
from PIL import Image


# ─── Header ───────────────────────────────────────────────────────────────────

def render_header():
    st.markdown("""
    <div class="sfie-header">
      <div class="sfie-title"><span>⬡</span> Student Future Intelligence Engine</div>
      <div class="sfie-sub">
        Behavioral science · Financial modelling · Qwen AI reasoning · Lifestyle visualisation
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Score Gauges ─────────────────────────────────────────────────────────────

def _score_color(score: float) -> str:
    if score >= 75: return "#22c55e"
    if score >= 55: return "#7c6fff"
    if score >= 40: return "#f59e0b"
    return "#ef4444"


def render_score_gauges(scores: dict, behavior: dict):
    domains = [
        ("Academic",  scores["academic"],  "📚"),
        ("Financial", scores["financial"], "💰"),
        ("Career",    scores["career"],    "💼"),
        ("Lifestyle", scores["lifestyle"], "🌱"),
    ]
    cols = st.columns(4)
    for i, (label, val, icon) in enumerate(domains):
        color = _score_color(val)
        with cols[i]:
            st.markdown(f"""
            <div class="score-gauge">
              <div class="gauge-label">{icon} {label}</div>
              <div class="gauge-value" style="color:{color};">{val:.0f}</div>
              <div class="gauge-bar-track">
                <div class="gauge-bar-fill" style="width:{val}%;background:{color};"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # Composite + badges row
    c = scores["composite"]
    risk   = behavior["risk_level"]
    trend  = behavior["trend"]
    badge_class = {"Low": "badge-low", "Moderate": "badge-moderate", "High": "badge-high"}[risk]
    trend_icon  = {"Improving": "↗", "Stable": "→", "Declining": "↘"}[trend]
    trend_color = {"Improving": "#22c55e", "Stable": "#7c6fff", "Declining": "#ef4444"}[trend]

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-top:.8rem;
         background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
         border-radius:12px;padding:1rem 1.5rem;">
      <div>
        <div class="gauge-label">COMPOSITE SCORE</div>
        <div style="font-family:'Epilogue',sans-serif;font-size:2rem;font-weight:900;
             color:{_score_color(c)};">{c:.0f}<span style="font-size:1rem;color:rgba(200,195,230,.5);">/100</span></div>
      </div>
      <div style="flex:1;height:1px;background:rgba(255,255,255,.07);"></div>
      <div style="display:flex;gap:.8rem;align-items:center;">
        <span class="{badge_class}">{risk} Risk</span>
        <span style="font-family:'Epilogue',sans-serif;font-weight:700;color:{trend_color};font-size:1.1rem;">
          {trend_icon} {trend}
        </span>
        <span style="background:rgba(124,111,255,.1);border:1px solid rgba(124,111,255,.25);
             border-radius:99px;padding:.2rem .75rem;font-size:.8rem;
             font-family:'JetBrains Mono',monospace;color:#7c6fff;">
          {behavior['profile']}
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Timeline Cards ───────────────────────────────────────────────────────────

def render_timeline_cards(simulation: dict):
    st.markdown('<div style="margin:1.2rem 0 .6rem;font-family:\'Epilogue\',sans-serif;font-size:1rem;font-weight:700;letter-spacing:.04em;">📈 Projected Outcomes</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    labels = {"5_year": "5 YEARS", "10_year": "10 YEARS", "25_year": "25 YEARS"}
    for i, (key, label) in enumerate(labels.items()):
        d = simulation[key]
        color = _score_color(d["composite"])
        with cols[i]:
            st.markdown(f"""
            <div class="timeline-card" data-years="{label}">
              <div class="tl-income" style="color:{color};">₹{d['income_lpa']} LPA</div>
              <div class="tl-stat">Age {d['future_age']} · Score {d['composite']}</div>
              <div style="margin-top:.7rem;display:flex;flex-direction:column;gap:.3rem;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;
                     color:rgba(180,170,220,.6);">
                  💼 {d['career_stability']}
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;
                     color:rgba(180,170,220,.6);">
                  💰 {d['fin_condition']}
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;
                     color:rgba(180,170,220,.6);">
                  🌱 {d['lifestyle_qual']}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)


# ─── Visual Future Tab ────────────────────────────────────────────────────────

def render_image_panel(images: dict, scores: dict, behavior: dict, simulation: dict):
    st.markdown("### 🖼  Lifestyle Environment Projections")
    st.markdown('<div style="color:rgba(200,195,230,.5);font-size:.88rem;margin-bottom:1.2rem;">AI-generated environment scenes based on your behavioral trajectory. No faces — pure lifestyle signals.</div>', unsafe_allow_html=True)

    horizon_meta = {
        "5_year":  ("5 Years",  simulation["5_year"]),
        "10_year": ("10 Years", simulation["10_year"]),
        "25_year": ("25 Years", simulation["25_year"]),
    }

    for key, (label, sim_d) in horizon_meta.items():
        img = images.get(key)
        if img is None:
            continue

        col_img, col_info = st.columns([3, 2])
        with col_img:
            st.image(img, use_container_width=True)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button(
                f"⬇ Download {label} Image",
                data=buf.getvalue(),
                file_name=f"sfie_{key}.png",
                mime="image/png",
            )

        with col_info:
            color = _score_color(sim_d["composite"])
            st.markdown(f"""
            <div class="card-accent" style="height:100%;">
              <div style="font-family:'Epilogue',sans-serif;font-size:1.2rem;
                   font-weight:800;margin-bottom:.8rem;color:#e8e4ff;">{label} Projection</div>
              <div style="display:flex;flex-direction:column;gap:.55rem;">
                <div>
                  <div class="metric-label">Projected Income</div>
                  <div class="metric-value" style="color:{color};">₹{sim_d['income_lpa']} LPA</div>
                </div>
                <div>
                  <div class="metric-label">Career Status</div>
                  <div style="font-size:.95rem;font-weight:600;">{sim_d['career_stability']}</div>
                </div>
                <div>
                  <div class="metric-label">Financial Condition</div>
                  <div style="font-size:.95rem;font-weight:600;">{sim_d['fin_condition']}</div>
                </div>
                <div>
                  <div class="metric-label">Lifestyle Quality</div>
                  <div style="font-size:.95rem;font-weight:600;">{sim_d['lifestyle_qual']}</div>
                </div>
                <div>
                  <div class="metric-label">Overall Score</div>
                  <div class="metric-value" style="color:{color};">{sim_d['composite']}<span style="font-size:.8rem;color:rgba(200,195,230,.4);">/100</span></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")


# ─── Analysis Dashboard Tab ───────────────────────────────────────────────────

def render_analysis_dashboard(processed: dict, scores: dict, behavior: dict, simulation: dict):
    st.markdown("### 📊  Behavioral Analysis Dashboard")

    render_score_gauges(scores, behavior)
    st.markdown("<br/>", unsafe_allow_html=True)
    render_timeline_cards(simulation)

    # Radar-style data table
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("#### Domain Detail")

    rows = [
        ("🎓 Academic",  scores["academic"],  processed["cgpa"], processed["study_hours"], processed["college_tier"]),
        ("💰 Financial", scores["financial"], processed["savings_habit"], processed["fin_discipline"], processed["family_income"]),
        ("💼 Career",    scores["career"],    processed["skill_level"], processed["has_experience"], processed["consistency"]),
        ("🌱 Lifestyle", scores["lifestyle"], processed["health_habits"], processed["sleep_quality"], processed["screen_time"]),
    ]

    header_cols = st.columns([2, 1, 2, 2, 2])
    for col, hdr in zip(header_cols, ["Domain", "Score", "Key Factor 1", "Key Factor 2", "Key Factor 3"]):
        col.markdown(f'<div class="metric-label">{hdr}</div>', unsafe_allow_html=True)

    for label, score, f1, f2, f3 in rows:
        col0, col1, col2, col3, col4 = st.columns([2, 1, 2, 2, 2])
        color = _score_color(score)
        col0.markdown(f'<div style="font-weight:600;font-size:.9rem;">{label}</div>', unsafe_allow_html=True)
        col1.markdown(f'<div style="font-family:\'Epilogue\',sans-serif;font-weight:800;color:{color};">{score:.0f}</div>', unsafe_allow_html=True)
        col2.markdown(f'<div style="font-size:.85rem;color:rgba(200,195,230,.7);">{f1}</div>', unsafe_allow_html=True)
        col3.markdown(f'<div style="font-size:.85rem;color:rgba(200,195,230,.7);">{f2}</div>', unsafe_allow_html=True)
        col4.markdown(f'<div style="font-size:.85rem;color:rgba(200,195,230,.7);">{f3}</div>', unsafe_allow_html=True)
        st.markdown('<hr/>', unsafe_allow_html=True)

    # Profile summary box
    st.markdown(f"""
    <div class="card-accent" style="margin-top:1rem;">
      <div style="display:flex;flex-wrap:wrap;gap:1.2rem;">
        <div>
          <div class="metric-label">Behavioral Profile</div>
          <div style="font-size:1rem;font-weight:700;color:#7c6fff;">{behavior['profile']}</div>
        </div>
        <div>
          <div class="metric-label">Risk Level</div>
          <div style="font-size:1rem;font-weight:700;">{behavior['risk_level']}</div>
        </div>
        <div>
          <div class="metric-label">Growth Trend</div>
          <div style="font-size:1rem;font-weight:700;">{behavior['trend']}</div>
        </div>
        <div>
          <div class="metric-label">Strongest Domain</div>
          <div style="font-size:1rem;font-weight:700;color:#22c55e;">{behavior['strongest']}</div>
        </div>
        <div>
          <div class="metric-label">Weakest Domain</div>
          <div style="font-size:1rem;font-weight:700;color:#ef4444;">{behavior['weakest']}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─── AI Insights Tab ──────────────────────────────────────────────────────────

def render_insights_panel(llm_output: dict, insights_data: dict, scores: dict, behavior: dict):
    st.markdown("### 🤖  AI-Powered Insights")
    st.markdown('<div style="color:rgba(200,195,230,.5);font-size:.85rem;margin-bottom:1rem;">Generated by Qwen via ChatGroq — behavioral science + data-driven reasoning.</div>', unsafe_allow_html=True)

    # Behavior narrative
    narr = llm_output.get("behavior_narrative", "")
    if narr:
        st.markdown("#### Your Behavioral Profile")
        st.markdown(f'<div class="narrative-box">{narr}</div>', unsafe_allow_html=True)

    st.markdown("#### Future Projections")
    future_narrs = llm_output.get("future_narratives", {})
    tabs = st.tabs(["5 Years", "10 Years", "25 Years"])
    for tab, key in zip(tabs, ["5_year", "10_year", "25_year"]):
        with tab:
            text = future_narrs.get(key, "")
            if text:
                st.markdown(f'<div class="narrative-box">{text}</div>', unsafe_allow_html=True)
            else:
                st.info("Narrative generation requires Groq API key.")

    # 4 domain insights
    st.markdown("#### Domain Risk Analysis")
    icons = {"academic_risk": "📚", "financial_risk": "💰", "career_signal": "💼", "lifestyle_warning": "🌱"}
    labels = {
        "academic_risk":    "Academic Risk",
        "financial_risk":   "Financial Pattern",
        "career_signal":    "Career Signal",
        "lifestyle_warning":"Lifestyle Status",
    }
    for key, icon in icons.items():
        text = insights_data.get(key, "")
        if text:
            st.markdown(f"""
            <div class="insight-row">
              <span class="insight-icon">{icon}</span>
              <div><strong>{labels[key]}:</strong> {text}</div>
            </div>
            """, unsafe_allow_html=True)

    # Strength / Threat summary
    strength = insights_data.get("top_strength", "")
    threat   = insights_data.get("top_threat", "")
    if strength or threat:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div style="background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.3);
                 border-radius:10px;padding:1rem;">
              <div class="metric-label" style="color:#22c55e;">TOP STRENGTH</div>
              <div style="font-size:.95rem;font-weight:600;margin-top:.3rem;">{strength}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.3);
                 border-radius:10px;padding:1rem;">
              <div class="metric-label" style="color:#ef4444;">TOP THREAT</div>
              <div style="font-size:.95rem;font-weight:600;margin-top:.3rem;">{threat}</div>
            </div>
            """, unsafe_allow_html=True)


# ─── Recommendations Tab ──────────────────────────────────────────────────────

def render_recommendations_panel(insights_data: dict, scores: dict, behavior: dict, processed: dict):
    st.markdown("### 💡  Personalised Recommendations")

    priority = insights_data.get("improvement_priority", behavior["weakest"])
    st.markdown(f"""
    <div style="background:rgba(124,111,255,.1);border:1px solid rgba(124,111,255,.3);
         border-radius:10px;padding:1rem 1.2rem;margin-bottom:1.2rem;">
      <div class="metric-label">HIGHEST PRIORITY ACTION AREA</div>
      <div style="font-family:'Epilogue',sans-serif;font-size:1.1rem;font-weight:700;
           color:#a08fff;margin-top:.3rem;">⚡ {priority}</div>
    </div>
    """, unsafe_allow_html=True)

    recs = insights_data.get("recommendations", [])
    if recs:
        for rec in recs:
            area   = rec.get("area", "")
            action = rec.get("action", "")
            impact = rec.get("impact", "Medium")
            impact_class = f"impact-{impact.lower()}"
            impact_label = {"High": "⬆ HIGH", "Medium": "→ MED", "Low": "↓ LOW"}.get(impact, impact)
            st.markdown(f"""
            <div class="rec-card">
              <div class="rec-area">{area}</div>
              <div style="flex:1;">
                <div class="rec-action">{action}</div>
              </div>
              <div class="{impact_class}" style="font-family:'JetBrains Mono',monospace;
                   font-size:.72rem;letter-spacing:.1em;flex-shrink:0;padding-top:.15rem;">
                {impact_label}
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Recommendations require Groq API key for personalised output.")

    # Static universal tip
    st.markdown("---")
    st.markdown("""
    <div class="card" style="font-size:.88rem;color:rgba(200,195,230,.65);line-height:1.75;">
      <strong style="color:#7c6fff;">Remember:</strong> Every projection here is based on your <em>current trajectory</em>.
      The most powerful lever you have is <strong>compound consistency</strong> — small daily improvements
      in the weakest domain create disproportionate long-term gains.
      The students who succeed are rarely the most talented — they are the most <em>deliberate</em>.
    </div>
    """, unsafe_allow_html=True)
