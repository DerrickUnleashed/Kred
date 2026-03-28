const steps = [
  {
    number: '01',
    title: 'Connect Your Accounts',
    description: 'Securely link your bank accounts, credit cards, and investment portfolios for comprehensive financial visibility.'
  },
  {
    number: '02',
    title: 'Set Your Goals',
    description: 'Define your financial objectives whether saving for a home, retirement, or building an emergency fund.'
  },
  {
    number: '03',
    title: 'Meet Kred Bird',
    description: 'Your AI companion analyzes your spending patterns and creates personalized recommendations in real-time.'
  },
  {
    number: '04',
    title: 'Watch Your Progress',
    description: 'Track your financial evolution through intuitive dashboards and future self visualization.'
  }
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="section-padding relative">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/2 left-0 w-full h-px bg-gradient-to-r from-transparent via-secondary to-transparent"></div>
      </div>
      
      <div className="container-custom">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-surface/50 border border-secondary rounded-full mb-6">
            <span className="text-text-secondary text-sm">Simple Process</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-text-primary mb-6">
            How KRED{' '}
            <span className="text-gradient">Transforms Your Finances</span>
          </h2>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto">
            Get started in minutes and start seeing results within days. No complex setup required.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <div className="text-7xl font-bold text-surface/50 absolute -top-4 -left-2 select-none">
                {step.number}
              </div>
              <div className="relative pt-8">
                <h3 className="text-xl font-semibold text-text-primary mb-3">{step.title}</h3>
                <p className="text-text-secondary">{step.description}</p>
              </div>
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-16 right-0 translate-x-1/2 w-24">
                  <svg className="w-full text-text-muted" viewBox="0 0 100 20" fill="none">
                    <path d="M0 10H100" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" />
                    <path d="M95 5L100 10L95 15" stroke="currentColor" strokeWidth="2" fill="none" />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
