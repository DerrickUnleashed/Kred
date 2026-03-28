import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { supabase } from '../lib/supabase';
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

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Income state
  const [monthlyIncome, setMonthlyIncome] = useState('');
  const [incomeLoading, setIncomeLoading] = useState(false);
  
  // Products state
  const [products, setProducts] = useState([]);
  const [productsLoading, setProductsLoading] = useState(true);
  const [productForm, setProductForm] = useState({
    name: '',
    quantity: '',
    cost_per_unit: '',
    category: 'Groceries',
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
      setMonthlyIncome(data.monthly_income || 0);
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
        .update({ monthly_income: monthlyIncome })
        .eq('user_id', user?.id);
    } else {
      await supabase
        .from('user_income')
        .insert([{ user_id: user?.id, monthly_income: monthlyIncome }]);
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
      total_cost: parseInt(productForm.quantity) * parseFloat(productForm.cost_per_unit),
    };

    if (editingId) {
      const { error } = await supabase
        .from('products')
        .update(productData)
        .eq('id', editingId);
      
      if (!error) {
        setEditingId(null);
        setProductForm({ name: '', quantity: '', cost_per_unit: '', category: 'Groceries' });
      }
    } else {
      await supabase
        .from('products')
        .insert([productData]);
    }

    if (!editingId) {
      setProductForm({ name: '', quantity: '', cost_per_unit: '', category: 'Groceries' });
    }
    
    fetchProducts();
  };

  const handleEdit = (product) => {
    setProductForm({
      name: product.name,
      quantity: product.quantity.toString(),
      cost_per_unit: product.cost_per_unit.toString(),
      category: product.category,
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
  const remaining = (parseFloat(monthlyIncome) || 0) - totalExpenses;

  const categoryData = CATEGORIES.map(cat => ({
    name: cat,
    value: products.filter(p => p.category === cat).reduce((sum, p) => sum + (p.total_cost || 0), 0),
  })).filter(d => d.value > 0);

  const productChartData = products.map(p => ({
    name: p.name.substring(0, 10),
    cost: p.total_cost,
    quantity: p.quantity,
  }));

  const monthlyData = [
    { month: 'Jan', income: parseFloat(monthlyIncome) || 0, expenses: totalExpenses },
    { month: 'Feb', income: parseFloat(monthlyIncome) || 0, expenses: 0 },
    { month: 'Mar', income: parseFloat(monthlyIncome) || 0, expenses: 0 },
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
      <nav className="bg-surface/80 backdrop-blur-xl border-b border-secondary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <span className="text-xl font-bold text-text-primary">KRED</span>
            </Link>
            <div className="flex items-center gap-4">
              <span className="text-text-secondary text-sm hidden sm:block">
                {user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-background border border-secondary rounded-xl text-text-primary hover:bg-secondary/50 transition-colors duration-200 cursor-pointer"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-wrap gap-2 mb-8">
          {['overview', 'products', 'income'].map((tab) => (
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
        </div>

        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <p className="text-text-secondary text-sm mb-1">Monthly Income</p>
                <p className="text-2xl font-bold text-blue-500">${parseFloat(monthlyIncome).toLocaleString() || '0'}</p>
              </div>
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <p className="text-text-secondary text-sm mb-1">Total Expenses</p>
                <p className="text-2xl font-bold text-red-400">${totalExpenses.toLocaleString()}</p>
              </div>
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <p className="text-text-secondary text-sm mb-1">Remaining</p>
                <p className={`text-2xl font-bold ${remaining >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  ${remaining.toLocaleString()}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
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

              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
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
                    <Line type="monotone" dataKey="income" stroke="#3B82F6" strokeWidth={2} dot={{ fill: '#3B82F6' }} />
                    <Line type="monotone" dataKey="expenses" stroke="#EF4444" strokeWidth={2} dot={{ fill: '#EF4444' }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'income' && (
          <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6 max-w-xl">
            <h2 className="text-xl font-semibold text-text-primary mb-6">Monthly Income</h2>
            <div className="flex gap-4">
              <input
                type="number"
                value={monthlyIncome}
                onChange={(e) => setMonthlyIncome(e.target.value)}
                placeholder="Enter your monthly income"
                className="flex-1 px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-blue-500 transition-colors"
              />
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
                    <label className="block text-sm text-text-secondary mb-2">Cost per Unit ($)</label>
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
                        setProductForm({ name: '', quantity: '', cost_per_unit: '', category: 'Groceries' });
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
                          <td className="py-3 px-4 text-text-secondary">{product.quantity}</td>
                          <td className="py-3 px-4 text-text-secondary">${product.cost_per_unit}</td>
                          <td className="py-3 px-4 text-blue-500 font-medium">${product.total_cost}</td>
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
      </main>
    </div>
  );
}
