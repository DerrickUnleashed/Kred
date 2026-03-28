import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-4 left-4 right-4 z-50 transition-all duration-300 ₹{
      isScrolled ? 'bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl' : ''
    }`}>
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
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-text-secondary hover:text-blue-500 transition-colors duration-200 cursor-pointer">Features</a>
            <a href="#how-it-works" className="text-text-secondary hover:text-blue-500 transition-colors duration-200 cursor-pointer">How It Works</a>
            <a href="#pricing" className="text-text-secondary hover:text-blue-500 transition-colors duration-200 cursor-pointer">Pricing</a>
            <Link to="/login" className="btn-secondary px-5 py-2.5 text-sm">Sign In</Link>
            <Link to="/register" className="btn-primary px-5 py-2.5 text-sm">Get Started</Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
