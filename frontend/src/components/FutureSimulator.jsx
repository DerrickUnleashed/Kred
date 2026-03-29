import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import Navbar from './Navbar';

const API_URL = import.meta.env.VITE_STOCKS_API_URL || 'http://localhost:8000';

const COUNTRIES = [
  "India", "United States", "United Kingdom", "Canada", "Australia",
  "Germany", "France", "Singapore", "UAE", "Netherlands", "Sweden",
  "Japan", "South Korea", "New Zealand", "Ireland", "Switzerland",
  "Malaysia", "Bangladesh", "Sri Lanka", "Nepal", "Pakistan",
  "South Africa", "Nigeria", "Kenya", "Brazil", "Mexico",
  "Italy", "Spain", "Portugal", "Poland", "Other"
];

const defaultProfile = {
  name: '',
  occupation: '',
  bio: '',
  country: 'India',
  age: 22,
  gender: 'Prefer not to say',
  edu_level: 'Undergraduate',
  cgpa: 7.5,
  field: 'Engineering / Technology',
  college_tier: 'Tier 2',
  study_hours: 20,
  target_career: 'Software Engineer',
  skill: 'Intermediate',
  experience: false,
  consistency: 'Medium',
  monthly_spend: 8000,
  savings: 'Medium',
  family_bg: 'Middle',
  discipline: 'Balanced',
  screen_time: 'Medium (4–8 h)',
  health: 'Average',
  sleep: 'Average',
};

export default function FutureSimulator() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(defaultProfile);
  const [results, setResults] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [error, setError] = useState('');
  const [isLoadingData, setIsLoadingData] = useState(false);

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
      loadUserSimulation();
    }
  }, [user]);

  const loadUserSimulation = async () => {
    if (!user) return;
    setIsLoadingData(true);
    
    try {
      const { data, error } = await supabase
        .from('fsve_simulations')
        .select('*')
        .eq('user_id', user.id)
        .single();

      if (data) {
        const savedProfile = {
          name: data.name || '',
          occupation: data.occupation || '',
          bio: data.bio || '',
          country: data.country || 'India',
          age: data.age || 22,
          gender: data.gender || 'Prefer not to say',
          edu_level: data.edu_level || 'Undergraduate',
          cgpa: data.cgpa || 7.5,
          field: data.field || 'Engineering / Technology',
          college_tier: data.college_tier || 'Tier 2',
          study_hours: data.study_hours || 20,
          target_career: data.target_career || 'Software Engineer',
          skill: data.skill || 'Intermediate',
          experience: data.experience || false,
          consistency: data.consistency || 'Medium',
          monthly_spend: data.monthly_spend || 8000,
          savings: data.savings || 'Medium',
          family_bg: data.family_bg || 'Middle',
          discipline: data.discipline || 'Balanced',
          screen_time: data.screen_time || 'Medium (4–8 h)',
          health: data.health || 'Average',
          sleep: data.sleep || 'Average',
        };
        setProfile(savedProfile);

        if (data.results) {
          setResults(data.results);
        }
      }
    } catch (err) {
      console.log('No saved simulation found or error:', err.message);
    }
    
    setIsLoadingData(false);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/');
  };

  const updateField = (field, value) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  const saveToSupabase = async (simulationResults) => {
    if (!user) return;

    const simulationData = {
      user_id: user.id,
      name: profile.name,
      occupation: profile.occupation,
      bio: profile.bio,
      country: profile.country,
      age: profile.age,
      gender: profile.gender,
      edu_level: profile.edu_level,
      cgpa: profile.cgpa,
      field: profile.field,
      college_tier: profile.college_tier,
      study_hours: profile.study_hours,
      target_career: profile.target_career,
      skill: profile.skill,
      experience: profile.experience,
      consistency: profile.consistency,
      monthly_spend: profile.monthly_spend,
      savings: profile.savings,
      family_bg: profile.family_bg,
      discipline: profile.discipline,
      screen_time: profile.screen_time,
      health: profile.health,
      sleep: profile.sleep,
      results: simulationResults,
      updated_at: new Date().toISOString(),
    };

    const { data: existing } = await supabase
      .from('fsve_simulations')
      .select('id')
      .eq('user_id', user.id)
      .single();

    if (existing) {
      await supabase
        .from('fsve_simulations')
        .update(simulationData)
        .eq('user_id', user.id);
    } else {
      simulationData.created_at = new Date().toISOString();
      await supabase
        .from('fsve_simulations')
        .insert([simulationData]);
    }
  };

  const runFullSimulation = async () => {
    setIsSimulating(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/fls/full-run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile),
      });

      if (!response.ok) {
        throw new Error('Simulation failed');
      }

      const data = await response.json();
      setResults(data);

      await saveToSupabase(data);
    } catch (err) {
      setError('Failed to run simulation. Please check if the backend is running.');
      console.error('Simulation error:', err);
    }

    setIsSimulating(false);
  };

  const getScoreColor = (score) => {
    if (score >= 75) return 'text-green-400';
    if (score >= 50) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getRiskBadge = (risk) => {
    const colors = {
      'Low': 'bg-green-500/20 text-green-400',
      'Moderate': 'bg-yellow-500/20 text-yellow-400',
      'High': 'bg-red-500/20 text-red-400',
    };
    return colors[risk] || 'bg-gray-500/20 text-gray-400';
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
          <h1 className="text-3xl font-bold text-text-primary">Future State Variable Engine</h1>
          <p className="text-text-secondary mt-1">AI-powered life trajectory engine. Project your future 5, 10, and 25 years ahead.</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
            <h2 className="text-xl font-semibold text-text-primary mb-6">Your Profile</h2>
            {isLoadingData && (
              <div className="mb-4 px-4 py-2 bg-accent/10 border border-accent/30 rounded-xl text-accent text-sm">
                Loading your saved data...
              </div>
            )}
            
            <div className="space-y-6 max-h-[70vh] overflow-y-auto pr-2">
              {/* Personal Section */}
              <div>
                <h3 className="text-sm font-semibold text-accent uppercase tracking-wider mb-4">Personal</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Name</label>
                    <input
                      type="text"
                      value={profile.name}
                      onChange={(e) => updateField('name', e.target.value)}
                      placeholder="Your name"
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
                    />
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Age</label>
                    <input
                      type="number"
                      min="10"
                      max="70"
                      value={profile.age}
                      onChange={(e) => updateField('age', parseInt(e.target.value) || 20)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    />
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Country</label>
                    <select
                      value={profile.country}
                      onChange={(e) => updateField('country', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      {COUNTRIES.map(c => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Gender</label>
                    <select
                      value={profile.gender}
                      onChange={(e) => updateField('gender', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Prefer not to say">Prefer not to say</option>
                    </select>
                  </div>
                  <div className="col-span-2">
                    <label className="block text-text-secondary text-sm mb-2">Occupation</label>
                    <input
                      type="text"
                      value={profile.occupation}
                      onChange={(e) => updateField('occupation', e.target.value)}
                      placeholder="e.g. 2nd Year B.Tech Student"
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
                    />
                  </div>
                </div>
              </div>

              {/* Academic Section */}
              <div>
                <h3 className="text-sm font-semibold text-accent uppercase tracking-wider mb-4">Academic</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Education Level</label>
                    <select
                      value={profile.edu_level}
                      onChange={(e) => updateField('edu_level', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      <option value="High School">High School</option>
                      <option value="Undergraduate">Undergraduate</option>
                      <option value="Postgraduate">Postgraduate</option>
                      <option value="PhD">PhD</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">CGPA (0-10)</label>
                    <input
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      value={profile.cgpa}
                      onChange={(e) => updateField('cgpa', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    />
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Field of Study</label>
                    <select
                      value={profile.field}
                      onChange={(e) => updateField('field', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      <option value="Engineering / Technology">Engineering / Technology</option>
                      <option value="Science">Science</option>
                      <option value="Commerce / Business">Commerce / Business</option>
                      <option value="Arts / Humanities">Arts / Humanities</option>
                      <option value="Medicine / Healthcare">Medicine / Healthcare</option>
                      <option value="Law">Law</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">College Tier</label>
                    <select
                      value={profile.college_tier}
                      onChange={(e) => updateField('college_tier', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      <option value="Tier 1">Tier 1</option>
                      <option value="Tier 2">Tier 2</option>
                      <option value="Tier 3">Tier 3</option>
                    </select>
                  </div>
                  <div className="col-span-2">
                    <label className="block text-text-secondary text-sm mb-2">Study Hours/Week: {profile.study_hours}</label>
                    <input
                      type="range"
                      min="0"
                      max="80"
                      value={profile.study_hours}
                      onChange={(e) => updateField('study_hours', parseInt(e.target.value))}
                      className="w-full accent-accent"
                    />
                  </div>
                </div>
              </div>

              {/* Career Section */}
              <div>
                <h3 className="text-sm font-semibold text-accent uppercase tracking-wider mb-4">Career</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Target Career</label>
                    <input
                      type="text"
                      value={profile.target_career}
                      onChange={(e) => updateField('target_career', e.target.value)}
                      placeholder="e.g. Software Engineer"
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
                    />
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Skill Level</label>
                    <select
                      value={profile.skill}
                      onChange={(e) => updateField('skill', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      <option value="Beginner">Beginner</option>
                      <option value="Intermediate">Intermediate</option>
                      <option value="Advanced">Advanced</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Experience</label>
                    <div className="flex items-center gap-4 mt-2">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={profile.experience}
                          onChange={(e) => updateField('experience', e.target.checked)}
                          className="w-5 h-5 accent-accent rounded"
                        />
                        <span className="text-text-primary">Has Experience</span>
                      </label>
                    </div>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Consistency</label>
                    <select
                      value={profile.consistency}
                      onChange={(e) => updateField('consistency', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      <option value="Low">Low</option>
                      <option value="Medium">Medium</option>
                      <option value="High">High</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Financial Section */}
              <div>
                <h3 className="text-sm font-semibold text-accent uppercase tracking-wider mb-4">Financial</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Monthly Spend (₹)</label>
                    <input
                      type="number"
                      min="0"
                      value={profile.monthly_spend}
                      onChange={(e) => updateField('monthly_spend', parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    />
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Savings Rate</label>
                    <select
                      value={profile.savings}
                      onChange={(e) => updateField('savings', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      <option value="Low">Low</option>
                      <option value="Medium">Medium</option>
                      <option value="High">High</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Family Background</label>
                    <select
                      value={profile.family_bg}
                      onChange={(e) => updateField('family_bg', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      <option value="Low">Low</option>
                      <option value="Middle">Middle</option>
                      <option value="High">High</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Financial Discipline</label>
                    <select
                      value={profile.discipline}
                      onChange={(e) => updateField('discipline', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      <option value="Impulsive">Impulsive</option>
                      <option value="Balanced">Balanced</option>
                      <option value="Disciplined">Disciplined</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Lifestyle Section */}
              <div>
                <h3 className="text-sm font-semibold text-accent uppercase tracking-wider mb-4">Lifestyle</h3>
                <div className="grid grid-cols-1 gap-4">
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Screen Time</label>
                    <select
                      value={profile.screen_time}
                      onChange={(e) => updateField('screen_time', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      <option value="Low (<4 h)">Low (&lt;4 h)</option>
                      <option value="Medium (4–8 h)">Medium (4–8 h)</option>
                      <option value="High (>8 h)">High (&gt;8 h)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Health</label>
                    <select
                      value={profile.health}
                      onChange={(e) => updateField('health', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      <option value="Poor">Poor</option>
                      <option value="Average">Average</option>
                      <option value="Good">Good</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-text-secondary text-sm mb-2">Sleep Quality</label>
                    <select
                      value={profile.sleep}
                      onChange={(e) => updateField('sleep', e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-accent"
                    >
                      <option value="Poor">Poor</option>
                      <option value="Average">Average</option>
                      <option value="Good">Good</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={runFullSimulation}
              disabled={isSimulating}
              className="w-full mt-6 px-6 py-4 bg-accent text-white font-semibold rounded-xl hover:bg-accent/90 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSimulating ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Simulating...
                </span>
              ) : (
                'Run Full Simulation'
              )}
            </button>

            {error && (
              <p className="mt-4 text-red-400 text-sm text-center">{error}</p>
            )}
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {results ? (
              <>
                {/* Composite Score */}
                <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-text-primary">Composite Score</h2>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskBadge(results.simulation?.scores?.risk || 'Moderate')}`}>
                      {results.simulation?.scores?.risk || 'Moderate'} Risk
                    </span>
                  </div>
                  <div className="text-center py-6">
                    <div className={`text-6xl font-bold ${getScoreColor(results.simulation?.scores?.composite || 50)}`}>
                      {results.simulation?.scores?.composite || 50}
                    </div>
                    <p className="text-text-secondary mt-2">Composite Life Score</p>
                  </div>
                  <div className="flex justify-center gap-4 mt-4">
                    <span className="text-text-muted text-sm">
                      Profile: <span className="text-text-primary">{results.simulation?.scores?.profile || 'Balanced'}</span>
                    </span>
                    <span className="text-text-muted text-sm">
                      Trend: <span className="text-text-primary">{results.simulation?.scores?.trend || 'Stable'}</span>
                    </span>
                  </div>
                </div>

                {/* Individual Scores */}
                <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                  <h3 className="text-lg font-semibold text-text-primary mb-4">Life Dimension Scores</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { label: 'Academic', value: results.simulation?.scores?.academic || 0 },
                      { label: 'Financial', value: results.simulation?.scores?.financial || 0 },
                      { label: 'Career', value: results.simulation?.scores?.career || 0 },
                      { label: 'Lifestyle', value: results.simulation?.scores?.lifestyle || 0 },
                    ].map((score) => (
                      <div key={score.label} className="bg-background/50 rounded-xl p-4 text-center border border-secondary">
                        <div className={`text-3xl font-bold ${getScoreColor(score.value)}`}>
                          {score.value}
                        </div>
                        <p className="text-text-secondary text-sm mt-1">{score.label}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Projections */}
                <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                  <h3 className="text-lg font-semibold text-text-primary mb-4">Future Projections</h3>
                  <div className="space-y-4">
                    {['5_year', '10_year', '25_year'].map((key) => {
                      const proj = results.simulation?.projections?.[key];
                      if (!proj) return null;
                      return (
                        <div key={key} className="bg-background/50 rounded-xl p-4 border border-secondary">
                          <div className="flex justify-between items-center mb-3">
                            <h4 className="text-accent font-semibold">
                              {proj.years === 5 ? '5 Years' : proj.years === 10 ? '10 Years' : '25 Years'}
                            </h4>
                            <span className="text-text-muted text-sm">Age {proj.age}</span>
                          </div>
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            <div>
                              <span className="text-text-muted">Composite:</span>
                              <span className={`ml-2 font-semibold ${getScoreColor(proj.composite)}`}>{proj.composite}</span>
                            </div>
                            <div>
                              <span className="text-text-muted">Income:</span>
                              <span className="ml-2 font-semibold text-accent">₹{proj.income_lpa || 0} LPA</span>
                            </div>
                            <div>
                              <span className="text-text-muted">Career:</span>
                              <span className="ml-2 text-text-primary">{proj.career_status || 'Stable'}</span>
                            </div>
                            <div>
                              <span className="text-text-muted">Finance:</span>
                              <span className="ml-2 text-text-primary">{proj.fin_status || 'Moderate'}</span>
                            </div>
                            <div className="col-span-2">
                              <span className="text-text-muted">Life Quality:</span>
                              <span className="ml-2 text-text-primary">{proj.life_quality || 'Average'}</span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Generated Image */}
                {results.image_b64 && (
                  <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-text-primary mb-4">10-Year Life Visualization</h3>
                    <img
                      src={`data:image/png;base64,${results.image_b64}`}
                      alt="Future life visualization"
                      className="w-full rounded-xl"
                    />
                    <p className="text-text-muted text-xs mt-2">
                      Generated via {results.image_source || 'AI'}
                    </p>
                  </div>
                )}

                {/* Analysis */}
                {results.analysis && (
                  <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-text-primary mb-4">AI Life Analysis</h3>
                    <div className="prose prose-invert max-w-none">
                      <p className="text-text-secondary whitespace-pre-wrap leading-relaxed">{results.analysis}</p>
                    </div>
                  </div>
                )}

                {/* Narrative */}
                {results.narrative && (
                  <div className="bg-gradient-to-r from-primary/30 to-surface border border-accent/30 rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-accent mb-4">Life Narrative</h3>
                    <p className="text-text-secondary italic whitespace-pre-wrap leading-relaxed">
                      "{results.narrative}"
                    </p>
                  </div>
                )}
              </>
            ) : (
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-12 text-center">
                <div className="w-20 h-20 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg className="w-10 h-10 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-text-primary mb-2">Ready to See Your Future?</h3>
                <p className="text-text-secondary">
                  Fill in your profile and click "Run Full Simulation" to see your personalized life trajectory.
                </p>
                {isLoadingData && (
                  <p className="text-accent mt-4 text-sm">Loading your saved simulation...</p>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
