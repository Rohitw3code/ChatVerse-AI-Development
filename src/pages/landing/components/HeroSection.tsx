import React, { useEffect } from 'react';
import { Zap, ArrowRight, Search, Bot, Sparkles, Users } from 'lucide-react';
import { useAuthStore } from '../../../stores';
import FabricButton from './FabricButton';

interface HeroSectionProps {
  handleGetStarted: () => void;
  handleUseAI: () => void;
}

const HeroSection: React.FC<HeroSectionProps> = ({ handleGetStarted, handleUseAI }) => {
  const { user } = useAuthStore();

  // Add monochrome fabric card animations
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes enhanced-fabric-flow {
        0% { 
          background-position: 0% 0%, 0% 0%, 0% 0%, 0% 0%, 0% 0%;
          transform: translateZ(0);
        }
        25% { 
          background-position: 25% 25%, -25% 50%, 50% -25%, 75% 25%, 100% 0%;
        }
        50% { 
          background-position: 50% 50%, -50% 100%, 100% -50%, 150% 50%, 200% 0%;
        }
        75% { 
          background-position: 75% 75%, -75% 150%, 150% -75%, 225% 75%, 300% 0%;
        }
        100% { 
          background-position: 100% 100%, -100% 200%, 200% -100%, 300% 100%, 400% 0%;
          transform: translateZ(0);
        }
      }
      
      @keyframes corner-tilt-hover {
        0% { 
          transform: perspective(1000px) rotateX(0deg) rotateY(0deg) rotateZ(0deg) scale(1);
        }
        100% { 
          transform: perspective(1000px) rotateX(-4deg) rotateY(6deg) rotateZ(1deg) scale(1.02);
        }
      }
      
      @keyframes fabric-pulse {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; }
      }
      
      .hero-card {
        background: 
          repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
          repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
          linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%);
        background-size: 40px 40px, 40px 40px, 100% 100%;
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      }
      
      .hero-card:hover {
        background: 
          repeating-linear-gradient(45deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 1px, transparent 1px, transparent 20px),
          repeating-linear-gradient(-45deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 20px),
          linear-gradient(135deg, rgba(40,40,40,0.8) 0%, rgba(30,30,30,0.6) 100%);
        background-size: 44px 44px, 44px 44px, 100% 100%;
        border-color: rgba(255, 255, 255, 0.25);
        transform: translateY(-4px) scale(1.02);
      }
      
      .hero-card.violet-accent:hover {
        border-color: rgba(139, 92, 246, 0.4);
        box-shadow: 0 25px 50px -12px rgba(139, 92, 246, 0.25);
      }
      
      .hero-card.blue-accent:hover {
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 25px 50px -12px rgba(59, 130, 246, 0.25);
      }
      
      .hero-card.emerald-accent:hover {
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 0 25px 50px -12px rgba(16, 185, 129, 0.25);
      }
      
      .fabric-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
          radial-gradient(circle at 25% 25%, rgba(255,255,255,0.015) 0%, transparent 50%),
          radial-gradient(circle at 75% 75%, rgba(255,255,255,0.01) 0%, transparent 50%);
        opacity: 0;
        transition: opacity 0.5s ease;
        pointer-events: none;
      }
      
      .hero-card:hover .fabric-overlay {
        opacity: 1;
      }
    `;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);

  return (
    <div className="text-center">
      {/* Material Design Typography Hierarchy */}
      <div className="space-y-6 mb-12">
        {/* Display Large - Main Heading */}
        <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold leading-tight tracking-tight text-white">
          <span className="block">ChatVerse</span>
        </h1>

        {/* Headline Medium - Subheading */}
        <h2 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-normal leading-relaxed text-white/80 max-w-4xl mx-auto">
          Transform Your Social Presence with{' '}
          <span className="font-semibold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            AI-Powered Automation
          </span>
        </h2>

        {/* Body Large - Description */}
        <p className="text-base sm:text-lg md:text-xl leading-relaxed text-white/70 max-w-3xl mx-auto font-light">
          Revolutionize your social media strategy with ChatVerse.{' '}
          <span className="font-medium text-white/85">Create, schedule, and engage</span>{' '}
          across all platforms using natural language commands. Let AI handle the complexity while you focus on growing your brand.
        </p>
      </div>

      {/* Fabric Design Button Group */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6 mb-12 sm:mb-16 px-4 sm:px-0">
        {/* Primary Fabric Button - Dark Gradient */}
        <FabricButton
          onClick={handleGetStarted}
          variant="primary"
          size="large"
          className="w-full sm:w-auto sm:min-w-[200px] lg:min-w-[240px] shadow-xl sm:shadow-2xl"
        >
          <Zap className="w-5 h-5 sm:w-6 sm:h-6 group-hover:rotate-12 transition-transform duration-300" />
          <span className="text-sm sm:text-base lg:text-lg">{user ? 'Go to Dashboard' : 'Get Started Free'}</span>
          <ArrowRight className="w-5 h-5 sm:w-6 sm:h-6 group-hover:translate-x-2 transition-transform duration-300" />
        </FabricButton>

        {/* Secondary Fabric Button - Light Gradient */}
        <FabricButton
          onClick={handleUseAI}
          variant="secondary"
          size="large"
          className="w-full sm:w-auto sm:min-w-[200px] lg:min-w-[240px] shadow-xl sm:shadow-2xl"
        >
          <Search className="w-5 h-5 sm:w-6 sm:h-6 group-hover:rotate-12 transition-transform duration-300" />
          <span className="text-sm sm:text-base lg:text-lg">Use AI for Automations</span>
        </FabricButton>
      </div>

      {/* Enhanced Fabric Design Feature Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 max-w-6xl mx-auto px-4 sm:px-6">
        {/* Feature Card 1 - Query-Based */}
        <div className="group hero-card violet-accent relative overflow-hidden rounded-2xl p-6 sm:p-8 transform-gpu transition-all duration-500">
          <div className="fabric-overlay"></div>
          <div className="relative z-10">
            <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-lg">
              <Bot className="w-7 h-7 sm:w-8 sm:h-8 text-white" />
            </div>
            <h3 className="text-lg sm:text-xl font-bold mb-3 bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent" style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}>
              Query-Based
            </h3>
            <p className="bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent text-sm leading-relaxed" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
              Use natural language to create powerful automations across all your social platforms with intuitive commands
            </p>
          </div>
        </div>

        {/* Feature Card 2 - AI-Powered */}
        <div className="group hero-card blue-accent relative overflow-hidden rounded-2xl p-6 sm:p-8 transform-gpu transition-all duration-500">
          <div className="fabric-overlay"></div>
          <div className="relative z-10">
            <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-lg">
              <Sparkles className="w-7 h-7 sm:w-8 sm:h-8 text-white" />
            </div>
            <h3 className="text-lg sm:text-xl font-bold mb-3 bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent" style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}>
              AI-Powered
            </h3>
            <p className="bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent text-sm leading-relaxed" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
              Advanced AI models handle content creation, scheduling, and engagement automatically with smart optimization
            </p>
          </div>
        </div>

        {/* Feature Card 3 - Multi-Platform */}
        <div className="group hero-card emerald-accent relative overflow-hidden rounded-2xl p-6 sm:p-8 transform-gpu sm:col-span-2 lg:col-span-1 transition-all duration-500">
          <div className="fabric-overlay"></div>
          <div className="relative z-10">
            <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-lg">
              <Users className="w-7 h-7 sm:w-8 sm:h-8 text-white" />
            </div>
            <h3 className="text-lg sm:text-xl font-bold mb-3 bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent" style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}>
              Multi-Platform
            </h3>
            <p className="bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent text-sm leading-relaxed" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
              Connect and manage Instagram, Twitter, LinkedIn, Facebook, and more from one unified dashboard
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroSection;
