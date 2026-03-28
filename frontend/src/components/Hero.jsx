import { Link } from 'react-router-dom';

export default function Hero() {
  const stats = [
    { value: '2.5M+', label: 'Users Protected' },
    { value: '94%', label: 'Spending Reduction' },
    { value: '₹12K', label: 'Avg. Savings/Year' },
    { value: '4.9★', label: 'User Rating' }
  ];

  return (
    <section className="relative min-h-screen flex items-center section-padding pt-32">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-accent/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>
      
      <div className="container-custom relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div className="text-center lg:text-left animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-surface/50 border border-secondary rounded-full mb-8">
              <span className="w-2 h-2 bg-accent rounded-full animate-pulse"></span>
              <span className="text-text-secondary text-sm">Behavioral Financial Platform</span>
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-text-primary leading-tight mb-6">
              Your Financial Future,{' '}
              <span className="text-gradient">Intelligently Guided</span>
            </h1>
            
            <p className="text-lg text-text-secondary mb-8 max-w-xl mx-auto lg:mx-0">
              KRED combines AI-powered behavior analysis with intelligent tools to transform your financial habits. Meet Kred Bird, your personal AI companion who guides every decision.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Link to="/login">
              <button className="btn-primary animate-pulse-glow">
                Start Free Trial
                <svg className="w-5 h-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </button>
              </Link>
              <button className="btn-secondary">
                Watch Demo
              </button>
            </div>
            
            <div className="mt-12 grid grid-cols-2 sm:grid-cols-4 gap-6">
              {stats.map((stat, index) => (
                <div key={index} className="animate-slide-up" style={{ animationDelay: `₹{index * 100}ms` }}>
                  <div className="text-2xl sm:text-3xl font-bold text-accent">{stat.value}</div>
                  <div className="text-sm text-text-muted">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="relative animate-fade-in animate-delay-300 h-[500px] lg:h-[500px] w-[400px] lg:w-[500px] mx-auto">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-transparent rounded-full blur-3xl"></div>
            <div className="relative h-full bg-surface/80 backdrop-blur-xl border border-secondary rounded-3xl p-6 lg:p-8 animate-float overflow-hidden">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-accent/20 rounded-xl flex items-center justify-center">
                  <svg className="w-7 h-7 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                  </svg>
                </div>
                <div>
                  <div className="text-text-primary font-semibold">Kred Bird</div>
                  <div className="text-text-muted text-sm">Your AI Companion</div>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="bg-secondary/50 rounded-xl p-4">
                  <div className="text-text-secondary text-sm mb-2">Today's Spending</div>
                  <div className="text-3xl font-bold text-accent">₹516.47</div>
                  <div className="text-text-muted text-sm mt-1">Under limit by ₹100.53</div>
                </div>
                
                <div className="bg-secondary/50 rounded-xl p-4">
                  <div className="text-text-secondary text-sm mb-2">Weekly Progress</div>
                  <div className="w-full h-2 bg-surface rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-blue-500 to-blue-400 rounded-full" style={{ width: '72%' }}></div>
                  </div>
                  <div className="flex justify-between text-xs text-text-muted mt-2">
                    <span>₹1700 spent</span>
                    <span>₹2000 budget</span>
                  </div>
                </div>
                
                <div className="bg-secondary/50 rounded-xl p-4">
                  <div className="text-text-secondary text-sm mb-3">AI Insight</div>
                  <p className="text-sm text-text-primary">You're 15% under budget this week. Consider allocating the savings toward your vacation fund.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
