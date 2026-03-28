import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import Navbar from './Navbar';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  BarController,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  BarController,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  ChartTooltip,
  Legend,
  Filler,
);

const API_URL = import.meta.env.VITE_STOCKS_API_URL || 'http://localhost:8000';

const ALL_STOCKS = [
  'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
  'HINDUNILVR', 'SBIN', 'BHARTIARTL', 'KOTAKBANK', 'ITC',
  'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA',
  'WIPRO', 'HCLTECH', 'TATAMOTORS', 'NESTLEIND', 'NTPC',
];

const RISK_PROFILES = {
  Conservative: [
    'Focus on quality blue-chip stocks with consistent dividends',
    'Consider index funds for diversified exposure',
    'Maintain 60%+ allocation to large-cap stocks',
  ],
  Moderate: [
    'Balance between growth and stability',
    'Combine large-caps with selective mid-cap opportunities',
    'Review portfolio every quarter',
  ],
  Aggressive: [
    'Higher exposure to growth sectors (IT, Pharma)',
    'Consider momentum stocks with higher beta',
    'Be prepared for volatility and longer holding periods',
  ],
};

const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: '#94A3B8', font: { family: 'IBM Plex Sans' } },
    },
    tooltip: {
      backgroundColor: '#0F172A',
      borderColor: '#1E293B',
      borderWidth: 1,
      titleColor: '#F8FAFC',
      bodyColor: '#F8FAFC',
      padding: 12,
      cornerRadius: 8,
    },
  },
  scales: {
    x: {
      grid: { color: '#1E293B', lineWidth: 1 },
      ticks: { color: '#94A3B8', font: { family: 'IBM Plex Sans', size: 10 } },
      border: { color: '#1E293B' },
    },
    y: {
      grid: { color: '#1E293B', lineWidth: 1 },
      ticks: { color: '#94A3B8', font: { family: 'IBM Plex Sans', size: 10 } },
      border: { color: '#1E293B' },
    },
  },
};

export default function Stocks() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('market');
  const [selectedStock, setSelectedStock] = useState('RELIANCE');
  const [riskProfile, setRiskProfile] = useState('Moderate');
  
  const [marketData, setMarketData] = useState({ indices: [], gainers: [], losers: [], sectorPerf: [] });
  const [stockInfo, setStockInfo] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [indicators, setIndicators] = useState(null);
  
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [marketInsight, setMarketInsight] = useState('');
  const [insightLoading, setInsightLoading] = useState(false);
  
  const chatEndRef = useRef(null);

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
    if (user && activeTab === 'market') {
      fetchMarketData();
    }
  }, [user, activeTab]);

  useEffect(() => {
    if (user && activeTab === 'analysis') {
      fetchStockData(selectedStock);
    }
  }, [user, activeTab, selectedStock]);

  const fetchMarketData = async () => {
    try {
      const [summaryRes, moversRes, sectorsRes] = await Promise.all([
        fetch(`${API_URL}/api/market/summary`),
        fetch(`${API_URL}/api/market/movers`),
        fetch(`${API_URL}/api/market/sectors`),
      ]);

      const summary = await summaryRes.json();
      const movers = await moversRes.json();
      const sectors = await sectorsRes.json();

      const indices = Object.entries(summary).map(([name, data]) => ({
        name,
        value: data.value,
        change: data.change,
        pct: data.pct,
      }));

      const sectorPerf = Object.entries(sectors).map(([sector, change]) => ({
        sector,
        change,
      }));

      setMarketData({
        indices,
        gainers: movers.gainers || [],
        losers: movers.losers || [],
        sectorPerf,
      });
    } catch (error) {
      console.error('Failed to fetch market data:', error);
    }
  };

  const fetchStockData = async (symbol) => {
    try {
      const [infoRes, historyRes, indicatorsRes] = await Promise.all([
        fetch(`${API_URL}/api/stock/${symbol}`),
        fetch(`${API_URL}/api/stock/${symbol}/history?period=1mo`),
        fetch(`${API_URL}/api/stock/${symbol}/indicators`),
      ]);

      const info = await infoRes.json();
      const history = await historyRes.json();
      const ind = await indicatorsRes.json();

      setStockInfo(info);
      setHistoricalData(history);
      setIndicators(ind);
    } catch (error) {
      console.error('Failed to fetch stock data:', error);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/');
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;

    const userMessage = { role: 'user', content: chatInput };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: chatInput,
          history: chatMessages.slice(-6),
          risk_profile: riskProfile,
        }),
      });
      const data = await response.json();
      setChatMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    }
    setChatLoading(false);
  };

  const generateMarketInsight = async () => {
    setInsightLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/chat/insight?risk_profile=${riskProfile}`, {
        method: 'POST',
      });
      const data = await response.json();
      setMarketInsight(data.response);
    } catch (error) {
      setMarketInsight('Sorry, I encountered an error generating the insight. Please try again.');
    }
    setInsightLoading(false);
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-text-primary">Loading...</div>
      </div>
    );
  }

  const formatPrice = (val) => {
    if (!val && val !== 0) return 'N/A';
    return `₹${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const sectorChartData = {
    labels: marketData.sectorPerf?.map(d => d.sector) || [],
    datasets: [
      {
        label: 'Change %',
        data: marketData.sectorPerf?.map(d => d.change) || [],
        backgroundColor: marketData.sectorPerf?.map(d => d.change >= 0 ? '#22c55e' : '#ef4444') || [],
        borderWidth: 0,
      },
    ],
  };

  const volumeChartData = {
    labels: historicalData?.map(d => d.date) || [],
    datasets: [
      {
        label: 'Volume',
        data: historicalData?.map(d => d.volume) || [],
        backgroundColor: historicalData?.map(d => d.close >= d.open ? '#22c55e80' : '#ef444480') || [],
      },
    ],
  };

  const candlestickData = {
    labels: historicalData?.map(d => d.date) || [],
    datasets: [
      {
        label: 'Close Price',
        data: historicalData?.map(d => d.close) || [],
        backgroundColor: historicalData?.map(d => d.close >= (d.open || d.close) ? '#22c55e' : '#ef4444') || [],
        borderColor: historicalData?.map(d => d.close >= (d.open || d.close) ? '#16a34a' : '#dc2626') || [],
        borderWidth: 1,
      },
    ],
  };

  const priceLineData = {
    labels: historicalData?.map(d => d.date) || [],
    datasets: [
      {
        label: 'Close Price',
        data: historicalData?.map(d => d.close) || [],
        borderColor: '#3b82f6',
        backgroundColor: '#3b82f620',
        fill: true,
        tension: 0,
        pointRadius: 0,
        pointHoverRadius: 4,
      },
    ],
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar user={user} onLogout={handleLogout} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-8">
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 text-text-secondary hover:text-blue-400 mb-4 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Dashboard
        </Link>
        
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-text-primary">KRED AI — Indian Market Intelligence</h1>
          <p className="text-text-secondary mt-1">Real-time stock market analysis and AI-powered insights</p>
        </div>

        <div className="flex flex-wrap gap-2 mb-6">
          {['market', 'analysis', 'ai-insights'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-xl font-medium transition-colors cursor-pointer ${
                activeTab === tab
                  ? 'bg-blue-500 text-white'
                  : 'bg-surface border border-secondary text-text-secondary hover:text-text-primary'
              }`}
            >
              {tab === 'market' ? 'Market Dashboard' : tab === 'analysis' ? 'Stock Analysis' : 'AI Insights'}
            </button>
          ))}
        </div>

        {activeTab === 'market' && (
          <div className="space-y-6">
            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
              <h2 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                <span>Market Indices</span>
                <button onClick={fetchMarketData} className="text-blue-400 text-sm hover:text-blue-300">Refresh</button>
              </h2>
              {marketData.indices?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {marketData.indices.map((idx) => (
                    <div key={idx.name} className="bg-background/50 rounded-xl p-4 border border-secondary">
                      <p className="text-text-muted text-xs uppercase tracking-wider mb-1">{idx.name}</p>
                      <p className="text-xl font-bold text-text-primary">{formatPrice(idx.value)}</p>
                      <p className={`text-sm font-semibold ${idx.pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {idx.pct >= 0 ? '▲' : '▼'} {Math.abs(idx.pct).toFixed(2)}%
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-text-muted">Loading market data...</div>
              )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <h2 className="text-lg font-semibold text-text-primary mb-4 text-green-400">🚀 Top Gainers</h2>
                {marketData.gainers?.length > 0 ? (
                  <div className="space-y-2">
                    {marketData.gainers.map((g) => (
                      <div key={g.symbol} className="flex items-center justify-between bg-background/50 rounded-lg p-3 border border-secondary">
                        <div>
                          <span className="font-bold text-blue-400">{g.symbol}</span>
                          <span className="text-text-muted text-sm ml-2">{g.name}</span>
                        </div>
                        <div className="text-right">
                          <p className="text-text-primary font-semibold">{formatPrice(g.price)}</p>
                          <p className="text-green-400 text-sm">+{g.change.toFixed(2)}%</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-text-muted">Loading gainers...</div>
                )}
              </div>

              <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
                <h2 className="text-lg font-semibold text-text-primary mb-4 text-red-400">📉 Top Losers</h2>
                {marketData.losers?.length > 0 ? (
                  <div className="space-y-2">
                    {marketData.losers.map((l) => (
                      <div key={l.symbol} className="flex items-center justify-between bg-background/50 rounded-lg p-3 border border-secondary">
                        <div>
                          <span className="font-bold text-blue-400">{l.symbol}</span>
                          <span className="text-text-muted text-sm ml-2">{l.name}</span>
                        </div>
                        <div className="text-right">
                          <p className="text-text-primary font-semibold">{formatPrice(l.price)}</p>
                          <p className="text-red-400 text-sm">{l.change.toFixed(2)}%</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-text-muted">Loading losers...</div>
                )}
              </div>
            </div>

            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
              <h2 className="text-lg font-semibold text-text-primary mb-4">Sector Performance</h2>
              {marketData.sectorPerf?.length > 0 ? (
                <div style={{ height: '300px' }}>
                  <Bar data={sectorChartData} options={chartDefaults} />
                </div>
              ) : (
                <div className="text-text-muted">Loading sector data...</div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-6">
            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
              <div className="flex flex-wrap gap-4 mb-6">
                <select
                  value={selectedStock}
                  onChange={(e) => setSelectedStock(e.target.value)}
                  className="px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-blue-500 cursor-pointer"
                >
                  {ALL_STOCKS.map((stock) => (
                    <option key={stock} value={stock}>{stock}</option>
                  ))}
                </select>
                <select
                  value={riskProfile}
                  onChange={(e) => setRiskProfile(e.target.value)}
                  className="px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-blue-500 cursor-pointer"
                >
                  <option value="Conservative">Conservative</option>
                  <option value="Moderate">Moderate</option>
                  <option value="Aggressive">Aggressive</option>
                </select>
              </div>

              {stockInfo ? (
                <>
                  <div className="bg-gradient-to-r from-blue-900/30 to-surface rounded-xl p-6 mb-6 border border-blue-500/30">
                    <h2 className="text-2xl font-bold text-text-primary">{stockInfo.name || selectedStock}</h2>
                    <p className="text-text-muted">{stockInfo.sector || 'N/A'} · {stockInfo.industry || 'N/A'} · NSE: {selectedStock}</p>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                    <div className="bg-background/50 rounded-xl p-4 text-center border border-secondary">
                      <p className="text-text-muted text-xs uppercase tracking-wider mb-1">Current Price</p>
                      <p className="text-lg font-bold text-text-primary">{formatPrice(stockInfo.price)}</p>
                    </div>
                    <div className="bg-background/50 rounded-xl p-4 text-center border border-secondary">
                      <p className="text-text-muted text-xs uppercase tracking-wider mb-1">Market Cap</p>
                      <p className="text-lg font-bold text-text-primary">{stockInfo.market_cap ? `₹${(stockInfo.market_cap / 1e12).toFixed(2)}T` : 'N/A'}</p>
                    </div>
                    <div className="bg-background/50 rounded-xl p-4 text-center border border-secondary">
                      <p className="text-text-muted text-xs uppercase tracking-wider mb-1">P/E Ratio</p>
                      <p className="text-lg font-bold text-text-primary">{stockInfo.pe || 'N/A'}</p>
                    </div>
                    <div className="bg-background/50 rounded-xl p-4 text-center border border-secondary">
                      <p className="text-text-muted text-xs uppercase tracking-wider mb-1">52W High</p>
                      <p className="text-lg font-bold text-green-400">{formatPrice(stockInfo.high52)}</p>
                    </div>
                    <div className="bg-background/50 rounded-xl p-4 text-center border border-secondary">
                      <p className="text-text-muted text-xs uppercase tracking-wider mb-1">52W Low</p>
                      <p className="text-lg font-bold text-red-400">{formatPrice(stockInfo.low52)}</p>
                    </div>
                    <div className="bg-background/50 rounded-xl p-4 text-center border border-secondary">
                      <p className="text-text-muted text-xs uppercase tracking-wider mb-1">Div Yield</p>
                      <p className="text-lg font-bold text-text-primary">{stockInfo.div_yield || 0}%</p>
                    </div>
                  </div>

                  {indicators && (
                    <>
                      <h3 className="text-lg font-semibold text-blue-400 border-l-4 border-blue-500 pl-3 mb-4">Technical Signals</h3>
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                        <div className="bg-background/50 rounded-xl p-4 text-center border border-secondary">
                          <p className="text-text-muted text-xs mb-1">RSI (14)</p>
                          <p className={`text-lg font-bold ${indicators.rsi > 70 ? 'text-red-400' : indicators.rsi < 30 ? 'text-green-400' : 'text-yellow-400'}`}>
                            {indicators.rsi || 'N/A'}
                          </p>
                        </div>
                        <div className="bg-background/50 rounded-xl p-4 text-center border border-secondary">
                          <p className="text-text-muted text-xs mb-1">MACD</p>
                          <p className={`text-lg font-bold ${indicators.macd > indicators.macd_signal ? 'text-green-400' : 'text-red-400'}`}>
                            {indicators.macd?.toFixed(2) || 'N/A'}
                          </p>
                        </div>
                        <div className="bg-background/50 rounded-xl p-4 text-center border border-secondary">
                          <p className="text-text-muted text-xs mb-1">Volatility</p>
                          <p className="text-lg font-bold text-yellow-400">{indicators.volatility || 'N/A'}%</p>
                        </div>
                        <div className="bg-background/50 rounded-xl p-4 text-center border border-secondary">
                          <p className="text-text-muted text-xs mb-1">Volume Ratio</p>
                          <p className="text-lg font-bold text-blue-400">{indicators.volume_ratio || 'N/A'}x</p>
                        </div>
                        <div className="bg-background/50 rounded-xl p-4 text-center border border-secondary">
                          <p className="text-text-muted text-xs mb-1">Beta</p>
                          <p className="text-lg font-bold text-text-primary">{stockInfo.beta || 'N/A'}</p>
                        </div>
                      </div>
                    </>
                  )}

                  {historicalData?.length > 0 ? (
                    <>
                      <h3 className="text-lg font-semibold text-text-primary mb-4">Price Trend</h3>
                      <div className="bg-background/50 rounded-xl p-4 border border-secondary mb-6">
                        <div style={{ height: '250px' }}>
                          <Line 
                            key={`line-${selectedStock}`}
                            data={priceLineData} 
                            options={{
                              ...chartDefaults,
                              elements: { line: { tension: 0 } },
                              plugins: {
                                ...chartDefaults.plugins,
                                legend: { display: false },
                              },
                            }} 
                          />
                        </div>
                      </div>

                      <h3 className="text-lg font-semibold text-text-primary mb-4">Volume</h3>
                      <div className="bg-background/50 rounded-xl p-4 border border-secondary">
                        <div style={{ height: '150px' }}>
                          <Bar 
                            key={`volume-${selectedStock}`}
                            data={volumeChartData} 
                            options={{
                              ...chartDefaults,
                              plugins: {
                                ...chartDefaults.plugins,
                                legend: { display: false },
                              },
                              scales: {
                                ...chartDefaults.scales,
                                x: { ...chartDefaults.scales.x, display: false },
                                y: {
                                  ...chartDefaults.scales.y,
                                  ticks: {
                                    ...chartDefaults.scales.y.ticks,
                                    callback: (val) => `${(val / 1000000).toFixed(0)}M`,
                                  },
                                },
                              },
                            }} 
                          />
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="text-text-muted">Loading price history...</div>
                  )}
                </>
              ) : (
                <div className="text-text-muted">Loading stock data...</div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'ai-insights' && (
          <div className="space-y-6">
            <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
              <h2 className="text-xl font-semibold text-text-primary mb-4">AI Market Intelligence</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-4">
                  <div className="flex gap-4">
                    <select
                      value={riskProfile}
                      onChange={(e) => setRiskProfile(e.target.value)}
                      className="px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary focus:outline-none focus:border-blue-500 cursor-pointer"
                    >
                      <option value="Conservative">Conservative</option>
                      <option value="Moderate">Moderate</option>
                      <option value="Aggressive">Aggressive</option>
                    </select>
                  </div>

                  <button
                    onClick={generateMarketInsight}
                    disabled={insightLoading}
                    className="w-full px-6 py-4 bg-blue-500 text-white font-semibold rounded-xl hover:bg-blue-600 transition-colors cursor-pointer disabled:opacity-50"
                  >
                    {insightLoading ? 'Generating...' : 'Generate Market Insight'}
                  </button>

                  {marketInsight && (
                    <div className="bg-gradient-to-r from-blue-900/30 to-surface border border-blue-500/30 rounded-xl p-6">
                      <p className="text-text-secondary whitespace-pre-wrap leading-relaxed">{marketInsight}</p>
                    </div>
                  )}

                  <div className="bg-surface border border-secondary rounded-xl p-4 mt-4">
                    <h3 className="text-lg font-semibold text-text-primary mb-4">KRED AI Chat</h3>
                    <div className="h-64 overflow-y-auto mb-4 space-y-3">
                      {chatMessages.length === 0 ? (
                        <p className="text-text-muted text-sm">Ask me anything about the Indian stock market!</p>
                      ) : (
                        chatMessages.map((msg, i) => (
                          <div key={i} className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-500/20 ml-8' : 'bg-background/50 mr-8'}`}>
                            <p className="text-sm text-text-primary">{msg.content}</p>
                          </div>
                        ))
                      )}
                      {chatLoading && (
                        <div className="bg-background/50 mr-8 p-3 rounded-lg">
                          <p className="text-sm text-text-muted">Thinking...</p>
                        </div>
                      )}
                      <div ref={chatEndRef} />
                    </div>
                    <form onSubmit={handleChatSubmit} className="flex gap-2">
                      <input
                        type="text"
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        placeholder="Ask about stocks, market trends..."
                        className="flex-1 px-4 py-3 bg-background border border-secondary rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-blue-500"
                        disabled={chatLoading}
                      />
                      <button
                        type="submit"
                        disabled={chatLoading || !chatInput.trim()}
                        className="px-6 py-3 bg-blue-500 text-white font-semibold rounded-xl hover:bg-blue-600 transition-colors cursor-pointer disabled:opacity-50"
                      >
                        Send
                      </button>
                    </form>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="bg-gradient-to-r from-blue-900/30 to-surface border border-blue-500/30 rounded-xl p-6">
                    <h4 className="text-lg font-semibold text-blue-400 mb-3">How to Use AI Insights</h4>
                    <ol className="text-text-secondary text-sm space-y-3">
                      <li>1. Set your <b className="text-text-primary">risk profile</b> to get personalized advice</li>
                      <li>2. Click <b className="text-blue-400">Generate Market Insight</b> for daily overview</li>
                      <li>3. Use <b className="text-blue-400">Chat</b> to ask questions about stocks</li>
                    </ol>
                    <p className="text-yellow-400 text-xs mt-4">⚠️ This is educational content, not financial advice. Always DYOR.</p>
                  </div>

                  <div className="bg-background/50 border border-secondary rounded-xl p-6">
                    <h4 className="text-lg font-semibold text-text-primary mb-3">Risk Profile Guide</h4>
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                        <span className="text-green-400 font-semibold text-sm">Conservative</span>
                      </div>
                      <p className="text-text-muted text-xs pl-5">Capital safety first. Think FD + blue-chips.</p>
                      
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 bg-yellow-500 rounded-full"></span>
                        <span className="text-yellow-400 font-semibold text-sm">Moderate</span>
                      </div>
                      <p className="text-text-muted text-xs pl-5">Balanced growth & safety. Diversified.</p>
                      
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 bg-red-500 rounded-full"></span>
                        <span className="text-red-400 font-semibold text-sm">Aggressive</span>
                      </div>
                      <p className="text-text-muted text-xs pl-5">High growth potential. Comfortable with dips.</p>
                    </div>
                  </div>

                  <div className="bg-background/50 border border-secondary rounded-xl p-6">
                    <h4 className="text-lg font-semibold text-text-primary mb-3">Tips for {riskProfile}</h4>
                    {RISK_PROFILES[riskProfile].map((tip, i) => (
                      <p key={i} className="text-text-secondary text-sm mb-2">• {tip}</p>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="mt-6 text-center text-text-muted text-sm">
          Data: Yahoo Finance · NSE/BSE · Last updated: {new Date().toLocaleString('en-IN')}
        </div>
      </main>
    </div>
  );
}
