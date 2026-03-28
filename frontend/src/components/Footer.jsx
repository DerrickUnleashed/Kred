export default function Footer() {
  return (
    <footer className="py-16 border-t border-secondary">
      <div className="container-custom">
        <div className="grid md:grid-cols-4 gap-12 mb-12">
          <div>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <span className="text-xl font-bold text-text-primary">KRED</span>
            </div>
            <p className="text-text-secondary text-sm">
              AI-powered behavioral financial platform with Kred Bird as your personal AI companion. Build wealth and achieve financial freedom.
            </p>
          </div>
          
          <div>
            <h4 className="text-text-primary font-semibold mb-4">Product</h4>
            <ul className="space-y-3">
              {['Features', 'Pricing', 'Integrations', 'API'].map((item, index) => (
                <li key={index}>
                  <a href="#" className="text-text-secondary hover:text-blue-500 transition-colors duration-200 cursor-pointer">{item}</a>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="text-text-primary font-semibold mb-4">Company</h4>
            <ul className="space-y-3">
              {['About', 'Blog', 'Careers', 'Press'].map((item, index) => (
                <li key={index}>
                  <a href="#" className="text-text-secondary hover:text-blue-500 transition-colors duration-200 cursor-pointer">{item}</a>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="text-text-primary font-semibold mb-4">Legal</h4>
            <ul className="space-y-3">
              {['Privacy', 'Terms', 'Security', 'Cookies'].map((item, index) => (
                <li key={index}>
                  <a href="#" className="text-text-secondary hover:text-blue-500 transition-colors duration-200 cursor-pointer">{item}</a>
                </li>
              ))}
            </ul>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row justify-between items-center pt-8 border-t border-secondary">
          <p className="text-text-muted text-sm mb-4 sm:mb-0">
            © 2026 KRED. All rights reserved.
          </p>
          <div className="flex gap-4">
          {['twitter', 'linkedin', 'github'].map((social, index) => (
            <a 
              href="https://github.com/DerrickUnleashed/Kred.git" 
              target="_blank" 
              rel="noopener noreferrer"
              className="w-10 h-10 bg-surface rounded-lg flex items-center justify-center text-text-secondary hover:text-blue-500 hover:bg-blue-500/10 transition-all duration-200 cursor-pointer"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
            </a>
          ))}
        </div>
        </div>
      </div>
    </footer>
  );
}
