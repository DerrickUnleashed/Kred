import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import Navbar from './Navbar';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

const API_URL = import.meta.env.VITE_STOCKS_API_URL || 'http://localhost:8000';

const SKILL_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Expert'];
const INSTITUTION_TIERS = [1, 2, 3, 4, 5];
const GENDERS = ['Male', 'Female', 'Prefer not to say'];
const EDUCATION_LEVELS = ['High School', 'Undergraduate', 'Postgraduate', 'PhD'];
const COUNTRIES = ['India', 'United States', 'United Kingdom', 'Canada', 'Australia', 'Germany', 'Singapore', 'UAE', 'Other'];

const PIE_COLORS = ['#3B82F6', '#f97316', '#ef4444', '#e879f9', '#22c55e'];
const REGRET_COLORS = ['#ef4444', '#f97316', '#f5c842', '#e879f9', '#3b82f6'];

const defaultInputs = {
  Full_Name: '',
  Age: 22,
  Gender: 'Male',
  Country: 'India',
  Education_Level: 'Undergraduate',
  Field_of_Study: 'Computer Science',
  Institution_Tier: 2,
  CGPA: 7.5,
  Study_Hours: 20,
  Target_Career: 'Software Developer',
  Skill_Level: 'Intermediate',
  Internships: 1,
  Consistency: 5,
  Monthly_Income: 50000,
  Fixed_Expenses: 15000,
  Variable_Expenses: 5000,
  Weekly_Spending: 2000,
  Current_Savings: 100000,
  Savings_Target: 500000,
  Savings_Duration: 12,
  Family_Income: 30000,
  Earning_Members: 2,
  Dependents: 2,
  Father_Occupation: '',
  Mother_Occupation: '',
  Family_Support: 5000,
  Family_Responsibility: 2000,
  Screen_Time: 4,
  Sleep_Duration: 7.0,
  Sleep_Quality: 7,
  Health_Score: 7,
  Sick_Days: 2,
  Medical_Expenses: 1000,
};

const fmtInr = (v) => {
  if (v >= 10000000) return `₹${(v / 10000000).toFixed(2)}Cr`;
  if (v >= 100000) return `₹${(v / 100000).toFixed(2)}L`;
  if (v >= 1000) return `₹${(v / 1000).toFixed(1)}K`;
  return `₹${v.toFixed(0)}`;
};

export default function AIBehavior() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [inputs, setInputs] = useState(defaultInputs);
  const [results, setResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [isLoadingData, setIsLoadingData] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const checkUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        navigate('/login');
      } else {
        setUser(user);
      }
      setLoading(false);
    };

    checkUser();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      if (!session?.user) {
        navigate('/login');
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  useEffect(() => {
    if (user) {
      loadSavedAnalysis();
    }
  }, [user]);

  const loadSavedAnalysis = async () => {
    if (!user) return;
    setIsLoadingData(true);
    
    try {
      const { data, error } = await supabase
        .from('ai_behavior_analysis')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      if (data && !error) {
        const savedInputs = {
          Full_Name: data.full_name || '',
          Age: data.age || 22,
          Gender: data.gender || 'Male',
          Country: data.country || 'India',
          Education_Level: data.education_level || 'Undergraduate',
          Field_of_Study: data.field_of_study || 'Computer Science',
          Institution_Tier: data.institution_tier || 2,
          CGPA: data.cgpa || 7.5,
          Study_Hours: data.study_hours || 20,
          Target_Career: data.target_career || 'Software Developer',
          Skill_Level: data.skill_level || 'Intermediate',
          Internships: data.internships || 1,
          Consistency: data.consistency || 5,
          Monthly_Income: data.monthly_income || 50000,
          Fixed_Expenses: data.fixed_expenses || 15000,
          Variable_Expenses: data.variable_expenses || 5000,
          Weekly_Spending: data.weekly_spending || 2000,
          Current_Savings: data.current_savings || 100000,
          Savings_Target: data.savings_target || 500000,
          Savings_Duration: data.savings_duration || 12,
          Family_Income: data.family_income || 30000,
          Earning_Members: data.earning_members || 2,
          Dependents: data.dependents || 2,
          Father_Occupation: data.father_occupation || '',
          Mother_Occupation: data.mother_occupation || '',
          Family_Support: data.family_support || 5000,
          Family_Responsibility: data.family_responsibility || 2000,
          Screen_Time: data.screen_time || 4,
          Sleep_Duration: data.sleep_duration || 7.0,
          Sleep_Quality: data.sleep_quality || 7,
          Health_Score: data.health_score || 7,
          Sick_Days: data.sick_days || 2,
          Medical_Expenses: data.medical_expenses || 1000,
        };
        setInputs(savedInputs);

        if (data.results) {
          setResults(data.results);
        }
      }
    } catch (err) {
      console.log('No saved analysis found');
    }
    
    setIsLoadingData(false);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/');
  };

  const updateField = (field, value) => {
    setInputs(prev => ({ ...prev, [field]: value }));
  };

  const saveToSupabase = async (analysisResults) => {
    if (!user) return;

    const analysisData = {
      user_id: user.id,
      full_name: inputs.Full_Name,
      age: inputs.Age,
      gender: inputs.Gender,
      country: inputs.Country,
      education_level: inputs.Education_Level,
      field_of_study: inputs.Field_of_Study,
      institution_tier: inputs.Institution_Tier,
      cgpa: inputs.CGPA,
      study_hours: inputs.Study_Hours,
      target_career: inputs.Target_Career,
      skill_level: inputs.Skill_Level,
      internships: inputs.Internships,
      consistency: inputs.Consistency,
      monthly_income: inputs.Monthly_Income,
      fixed_expenses: inputs.Fixed_Expenses,
      variable_expenses: inputs.Variable_Expenses,
      weekly_spending: inputs.Weekly_Spending,
      current_savings: inputs.Current_Savings,
      savings_target: inputs.Savings_Target,
      savings_duration: inputs.Savings_Duration,
      family_income: inputs.Family_Income,
      earning_members: inputs.Earning_Members,
      dependents: inputs.Dependents,
      father_occupation: inputs.Father_Occupation,
      mother_occupation: inputs.Mother_Occupation,
      family_support: inputs.Family_Support,
      family_responsibility: inputs.Family_Responsibility,
      screen_time: inputs.Screen_Time,
      sleep_duration: inputs.Sleep_Duration,
      sleep_quality: inputs.Sleep_Quality,
      health_score: inputs.Health_Score,
      sick_days: inputs.Sick_Days,
      medical_expenses: inputs.Medical_Expenses,
      results: analysisResults,
    };

    const { data: existing } = await supabase
      .from('ai_behavior_analysis')
      .select('id')
      .eq('user_id', user.id)
      .limit(1)
      .single();

    if (existing) {
      await supabase
        .from('ai_behavior_analysis')
        .update(analysisData)
        .eq('user_id', user.id);
    } else {
      await supabase
        .from('ai_behavior_analysis')
        .insert([analysisData]);
    }
  };

  const runAnalysis = async () => {
    setIsAnalyzing(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/lrb/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputs),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setResults(data);
      await saveToSupabase(data);
    } catch (err) {
      setError('Failed to run analysis. Please check if the backend is running.');
      console.error('Analysis error:', err);
    }

    setIsAnalyzing(false);
  };

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-400';
    if (score >= 45) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreBg = (score) => {
    if (score >= 70) return 'bg-green-500/20 border-green-500/30';
    if (score >= 45) return 'bg-yellow-500/20 border-yellow-500/30';
    return 'bg-red-500/20 border-red-500/30';
  };

  const getUrgencyColor = (urgency) => {
    if (urgency === 'Critical') return 'text-red-400';
    if (urgency === 'High') return 'text-orange-400';
    if (urgency === 'Medium') return 'text-yellow-400';
    return 'text-green-400';
  };

  const projectionChartData = () => {
    if (!results?.projections) return [];
    const years = [5, 10, 20, 30];
    return years.map(y => ({
      age: `Age ${inputs.Age + y}`,
      year: y,
      current: results.projections.current_behavior_wealth?.[y] || 0,
      optimized: results.projections.optimized_behavior_wealth?.[y] || 0,
    }));
  };

  const expensePieData = () => {
    if (!results?.financials) return [];
    const weeklyMonthly = inputs.Weekly_Spending * 4.33;
    return [
      { name: 'Fixed', value: inputs.Fixed_Expenses },
      { name: 'Variable', value: inputs.Variable_Expenses },
      { name: 'Weekly', value: weeklyMonthly },
      { name: 'Family Resp', value: inputs.Family_Responsibility },
      { name: 'Savings', value: Math.max(results.financials.monthly_savings || 0, 0) },
    ];
  };

  const regretChartData = () => {
    if (!results?.regret_analysis) return [];
    const r = results.regret_analysis;
    return [
      { name: 'Discretionary', value: r.discretionary_spending_regret || 0 },
      { name: 'Screen Time', value: r.screen_time_wealth_loss || 0 },
      { name: 'Sleep Deficit', value: r.sleep_deficit_income_loss || 0 },
      { name: 'Career Gap', value: r.career_gap_wealth_loss || 0 },
      { name: 'Health', value: r.health_negligence_loss || 0 },
    ];
  };

  const savingsProjectionData = () => {
    if (!results?.projections) return [];
    const years = [5, 10, 20, 30];
    return years.map(y => ({
      timeline: `${y} Years (Age ${inputs.Age + y})`,
      current: results.projections.current_behavior_wealth?.[y] || 0,
      optimized: results.projections.optimized_behavior_wealth?.[y] || 0,
      gap: (results.projections.optimized_behavior_wealth?.[y] || 0) - (results.projections.current_behavior_wealth?.[y] || 0),
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-text-primary">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar user={user} onLogout={handleLogout} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-8">
        <button
          onClick={() => navigate('/dashboard')}
          className="inline-flex items-center gap-2 text-text-secondary hover:text-accent mb-4 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Dashboard
        </button>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-primary">Life Intelligence Report</h1>
          <p className="text-text-secondary mt-1">
            Analysis for {inputs.Full_Name || 'User'} · Age {inputs.Age} · {inputs.Field_of_Study}
          </p>
        </div>

        {results && (
          <div className="flex flex-wrap gap-2 mb-8">
            {['overview', 'financial', 'projection', 'regret', 'ai-insights'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-xl font-medium transition-colors cursor-pointer ${
                  activeTab === tab
                    ? 'bg-accent text-white'
                    : 'bg-surface border border-secondary text-text-secondary hover:text-text-primary'
                }`}
              >
                {tab === 'ai-insights' ? 'AI Insights' : tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-8">
          <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-text-primary">Your Profile</h2>
              {isLoadingData && (
                <span className="text-accent text-sm">Loading saved data...</span>
              )}
            </div>
            
            <div className="space-y-6 max-h-[75vh] overflow-y-auto pr-2">
              <div>
                <h3 className="text-sm font-semibold text-accent uppercase tracking-wider mb-4">Personal</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-text-secondary text-sm mb-2">Full Name</label>
                    <input type="text" value={inputs.Full_Name} onChange={(e) => updateField('Full_Name', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" />
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Age</label>
                    <input type="number" value={inputs.Age} onChange={(e) => updateField('Age', parseInt(e.target.value) || 22)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" />
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Gender</label>
                    <select value={inputs.Gender} onChange={(e) => updateField('Gender', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent">
                      {GENDERS.map(g => <option key={g} value={g}>{g}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Country</label>
                    <select value={inputs.Country} onChange={(e) => updateField('Country', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent">
                      {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Education Level</label>
                    <select value={inputs.Education_Level} onChange={(e) => updateField('Education_Level', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent">
                      {EDUCATION_LEVELS.map(e => <option key={e} value={e}>{e}</option>)}
                    </select>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-accent uppercase tracking-wider mb-4">Academic</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Field of Study</label>
                    <input type="text" value={inputs.Field_of_Study} onChange={(e) => updateField('Field_of_Study', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" />
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Institution Tier</label>
                    <select value={inputs.Institution_Tier} onChange={(e) => updateField('Institution_Tier', parseInt(e.target.value))}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent">
                      {INSTITUTION_TIERS.map(t => <option key={t} value={t}>Tier {t}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">CGPA (0-10)</label>
                    <input type="number" step="0.1" min="0" max="10" value={inputs.CGPA} onChange={(e) => updateField('CGPA', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" />
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Study Hours/Week: {inputs.Study_Hours}</label>
                    <input type="range" min="0" max="60" value={inputs.Study_Hours} onChange={(e) => updateField('Study_Hours', parseInt(e.target.value))}
                      className="w-full accent-accent" />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-text-secondary text-sm mb-2">Target Career</label>
                    <input type="text" value={inputs.Target_Career} onChange={(e) => updateField('Target_Career', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" />
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Skill Level</label>
                    <select value={inputs.Skill_Level} onChange={(e) => updateField('Skill_Level', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent">
                      {SKILL_LEVELS.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Internships</label>
                    <input type="number" min="0" value={inputs.Internships} onChange={(e) => updateField('Internships', parseInt(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" />
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Consistency (1-10)</label>
                    <input type="range" min="1" max="10" value={inputs.Consistency} onChange={(e) => updateField('Consistency', parseInt(e.target.value))}
                      className="w-full accent-accent" />
                    <span className="text-text-muted text-xs">Value: {inputs.Consistency}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-accent uppercase tracking-wider mb-4">Financial</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="block text-text-secondary text-sm mb-2">Monthly Income (₹)</label>
                    <input type="number" value={inputs.Monthly_Income} onChange={(e) => updateField('Monthly_Income', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div><label className="block text-text-secondary text-sm mb-2">Fixed Expenses (₹)</label>
                    <input type="number" value={inputs.Fixed_Expenses} onChange={(e) => updateField('Fixed_Expenses', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div><label className="block text-text-secondary text-sm mb-2">Variable Expenses (₹)</label>
                    <input type="number" value={inputs.Variable_Expenses} onChange={(e) => updateField('Variable_Expenses', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div><label className="block text-text-secondary text-sm mb-2">Weekly Spending (₹)</label>
                    <input type="number" value={inputs.Weekly_Spending} onChange={(e) => updateField('Weekly_Spending', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div><label className="block text-text-secondary text-sm mb-2">Current Savings (₹)</label>
                    <input type="number" value={inputs.Current_Savings} onChange={(e) => updateField('Current_Savings', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div><label className="block text-text-secondary text-sm mb-2">Savings Target (₹)</label>
                    <input type="number" value={inputs.Savings_Target} onChange={(e) => updateField('Savings_Target', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div><label className="block text-text-secondary text-sm mb-2">Family Income (₹)</label>
                    <input type="number" value={inputs.Family_Income} onChange={(e) => updateField('Family_Income', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div><label className="block text-text-secondary text-sm mb-2">Family Support (₹)</label>
                    <input type="number" value={inputs.Family_Support} onChange={(e) => updateField('Family_Support', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div className="col-span-2"><label className="block text-text-secondary text-sm mb-2">Family Responsibility (₹)</label>
                    <input type="number" value={inputs.Family_Responsibility} onChange={(e) => updateField('Family_Responsibility', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-accent uppercase tracking-wider mb-4">Lifestyle</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="block text-text-secondary text-sm mb-2">Screen Time (hrs/day)</label>
                    <input type="number" step="0.5" value={inputs.Screen_Time} onChange={(e) => updateField('Screen_Time', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div><label className="block text-text-secondary text-sm mb-2">Sleep Duration (hrs)</label>
                    <input type="number" step="0.5" value={inputs.Sleep_Duration} onChange={(e) => updateField('Sleep_Duration', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Sleep Quality (1-10)</label>
                    <input type="range" min="1" max="10" value={inputs.Sleep_Quality} onChange={(e) => updateField('Sleep_Quality', parseInt(e.target.value))}
                      className="w-full accent-accent" />
                    <span className="text-text-muted text-xs">Value: {inputs.Sleep_Quality}</span>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Health Score (1-10)</label>
                    <input type="range" min="1" max="10" value={inputs.Health_Score} onChange={(e) => updateField('Health_Score', parseInt(e.target.value))}
                      className="w-full accent-accent" />
                    <span className="text-text-muted text-xs">Value: {inputs.Health_Score}</span>
                  </div>
                  <div><label className="block text-text-secondary text-sm mb-2">Sick Days/Month</label>
                    <input type="number" min="0" value={inputs.Sick_Days} onChange={(e) => updateField('Sick_Days', parseInt(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div><label className="block text-text-secondary text-sm mb-2">Medical Expenses (₹)</label>
                    <input type="number" value={inputs.Medical_Expenses} onChange={(e) => updateField('Medical_Expenses', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-accent uppercase tracking-wider mb-4">Family</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="block text-text-secondary text-sm mb-2">Earning Members</label>
                    <input type="number" min="1" value={inputs.Earning_Members} onChange={(e) => updateField('Earning_Members', parseInt(e.target.value) || 1)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div><label className="block text-text-secondary text-sm mb-2">Dependents</label>
                    <input type="number" min="0" value={inputs.Dependents} onChange={(e) => updateField('Dependents', parseInt(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div><label className="block text-text-secondary text-sm mb-2">Father's Occupation</label>
                    <input type="text" value={inputs.Father_Occupation} onChange={(e) => updateField('Father_Occupation', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                  <div><label className="block text-text-secondary text-sm mb-2">Mother's Occupation</label>
                    <input type="text" value={inputs.Mother_Occupation} onChange={(e) => updateField('Mother_Occupation', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent" /></div>
                </div>
              </div>
            </div>

            <button onClick={runAnalysis} disabled={isAnalyzing}
              className="w-full mt-6 px-6 py-4 bg-gradient-to-r from-accent to-orange-500 text-white font-semibold rounded-xl hover:opacity-90 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">
              {isAnalyzing ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Analyzing...
                </span>
              ) : 'Run Analysis'}
            </button>

            {error && <p className="mt-4 text-red-400 text-sm text-center">{error}</p>}
          </div>

          <div className="space-y-6">
            {results ? (
              <>
                {activeTab === 'overview' && (
                  <>
                    <div className="grid grid-cols-5 gap-3">
                      <div className={`p-4 rounded-xl border ${getScoreBg(results.scores?.behavior || 0)} text-center`}>
                        <p className="text-text-muted text-xs uppercase mb-1">Overall</p>
                        <p className={`text-2xl font-bold ${getScoreColor(results.scores?.behavior || 0)}`}>{results.scores?.behavior || 0}</p>
                        <p className="text-text-muted text-xs mt-1">Peer: {results.behavioral_profile?.peer_comparison || 'N/A'}</p>
                      </div>
                      <div className={`p-4 rounded-xl border ${getScoreBg(results.scores?.academic || 0)} text-center`}>
                        <p className="text-text-muted text-xs uppercase mb-1">Academic</p>
                        <p className={`text-2xl font-bold ${getScoreColor(results.scores?.academic || 0)}`}>{results.scores?.academic || 0}</p>
                        <p className="text-text-muted text-xs mt-1">30% weight</p>
                      </div>
                      <div className={`p-4 rounded-xl border ${getScoreBg(results.scores?.financial || 0)} text-center`}>
                        <p className="text-text-muted text-xs uppercase mb-1">Financial</p>
                        <p className={`text-2xl font-bold ${getScoreColor(results.scores?.financial || 0)}`}>{results.scores?.financial || 0}</p>
                        <p className="text-text-muted text-xs mt-1">25% weight</p>
                      </div>
                      <div className={`p-4 rounded-xl border ${getScoreBg(results.scores?.career || 0)} text-center`}>
                        <p className="text-text-muted text-xs uppercase mb-1">Career</p>
                        <p className={`text-2xl font-bold ${getScoreColor(results.scores?.career || 0)}`}>{results.scores?.career || 0}</p>
                        <p className="text-text-muted text-xs mt-1">25% weight</p>
                      </div>
                      <div className={`p-4 rounded-xl border ${getScoreBg(results.scores?.lifestyle || 0)} text-center`}>
                        <p className="text-text-muted text-xs uppercase mb-1">Lifestyle</p>
                        <p className={`text-2xl font-bold ${getScoreColor(results.scores?.lifestyle || 0)}`}>{results.scores?.lifestyle || 0}</p>
                        <p className="text-text-muted text-xs mt-1">20% weight</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-4 gap-3">
                      <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-xl p-4 text-center">
                        <p className="text-text-muted text-xs uppercase mb-1">Profile</p>
                        <p className="text-lg font-bold text-accent">{results.behavioral_profile?.profile || 'N/A'}</p>
                      </div>
                      <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-xl p-4 text-center">
                        <p className="text-text-muted text-xs uppercase mb-1">Urgency</p>
                        <p className={`text-lg font-bold ${getUrgencyColor(results.behavioral_profile?.urgency)}`}>{results.behavioral_profile?.urgency || 'N/A'}</p>
                      </div>
                      <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-xl p-4 text-center">
                        <p className="text-text-muted text-xs uppercase mb-1">Monthly Savings</p>
                        <p className="text-lg font-bold text-green-400">{fmtInr(results.financials?.monthly_savings || 0)}</p>
                      </div>
                      <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-xl p-4 text-center">
                        <p className="text-text-muted text-xs uppercase mb-1">Savings Rate</p>
                        <p className="text-lg font-bold text-accent">{(results.financials?.savings_rate_pct || 0).toFixed(1)}%</p>
                      </div>
                    </div>

                    {results.behavioral_profile?.flags?.length > 0 && (
                      <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                        <h3 className="text-lg font-semibold text-text-primary mb-4">Risk Flags</h3>
                        <div className="grid grid-cols-3 gap-3">
                          {results.behavioral_profile.flags.map((flag, idx) => (
                            <div key={idx} className={`p-3 rounded-xl border ${
                              flag.severity === 'critical' ? 'bg-red-500/10 border-red-500/30 text-red-400' :
                              flag.severity === 'high' ? 'bg-orange-500/10 border-orange-500/30 text-orange-400' :
                              'bg-yellow-500/10 border-yellow-500/30 text-yellow-400'
                            }`}>
                              <p className="text-xs uppercase font-bold">{flag.severity}</p>
                              <p className="text-sm font-semibold mt-1">{flag.flag?.replace(/_/g, ' ')}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}

                {activeTab === 'financial' && (
                  <>
                    <div className="grid grid-cols-4 gap-3">
                      {[
                        { label: 'Effective Income', value: fmtInr(results.financials?.effective_income || 0), cls: '' },
                        { label: 'Total Expenses', value: fmtInr(results.financials?.total_monthly_expenses || 0), cls: (results.financials?.expense_ratio_pct || 0) > 80 ? 'text-red-400' : 'text-yellow-400' },
                        { label: 'Monthly Savings', value: fmtInr(results.financials?.monthly_savings || 0), cls: 'text-green-400' },
                        { label: 'Burn Rate', value: `${(results.financials?.burn_rate_pct || 0).toFixed(1)}%`, cls: (results.financials?.burn_rate_pct || 0) > 60 ? 'text-red-400' : 'text-yellow-400' },
                        { label: 'Expense Ratio', value: `${(results.financials?.expense_ratio_pct || 0).toFixed(1)}%`, cls: (results.financials?.expense_ratio_pct || 0) > 80 ? 'text-red-400' : 'text-yellow-400' },
                        { label: 'Dependency Ratio', value: (results.financials?.dependency_ratio || 0).toFixed(2), cls: (results.financials?.dependency_ratio || 0) > 1.5 ? 'text-red-400' : 'text-yellow-400' },
                        { label: 'Savings Rate', value: `${(results.financials?.savings_rate_pct || 0).toFixed(1)}%`, cls: 'text-accent' },
                        { label: 'Months to Target', value: typeof results.financials?.months_to_savings_target === 'number' ? `${results.financials.months_to_savings_target}` : 'Never', cls: results.financials?.months_to_savings_target === 'Never at current rate' ? 'text-red-400' : 'text-accent' },
                      ].map((m, i) => (
                        <div key={i} className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-xl p-4">
                          <p className="text-text-muted text-xs uppercase mb-1">{m.label}</p>
                          <p className={`text-xl font-bold ${m.cls}`}>{m.value}</p>
                        </div>
                      ))}
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                      <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                        <h3 className="text-lg font-semibold text-text-primary mb-4">Wealth Projection</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <LineChart data={projectionChartData()}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                            <XAxis dataKey="age" stroke="#94A3B8" />
                            <YAxis stroke="#94A3B8" tickFormatter={(v) => fmtInr(v)} />
                            <Tooltip formatter={(value) => fmtInr(value)} contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', color: '#F8FAFC' }} />
                            <Legend />
                            <Line type="monotone" dataKey="current" stroke="#ef4444" strokeWidth={2} strokeDasharray="5 5" name="Current" />
                            <Line type="monotone" dataKey="optimized" stroke="#22c55e" strokeWidth={2} name="Optimized" />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                      <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                        <h3 className="text-lg font-semibold text-text-primary mb-4">Expense Breakdown</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <PieChart>
                            <Pie data={expensePieData()} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                              {expensePieData().map((_, index) => (
                                <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip formatter={(value) => fmtInr(value)} contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', color: '#F8FAFC' }} />
                          </PieChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                      <h3 className="text-lg font-semibold text-text-primary mb-4">Savings Growth Projections</h3>
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b border-secondary">
                              <th className="text-left text-text-muted text-sm py-2">Timeline</th>
                              <th className="text-right text-text-muted text-sm py-2">Current Path</th>
                              <th className="text-right text-text-muted text-sm py-2">Optimized Path</th>
                              <th className="text-right text-text-muted text-sm py-2">Gap</th>
                            </tr>
                          </thead>
                          <tbody>
                            {savingsProjectionData().map((row, i) => (
                              <tr key={i} className="border-b border-secondary/50">
                                <td className="text-text-primary py-2">{row.timeline}</td>
                                <td className="text-right text-red-400 py-2">{fmtInr(row.current)}</td>
                                <td className="text-right text-green-400 py-2">{fmtInr(row.optimized)}</td>
                                <td className="text-right text-accent py-2">{fmtInr(row.gap)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </>
                )}

                {activeTab === 'projection' && (
                  <>
                    <div className="grid grid-cols-2 gap-6">
                      <div className="bg-surface/80 backdrop-blur-xl border border-red-500/30 rounded-2xl p-6">
                        <h3 className="text-lg font-semibold text-red-400 mb-4">Current Path</h3>
                        {[5, 10, 20, 30].map(y => (
                          <div key={y} className="flex justify-between items-center p-3 bg-red-500/10 rounded-xl mb-2">
                            <span className="text-text-muted">Age {inputs.Age + y} (+{y}yr)</span>
                            <span className="text-xl font-bold text-red-400">{fmtInr(results.projections?.current_behavior_wealth?.[y] || 0)}</span>
                          </div>
                        ))}
                      </div>
                      <div className="bg-surface/80 backdrop-blur-xl border border-green-500/30 rounded-2xl p-6">
                        <h3 className="text-lg font-semibold text-green-400 mb-4">Optimized Path</h3>
                        {[5, 10, 20, 30].map(y => (
                          <div key={y} className="flex justify-between items-center p-3 bg-green-500/10 rounded-xl mb-2">
                            <span className="text-text-muted">Age {inputs.Age + y} (+{y}yr)</span>
                            <span className="text-xl font-bold text-green-400">{fmtInr(results.projections?.optimized_behavior_wealth?.[y] || 0)}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                      <h3 className="text-lg font-semibold text-text-primary mb-4">Career Milestones</h3>
                      {results.projections?.career_milestones?.map((m, i) => {
                        const pctGrowth = ((m.projected_monthly_income - inputs.Monthly_Income) / Math.max(inputs.Monthly_Income, 1)) * 100;
                        return (
                          <div key={i} className="flex justify-between items-center p-4 bg-background/50 rounded-xl mb-2">
                            <div>
                              <p className="text-text-primary font-semibold">+{m.year} Years · Age {m.age}</p>
                              <p className="text-text-muted text-sm">Based on consistency score {inputs.Consistency}/10</p>
                            </div>
                            <div className="text-right">
                              <p className="text-xl font-bold text-accent">{fmtInr(m.projected_monthly_income)}/mo</p>
                              <p className={`text-sm ${pctGrowth >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {pctGrowth >= 0 ? '+' : ''}{pctGrowth.toFixed(0)}% from now
                              </p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </>
                )}

                {activeTab === 'regret' && (
                  <>
                    <div className="bg-gradient-to-r from-red-900/30 to-red-950/30 border border-red-500/50 rounded-2xl p-8 text-center">
                      <p className="text-red-400 text-sm uppercase tracking-wider mb-2">Total Lifetime Regret Cost</p>
                      <p className="text-5xl font-bold text-red-400">{fmtInr(results.regret_analysis?.total_lifetime_regret_cost || 0)}</p>
                      <p className="text-text-muted mt-2">
                        ≈ {fmtInr(results.regret_analysis?.monthly_regret_equivalent || 0)}/mo in lost potential
                      </p>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      {[
                        { label: 'Discretionary Spending', value: results.regret_analysis?.discretionary_spending_regret || 0, sub: `${Math.round((results.regret_analysis?.discretionary_spending_regret || 0) / (results.regret_analysis?.projection_years || 35) / 12).toLocaleString()}/mo compounded` },
                        { label: 'Screen Time Loss', value: results.regret_analysis?.screen_time_wealth_loss || 0, sub: `${(results.regret_analysis?.screen_productivity_drag_pct || 0).toFixed(1)}% drag` },
                        { label: 'Sleep Deficit', value: results.regret_analysis?.sleep_deficit_income_loss || 0, sub: `${(results.regret_analysis?.sleep_productivity_drag_pct || 0).toFixed(1)}% drag` },
                        { label: 'Career Gap Loss', value: results.regret_analysis?.career_gap_wealth_loss || 0, sub: `${(results.regret_analysis?.career_drag_pct || 0).toFixed(1)}% career drag` },
                        { label: 'Health Negligence', value: results.regret_analysis?.health_negligence_loss || 0, sub: `${(results.regret_analysis?.health_drag_pct || 0).toFixed(1)}% health drag` },
                        { label: 'Late Investing', value: results.regret_analysis?.late_investing_opportunity_loss || 0, sub: 'Delayed start cost' },
                      ].map((item, i) => (
                        <div key={i} className="bg-gradient-to-br from-red-950/50 to-red-900/50 border border-red-500/30 rounded-xl p-4">
                          <p className="text-red-400 text-xs uppercase tracking-wider mb-2">{item.label}</p>
                          <p className="text-2xl font-bold text-red-400">{fmtInr(item.value)}</p>
                          <p className="text-text-muted text-xs mt-1">{item.sub}</p>
                        </div>
                      ))}
                    </div>

                    <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                      <h3 className="text-lg font-semibold text-text-primary mb-4">Regret Cost Breakdown</h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={regretChartData()} layout="vertical">
                          <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                          <XAxis type="number" stroke="#94A3B8" tickFormatter={(v) => fmtInr(v)} />
                          <YAxis dataKey="name" type="category" stroke="#94A3B8" width={100} />
                          <Tooltip formatter={(value) => fmtInr(value)} contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', color: '#F8FAFC' }} />
                          <Bar dataKey="value" fill="#ef4444" radius={[0, 4, 4, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="bg-surface/80 backdrop-blur-xl border border-green-500/30 rounded-2xl p-6">
                      <h3 className="text-lg font-semibold text-green-400 mb-4">Opportunity Costs</h3>
                      <div className="space-y-2">
                        {Object.entries(results.behavioral_profile?.opportunity_costs || {}).map(([key, value]) => (
                          <div key={key} className="flex justify-between items-center p-3 bg-green-500/10 border border-green-500/20 rounded-xl">
                            <span className="text-green-400 text-sm">{key.replace(/_/g, ' ')}</span>
                            <span className="text-green-400 font-bold">{fmtInr(value)}/yr</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}

                {activeTab === 'ai-insights' && (
                  <>
                    {results.llm_output?.summary && (
                      <div className="bg-surface/80 backdrop-blur-xl border-l-4 border-accent rounded-2xl p-6">
                        <p className="text-text-muted text-sm uppercase tracking-wider mb-2">Executive Summary</p>
                        <p className="text-text-secondary">{results.llm_output.summary}</p>
                      </div>
                    )}

                    {results.llm_output?.scores && (
                      <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                        <h3 className="text-lg font-semibold text-text-primary mb-4">AI-Computed Scores</h3>
                        <div className="grid grid-cols-4 gap-3">
                          {Object.entries(results.llm_output.scores).map(([key, item]) => {
                            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                            const val = item?.value || 0;
                            return (
                              <div key={key} className={`p-3 rounded-xl border ${getScoreBg(val)} text-center`}>
                                <p className="text-text-muted text-xs mb-1">{label}</p>
                                <p className={`text-2xl font-bold ${getScoreColor(val)}`}>{val}</p>
                                {item?.reason && <p className="text-text-muted text-xs mt-1 truncate">{item.reason}</p>}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {results.llm_output?.future_projection && (
                      <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                        <h3 className="text-lg font-semibold text-text-primary mb-4">Future Projection</h3>
                        <div className="grid grid-cols-2 gap-4">
                          {results.llm_output.future_projection.qualitative && (
                            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
                              <p className="text-red-400 text-sm font-semibold mb-2">Qualitative Outlook</p>
                              <p className="text-text-secondary text-sm">{results.llm_output.future_projection.qualitative}</p>
                            </div>
                          )}
                          {results.llm_output.future_projection.numeric && (
                            <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                              <p className="text-blue-400 text-sm font-semibold mb-2">Numeric Projection</p>
                              <p className="text-text-secondary text-sm">{results.llm_output.future_projection.numeric}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {(results.llm_output?.retirement_delay_risk || results.llm_output?.future_lifestyle_tier) && (
                      <div className="grid grid-cols-2 gap-4">
                        {results.llm_output.retirement_delay_risk && (
                          <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-xl p-4 text-center">
                            <p className="text-text-muted text-sm">Retirement Delay Risk</p>
                            <p className={`text-2xl font-bold ${getUrgencyColor(results.llm_output.retirement_delay_risk)}`}>{results.llm_output.retirement_delay_risk}</p>
                          </div>
                        )}
                        {results.llm_output.future_lifestyle_tier && (
                          <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-xl p-4 text-center">
                            <p className="text-text-muted text-sm">Future Lifestyle Tier</p>
                            <p className={`text-2xl font-bold ${results.llm_output.future_lifestyle_tier === 'Critical' || results.llm_output.future_lifestyle_tier === 'At Risk' ? 'text-red-400' : 'text-green-400'}`}>{results.llm_output.future_lifestyle_tier}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {results.llm_output?.lifepath_analysis && (
                      <div className="grid grid-cols-2 gap-4">
                        {results.llm_output.lifepath_analysis.current_behavior && (
                          <div className="bg-surface/80 backdrop-blur-xl border border-red-500/30 rounded-xl p-4">
                            <p className="text-red-400 font-semibold mb-3">Current Behavior</p>
                            {Object.entries(results.llm_output.lifepath_analysis.current_behavior).map(([k, v]) => (
                              <div key={k} className="mb-2">
                                <p className="text-text-muted text-xs uppercase">{k.replace(/_/g, ' ')}</p>
                                <p className="text-text-secondary text-sm">{v}</p>
                              </div>
                            ))}
                          </div>
                        )}
                        {results.llm_output.lifepath_analysis.optimized_behavior && (
                          <div className="bg-surface/80 backdrop-blur-xl border border-green-500/30 rounded-xl p-4">
                            <p className="text-green-400 font-semibold mb-3">Optimized Behavior</p>
                            {Object.entries(results.llm_output.lifepath_analysis.optimized_behavior).map(([k, v]) => (
                              <div key={k} className="mb-2">
                                <p className="text-text-muted text-xs uppercase">{k.replace(/_/g, ' ')}</p>
                                <p className="text-text-secondary text-sm">{v}</p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {results.llm_output?.health_impact && (
                      <div className="bg-surface/80 backdrop-blur-xl border border-blue-500/30 rounded-xl p-4">
                        <h3 className="text-lg font-semibold text-blue-400 mb-2">Health Impact Analysis</h3>
                        <p className="text-text-secondary">{results.llm_output.health_impact}</p>
                      </div>
                    )}

                    {results.llm_output?.peer_comparison && (
                      <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-xl p-4">
                        <h3 className="text-lg font-semibold text-text-primary mb-2">Peer Comparison</h3>
                        <p className="text-text-secondary">{results.llm_output.peer_comparison}</p>
                      </div>
                    )}

                    {results.llm_output?.micro_regret?.length > 0 && (
                      <div className="bg-surface/80 backdrop-blur-xl border border-red-500/30 rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-red-400 mb-4">Micro-Regret Insights</h3>
                        <div className="space-y-3">
                          {results.llm_output.micro_regret.map((item, idx) => (
                            <div key={idx} className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-text-secondary text-sm">{item}</div>
                          ))}
                        </div>
                      </div>
                    )}

                    {results.llm_output?.opportunity_cost?.length > 0 && (
                      <div className="bg-surface/80 backdrop-blur-xl border border-yellow-500/30 rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-yellow-400 mb-4">Opportunity Cost Insights</h3>
                        <div className="space-y-3">
                          {results.llm_output.opportunity_cost.map((item, idx) => (
                            <div key={idx} className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-xl text-text-secondary text-sm">{item}</div>
                          ))}
                        </div>
                      </div>
                    )}

                    {results.llm_output?.recommendations?.length > 0 && (
                      <div className="bg-surface/80 backdrop-blur-xl border border-green-500/30 rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-green-400 mb-4">Action Plan</h3>
                        <div className="space-y-3">
                          {results.llm_output.recommendations.map((rec, idx) => (
                            <div key={idx} className="flex gap-3 p-3 bg-green-500/10 border border-green-500/20 rounded-xl">
                              <span className="flex-shrink-0 w-6 h-6 bg-green-500/20 text-green-400 rounded-full flex items-center justify-center text-xs font-bold">{idx + 1}</span>
                              <p className="text-text-secondary text-sm">{rec}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {results.llm_output?.final_statement && (
                      <div className="bg-gradient-to-r from-accent/10 to-orange-500/10 border border-accent/30 rounded-2xl p-8 text-center">
                        <p className="text-accent font-semibold mb-2">Final Statement</p>
                        <p className="text-text-primary text-lg italic">{results.llm_output.final_statement}</p>
                      </div>
                    )}
                  </>
                )}
              </>
            ) : (
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-12 text-center">
                <div className="w-20 h-20 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg className="w-10 h-10 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-text-primary mb-2">Ready for Deep Analysis?</h3>
                <p className="text-text-secondary">Fill in your profile and click "Run Analysis" to get comprehensive insights into your life behavior.</p>
                {isLoadingData && <p className="text-accent mt-4 text-sm">Loading your saved analysis...</p>}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
