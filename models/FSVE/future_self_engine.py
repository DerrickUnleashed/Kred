"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          KRED — FUTURE SELF VISUALIZATION ENGINE                           ║
║          Minimal Input + Emotional AI + Future Self Images                 ║
║          Powered by Hugging Face FLUX.2 (Free)                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from dataclasses import dataclass
from typing import Optional, Dict, List
import warnings
import json
import os
import base64
from datetime import datetime
from io import BytesIO
import random
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print(" Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed. Install: pip install python-dotenv")

# Fix for Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

warnings.filterwarnings("ignore")

# Try to import Hugging Face client
try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("⚠️ huggingface_hub not installed. Run: pip install huggingface_hub")

# Try to import PIL for image handling
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL not installed. Install: pip install Pillow")


# ─────────────────────────────────────────────────────────────────────────────
# PART 1: MINIMAL USER INPUT
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class MinimalUserProfile:
    """Minimal input for students - only essential info."""
    name: str
    age: int
    monthly_income: float
    monthly_expenses: float
    current_savings: float
    photo_path: Optional[str] = None
    base64_photo: Optional[str] = None
    
    def __post_init__(self):
        """Auto-calculate derived fields with safe division."""
        # Ensure income is positive to avoid division by zero
        if self.monthly_income <= 0:
            self.monthly_income = 1.0
            print("  ⚠️ Income set to minimum Rs.1 for calculations")
        
        # Ensure expenses don't exceed income
        if self.monthly_expenses > self.monthly_income:
            self.monthly_expenses = self.monthly_income * 0.8
            print(f"  ⚠️ Expenses adjusted to Rs.{self.monthly_expenses:,.0f} (80% of income)")
        
        # Safe calculation of savings rate
        self.savings_rate = max(0, min(100, (self.monthly_income - self.monthly_expenses) / self.monthly_income * 100))
        
        # Default values
        self.retirement_age = 60
        self.expected_return_rate = 10.0
        self.inflation_rate = 6.0
        self.risk_profile = "medium"
        self.years_to_retire = max(0, self.retirement_age - self.age)
        
        # Emotional state detection
        if self.savings_rate < 10:
            self.emotional_state = "anxious"
            self.awareness_message = "⚠️ Your savings are very low. Let's see what happens if you save just a little more."
        elif self.savings_rate < 20:
            self.emotional_state = "cautious"
            self.awareness_message = "🌱 You're on the right track! Small changes today create big differences tomorrow."
        elif self.savings_rate < 35:
            self.emotional_state = "hopeful"
            self.awareness_message = "🌟 Good savings habit! Let's visualize how this grows over time."
        else:
            self.emotional_state = "inspired"
            self.awareness_message = "🔥 Amazing savings discipline! Your future self will thank you."
        
        # Load photo if provided
        if self.photo_path and os.path.exists(self.photo_path):
            try:
                with open(self.photo_path, "rb") as f:
                    self.base64_photo = base64.b64encode(f.read()).decode('utf-8')
                print(f"  ✓ Photo loaded: {self.photo_path}")
            except Exception as e:
                print(f"  ⚠️ Could not load photo: {e}")
                self.photo_path = None


# ─────────────────────────────────────────────────────────────────────────────
# PART 2: FINANCIAL SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

class SimpleFinancialSimulator:
    """Simplified financial projection engine."""
    
    def __init__(self, profile: MinimalUserProfile):
        self.p = profile
    
    def simulate_scenario(self, savings_boost: float = 0) -> dict:
        """Simulate future wealth with optional savings boost."""
        base_monthly_savings = self.p.monthly_income * (self.p.savings_rate / 100)
        boosted_savings = base_monthly_savings * (1 + savings_boost / 100)
        
        r_monthly = (self.p.expected_return_rate / 100) / 12
        n_months = max(1, self.p.years_to_retire * 12)
        
        wealth_current = self.p.current_savings
        wealth_boosted = self.p.current_savings
        
        yearly_current = []
        yearly_boosted = []
        
        for month in range(1, n_months + 1):
            wealth_current = wealth_current * (1 + r_monthly) + base_monthly_savings
            wealth_boosted = wealth_boosted * (1 + r_monthly) + boosted_savings
            
            if month % 12 == 0:
                yearly_current.append(wealth_current)
                yearly_boosted.append(wealth_boosted)
        
        # Handle empty yearly data
        if not yearly_current:
            yearly_current = [wealth_current]
            yearly_boosted = [wealth_boosted]
        
        # Inflation adjustment
        real_current = wealth_current / ((1 + self.p.inflation_rate / 100) ** max(1, self.p.years_to_retire))
        real_boosted = wealth_boosted / ((1 + self.p.inflation_rate / 100) ** max(1, self.p.years_to_retire))
        
        return {
            "current": {
                "monthly_savings": round(base_monthly_savings, 2),
                "final_corpus": round(wealth_current, 2),
                "real_corpus": round(real_current, 2),
                "monthly_retirement_income": round(real_current * 0.04 / 12, 2),
                "yearly_wealth": yearly_current
            },
            "improved": {
                "monthly_savings": round(boosted_savings, 2),
                "final_corpus": round(wealth_boosted, 2),
                "real_corpus": round(real_boosted, 2),
                "monthly_retirement_income": round(real_boosted * 0.04 / 12, 2),
                "yearly_wealth": yearly_boosted,
                "savings_boost": savings_boost
            },
            "difference": {
                "corpus_gap": round(real_boosted - real_current, 2),
                "monthly_income_gap": round((real_boosted * 0.04 / 12) - (real_current * 0.04 / 12), 2),
                "percentage_improvement": round(((real_boosted - real_current) / max(real_current, 1)) * 100, 2)
            }
        }


# ─────────────────────────────────────────────────────────────────────────────
# PART 3: HUGGING FACE AI IMAGE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

class HuggingFaceImageGenerator:
    """Generate future self images using Hugging Face Inference API (Free)."""
    
    def __init__(self, profile: MinimalUserProfile):
        self.profile = profile
        self.client = None
        self.hf_token = None
        
        # Try to get token from environment variable
        self.hf_token = os.environ.get("HF_TOKEN")
        
        if not self.hf_token:
            print("\n⚠️ HF_TOKEN not found in environment variables!")
            print("   Please set HF_TOKEN in your .env file or environment.")
            print("   Format: HF_TOKEN=hf_your_token_here\n")
        else:
            print(f" HF_TOKEN found (length: {len(self.hf_token)} characters)")
            
            if HF_AVAILABLE:
                try:
                    self.client = InferenceClient(
                        provider="fal-ai",
                        api_key=self.hf_token
                    )
                    print(" Hugging Face AI client initialized successfully!")
                except Exception as e:
                    print(f"⚠️ Could not initialize Hugging Face client: {e}")
                    self.client = None
            else:
                print("⚠️ huggingface_hub not installed. Run: pip install huggingface_hub")
    
    def is_available(self) -> bool:
        """Check if image generation is available."""
        return self.client is not None and self.hf_token is not None
    
    def generate_stage_image(self, age: int, wealth: float, message: str) -> str:
        """Generate AI image of user at a specific age."""
        
        if not self.is_available():
            print(f"  ⚠️ AI image generation not available. Check HF_TOKEN setup.")
            return self._create_text_based_image(age, wealth, message)
        
        try:
            # Build age-appropriate prompt
            if age <= 30:
                style = "young professional, energetic, vibrant, modern"
            elif age <= 50:
                style = "middle-aged, successful, confident, established"
            else:
                style = "elderly, wise, content, peaceful, experienced"
            
            # Financial context based on wealth
            if wealth > 1_00_00_000:  # > 1 Crore
                context = "living in a luxurious home, smiling happily, successful lifestyle"
            elif wealth > 50_00_000:  # > 50 Lakhs
                context = "living in a comfortable home, content, enjoying life"
            elif wealth > 10_00_000:  # > 10 Lakhs
                context = "living modestly, hopeful expression, planning for future"
            else:
                context = "simple life, thoughtful expression, determined look"
            
            # Personalized prompt with user's name
            prompt = (
                f"High quality portrait of {self.profile.name}, a {age} year old Indian person, "
                f"{style}, {context}, realistic photograph style, soft warm lighting, "
                f"natural smile, high detail, professional photography, 4k resolution, "
                f"sharp focus, beautiful composition"
            )
            
            negative_prompt = (
                "cartoon, anime, drawing, painting, sketch, distorted, blurry, ugly, "
                "deformed, extra limbs, bad anatomy, watermark, text, logo, signature, "
                "grayscale, black and white, sad, crying"
            )
            
            print(f"  🎨 Generating your age {age} portrait...")
            print(f"     Prompt: {prompt[:100]}...")
            
            # Call Hugging Face API with better parameters
            image = self.client.text_to_image(
                prompt=prompt,
                model="black-forest-labs/FLUX.2-klein-4B",
                negative_prompt=negative_prompt,
                num_inference_steps=25,  # More steps = better quality
                guidance_scale=7.5,
                height=768,  # Higher resolution
                width=768
            )
            
            print(f"  ✓ Image generated successfully!")
            
            # Add financial overlay text
            if PIL_AVAILABLE:
                try:
                    draw = ImageDraw.Draw(image)
                    
                    # Try to load a better font, fallback to default
                    try:
                        # Windows font
                        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 24)
                    except:
                        try:
                            # Linux font
                            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 24)
                        except:
                            font = ImageFont.load_default()
                    
                    # Draw semi-transparent overlay for text
                    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
                    overlay_draw = ImageDraw.Draw(overlay)
                    overlay_draw.rectangle([(0, 0), (image.width, 100)], fill=(0, 0, 0, 180))
                    image.paste(overlay, (0, 0), overlay)
                    
                    # Add text overlay
                    draw.text((20, 15), f"✨ AGE: {age}", fill=(255, 255, 255), font=font)
                    draw.text((20, 50), f"💰 WEALTH: Rs.{wealth:,.0f}", fill=(255, 255, 255), font=font)
                    
                    # Add message at bottom
                    msg_lines = self._wrap_text(message, 45)
                    y_pos = image.height - 80
                    for line in msg_lines[:3]:
                        draw.text((20, y_pos), line, fill=(200, 255, 200), font=font)
                        y_pos += 30
                    
                except Exception as e:
                    print(f"  ⚠️ Could not add overlay text: {e}")
            
            # Save image with high quality
            filename = f"future_self_age_{age}.png"
            image.save(filename, quality=95)
            print(f"  ✓ Saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"  ❌ Image generation failed: {e}")
            print(f"     Check your internet connection and HF_TOKEN")
            return self._create_text_based_image(age, wealth, message)
    
    def generate_comparison_image(self, age: int, current_wealth: float, improved_wealth: float, message: str) -> str:
        """Generate side-by-side comparison of current vs improved future."""
        
        if not self.is_available():
            return None
        
        try:
            prompt = (
                f"Split screen portrait of {self.profile.name} at age {age}, "
                f"left side showing modest lifestyle, right side showing successful wealthy lifestyle, "
                f"realistic style, Indian person, professional photography, high quality"
            )
            
            print(f"  🎨 Generating comparison for age {age}...")
            
            image = self.client.text_to_image(
                prompt=prompt,
                model="black-forest-labs/FLUX.2-klein-4B",
                num_inference_steps=25,
                guidance_scale=7.5,
                height=512,
                width=1024
            )
            
            # Add comparison text
            if PIL_AVAILABLE:
                draw = ImageDraw.Draw(image)
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                
                draw.text((50, 30), f"Current: Rs.{current_wealth:,.0f}", fill=(255, 100, 100), font=font)
                draw.text((image.width - 300, 30), f"Improved: Rs.{improved_wealth:,.0f}", fill=(100, 255, 100), font=font)
                draw.text((20, image.height - 50), message[:60], fill=(255, 255, 255), font=font)
            
            filename = f"future_self_comparison_age_{age}.png"
            image.save(filename)
            print(f"  ✓ Saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"  ⚠️ Comparison image failed: {e}")
            return None
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to fit within width."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word) + 1
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _create_text_based_image(self, age: int, wealth: float, message: str) -> str:
        """Fallback text-based representation with proper encoding."""
        filename = f"future_self_age_{age}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"  YOUR FUTURE SELF AT AGE {age}\n")
            f.write("=" * 60 + "\n")
            f.write(f"  Wealth: Rs.{wealth:,.0f}\n")
            f.write(f"  {message}\n")
            f.write("=" * 60 + "\n")
            f.write("\n   TIP: To generate real AI images:\n")
            f.write("     1. Get HF_TOKEN from huggingface.co/settings/tokens\n")
            f.write("     2. Add to .env file: HF_TOKEN=hf_your_token\n")
            f.write("     3. Run the script again\n")
        print(f"  ✓ Saved text representation: {filename}")
        return filename


# ─────────────────────────────────────────────────────────────────────────────
# PART 4: EMOTIONAL AWARENESS ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class EmotionalAwarenessEngine:
    """Generates emotionally resonant messages."""
    
    @staticmethod
    def get_life_stage_messages(profile: MinimalUserProfile, simulation: dict) -> Dict[int, str]:
        """Generate messages for different life stages."""
        ages = [30, 40, 50, 60]
        messages = {}
        
        for age in ages:
            if age <= profile.age:
                messages[age] = f"🎯 You are {age} years old now. Keep going!"
                continue
            
            years = age - profile.age
            target_wealth = EmotionalAwarenessEngine._estimate_wealth_at_age(simulation, years)
            
            if target_wealth < 10_00_000:
                message = f"⚠️ At {age}, your wealth could be Rs.{target_wealth:,.0f}. Start saving more today!"
            elif target_wealth < 50_00_000:
                message = f"🌱 At {age}, you could have Rs.{target_wealth:,.0f}. Good foundation!"
            elif target_wealth < 1_00_00_000:
                message = f"🌟 At {age}, you could reach Rs.{target_wealth:,.0f}! Amazing progress!"
            else:
                message = f"✨ At {age}, you could have Rs.{target_wealth:,.0f}! Future you is smiling!"
            
            messages[age] = message
        
        return messages
    
    @staticmethod
    def _estimate_wealth_at_age(simulation: dict, years: int) -> float:
        yearly_data = simulation["current"]["yearly_wealth"]
        if yearly_data and years <= len(yearly_data):
            return yearly_data[years - 1]
        return yearly_data[-1] if yearly_data else 0
    
    @staticmethod
    def get_motivational_message(simulation: dict, profile: MinimalUserProfile) -> str:
        gap = simulation["difference"]["corpus_gap"]
        current_income = simulation["current"]["monthly_retirement_income"]
        improved_income = simulation["improved"]["monthly_retirement_income"]
        
        if gap <= 0:
            return f"🎉 {profile.name}, you're on the right track! Your future self will have Rs.{current_income:,.0f} monthly in retirement."
        
        if gap < 10_00_000:
            return f" {profile.name}, by saving just a little more each month, you could add Rs.{improved_income - current_income:,.0f} to your monthly retirement income."
        
        if gap < 50_00_000:
            return f"🌟 {profile.name}, imagine having Rs.{improved_income:,.0f} every month instead of Rs.{current_income:,.0f}. Small steps matter!"
        
        return f"🔥 {profile.name}, you have the power to create a Rs.{gap:,.0f} difference in your future! Every Rs.100 saved today makes a huge impact."


# ─────────────────────────────────────────────────────────────────────────────
# PART 5: FINANCIAL VISUALIZER
# ─────────────────────────────────────────────────────────────────────────────

class FinancialVisualizer:
    """Create beautiful financial projection graphs."""
    
    def __init__(self, profile: MinimalUserProfile):
        self.profile = profile
    
    def create_dashboard(self, simulation: dict) -> str:
        """Create comprehensive financial dashboard."""
        fig = plt.figure(figsize=(16, 10))
        fig.patch.set_facecolor('#0d1117')
        gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.3)
        
        # Chart 1: Wealth Growth
        ax1 = fig.add_subplot(gs[0, :])
        self._plot_wealth_growth(ax1, simulation)
        
        # Chart 2: Monthly Income Comparison
        ax2 = fig.add_subplot(gs[1, 0])
        self._plot_income_comparison(ax2, simulation)
        
        # Chart 3: Savings Impact
        ax3 = fig.add_subplot(gs[1, 1])
        self._plot_savings_impact(ax3, simulation)
        
        fig.suptitle(f"KRED — {self.profile.name}'s Financial Future",
                     color='#e6edf3', fontsize=18, fontweight='bold', y=0.98)
        
        filename = "kred_financial_dashboard.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close()
        
        return filename
    
    def _plot_wealth_growth(self, ax, simulation):
        years = list(range(self.profile.age + 1, min(self.profile.retirement_age + 1, self.profile.age + len(simulation["current"]["yearly_wealth"]) + 1)))
        current_yearly = simulation["current"]["yearly_wealth"]
        improved_yearly = simulation["improved"]["yearly_wealth"]
        
        years = years[:len(current_yearly)]
        current_yearly = current_yearly[:len(years)]
        improved_yearly = improved_yearly[:len(years)]
        
        if years:
            ax.plot(years, [v/1e6 for v in current_yearly], 
                    color='#58a6ff', linewidth=2.5, label='Current Path')
            ax.plot(years, [v/1e6 for v in improved_yearly], 
                    color='#3fb950', linewidth=2.5, linestyle='--', label='With Small Change')
            ax.fill_between(years, 
                           [v/1e6 for v in current_yearly],
                           [v/1e6 for v in improved_yearly],
                           alpha=0.2, color='#3fb950')
        
        ax.set_title("Your Wealth Journey", color='#e6edf3', fontsize=12, fontweight='bold')
        ax.set_xlabel("Age", color='#8b949e')
        ax.set_ylabel("Corpus (Rs. Millions)", color='#8b949e')
        ax.legend(facecolor='#161b22', labelcolor='#e6edf3')
        ax.grid(color='#21262d', linewidth=0.5)
        ax.set_facecolor('#161b22')
    
    def _plot_income_comparison(self, ax, simulation):
        current_income = simulation["current"]["monthly_retirement_income"]
        improved_income = simulation["improved"]["monthly_retirement_income"]
        
        bars = ax.bar(['Current', 'With 10% More Savings'], 
                     [max(0, current_income/1000), max(0, improved_income/1000)],
                     color=['#58a6ff', '#3fb950'], edgecolor='#30363d')
        
        for bar, val in zip(bars, [current_income/1000, improved_income/1000]):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                       f'Rs.{val:.0f}K', ha='center', va='bottom', color='#e6edf3')
        
        ax.set_title("Monthly Retirement Income", color='#e6edf3', fontsize=12, fontweight='bold')
        ax.set_ylabel("Thousands (Rs.)", color='#8b949e')
        ax.set_facecolor('#161b22')
    
    def _plot_savings_impact(self, ax, simulation):
        pct_improvement = simulation["difference"]["percentage_improvement"]
        
        ax.pie([max(0, pct_improvement), max(0, 100 - pct_improvement)], 
               colors=['#3fb950', '#30363d'], startangle=90)
        ax.text(0, 0, f'+{pct_improvement:.0f}%\nBetter', 
               ha='center', va='center', color='#e6edf3', fontsize=12, fontweight='bold')
        ax.set_title(f"Wealth Improvement Potential", color='#e6edf3', fontsize=12, fontweight='bold')


# ─────────────────────────────────────────────────────────────────────────────
# PART 6: MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

def get_minimal_user_input():
    """Get only essential inputs from user with validation."""
    print("\n" + "=" * 60)
    print("  KRED — Your Financial Future Visualizer")
    print("  Let's imagine your future self")
    print("=" * 60)
    
    print("\n📝 Just a few quick questions:\n")
    
    name = input("  What's your name? ").strip() or "Friend"
    
    # Age validation
    while True:
        try:
            age = int(input("  Your age: "))
            if 0 <= age <= 120:
                break
            else:
                print("  ⚠️ Please enter a valid age between 0 and 120")
        except ValueError:
            print("  ⚠️ Please enter a valid number")
    
    # Income validation
    while True:
        try:
            monthly_income = float(input("  Monthly income (Rs.): "))
            if monthly_income >= 0:
                break
            else:
                print("  ⚠️ Income cannot be negative")
        except ValueError:
            print("  ⚠️ Please enter a valid number")
    
    # Expenses validation
    while True:
        try:
            monthly_expenses = float(input("  Monthly expenses (Rs.): "))
            if 0 <= monthly_expenses <= monthly_income:
                break
            elif monthly_expenses < 0:
                print("  ⚠️ Expenses cannot be negative")
            else:
                print(f"  ⚠️ Expenses (Rs.{monthly_expenses:,.0f}) cannot exceed income (Rs.{monthly_income:,.0f})")
        except ValueError:
            print("  ⚠️ Please enter a valid number")
    
    # Savings validation
    while True:
        try:
            current_savings = float(input("  Current savings (Rs.): "))
            if current_savings >= 0:
                break
            else:
                print("  ⚠️ Savings cannot be negative")
        except ValueError:
            print("  ⚠️ Please enter a valid number")
    
    # Optional: photo upload
    photo_path = None
    photo_choice = input("\n  Want to see your future self? Upload a photo? (y/n): ").strip().lower()
    if photo_choice == 'y':
        photo_path = input("  Enter photo path (e.g., C:/path/to/photo.jpg): ").strip()
        if not os.path.exists(photo_path):
            print("  ⚠️ Photo not found. Using text visualization instead.")
            photo_path = None
    
    return MinimalUserProfile(
        name=name,
        age=age,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        current_savings=current_savings,
        photo_path=photo_path
    )


def main():
    """Main application flow."""
    # Get minimal user input
    profile = get_minimal_user_input()
    
    print(f"\n✨ Hi {profile.name}! Let's visualize your future...")
    print(profile.awareness_message)
    
    # Run simulation
    simulator = SimpleFinancialSimulator(profile)
    simulation = simulator.simulate_scenario(savings_boost=10)
    
    # Generate emotional messages
    emotional_engine = EmotionalAwarenessEngine()
    life_stage_messages = emotional_engine.get_life_stage_messages(profile, simulation)
    motivational_message = emotional_engine.get_motivational_message(simulation, profile)
    
    # Display financial snapshot
    print("\n" + "=" * 60)
    print("  📊 YOUR FINANCIAL SNAPSHOT")
    print("=" * 60)
    print(f"  Current Monthly Savings: Rs.{simulation['current']['monthly_savings']:,.0f}")
    print(f"  If you save Rs.{simulation['improved']['monthly_savings'] - simulation['current']['monthly_savings']:,.0f} more each month...")
    print(f"  Your retirement corpus could grow by Rs.{simulation['difference']['corpus_gap']:,.0f}")
    print(f"  That's +{simulation['difference']['percentage_improvement']:.1f}% more wealth!")
    
    # Initialize AI image generator
    image_gen = HuggingFaceImageGenerator(profile)
    
    # Check if AI is available
    if not image_gen.is_available():
        print("\n" + "=" * 60)
        print("  🔑 HUGGING FACE TOKEN REQUIRED")
        print("=" * 60)
        print("\n  To generate AI images of your future self, you need a Hugging Face token.")
        print("  Steps to get your token:")
        print("    1. Sign up at: https://huggingface.co/join")
        print("    2. Go to: https://huggingface.co/settings/tokens")
        print("    3. Click 'New token' and copy it")
        print("    4. Add to .env file: HF_TOKEN=hf_your_token")
        print("\n   Without token, you'll get text-based visualization only.")
        
        use_ai = input("\n  Continue without AI images? (y/n): ").strip().lower()
        if use_ai != 'y':
            print("\n  👋 See you next time! Set HF_TOKEN and run again.")
            return
    
    # Generate future self images
    print("\n" + "=" * 60)
    print("  🎨 CREATING YOUR FUTURE SELF PORTRAITS")
    print("=" * 60)
    
    generated_images = []
    
    for age, message in life_stage_messages.items():
        if age > profile.age:
            years = age - profile.age
            yearly_wealth = simulation["current"]["yearly_wealth"]
            if yearly_wealth and years <= len(yearly_wealth):
                wealth = yearly_wealth[years - 1]
            else:
                wealth = simulation["current"]["final_corpus"]
            
            print(f"\n  📸 Age {age} portrait:")
            print(f"     {message}")
            
            img_path = image_gen.generate_stage_image(age, wealth, message)
            generated_images.append(img_path)
            
            # Also generate comparison for key ages
            if age in [50, 60]:
                improved_yearly = simulation["improved"]["yearly_wealth"]
                if improved_yearly and years <= len(improved_yearly):
                    improved_wealth = improved_yearly[years - 1]
                else:
                    improved_wealth = simulation["improved"]["final_corpus"]
                comp_path = image_gen.generate_comparison_image(age, wealth, improved_wealth, f"Save just 10% more = +Rs.{improved_wealth - wealth:,.0f}")
                if comp_path:
                    generated_images.append(comp_path)
    
    # Create financial dashboard
    visualizer = FinancialVisualizer(profile)
    dashboard_path = visualizer.create_dashboard(simulation)
    print(f"\n  📊 Financial dashboard saved: {dashboard_path}")
    
    # Display motivational message
    print("\n" + "=" * 60)
    print("  🌟 YOUR PERSONAL MESSAGE")
    print("=" * 60)
    print(f"\n  {motivational_message}\n")
    
    # Show what-if scenarios
    print("\n" + "=" * 60)
    print("   WHAT IF YOU SAVED A LITTLE MORE?")
    print("=" * 60)
    
    for boost in [5, 10, 15, 20]:
        scenario = simulator.simulate_scenario(savings_boost=boost)
        extra_monthly = scenario["improved"]["monthly_savings"] - simulation["current"]["monthly_savings"]
        extra_corpus = scenario["difference"]["corpus_gap"]
        
        if extra_monthly > 0:
            print(f"\n  📈 Save Rs.{extra_monthly:,.0f} more/month → +Rs.{extra_corpus:,.0f} at retirement")
    
    # Save full report
    report = {
        "user": {
            "name": profile.name,
            "age": profile.age,
            "monthly_income": profile.monthly_income,
            "monthly_expenses": profile.monthly_expenses,
            "savings_rate": profile.savings_rate,
            "emotional_state": profile.emotional_state
        },
        "financial_projection": {
            "current_scenario": simulation["current"],
            "improved_scenario": simulation["improved"],
            "difference": simulation["difference"]
        },
        "life_stage_messages": life_stage_messages,
        "motivational_message": motivational_message,
        "generated_images": generated_images
    }
    
    with open("kred_future_report.json", "w", encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("   COMPLETE! Your future self report is ready.")
    print("  📁 Check these files:")
    print(f"     - {dashboard_path} (Your financial graph)")
    for img in generated_images[:5]:
        if img.endswith('.png'):
            print(f"     - {img} (AI generated image)")
        else:
            print(f"     - {img} (Text representation)")
    print("     - kred_future_report.json (Full data report)")
    print("=" * 60)
    print("\n  🌈 Remember: Small changes today create big differences tomorrow!\n")


if __name__ == "__main__":
    main()