# simple_test.py - Direct test without API
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Test if kred_package can be imported
try:
    from kred_package.core.pipeline import KredAIPipeline
    print("✅ Successfully imported KredAIPipeline")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test with minimal data
user_profile = {
    "age": 21,
    "cgpa": 7.5,
    "monthly_spend": 18000,
    "skill": "Intermediate",
    "field": "Engineering / Technology",
    "college_tier": "Tier 2",
    "edu_level": "Undergraduate",
    "study_hours": 20,
    "savings": "Medium",
    "family_bg": "Middle",
    "discipline": "Balanced",
    "consistency": "Medium",
    "screen_time": "Medium (4-6 hrs)",
    "health": "Average",
    "sleep": "Average",
    "experience": False,
    "country": "India",
    "target_career": "Engineer"
}

print("\n🚀 Running pipeline...")
try:
    pipeline = KredAIPipeline()
    result = pipeline.run(
        user_profile=user_profile,
        expenses=[],
        financial_state={"daily_limit": 600},
        user_id=1,
        generate_images=False
    )
    print(f"✅ Success! Composite Score: {result['future_self']['scores']['composite']}")
except Exception as e:
    print(f"❌ Pipeline error: {e}")
    import traceback
    traceback.print_exc()