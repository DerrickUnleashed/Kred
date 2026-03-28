import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import Navbar from './Navbar';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';

const CATEGORIES = [
  'Groceries',
  'Electronics',
  'Clothing',
  'Utilities',
  'Healthcare',
  'Entertainment',
  'Transportation',
  'Education',
  'Housing',
  'Other',
];

const COLORS = ['#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#2563EB', '#1D4ED8', '#1E40AF', '#1E3A8A', '#172554', '#3B82F680'];
const ESSENTIAL_COLORS = ['#3B82F6', '#F97316'];

const computeDynamicLimit = (monthlyIncome, expectedSavings, products, totalExpenses) => {
  const income = parseFloat(monthlyIncome) || 0;
  const savings = parseFloat(expectedSavings) || 0;
  const savingsRatio = income > 0 ? savings / income : 0.2;
  
  const usable = income * (1 - savingsRatio);
  const baseLimit = usable / 30;
  
  const now = new Date();
  const hoursPassedToday = now.getHours() + now.getMinutes() / 60;
  const today = now.getDate();
  const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
  const daysPassedMonth = today;
  const daysLeftMonth = Math.max(daysInMonth - daysPassedMonth, 0);
  
  const essentialCount = products.filter(p => p.is_essential).length;
  const nonEssentialCount = products.filter(p => !p.is_essential).length;
  const impulsiveRatio = products.length > 0 ? nonEssentialCount / products.length : 0;
  
  const dayOfWeek = now.getDay();
  const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
  const isEvening = hoursPassedToday >= 18;
  
  let behaviorFactor = 1.0;
  if (impulsiveRatio > 0.5) behaviorFactor = 0.7;
  else if (impulsiveRatio > 0.3) behaviorFactor = 0.85;
  
  let contextFactor = 1.0;
  if (isEvening && hoursPassedToday >= 21) contextFactor = 0.6;
  else if (isEvening) contextFactor = 0.8;
  if (isWeekend) contextFactor *= 0.9;
  
  const remainingBudget = Math.max(usable - totalExpenses, 0);
  const monthlyRemaining = remainingBudget;
  const weeklyRemaining = remainingBudget * 7 / 30;
  const categoryRemaining = remainingBudget;
  
  const monthlyConstraint = daysLeftMonth > 0 ? monthlyRemaining / daysLeftMonth : 0;
  const weeklyConstraint = weeklyRemaining / Math.max(7 - dayOfWeek, 1);
  
  const constraintLimit = Math.min(monthlyConstraint, weeklyConstraint, categoryRemaining);
  
  const goalFactor = savingsRatio >= 0.2 ? 1.0 : savingsRatio >= 0.1 ? 0.85 : 0.7;
  
  const adjustedLimit = baseLimit * behaviorFactor * contextFactor * goalFactor;
  const finalLimit = Math.min(adjustedLimit, constraintLimit);
  
  const prevLimit = baseLimit;
  const smoothedLimit = 0.7 * prevLimit + 0.3 * finalLimit;
  
  const minLimit = 0.6 * baseLimit;
  const maxLimit = baseLimit;
  const boundedLimit = Math.max(Math.min(smoothedLimit, maxLimit), minLimit);
  
  const currentHourlySpend = products.reduce((sum, p) => sum + (p.total_cost || 0), 0) / Math.max(hoursPassedToday, 1);
  const estimatedDailySpend = currentHourlySpend * 24;
  const spentToday = Math.min(estimatedDailySpend, totalExpenses);
  
  const safeSpendNow = Math.max(boundedLimit - spentToday, 0);
  
  const limitRatio = boundedLimit / baseLimit;
  let status = 'tight';
  if (limitRatio > 0.8) status = 'relaxed';
  else if (limitRatio > 0.5) status = 'moderate';
  
  const explanation = {};
  if (behaviorFactor < 0.7) explanation.behavior = 'High impulsive spending detected';
  if (contextFactor < 0.7) explanation.context = 'Evening or weekend spending risk';
  if (goalFactor < 0.85) explanation.goal = 'Savings goal pressure is high';
  
  return {
    dynamic_limit: Math.round(boundedLimit),
    safe_spend_now: Math.round(safeSpendNow),
    status,
    behavior_factor: behaviorFactor.toFixed(2),
    context_factor: contextFactor.toFixed(2),
    goal_factor: goalFactor.toFixed(2),
    explanation,
    base_limit: Math.round(baseLimit),
    spent_today: Math.round(spentToday),
    remaining_budget: Math.round(remainingBudget),
    impulsive_ratio: (impulsiveRatio * 100).toFixed(0),
    essential_count: essentialCount,
    non_essential_count: nonEssentialCount,
  };
};

const computeBehaviorAnalysis = (monthlyIncome, expectedSavings, products, totalExpenses) => {
  const income = parseFloat(monthlyIncome) || 0;
  const savings = parseFloat(expectedSavings) || 0;
  
  const essentialExpenses = products.filter(p => p.is_essential).reduce((sum, p) => sum + (p.total_cost || 0), 0);
  const nonEssentialExpenses = products.filter(p => !p.is_essential).reduce((sum, p) => sum + (p.total_cost || 0), 0);
  const essentialCount = products.filter(p => p.is_essential).length;
  const nonEssentialCount = products.filter(p => !p.is_essential).length;
  
  const impulsiveRatio = products.length > 0 ? nonEssentialCount / products.length : 0;
  
  const categorySpending = {};
  products.forEach(p => {
    if (!categorySpending[p.category]) {
      categorySpending[p.category] = { count: 0, total: 0 };
    }
    categorySpending[p.category].count++;
    categorySpending[p.category].total += p.total_cost || 0;
  });
  
  const volatility = products.length > 1 
    ? products.reduce((sum, p) => sum + Math.abs((p.total_cost || 0) - (totalExpenses / products.length)), 0) / products.length
    : 0;
  
  const avgSpend = products.length > 0 ? totalExpenses / products.length : 0;
  const overspendingFrequency = products.filter(p => (p.total_cost || 0) > avgSpend * 1.5).length;
  
  let score = 100;
  
  if (impulsiveRatio > 0.5) score -= 30;
  else if (impulsiveRatio > 0.3) score -= 15;
  
  if (volatility > avgSpend * 0.5) score -= 20;
  else if (volatility > avgSpend * 0.3) score -= 10;
  
  if (overspendingFrequency > products.length * 0.3) score -= 15;
  
  const savingsRatio = income > 0 ? savings / income : 0;
  if (savingsRatio < 0.1) score -= 20;
  else if (savingsRatio < 0.2) score -= 10;
  
  score = Math.max(0, Math.min(100, score));
  
  let riskLevel = 'low';
  if (score < 40) riskLevel = 'high';
  else if (score < 70) riskLevel = 'medium';
  
  let profile = 'disciplined';
  if (impulsiveRatio > 0.5 && volatility > avgSpend * 0.3) profile = 'impulsive';
  else if (impulsiveRatio > 0.3) profile = 'occasional_impulsive';
  else if (savingsRatio >= 0.2) profile = 'saver';
  else if (products.length === 0) profile = 'no_data';
  
  const insights = [];
  const recommendations = [];
  
  if (profile === 'impulsive') {
    insights.push('High ratio of non-essential purchases detected');
    insights.push('Significant spending volatility observed');
    recommendations.push('Try the 24-hour rule before non-essential purchases');
    recommendations.push('Set stricter daily limits for discretionary spending');
  }
  
  if (savingsRatio < 0.15) {
    insights.push('Savings rate below recommended 20%');
    recommendations.push('Consider automating savings right after income');
  }
  
  if (nonEssentialExpenses > essentialExpenses * 0.5) {
    insights.push('Non-essential spending is high compared to essentials');
    recommendations.push('Prioritize essential purchases before discretionary items');
  }
  
  if (products.length > 10) {
    insights.push('High frequency of purchases recorded');
    recommendations.push('Consider consolidating similar purchases');
  }
  
  if (categorySpending['Entertainment']?.total > income * 0.1) {
    insights.push('Entertainment spending exceeds 10% of income');
    recommendations.push('Set a monthly entertainment budget');
  }
  
  if (insights.length === 0) {
    insights.push('Your spending patterns are well-balanced');
    recommendations.push('Continue maintaining your current financial habits');
  }
  
  const simulation = {
    chart: products.slice(0, 10).map((p, i) => ({
      date: `Day ${i + 1}`,
      actual: p.total_cost || 0,
      predicted: avgSpend,
    })),
    projection: {
      current_spend_5y: Math.round(totalExpenses * 12 * 5),
      improved_spend_5y: Math.round(totalExpenses * 0.8 * 12 * 5),
      potential_savings: Math.round(totalExpenses * 0.2 * 12 * 5),
      note: savingsRatio >= 0.2 
        ? 'You are on track to meet your savings goals'
        : 'Improving your spending habits could save significant amounts over 5 years',
    },
  };
  
  const patterns = {
    overspending: {
      frequency: overspendingFrequency,
      volatility: Math.round(volatility),
      avg_spend: Math.round(avgSpend),
    },
    categories: categorySpending,
    trend: products.length >= 3 
      ? (products[0].total_cost > products[products.length - 1].total_cost ? 'increasing' : 'decreasing')
      : 'insufficient_data',
  };
  
  return {
    risk_level: riskLevel,
    behavior_score: score,
    behavior_profile: profile,
    patterns,
    insights,
    recommendations,
    simulation,
    essential_count: essentialCount,
    non_essential_count: nonEssentialCount,
    essential_expenses: Math.round(essentialExpenses),
    non_essential_expenses: Math.round(nonEssentialExpenses),
    savings_ratio: (savingsRatio * 100).toFixed(0),
  };
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Income state
  const [monthlyIncome, setMonthlyIncome] = useState('');
  const [expectedSavings, setExpectedSavings] = useState('');
  const [incomeLoading, setIncomeLoading] = useState(false);
  
  // Products state
  const [products, setProducts] = useState([]);
  const [productsLoading, setProductsLoading] = useState(true);
  const [productForm, setProductForm] = useState({
    name: '',
    quantity: '',
    cost_per_unit: '',
    category: 'Groceries',
    is_essential: false,
  });
  const [editingId, setEditingId] = useState(null);

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
      fetchIncome();
      fetchProducts();
    }
  }, [user]);

  const fetchIncome = async () => {
    const { data } = await supabase
      .from('user_income')
      .select('*')
      .eq('user_id', user?.id)
      .single();
    
    if (data) {
      setMonthlyIncome(data.monthly_income || '');
      setExpectedSavings(data.expected_savings || '');
    }
  };

  const fetchProducts = async () => {
    setProductsLoading(true);
    const { data } = await supabase
      .from('products')
      .select('*')
      .eq('user_id', user?.id)
      .order('created_at', { ascending: false });
    
    if (data) {
      setProducts(data);
    }
    setProductsLoading(false);
  };

  const saveIncome = async () => {
    setIncomeLoading(true);
    
    const { data: existing } = await supabase
      .from('user_income')
      .select('id')
      .eq('user_id', user?.id)
      .single();

    if (existing) {
      await supabase
        .from('user_income')
        .update({ 
          monthly_income: monthlyIncome,
          expected_savings: expectedSavings,
        })
        .eq('user_id', user?.id);
    } else {
      await supabase
        .from('user_income')
        .insert([{ 
          user_id: user?.id, 
          monthly_income: monthlyIncome,
          expected_savings: expectedSavings,
        }]);
    }
    
    setIncomeLoading(false);
  };

  const handleProductSubmit = async (e) => {
    e.preventDefault();
    
    const productData = {
      user_id: user?.id,
      name: productForm.name,
      quantity: parseInt(productForm.quantity),
      cost_per_unit: parseFloat(productForm.cost_per_unit),
      category: productForm.category,
      is_essential: productForm.is_essential,
      total_cost: parseInt(productForm.quantity) * parseFloat(productForm.cost_per_unit),
    };

    if (editingId) {
      const { error } = await supabase
        .from('products')
        .update(productData)
        .eq('id', editingId);
      
      if (!error) {
        setEditingId(null);
        setProductForm({ name: '', quantity: '', cost_per_unit: '', category: 'Groceries', is_essential: false });
      }
    } else {
      await supabase
        .from('products')
        .insert([productData]);
    }

    if (!editingId) {
      setProductForm({ name: '', quantity: '', cost_per_unit: '', category: 'Groceries', is_essential: false });
    }
    
    fetchProducts();
  };

  const handleEdit = (product) => {
    setProductForm({
      name: product.name,
      quantity: product.quantity.toString(),
      cost_per_unit: product.cost_per_unit.toString(),
      category: product.category,
      is_essential: product.is_essential || false,
    });
    setEditingId(product.id);
  };

  const handleDelete = async (id) => {
    await supabase.from('products').delete().eq('id', id);
    fetchProducts();
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/');
  };

  const totalExpenses = products.reduce((sum, p) => sum + (p.total_cost || 0), 0);
  const expectedExpenses = (parseFloat(monthlyIncome) || 0) - (parseFloat(expectedSavings) || 0);
  const remaining = (parseFloat(monthlyIncome) || 0) - totalExpenses;
  
  const essentialExpenses = products.filter(p => p.is_essential).reduce((sum, p) => sum + (p.total_cost || 0), 0);
  const nonEssentialExpenses = products.filter(p => !p.is_essential).reduce((sum, p) => sum + (p.total_cost || 0), 0);

  const categoryData = CATEGORIES.map(cat => ({
    name: cat,
    value: products.filter(p => p.category === cat).reduce((sum, p) => sum + (p.total_cost || 0), 0),
  })).filter(d => d.value > 0);

  const essentialData = [
    { name: 'Essential', value: essentialExpenses },
    { name: 'Non-Essential', value: nonEssentialExpenses },
  ].filter(d => d.value > 0);

  const productChartData = products.map(p => ({
    name: p.name.substring(0, 10),
    cost: p.total_cost,
    quantity: p.quantity,
  }));

  const monthlyData = [
    { month: 'Jan', income: parseFloat(monthlyIncome) || 0, expected: expectedExpenses, actual: totalExpenses },
    { month: 'Feb', income: parseFloat(monthlyIncome) || 0, expected: expectedExpenses, actual: 0 },
    { month: 'Mar', income: parseFloat(monthlyIncome) || 0, expected: expectedExpenses, actual: 0 },
  ];

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
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24">
        <div className="flex flex-wrap gap-2 mb-8">
          {['overview', 'products', 'income', 'dynamic-limit', 'ai-behavior'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-xl font-medium transition-colors cursor-pointer ${
                activeTab === tab
                  ? 'bg-blue-500 text-white'
                  : 'bg-surface border border-secondary text-text-secondary hover:text-text-primary'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
          <Link
            to="/stocks"
            className="px-4 py-2 rounded-xl font-medium bg-surface border border-secondary text-text-secondary hover:text-blue-500 hover:border-blue-500 transition-colors"
          >
            Stocks
          </Link>
        </div>

        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <p className="text-text-secondary text-sm mb-1">Monthly Income</p>
                <p className="text-2xl font-bold text-blue-500">₹{parseFloat(monthlyIncome).toLocaleString() || '0'}</p>
              </div>
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <p className="text-text-secondary text-sm mb-1">Expected Savings</p>
                <p className="text-2xl font-bold text-green-400">₹{parseFloat(expectedSavings).toLocaleString() || '0'}</p>
              </div>
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <p className="text-text-secondary text-sm mb-1">Expected Expense</p>
                <p className="text-2xl font-bold text-yellow-400">₹{expectedExpenses.toLocaleString() || '0'}</p>
              </div>
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <p className="text-text-secondary text-sm mb-1">Remaining</p>
                <p className={`text-2xl font-bold ₹{remaining >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  ₹{remaining.toLocaleString()}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <p className="text-text-secondary text-sm mb-1">Essential Expenses</p>
                <p className="text-2xl font-bold text-blue-500">₹{essentialExpenses.toLocaleString()}</p>
              </div>
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <p className="text-text-secondary text-sm mb-1">Non-Essential Expenses</p>
                <p className="text-2xl font-bold text-orange-400">₹{nonEssentialExpenses.toLocaleString()}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Essential vs Non-Essential</h3>
                {essentialData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={essentialData}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        fill="#3B82F6"
                        dataKey="value"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        labelLine={false}
                      >
                        {essentialData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={ESSENTIAL_COLORS[index % ESSENTIAL_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#0F172A', 
                          border: '1px solid #1E293B',
                          borderRadius: '8px',
                          color: '#F8FAFC'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-text-muted">
                    No expense data yet
                  </div>
                )}
              </div>

              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Expenses by Category</h3>
                {categoryData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={categoryData}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        fill="#3B82F6"
                        dataKey="value"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        labelLine={false}
                      >
                        {categoryData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#0F172A', 
                          border: '1px solid #1E293B',
                          borderRadius: '8px',
                          color: '#F8FAFC'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-text-muted">
                    No expense data yet
                  </div>
                )}
              </div>

              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6 lg:col-span-2">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Product Costs</h3>
                {productChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={productChartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                      <XAxis dataKey="name" stroke="#94A3B8" />
                      <YAxis stroke="#94A3B8" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#0F172A', 
                          border: '1px solid #1E293B',
                          borderRadius: '8px',
                          color: '#F8FAFC'
                        }}
                      />
                      <Bar dataKey="cost" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-text-muted">
                    No product data yet
                  </div>
                )}
              </div>

              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6 lg:col-span-2">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Monthly Overview</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                    <XAxis dataKey="month" stroke="#94A3B8" />
                    <YAxis stroke="#94A3B8" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#0F172A', 
                        border: '1px solid #1E293B',
                        borderRadius: '8px',
                        color: '#F8FAFC'
                      }}
                    />
                    <Line type="monotone" dataKey="income" stroke="#3B82F6" strokeWidth={2} dot={{ fill: '#3B82F6' }} name="Income" />
                    <Line type="monotone" dataKey="expected" stroke="#F59E0B" strokeWidth={2} strokeDasharray="5 5" dot={{ fill: '#F59E0B' }} name="Expected Expense" />
                    <Line type="monotone" dataKey="actual" stroke="#EF4444" strokeWidth={2} dot={{ fill: '#EF4444' }} name="Actual Expense" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'income' && (
          <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6 max-w-2xl">
            <h2 className="text-xl font-semibold text-text-primary mb-6">Monthly Income & Savings</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-text-secondary mb-2">Monthly Income (₹)</label>
                  <input
                    type="number"
                    value={monthlyIncome}
                    onChange={(e) => setMonthlyIncome(e.target.value)}
                    placeholder="Enter your monthly income"
                    className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-blue-500 transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm text-text-secondary mb-2">Expected Savings (₹)</label>
                  <input
                    type="number"
                    value={expectedSavings}
                    onChange={(e) => setExpectedSavings(e.target.value)}
                    placeholder="How much you want to save"
                    className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-blue-500 transition-colors"
                  />
                </div>
              </div>
              <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                <p className="text-text-secondary text-sm">
                  <span className="text-blue-500 font-medium">Expected Expense:</span> 
                  <span className="text-text-primary font-semibold ml-2">₹{expectedExpenses.toLocaleString()}</span>
                  <span className="text-text-muted text-xs ml-2">(Income - Savings)</span>
                </p>
              </div>
              <button
                onClick={saveIncome}
                disabled={incomeLoading}
                className="px-6 py-3 bg-blue-500 text-white font-semibold rounded-xl hover:bg-blue-600 transition-colors disabled:opacity-50 cursor-pointer"
              >
                {incomeLoading ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        )}

        {activeTab === 'products' && (
          <div className="space-y-6">
            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6 max-w-2xl">
              <h2 className="text-xl font-semibold text-text-primary mb-6">
                {editingId ? 'Edit Product' : 'Add Product'}
              </h2>
              <form onSubmit={handleProductSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-text-secondary mb-2">Product Name</label>
                    <input
                      type="text"
                      value={productForm.name}
                      onChange={(e) => setProductForm({ ...productForm, name: e.target.value })}
                      required
                      placeholder="e.g., Laptop"
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-text-secondary mb-2">Category</label>
                    <select
                      value={productForm.category}
                      onChange={(e) => setProductForm({ ...productForm, category: e.target.value })}
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-blue-500 transition-colors cursor-pointer"
                    >
                      {CATEGORIES.map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-text-secondary mb-2">Quantity</label>
                    <input
                      type="number"
                      value={productForm.quantity}
                      onChange={(e) => setProductForm({ ...productForm, quantity: e.target.value })}
                      required
                      min="1"
                      placeholder="e.g., 2"
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-text-secondary mb-2">Cost per Unit (₹)</label>
                    <input
                      type="number"
                      value={productForm.cost_per_unit}
                      onChange={(e) => setProductForm({ ...productForm, cost_per_unit: e.target.value })}
                      required
                      min="0"
                      step="0.01"
                      placeholder="e.g., 999.99"
                      className="w-full px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-background border border-secondary rounded-xl">
                  <div>
                    <span className="font-medium text-text-primary">Essential Item</span>
                    <p className="text-text-muted text-sm">Toggle if this is a necessary expense</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setProductForm({ ...productForm, is_essential: !productForm.is_essential })}
                    className={`relative w-14 h-8 rounded-full transition-colors duration-200 cursor-pointer ${
                      productForm.is_essential ? 'bg-blue-500' : 'bg-secondary'
                    }`}
                  >
                    <span
                      className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-transform duration-200 ${
                        productForm.is_essential ? 'translate-x-0' : '-translate-x-6'
                      }`}
                    />
                  </button>
                </div>

                <div className="flex gap-4">
                  <button
                    type="submit"
                    className="px-6 py-3 bg-blue-500 text-white font-semibold rounded-xl hover:bg-blue-600 transition-colors cursor-pointer"
                  >
                    {editingId ? 'Update Product' : 'Add Product'}
                  </button>
                  {editingId && (
                    <button
                      type="button"
                      onClick={() => {
                        setEditingId(null);
                        setProductForm({ name: '', quantity: '', cost_per_unit: '', category: 'Groceries', is_essential: false });
                      }}
                      className="px-6 py-3 bg-background border border-secondary text-text-primary font-semibold rounded-xl hover:bg-secondary/50 transition-colors cursor-pointer"
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </form>
            </div>

            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
              <h2 className="text-xl font-semibold text-text-primary mb-4">Product List</h2>
              {productsLoading ? (
                <p className="text-text-muted">Loading...</p>
              ) : products.length === 0 ? (
                <p className="text-text-muted">No products added yet</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-secondary">
                        <th className="text-left py-3 px-4 text-text-secondary font-medium">Product</th>
                        <th className="text-left py-3 px-4 text-text-secondary font-medium">Category</th>
                        <th className="text-left py-3 px-4 text-text-secondary font-medium">Essential</th>
                        <th className="text-left py-3 px-4 text-text-secondary font-medium">Qty</th>
                        <th className="text-left py-3 px-4 text-text-secondary font-medium">Unit Cost</th>
                        <th className="text-left py-3 px-4 text-text-secondary font-medium">Total</th>
                        <th className="text-left py-3 px-4 text-text-secondary font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {products.map((product) => (
                        <tr key={product.id} className="border-b border-secondary/50 hover:bg-secondary/20">
                          <td className="py-3 px-4 text-text-primary">{product.name}</td>
                          <td className="py-3 px-4 text-text-secondary">{product.category}</td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                              product.is_essential 
                                ? 'bg-blue-500/20 text-blue-400' 
                                : 'bg-orange-500/20 text-orange-400'
                            }`}>
                              {product.is_essential ? 'Essential' : 'Non-Essential'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-text-secondary">{product.quantity}</td>
                          <td className="py-3 px-4 text-text-secondary">₹{product.cost_per_unit}</td>
                          <td className="py-3 px-4 text-blue-500 font-medium">₹{product.total_cost}</td>
                          <td className="py-3 px-4">
                            <div className="flex gap-2">
                              <button
                                onClick={() => handleEdit(product)}
                                className="px-3 py-1 text-sm bg-blue-500/20 text-blue-500 rounded-lg hover:bg-blue-500/30 transition-colors cursor-pointer"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => handleDelete(product.id)}
                                className="px-3 py-1 text-sm bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors cursor-pointer"
                              >
                                Delete
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'dynamic-limit' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {(() => {
                const limitData = computeDynamicLimit(monthlyIncome, expectedSavings, products, totalExpenses);
                return (
                  <>
                    <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                      <p className="text-text-secondary text-sm mb-1">Daily Dynamic Limit</p>
                      <p className="text-3xl font-bold text-blue-500">₹{limitData.dynamic_limit.toLocaleString()}</p>
                    </div>
                    <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                      <p className="text-text-secondary text-sm mb-1">Safe to Spend Now</p>
                      <p className={`text-3xl font-bold ${limitData.safe_spend_now > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        ₹{limitData.safe_spend_now.toLocaleString()}
                      </p>
                    </div>
                    <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                      <p className="text-text-secondary text-sm mb-1">Status</p>
                      <span className={`inline-block px-3 py-1 text-lg font-semibold rounded-full ${
                        limitData.status === 'relaxed' ? 'bg-green-500/20 text-green-400' :
                        limitData.status === 'moderate' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-red-500/20 text-red-400'
                      }`}>
                        {limitData.status.toUpperCase()}
                      </span>
                    </div>
                  </>
                );
              })()}
            </div>

            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Decision Factors</h3>
              {(() => {
                const limitData = computeDynamicLimit(monthlyIncome, expectedSavings, products, totalExpenses);
                return (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-background/50 rounded-xl p-4">
                      <p className="text-text-muted text-sm mb-2">Behavior Factor</p>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full transition-all ${
                              parseFloat(limitData.behavior_factor) >= 0.85 ? 'bg-green-500' :
                              parseFloat(limitData.behavior_factor) >= 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${parseFloat(limitData.behavior_factor) * 100}%` }}
                          />
                        </div>
                        <span className="text-text-primary font-semibold">{limitData.behavior_factor}</span>
                      </div>
                      <p className="text-text-muted text-xs mt-2">
                        {parseFloat(limitData.behavior_factor) >= 0.85 ? 'Good spending habits' :
                         parseFloat(limitData.behavior_factor) >= 0.7 ? 'Moderate risk' : 'High impulsive spending'}
                      </p>
                    </div>
                    <div className="bg-background/50 rounded-xl p-4">
                      <p className="text-text-muted text-sm mb-2">Context Factor</p>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full transition-all ${
                              parseFloat(limitData.context_factor) >= 0.85 ? 'bg-green-500' :
                              parseFloat(limitData.context_factor) >= 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${parseFloat(limitData.context_factor) * 100}%` }}
                          />
                        </div>
                        <span className="text-text-primary font-semibold">{limitData.context_factor}</span>
                      </div>
                      <p className="text-text-muted text-xs mt-2">
                        {parseFloat(limitData.context_factor) >= 0.85 ? 'Low risk time' :
                         parseFloat(limitData.context_factor) >= 0.7 ? 'Moderate risk' : 'High risk time (evening/weekend)'}
                      </p>
                    </div>
                    <div className="bg-background/50 rounded-xl p-4">
                      <p className="text-text-muted text-sm mb-2">Goal Factor</p>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full transition-all ${
                              parseFloat(limitData.goal_factor) >= 0.85 ? 'bg-green-500' :
                              parseFloat(limitData.goal_factor) >= 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${parseFloat(limitData.goal_factor) * 100}%` }}
                          />
                        </div>
                        <span className="text-text-primary font-semibold">{limitData.goal_factor}</span>
                      </div>
                      <p className="text-text-muted text-xs mt-2">
                        {parseFloat(limitData.goal_factor) >= 0.85 ? 'On track for savings' :
                         parseFloat(limitData.goal_factor) >= 0.7 ? 'Some savings pressure' : 'High savings goal pressure'}
                      </p>
                    </div>
                  </div>
                );
              })()}
            </div>

            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Insights & Recommendations</h3>
              {(() => {
                const limitData = computeDynamicLimit(monthlyIncome, expectedSavings, products, totalExpenses);
                const insights = [];
                
                if (limitData.explanation.behavior) {
                  insights.push({ type: 'warning', text: limitData.explanation.behavior });
                }
                if (limitData.explanation.context) {
                  insights.push({ type: 'warning', text: limitData.explanation.context });
                }
                if (limitData.explanation.goal) {
                  insights.push({ type: 'warning', text: limitData.explanation.goal });
                }
                
                if (limitData.safe_spend_now === 0) {
                  insights.push({ type: 'error', text: "You've reached today's limit. Avoid further spending." });
                } else if (limitData.safe_spend_now < 100) {
                  insights.push({ type: 'warning', text: 'Low remaining spend. Be cautious with purchases.' });
                } else {
                  insights.push({ type: 'success', text: 'You are within a safe spending range.' });
                }
                
                if (limitData.impulsive_ratio > 50) {
                  insights.push({ type: 'warning', text: `${limitData.impulsive_ratio}% of your purchases are non-essential. Consider reducing impulsive buying.` });
                }
                
                if (insights.length === 0) {
                  insights.push({ type: 'success', text: 'All factors look healthy. Keep up the good financial habits!' });
                }
                
                return (
                  <div className="space-y-3">
                    {insights.map((insight, index) => (
                      <div 
                        key={index}
                        className={`p-4 rounded-xl flex items-start gap-3 ${
                          insight.type === 'error' ? 'bg-red-500/10 border border-red-500/30' :
                          insight.type === 'warning' ? 'bg-yellow-500/10 border border-yellow-500/30' :
                          'bg-green-500/10 border border-green-500/30'
                        }`}
                      >
                        <span className={`text-xl ${
                          insight.type === 'error' ? 'text-red-400' :
                          insight.type === 'warning' ? 'text-yellow-400' :
                          'text-green-400'
                        }`}>
                          {insight.type === 'error' ? '🚨' : insight.type === 'warning' ? '⚠️' : ''}
                        </span>
                        <p className={`text-sm ${
                          insight.type === 'error' ? 'text-red-300' :
                          insight.type === 'warning' ? 'text-yellow-300' :
                          'text-green-300'
                        }`}>
                          {insight.text}
                        </p>
                      </div>
                    ))}
                  </div>
                );
              })()}
            </div>

            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Spending Analysis</h3>
              {(() => {
                const limitData = computeDynamicLimit(monthlyIncome, expectedSavings, products, totalExpenses);
                return (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 bg-background/50 rounded-xl">
                      <p className="text-text-muted text-sm mb-1">Base Limit</p>
                      <p className="text-xl font-bold text-text-primary">₹{limitData.base_limit.toLocaleString()}</p>
                      <p className="text-text-muted text-xs">per day</p>
                    </div>
                    <div className="text-center p-4 bg-background/50 rounded-xl">
                      <p className="text-text-muted text-sm mb-1">Spent Today</p>
                      <p className="text-xl font-bold text-orange-400">₹{limitData.spent_today.toLocaleString()}</p>
                      <p className="text-text-muted text-xs">estimated</p>
                    </div>
                    <div className="text-center p-4 bg-background/50 rounded-xl">
                      <p className="text-text-muted text-sm mb-1">Month Budget Left</p>
                      <p className="text-xl font-bold text-green-400">₹{limitData.remaining_budget.toLocaleString()}</p>
                      <p className="text-text-muted text-xs">remaining</p>
                    </div>
                    <div className="text-center p-4 bg-background/50 rounded-xl">
                      <p className="text-text-muted text-sm mb-1">Non-Essential</p>
                      <p className="text-xl font-bold text-orange-400">{limitData.impulsive_ratio}%</p>
                      <p className="text-text-muted text-xs">of purchases</p>
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        )}

        {activeTab === 'ai-behavior' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {(() => {
                const behaviorData = computeBehaviorAnalysis(monthlyIncome, expectedSavings, products, totalExpenses);
                return (
                  <>
                    <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                      <p className="text-text-secondary text-sm mb-1">Behavior Score</p>
                      <div className="flex items-center gap-3">
                        <p className={`text-4xl font-bold ${
                          behaviorData.behavior_score >= 70 ? 'text-green-400' :
                          behaviorData.behavior_score >= 40 ? 'text-yellow-400' : 'text-red-400'
                        }`}>
                          {behaviorData.behavior_score}
                        </p>
                        <span className="text-text-muted">/ 100</span>
                      </div>
                    </div>
                    <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                      <p className="text-text-secondary text-sm mb-1">Risk Level</p>
                      <span className={`inline-block px-4 py-2 text-lg font-semibold rounded-full ${
                        behaviorData.risk_level === 'low' ? 'bg-green-500/20 text-green-400' :
                        behaviorData.risk_level === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-red-500/20 text-red-400'
                      }`}>
                        {behaviorData.risk_level.toUpperCase()}
                      </span>
                    </div>
                    <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                      <p className="text-text-secondary text-sm mb-1">Behavior Profile</p>
                      <p className="text-xl font-semibold text-blue-400 capitalize">
                        {behaviorData.behavior_profile.replace('_', ' ')}
                      </p>
                    </div>
                  </>
                );
              })()}
            </div>

            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Spending Behavior Chart</h3>
              {(() => {
                const behaviorData = computeBehaviorAnalysis(monthlyIncome, expectedSavings, products, totalExpenses);
                const chartData = behaviorData.simulation.chart || [];
                return chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                      <XAxis dataKey="date" stroke="#94A3B8" />
                      <YAxis stroke="#94A3B8" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#0F172A', 
                          border: '1px solid #1E293B',
                          borderRadius: '8px',
                          color: '#F8FAFC'
                        }}
                      />
                      <Bar dataKey="actual" fill="#3B82F6" name="Actual" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="predicted" fill="#60A5FA" name="Predicted Avg" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-text-muted">
                    Add products to see spending behavior chart
                  </div>
                );
              })()}
              <p className="text-text-muted text-sm text-center mt-2">Actual vs Predicted Spending</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Spending Patterns</h3>
                {(() => {
                  const behaviorData = computeBehaviorAnalysis(monthlyIncome, expectedSavings, products, totalExpenses);
                  const patterns = behaviorData.patterns;
                  return (
                    <div className="space-y-4">
                      <div className="bg-background/50 rounded-xl p-4">
                        <p className="text-text-secondary text-sm mb-2">Overspending Frequency</p>
                        <div className="flex items-center gap-3">
                          <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${
                                patterns.overspending.frequency <= 2 ? 'bg-green-500' :
                                patterns.overspending.frequency <= 4 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${Math.min(patterns.overspending.frequency * 20, 100)}%` }}
                            />
                          </div>
                          <span className="text-text-primary font-medium">{patterns.overspending.frequency} times</span>
                        </div>
                      </div>
                      <div className="bg-background/50 rounded-xl p-4">
                        <p className="text-text-secondary text-sm mb-2">Spending Volatility</p>
                        <p className="text-xl font-bold text-blue-400">₹{patterns.overspending.volatility.toLocaleString()}</p>
                        <p className="text-text-muted text-xs">Average deviation from mean</p>
                      </div>
                      <div className="bg-background/50 rounded-xl p-4">
                        <p className="text-text-secondary text-sm mb-2">Spending Trend</p>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          patterns.trend === 'decreasing' ? 'bg-green-500/20 text-green-400' :
                          patterns.trend === 'increasing' ? 'bg-red-500/20 text-red-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {patterns.trend === 'insufficient_data' ? 'Not enough data' : patterns.trend.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  );
                })()}
              </div>

              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Essential vs Non-Essential</h3>
                {(() => {
                  const behaviorData = computeBehaviorAnalysis(monthlyIncome, expectedSavings, products, totalExpenses);
                  const essentialData = [
                    { name: 'Essential', value: behaviorData.essential_count, amount: behaviorData.essential_expenses },
                    { name: 'Non-Essential', value: behaviorData.non_essential_count, amount: behaviorData.non_essential_expenses },
                  ];
                  return (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-4 bg-blue-500/10 rounded-xl">
                          <p className="text-2xl font-bold text-blue-400">{behaviorData.essential_count}</p>
                          <p className="text-text-secondary text-sm">Essential Items</p>
                          <p className="text-text-muted text-xs">₹{behaviorData.essential_expenses.toLocaleString()}</p>
                        </div>
                        <div className="text-center p-4 bg-orange-500/10 rounded-xl">
                          <p className="text-2xl font-bold text-orange-400">{behaviorData.non_essential_count}</p>
                          <p className="text-text-secondary text-sm">Non-Essential Items</p>
                          <p className="text-text-muted text-xs">₹{behaviorData.non_essential_expenses.toLocaleString()}</p>
                        </div>
                      </div>
                      <div className="bg-background/50 rounded-xl p-4">
                        <p className="text-text-secondary text-sm mb-2">Savings Rate</p>
                        <div className="flex items-center gap-3">
                          <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${
                                parseInt(behaviorData.savings_ratio) >= 20 ? 'bg-green-500' :
                                parseInt(behaviorData.savings_ratio) >= 10 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${Math.min(parseInt(behaviorData.savings_ratio) * 5, 100)}%` }}
                            />
                          </div>
                          <span className="text-text-primary font-medium">{behaviorData.savings_ratio}%</span>
                        </div>
                        <p className="text-text-muted text-xs mt-2">
                          {parseInt(behaviorData.savings_ratio) >= 20 ? 'On track for savings' :
                           parseInt(behaviorData.savings_ratio) >= 10 ? 'Could improve savings rate' :
                           'Focus on increasing savings'}
                        </p>
                      </div>
                    </div>
                  );
                })()}
              </div>
            </div>

            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Insights</h3>
              {(() => {
                const behaviorData = computeBehaviorAnalysis(monthlyIncome, expectedSavings, products, totalExpenses);
                return (
                  <div className="space-y-3">
                    {behaviorData.insights.map((insight, index) => (
                      <div key={index} className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl flex items-start gap-3">
                        <span className="text-xl"></span>
                        <p className="text-blue-300">{insight}</p>
                      </div>
                    ))}
                  </div>
                );
              })()}
            </div>

            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Recommendations</h3>
              {(() => {
                const behaviorData = computeBehaviorAnalysis(monthlyIncome, expectedSavings, products, totalExpenses);
                return (
                  <div className="space-y-3">
                    {behaviorData.recommendations.map((rec, index) => (
                      <div key={index} className="p-4 bg-green-500/10 border border-green-500/30 rounded-xl flex items-start gap-3">
                        <span className="text-xl"></span>
                        <p className="text-green-300">{rec}</p>
                      </div>
                    ))}
                  </div>
                );
              })()}
            </div>

            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">5-Year Future Projection</h3>
              {(() => {
                const behaviorData = computeBehaviorAnalysis(monthlyIncome, expectedSavings, products, totalExpenses);
                const projection = behaviorData.simulation.projection || {};
                return (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-background/50 rounded-xl p-4 text-center">
                        <p className="text-text-muted text-sm mb-1">Current 5Y Spend</p>
                        <p className="text-xl font-bold text-red-400">₹{projection.current_spend_5y?.toLocaleString() || 0}</p>
                      </div>
                      <div className="bg-background/50 rounded-xl p-4 text-center">
                        <p className="text-text-muted text-sm mb-1">Improved 5Y Spend</p>
                        <p className="text-xl font-bold text-green-400">₹{projection.improved_spend_5y?.toLocaleString() || 0}</p>
                      </div>
                      <div className="bg-background/50 rounded-xl p-4 text-center">
                        <p className="text-text-muted text-sm mb-1">Potential Savings</p>
                        <p className="text-xl font-bold text-blue-400">₹{projection.potential_savings?.toLocaleString() || 0}</p>
                      </div>
                    </div>
                    {projection.note && (
                      <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                        <p className="text-blue-300 text-sm">{projection.note}</p>
                      </div>
                    )}
                  </div>
                );
              })()}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
