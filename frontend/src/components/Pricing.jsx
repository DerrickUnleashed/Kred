export default function Pricing() {
  return (
    <section id="pricing" className="section-padding relative">
      <div className="container-custom">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-surface/50 border border-secondary rounded-full mb-6">
            <span className="text-text-secondary text-sm">Simple Pricing</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-text-primary mb-6">
            Start Your Journey to{' '}
            <span className="text-gradient">Financial Freedom</span>
          </h2>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto">
            Choose the plan that fits your needs. All plans include a 14-day free trial.
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="card">
            <div className="text-text-secondary text-sm font-medium mb-2">Starter</div>
            <div className="flex items-baseline gap-1 mb-6">
              <span className="text-4xl font-bold text-text-primary">$0</span>
              <span className="text-text-muted">/month</span>
            </div>
            <ul className="space-y-3 mb-8">
              {['Budget tracking', 'Basic insights', '1 connected account', 'Email support'].map((feature, index) => (
                <li key={index} className="flex items-center gap-3 text-text-secondary">
                  <svg className="w-5 h-5 text-blue-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>
            <button className="btn-secondary w-full">Get Started</button>
          </div>
          
          <div className="card border-blue-500 relative">
            <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-blue-500 text-white text-sm font-semibold rounded-full">
              Most Popular
            </div>
            <div className="text-text-secondary text-sm font-medium mb-2">Pro</div>
            <div className="flex items-baseline gap-1 mb-6">
              <span className="text-4xl font-bold text-text-primary">$12</span>
              <span className="text-text-muted">/month</span>
            </div>
            <ul className="space-y-3 mb-8">
              {['All Starter features', 'AI behavior analysis', 'Dynamic spending limits', 'Future self visualization', 'Priority support'].map((feature, index) => (
                <li key={index} className="flex items-center gap-3 text-text-secondary">
                  <svg className="w-5 h-5 text-blue-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>
            <button className="btn-primary w-full">Start Free Trial</button>
          </div>
          
          <div className="card">
            <div className="text-text-secondary text-sm font-medium mb-2">Enterprise</div>
            <div className="flex items-baseline gap-1 mb-6">
              <span className="text-4xl font-bold text-text-primary">$49</span>
              <span className="text-text-muted">/month</span>
            </div>
            <ul className="space-y-3 mb-8">
              {['All Pro features', 'Stock analysis module', 'Unlimited accounts', 'Custom goals', 'Dedicated advisor', 'API access'].map((feature, index) => (
                <li key={index} className="flex items-center gap-3 text-text-secondary">
                  <svg className="w-5 h-5 text-blue-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>
            <button className="btn-secondary w-full">Contact Sales</button>
          </div>
        </div>
      </div>
    </section>
  );
}
