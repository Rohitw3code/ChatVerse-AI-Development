import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores';
import Navigation from './components/Navigation';
import HeroSection from './components/HeroSection';
import QueryShowcase from './components/QueryShowcase';
import FeatureGrid from './components/FeatureGrid';
import Footer from './components/Footer';

function LandingPage() {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const navigate = useNavigate();

  // Handle mouse movement for background effect
  const handleMouseMove = useCallback((e: MouseEvent) => {
    setMousePosition({ x: e.clientX, y: e.clientY });
  }, []);

  // Add mouse move listener
  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [handleMouseMove]);

  // Inject CSS for dynamic background effect
  useEffect(() => {
    const styleId = 'mouse-pull-background';
    if (document.getElementById(styleId)) return;

    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      .mouse-pull-bg {
        transition: transform 0.3s ease-out, filter 0.3s ease-out;
        will-change: transform, filter;
      }
      
      .mouse-pull-bg::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%), 
          rgba(255,255,255,0.08) 0%, 
          rgba(255,255,255,0.04) 20%, 
          rgba(255,255,255,0.02) 40%, 
          transparent 60%);
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease-out;
      }
      
      .mouse-pull-bg:hover::before {
        opacity: 1;
      }
    `;
    document.head.appendChild(style);
  }, []);

  const handleGetStarted = () => {
    const { user } = useAuthStore.getState();
    if (user) {
      navigate('/platforms');
    } else {
      navigate('/get-started');
    }
  };

  const handleUseAI = () => {
    const { user } = useAuthStore.getState();
    if (user) {
      const providerId = user.id;
      const newChatId = `chat_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
      navigate(`/chat/${newChatId}?provider_id=${providerId}`);
    } else {
      navigate('/get-started');
    }
  };

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden" style={{ backgroundColor: '#0a0a0a' }}>
      {/* Multi-layer Background with Mouse Pull Effect */}
      <div
        className="absolute inset-0 mouse-pull-bg"
        style={{
          backgroundColor: '#0a0a0a',
          backgroundImage: `
          radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0),
          radial-gradient(circle at 3px 3px, rgba(255,255,255,0.08) 1px, transparent 0),
          radial-gradient(circle at 5px 5px, rgba(255,255,255,0.04) 1px, transparent 0)
        `,
          backgroundSize: '20px 20px, 40px 40px, 60px 60px',
          transform: `translate(${(mousePosition.x - window.innerWidth / 2) * 0.02}px, ${(mousePosition.y - window.innerHeight / 2) * 0.02}px)`,
          '--mouse-x': `${(mousePosition.x / window.innerWidth) * 100}%`,
          '--mouse-y': `${(mousePosition.y / window.innerHeight) * 100}%`,
        } as React.CSSProperties}
      ></div>
      
      {/* Dynamic pull effect overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `radial-gradient(circle 200px at ${mousePosition.x}px ${mousePosition.y}px, 
            rgba(255,255,255,0.03) 0%, 
            rgba(255,255,255,0.01) 50%, 
            transparent 70%)`,
          opacity: mousePosition.x > 0 ? 1 : 0,
          transition: 'opacity 0.3s ease-out',
        }}
      ></div>

      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
          repeating-linear-gradient(
            90deg,
            transparent,
            transparent 2px,
            rgba(255,255,255,0.03) 2px,
            rgba(255,255,255,0.03) 4px
          ),
          repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(255,255,255,0.03) 2px,
            rgba(255,255,255,0.03) 4px
          )
        `,
          transform: `translate(${(mousePosition.x - window.innerWidth / 2) * 0.01}px, ${(mousePosition.y - window.innerHeight / 2) * 0.01}px)`,
          transition: 'transform 0.2s ease-out',
        }}
      ></div>

      <div 
        className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-gray-900/20"
        style={{
          transform: `translate(${(mousePosition.x - window.innerWidth / 2) * 0.005}px, ${(mousePosition.y - window.innerHeight / 2) * 0.005}px)`,
          transition: 'transform 0.4s ease-out',
        }}
      ></div>
      
      {/* Upward pull effect for dots near cursor */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `radial-gradient(circle 150px at ${mousePosition.x}px ${mousePosition.y - 20}px, 
            rgba(255,255,255,0.1) 0%, 
            rgba(255,255,255,0.05) 30%, 
            transparent 60%)`,
          opacity: mousePosition.x > 0 ? 0.8 : 0,
          transition: 'opacity 0.2s ease-out',
          filter: 'blur(1px)',
        }}
      ></div>

      {/* Navigation */}
      <Navigation isMenuOpen={isMenuOpen} setIsMenuOpen={setIsMenuOpen} />

      {/* Main Content */}
      <main className="relative overflow-hidden py-4 sm:py-8 lg:py-8">
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Hero Section */}
          <HeroSection handleGetStarted={handleGetStarted} handleUseAI={handleUseAI} />

          {/* Query Showcase Section */}
          <QueryShowcase handleGetStarted={handleGetStarted} handleUseAI={handleUseAI} />

          {/* Feature Grid Section */}
          <FeatureGrid />
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}

export default LandingPage;
