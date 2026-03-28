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
    <section id="how-it-works" className="section-padding relative overflow-hidden bg-background">
      {/* Background Decorative Gradient Line */}
      <div className="absolute top-[45%] left-0 w-full h-px bg-gradient-to-r from-transparent via-secondary/50 to-transparent hidden lg:block" />
      
      <div className="container-custom relative z-10">
        <div className="text-center mb-20 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-surface border border-secondary rounded-full mb-6">
            <span className="text-blue-400 text-xs font-bold uppercase tracking-widest">The Process</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-text-primary mb-6 tracking-tight">
            How KRED <span className="text-gradient">Transforms Finances</span>
          </h2>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto">
            A streamlined approach to managing your wealth. Simple, secure, and automated.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-12 lg:gap-10">
          {steps.map((step, index) => (
            <div key={index} className="group relative flex flex-col items-start">
              
              {/* Number Header - Fixed Height for perfect Title Alignment */}
              <div className="relative mb-8 h-20 flex items-end">
                <span className="text-7xl font-black text-secondary/40 transition-all duration-300 group-hover:text-blue-500/30 group-hover:-translate-y-1 select-none">
                  {step.number}
                </span>
              </div>

              {/* Content */}
              <div className="relative">
                <h3 className="text-xl font-bold text-text-primary mb-4 group-hover:text-blue-400 transition-colors">
                  {step.title}
                </h3>
                <p className="text-text-secondary text-base leading-relaxed border-l-2 border-transparent group-hover:border-blue-500/50 pl-0 group-hover:pl-4 transition-all duration-300">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}