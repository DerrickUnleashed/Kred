import { useEffect, useRef, useState } from "react";
import { useNavigate, Link } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import Navbar from "./Navbar";

const videos = [
  { url: "/videos/1.mp4", title: "How to make profit?" },
  { url: "/videos/2.mp4", title: "Save smarter" },
  { url: "/videos/3.mp4", title: "Inflation explained" },
  { url: "/videos/4.mp4", title: "Stock changes" },
  { url: "/videos/5.mp4", title: "Filing insurance" }
];

const loopedVideos = [...videos, ...videos, ...videos, ...videos, ...videos];

export default function Reels() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef(null);

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
    navigate('/login');
  };

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const vids = container.querySelectorAll(".main-video");
    const bgVids = container.querySelectorAll(".bg-video");

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const video = entry.target;
          const idx = Array.from(vids).indexOf(video);
          const bgVid = bgVids[idx];
          
          if (entry.isIntersecting) {
            video.currentTime = 0;
            const playPromise = video.play();
            if (playPromise !== undefined) {
              playPromise.catch(() => {});
            }
            if (bgVid) {
              bgVid.currentTime = 0;
              bgVid.play();
            }
          } else {
            video.pause();
            if (bgVid) bgVid.pause();
          }
        });
      },
      { threshold: 0.6 }
    );

    vids.forEach((v) => observer.observe(v));

    return () => observer.disconnect();
  }, []);

  if (loading) return null;

  return (
    <div className="min-h-screen bg-background">
      <Navbar user={user} onLogout={handleLogout} />
      
      <main className="max-w-2xl mx-auto px-4 sm:px-6 pt-20 pb-4">
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 text-text-secondary hover:text-accent mb-4 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </Link>

        <div 
          ref={containerRef}
          style={{
            height: 'calc(100vh - 180px)',
            overflowY: 'scroll',
            scrollSnapType: 'y mandatory',
            scrollBehavior: 'smooth'
          }}
        >
          {loopedVideos.map((video, i) => (
            <div 
              key={i}
              style={{
                height: 'calc(100vh - 180px)',
                scrollSnapAlign: 'start',
                position: 'relative',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                background: 'black'
              }}
            >
              <video 
                className="bg-video" 
                src={video.url} 
                muted 
                loop 
                autoPlay
                playsInline
                style={{
                  position: 'absolute',
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  filter: 'blur(30px) brightness(0.4)',
                  transform: 'scale(1.1)'
                }}
              />
              <video 
                className="main-video" 
                src={video.url} 
                muted 
                loop 
                autoPlay
                playsInline
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  zIndex: 2
                }}
              />
              <div 
                style={{
                  position: 'absolute',
                  bottom: '40px',
                  left: '24px',
                  color: 'white',
                  zIndex: 3,
                  fontSize: '24px',
                  fontWeight: '700',
                  textShadow: '0 2px 4px rgba(0,0,0,0.5)'
                }}
              >
                {video.title}
              </div>
            </div>
          ))}
        </div>
      </main>
      <style>{`
        div::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  );
}
