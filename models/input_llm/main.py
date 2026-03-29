import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# ---------------- SETUP ---------------- #

load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0.5,
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=4000
)

# ---------------- PROMPT TEMPLATE ---------------- #

template = """
You are an advanced AI financial behavior analyst integrated into a system called "KRED".

Your role is to analyze a Gen Z student's academic, financial, lifestyle, and background data to generate deep, structured insights that address the problem of "Retirement Blindness" — the tendency to ignore long-term financial planning due to focus on short-term lifestyle.

You must transform raw input data into meaningful, personalized, and actionable insights that:
- Reveal hidden long-term consequences
- Quantify future outcomes
- Bridge the gap between awareness and action
- Drive behavioral change

---

### INPUT DATA

You will receive structured user data containing:

1. Personal & Academic Information  
2. Financial Data  
3. Family Background  
4. Lifestyle & Health Metrics  

Use ALL inputs. Do not ignore any field.

---

### ANALYSIS OBJECTIVE

You must evaluate:

- Current financial stability  
- Behavioral discipline  
- Long-term wealth trajectory  
- Career growth potential  
- Health-to-finance impact  
- Dependency and responsibility burden  

You must connect PRESENT behavior → FUTURE consequences.

---

### OUTPUT REQUIREMENTS

Generate the following outputs in a structured format.

---

### 1. SUMMARY INSIGHT (MANDATORY)

Provide a concise paragraph summarizing:
- Current situation
- Key risks
- Long-term outlook

Tone: Professional, clear, impactful.

---

### 2. KEY METRIC SCORES (0–100)

Compute and explain:

- Retirement Readiness Index  
- Savings Discipline Score  
- Financial Burn Rate Indicator  
- Lifestyle Risk Index  
- Career Growth Potential Score  
- Financial Dependency Ratio  
- Wealth Acceleration Potential  
- Intervention Urgency Level  

Each must include:
- Score (0–100)
- 1-line explanation

---

### 3. FUTURE PROJECTIONS

Generate:

- Future Wealth Projection (qualitative + approximate numeric)
- Retirement Delay Risk (Low / Medium / High)
- Future Lifestyle Tier (Comfortable / Stable / At Risk)

---

### 4. LIFEPATH ANALYSIS (CORE FEATURE)

Simulate TWO paths:

A. Current Behavior Path  
B. Optimized Behavior Path  

Compare:
- Wealth
- Career growth
- Financial stability

Clearly explain the gap.

---

### 5. MICRO-REGRET INSIGHTS (CRITICAL)

Generate 3–5 statements like:

- "Spending ₹X today = ₹Y lost in future wealth"
- "Delaying savings by Z months reduces future wealth by …"

Make them:
- Short
- Impactful
- Emotionally engaging

---

### 6. OPPORTUNITY COST ANALYSIS

Identify:
- Missed savings opportunities
- Underutilized income potential
- Inefficient spending patterns

---

### 7. BEHAVIORAL PROFILE

Classify the user as:
- Disciplined / Moderate / Impulsive  

Explain WHY based on data.

---

### 8. HEALTH → WEALTH IMPACT

Analyze:
- Sleep
- Screen time
- Health score  

Explain how these affect:
- Productivity
- Future income
- Medical expenses

---

### 9. PEER COMPARISON (GEN Z CONTEXT)

Compare user with similar peers:

- Below Average / Average / Above Average  

Based on:
- Savings
- Discipline
- Career readiness

---

### 10. ACTIONABLE RECOMMENDATIONS (VERY IMPORTANT)

Provide:

- 5–7 specific actions  
- Must be:
  - Practical
  - Personalized
  - Immediate

---

### 11. FINAL INSIGHT STATEMENT

End with a powerful statement that:

- Connects present actions to future consequences  
- Motivates behavioral change  

---

### OUTPUT FORMAT (STRICT)

Return ONLY valid JSON:

{{
  "summary": "...",
  "scores": {{
    "retirement_readiness": {{ "value": X, "reason": "..." }}
  }},
  "future_projection": {{ ... }},
  "lifepath_analysis": {{ ... }},
  "micro_regret": [ ... ],
  "opportunity_cost": [ ... ],
  "behavior_profile": "...",
  "health_impact": "...",
  "peer_comparison": "...",
  "recommendations": [ ... ],
  "final_statement": "..."
}}

---

### IMPORTANT RULES

- Do NOT hallucinate data  
- Base all insights on given inputs  
- Be precise, not generic  
- Avoid vague advice  
- Focus on cause → effect relationships  
- Make outputs understandable for a student  

---

### GOAL

Your output must make the user feel:

- "I understand my future clearly"
- "My current behavior has real consequences"
- "I need to act now"

---

### USER DATA

{user_input}
"""

prompt = PromptTemplate(
    input_variables=["user_input"],
    template=template
)

# ---------------- DEFAULT VALUES ---------------- #

def get_default_user_data():
    """Return default values for a mid-range student"""
    return {
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

# ---------------- INPUT COLLECTION WITH DEFAULTS ---------------- #

def get_user_input():
    print("\nEnter User Details (Press Enter to use default values):\n")
    
    defaults = get_default_user_data()
    
    # Helper function to get input with default
    def get_input_with_default(prompt_text, default_value, input_type=str):
        user_input = input(f"{prompt_text} (Default: {default_value}): ").strip()
        if user_input == "":
            return default_value
        try:
            if input_type == int:
                return int(user_input)
            elif input_type == float:
                return float(user_input)
            else:
                return user_input
        except ValueError:
            print(f"Invalid input. Using default: {default_value}")
            return default_value
    
    data = {
        "Full Name": get_input_with_default("Full Name", defaults["Full Name"], str),
        "Age": get_input_with_default("Current Age", defaults["Age"], int),
        "Gender": get_input_with_default("Gender", defaults["Gender"], str),
        "Country": get_input_with_default("Country", defaults["Country"], str),
        "Education Level": get_input_with_default("Education Level", defaults["Education Level"], str),
        "Field of Study": get_input_with_default("Field of Study", defaults["Field of Study"], str),
        "Institution Tier": get_input_with_default("Institution Tier (1/2/3)", defaults["Institution Tier"], int),
        "CGPA": get_input_with_default("CGPA/GPA", defaults["CGPA"], float),
        "Study Hours": get_input_with_default("Study Hours per Week", defaults["Study Hours"], int),
        "Target Career": get_input_with_default("Target Career", defaults["Target Career"], str),
        "Skill Level": get_input_with_default("Skill Level", defaults["Skill Level"], str),
        "Internships": get_input_with_default("Internships (0/1/2)", defaults["Internships"], int),
        "Consistency": get_input_with_default("Consistency (0–10)", defaults["Consistency"], int),
        "Monthly Income": get_input_with_default("Monthly Income (Rs)", defaults["Monthly Income"], float),
        "Fixed Expenses": get_input_with_default("Fixed Expenses (Rs)", defaults["Fixed Expenses"], float),
        "Variable Expenses": get_input_with_default("Variable Expenses (Rs)", defaults["Variable Expenses"], float),
        "Weekly Spending": get_input_with_default("Weekly Spending (Rs)", defaults["Weekly Spending"], float),
        "Current Savings": get_input_with_default("Current Savings (Rs)", defaults["Current Savings"], float),
        "Savings Target": get_input_with_default("Savings Target (Rs)", defaults["Savings Target"], float),
        "Savings Duration": get_input_with_default("Savings Duration (Months)", defaults["Savings Duration"], int),
        "Family Income": get_input_with_default("Family Income (Rs)", defaults["Family Income"], float),
        "Earning Members": get_input_with_default("Earning Members", defaults["Earning Members"], int),
        "Dependents": get_input_with_default("Dependents", defaults["Dependents"], int),
        "Father Occupation": get_input_with_default("Father Occupation", defaults["Father Occupation"], str),
        "Mother Occupation": get_input_with_default("Mother Occupation", defaults["Mother Occupation"], str),
        "Family Support": get_input_with_default("Family Support (Rs)", defaults["Family Support"], float),
        "Family Responsibility": get_input_with_default("Family Responsibility (Rs)", defaults["Family Responsibility"], float),
        "Screen Time": get_input_with_default("Screen Time (Hours)", defaults["Screen Time"], float),
        "Sleep Duration": get_input_with_default("Sleep Duration (Hours)", defaults["Sleep Duration"], float),
        "Sleep Quality": get_input_with_default("Sleep Quality (0–10)", defaults["Sleep Quality"], int),
        "Health Score": get_input_with_default("Health Score (0–10)", defaults["Health Score"], int),
        "Sick Days": get_input_with_default("Sick Days", defaults["Sick Days"], int),
        "Medical Expenses": get_input_with_default("Medical Expenses (Rs)", defaults["Medical Expenses"], float)
    }
    
    return data

# ---------------- MAIN ---------------- #

def main():
    user_data = get_user_input()

    user_input_str = "\n".join([f"{k}: {v}" for k, v in user_data.items()])
    final_prompt = prompt.format(user_input=user_input_str)

    print("\nAnalyzing...\n")

    try:
        response = llm.invoke(final_prompt)
        raw_output = response.content

        # ---------------- JSON PARSING ---------------- #
        # Try to extract JSON from the response
        try:
            # Find JSON in the response (in case there's text before/after)
            start_idx = raw_output.find('{')
            end_idx = raw_output.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = raw_output[start_idx:end_idx]
                llm_output = json.loads(json_str)
            else:
                llm_output = json.loads(raw_output)
        except Exception as e:
            print("⚠️ JSON parsing failed. Returning raw output.")
            print(f"Error: {e}")
            print(f"Raw output: {raw_output[:500]}...")  # Show first 500 chars
            llm_output = {"raw_output": raw_output}

        # ---------------- COMBINED OBJECT ---------------- #
        kred_profile = {
            "user_input": user_data,
            "llm_output": llm_output
        }

        print("\n----- FINAL STRUCTURED OUTPUT -----\n")
        print(json.dumps(kred_profile, indent=4))

        return kred_profile
        
    except Exception as e:
        print(f"\n❌ Error during LLM invocation: {e}")
        return None


if __name__ == "__main__":
    main()