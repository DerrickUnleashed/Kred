import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Kred System", layout="wide")

st.title("🧠 Kred Financial System (Test UI)")

# -------------------------------
# 🔹 USER SETUP
# -------------------------------
st.header("👤 Setup User")

income = st.number_input("Monthly Income", min_value=0)

if st.button("Create User"):
    res = requests.post(f"{BASE_URL}/setup", params={"income": income})
    st.write(res.json())


# -------------------------------
# 🔹 ADD EXPENSE
# -------------------------------
st.header("💸 Add Expense")

user_id = st.number_input("User ID", min_value=1)
amount = st.number_input("Amount", min_value=0)
category = st.text_input("Category")

if st.button("Add Expense"):
    res = requests.post(
        f"{BASE_URL}/expense",
        params={
            "user_id": user_id,
            "amount": amount,
            "category": category
        }
    )
    st.write(res.json())


# -------------------------------
# 🔹 SWIPE
# -------------------------------
st.header("👉 Swipe (Behavior)")

expense_id = st.number_input("Expense ID", min_value=1)
tag = st.selectbox("Tag", ["essential", "impulsive"])

if st.button("Swipe"):
    res = requests.post(
        f"{BASE_URL}/expense/swipe",
        params={
            "expense_id": expense_id,
            "tag": tag
        }
    )
    st.write(res.json())


# -------------------------------
# 🔹 DASHBOARD
# -------------------------------
st.header("📊 Dashboard")

if st.button("Get Dashboard"):
    res = requests.get(f"{BASE_URL}/dashboard/{user_id}")
    st.write(res.json())


# -------------------------------
# 🔹 INSIGHTS
# -------------------------------
st.header("🧠 Insights")

if st.button("Get Insights"):
    res = requests.get(f"{BASE_URL}/insights/{user_id}")
    st.write(res.json())


# -------------------------------
# 🔹 PLANNED EXPENSE
# -------------------------------
st.header("📅 Planned Expense")

planned_amount = st.number_input("Planned Amount", min_value=0)
planned_date = st.date_input("Planned Date")

if st.button("Add Planned Expense"):
    res = requests.post(
        f"{BASE_URL}/planned",
        params={
            "user_id": user_id,
            "amount": planned_amount,
            "planned_date": str(planned_date)
        }
    )
    st.write(res.json())


# ===============================
# ⚡ DYNAMIC LIMIT ENGINE
# ===============================

st.header("⚡ Dynamic Spending Limit Engine")

if st.button("Get Dynamic Limit"):
    res = requests.get(f"{BASE_URL}/dynamic-limit/{user_id}")

    if res.status_code != 200:
        st.error("Error fetching dynamic limit")
    else:
        data = res.json()

        if "error" in data:
            st.error(data["error"])
        else:
            col1, col2, col3 = st.columns(3)

            col1.metric("💰 Dynamic Limit", f"₹{data['dynamic_limit']}")
            col2.metric("🟢 Safe to Spend Now", f"₹{data['safe_spend_now']}")
            col3.metric("📊 Status", data["status"].upper())

            st.divider()

            st.subheader("🧠 Decision Factors")

            col4, col5, col6 = st.columns(3)

            col4.metric("Behavior", data["behavior_factor"])
            col5.metric("Context", data["context_factor"])
            col6.metric("Goal", data["goal_factor"])

            st.divider()

            st.subheader("📌 Explanation")

            if data["explanation"]:
                for key, value in data["explanation"].items():
                    st.write(f"**{key.capitalize()}**: {value}")
            else:
                st.success("All factors look healthy ")

            st.divider()

            if data["safe_spend_now"] == 0:
                st.error("🚨 You have reached today's limit. Avoid further spending.")
            elif data["safe_spend_now"] < 100:
                st.warning("⚠️ Low remaining spend. Be cautious.")
            else:
                st.success(" You are within a safe spending range.")


# ===============================
# 🧠 AI BEHAVIOR ENGINE (NEW)
# ===============================

st.header("🧠 AI Behavior Analysis Engine")

if st.button("Analyze Behavior"):
    res = requests.get(f"{BASE_URL}/ai-behavior/{user_id}")

    if res.status_code != 200:
        st.error("Error fetching behavior analysis")
    else:
        data = res.json()

        if "error" in data:
            st.error(data["error"])
        else:
            # 🔹 Summary
            col1, col2, col3 = st.columns(3)

            col1.metric("📊 Behavior Score", data["behavior_score"])
            col2.metric("⚠️ Risk Level", data["risk_level"].upper())
            col3.metric("🧬 Profile", data["behavior_profile"].capitalize())

            st.divider()

            # 🔹 Patterns
            st.subheader("📊 Patterns")
            st.json(data["patterns"])

            st.divider()

            # 🔹 Insights
            st.subheader("🧠 Insights")
            for insight in data["insights"]:
                st.write(f"- {insight}")

            # 🔹 Recommendations
            st.subheader(" Recommendations")
            for rec in data["recommendations"]:
                st.write(f"- {rec}")

            st.divider()

            # 🔹 Chart
            st.subheader("📊 Spending Behavior Chart")

            chart_data = data["simulation"].get("chart", [])

            if chart_data:
                df = pd.DataFrame(chart_data)
                st.bar_chart(df.set_index("date")[["actual", "predicted"]])
                st.caption("Actual vs Predicted Spending")
            else:
                st.info("Not enough data for chart")

            st.divider()

            # 🔹 Projection
            st.subheader("🔮 Future Projection")

            projection = data["simulation"].get("projection", {})

            if projection:
                col4, col5, col6 = st.columns(3)

                col4.metric("💸 Current 5Y Spend", f"₹{projection.get('current_spend_5y', 0)}")
                col5.metric("📉 Improved 5Y Spend", f"₹{projection.get('improved_spend_5y', 0)}")
                col6.metric("💰 Potential Savings", f"₹{projection.get('potential_savings', 0)}")

                st.info(projection.get("note", ""))

                if "warning" in projection:
                    st.warning(projection["warning"])
            else:
                st.info("Projection not available")