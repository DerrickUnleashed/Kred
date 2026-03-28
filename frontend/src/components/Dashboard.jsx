import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';
import { supabase } from '../lib/supabase';

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

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

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/');
  };

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
              <span className="text-xl font-bold text-text-primary">Kres</span>
            </Link>
            <div className="flex items-center gap-4">
              <span className="text-text-secondary text-sm">
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

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-text-primary mb-8">Dashboard</h1>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Welcome back!</h2>
            <p className="text-text-secondary">
              {user?.user_metadata?.full_name || user?.email}
            </p>
          </div>
          
          <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Quick Stats</h2>
            <p className="text-text-secondary">Dashboard features coming soon...</p>
          </div>
          
          <div className="bg-surface/80 backdrop-blur-xl border border-secondary rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Notifications</h2>
            <p className="text-text-secondary">No new notifications</p>
          </div>
        </div>
      </main>
    </div>
  );
}
