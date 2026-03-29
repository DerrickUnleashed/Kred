import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import logo from '../assets/bot.png';
import { KredBird } from './KredBird.jsx';

export default function Navbar({ user, onLogout }) {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
    <nav className={`fixed top-4 left-4 right-4 z-50 transition-all duration-300 ${
      isScrolled ? 'bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl' : ''
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-accent rounded-xl flex items-center justify-center">
              <img 
                src={logo} 
                alt="Company Logo" 
                className="w-6 h-6 object-contain" 
              />
            </div>
            <span className="text-xl font-bold text-text-primary">KRED</span>
          </Link>
          {user ? (
            <div className="flex items-center gap-4">
              <span className="text-text-secondary text-sm hidden sm:block">
                {user.email}
              </span>
              <button
                onClick={onLogout}
                className="px-4 py-2 bg-background border border-secondary rounded-xl text-text-primary hover:bg-secondary/50 transition-colors duration-200 cursor-pointer"
              >
                Sign out
              </button>
            </div>
          ) : (
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="relative group text-text-secondary hover:text-accent transition-colors duration-200 cursor-pointer">
                Features
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-accent group-hover:w-full transition-all duration-200"></span>
              </a>
              <a href="#how-it-works" className="relative group text-text-secondary hover:text-accent transition-colors duration-200 cursor-pointer">
                How It Works
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-accent group-hover:w-full transition-all duration-200"></span>
              </a>
              <Link to="/login" className="btn-secondary px-5 py-2.5 text-sm">Sign In</Link>
              <Link to="/register" className="btn-primary px-5 py-2.5 text-sm">Get Started</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
    <KredBird />
    </>
  );
}
