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
              <a key={index} href="#" className="w-10 h-10 bg-surface rounded-lg flex items-center justify-center text-text-secondary hover:text-blue-500 hover:bg-blue-500/10 transition-all duration-200 cursor-pointer">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.477 2 2 6.477 2 12c0 5.523 4.477 10 10 10s10-4.477 10-10c0-5.523-4.477-10-10-10z"/>
                </svg>
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
