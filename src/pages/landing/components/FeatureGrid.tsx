import React, { useEffect } from 'react';
import { Users, Sparkles, Zap, BarChart3, Shield, Bot, ArrowRight, Repeat } from 'lucide-react';
import PlatformLogos from './PlatformLogos';
import AutomationExamples from './AutomationExamples';

const FeatureGrid: React.FC = () => {
  // Add fabric styling
  useEffect(() => {
    const styleId = 'feature-grid-fabric-styles';
    if (document.getElementById(styleId)) return;

    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      .fabric-card {
        background: 
          repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
          repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
          linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%);
        background-size: 40px 40px, 40px 40px, 100% 100%;
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      }
      
      .fabric-card:hover {
        background: 
          repeating-linear-gradient(45deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 1px, transparent 1px, transparent 20px),
          repeating-linear-gradient(-45deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 20px),
          linear-gradient(135deg, rgba(40,40,40,0.8) 0%, rgba(30,30,30,0.6) 100%);
        background-size: 44px 44px, 44px 44px, 100% 100%;
        border-color: rgba(255, 255, 255, 0.25);
        transform: translateY(-4px) scale(1.02);
      }
      
      .fabric-card.violet-accent:hover {
        border-color: rgba(139, 92, 246, 0.4);
        box-shadow: 0 25px 50px -12px rgba(139, 92, 246, 0.25);
      }
      
      .fabric-card.blue-accent:hover {
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 25px 50px -12px rgba(59, 130, 246, 0.25);
      }
      
      .fabric-card.emerald-accent:hover {
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 0 25px 50px -12px rgba(16, 185, 129, 0.25);
      }
      
      .fabric-card.orange-accent:hover {
        border-color: rgba(249, 115, 22, 0.4);
        box-shadow: 0 25px 50px -12px rgba(249, 115, 22, 0.25);
      }
      
      .dark-section {
        background: 
          repeating-linear-gradient(0deg, rgba(255,255,255,0.01) 0px, rgba(255,255,255,0.01) 1px, transparent 1px, transparent 30px),
          repeating-linear-gradient(90deg, rgba(255,255,255,0.008) 0px, rgba(255,255,255,0.008) 1px, transparent 1px, transparent 30px),
          linear-gradient(135deg, rgba(25,25,25,0.8) 0%, rgba(15,15,15,0.7) 100%);
        background-size: 60px 60px, 60px 60px, 100% 100%;
      }
    `;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);

  return (
    <>
      {/* What is ChatVerse Section */}
      <div className="mt-16 sm:mt-24 mb-12 sm:mb-16 px-4 sm:px-0">
        <div className="text-center mb-8 sm:mb-12">
          <h2
            className="text-2xl sm:text-3xl md:text-4xl font-bold bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent mb-4 sm:mb-6"
            style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}
          >
            What is ChatVerse?
          </h2>
          <p
            className="text-base sm:text-lg bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent max-w-4xl mx-auto leading-relaxed"
            style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
          >
            ChatVerse is a comprehensive social media automation platform offering two powerful approaches:
            <span className="font-medium bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent">
              {' '}Query-based automation
            </span>{' '}
            for natural language commands and
            <span className="font-medium bg-gradient-to-r from-cyan-300 to-blue-300 bg-clip-text text-transparent">
              {' '}data-driven automation
            </span>{' '}
            for custom inputs and AI model selection. From content creation to audience engagement, we handle the complexity so you can focus on growing your brand.
          </p>
        </div>
      </div>

      {/* Feature Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mt-12 sm:mt-20 px-4 sm:px-0">
        <div className="group fabric-card violet-accent p-6 rounded-2xl transition-all duration-500">
          <div className="w-14 h-14 bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4 group-hover:rotate-6 transition-transform duration-300">
            <Users className="w-7 h-7 text-white" />
          </div>
          <h3
            className="text-lg font-bold mb-3 bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent"
            style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}
          >
            Multi-Platform Hub
          </h3>
          <p
            className="bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent text-sm leading-relaxed"
            style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
          >
            Connect Instagram, Twitter, LinkedIn, Facebook, TikTok, and more from one unified dashboard.
          </p>
        </div>

        <div className="group fabric-card blue-accent p-6 rounded-2xl transition-all duration-500">
          <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-2xl flex items-center justify-center mb-4 group-hover:rotate-6 transition-transform duration-300">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <h3
            className="text-lg font-bold mb-3 bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent"
            style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}
          >
            AI Content Engine
          </h3>
          <p
            className="bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent text-sm leading-relaxed"
            style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
          >
            Generate engaging posts, captions, and hashtags tailored to your brand voice and audience.
          </p>
        </div>

        <div className="group fabric-card emerald-accent p-6 rounded-2xl transition-all duration-500">
          <div className="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center mb-4 group-hover:rotate-6 transition-transform duration-300">
            <Zap className="w-7 h-7 text-white" />
          </div>
          <h3
            className="text-lg font-bold mb-3 bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent"
            style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}
          >
            Smart Scheduling
          </h3>
          <p
            className="bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent text-sm leading-relaxed"
            style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
          >
            AI analyzes your audience behavior to post at optimal times for maximum engagement.
          </p>
        </div>

        <div className="group fabric-card orange-accent p-6 rounded-2xl transition-all duration-500">
          <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl flex items-center justify-center mb-4 group-hover:rotate-6 transition-transform duration-300">
            <BarChart3 className="w-7 h-7 text-white" />
          </div>
          <h3
            className="text-lg font-bold mb-3 bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent"
            style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}
          >
            Deep Analytics
          </h3>
          <p
            className="bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent text-sm leading-relaxed"
            style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
          >
            Track performance, growth metrics, and ROI across all platforms with detailed insights.
          </p>
        </div>
      </div>

      {/* No Code Automation Section */}
      <div className="mt-24 pt-16 border-t border-white/10 dark-section rounded-3xl p-8 sm:p-12">
        <div className="text-center mb-12">
          <h2
            className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent mb-6 tracking-tight"
            style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}
          >
            Automate Your Social Presence with No Code
          </h2>
          <p
            className="text-lg bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent max-w-4xl mx-auto leading-relaxed"
            style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
          >
            Our intuitive automation tool allows you to streamline your social media workflow without writing a single line of code. Simply provide your queries or fill in the values manually to set up powerful automation flows.
          </p>
        </div>
        
        {/* Automation Flow Diagram */}
        <div className="flex flex-col items-center justify-center relative my-16">
          <div className="flex items-center space-x-8 animate-fade-in-up">
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg">
                <Bot className="w-8 h-8 text-white" />
              </div>
              <p className="mt-2 text-sm text-gray-400 font-medium">Query Input</p>
            </div>
            <div className="relative">
              <ArrowRight className="w-10 h-10 text-gray-500 animate-pulse-right" />
            </div>
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg">
                <Repeat className="w-8 h-8 text-white animate-spin-slow" />
              </div>
              <p className="mt-2 text-sm text-gray-400 font-medium">Automation Logic</p>
            </div>
            <div className="relative">
              <ArrowRight className="w-10 h-10 text-gray-500 animate-pulse-right" />
            </div>
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-2xl flex items-center justify-center shadow-lg">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <p className="mt-2 text-sm text-gray-400 font-medium">Action Performed</p>
            </div>
          </div>
        </div>
        
        {/* Automation Types Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
          <div className="group fabric-card violet-accent p-8 rounded-3xl transition-all duration-500">
            <h3
              className="text-xl font-bold mb-3 bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent text-center"
              style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}
            >
              Query-Based Automation
            </h3>
            <p
              className="bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent text-sm text-center leading-relaxed"
              style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
            >
              Simply give a query and let our AI handle the rest, from content creation to scheduling and posting across platforms.
            </p>
          </div>
          <div className="group fabric-card blue-accent p-8 rounded-3xl transition-all duration-500">
            <h3
              className="text-xl font-bold mb-3 bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent text-center"
              style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}
            >
              Data Scraping & Reporting
            </h3>
            <p
              className="bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent text-sm text-center leading-relaxed"
              style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
            >
              Scrape social media data and use it to create insightful reports, allowing AI to make informed decisions or send you daily email summaries.
            </p>
          </div>
          <div className="group fabric-card emerald-accent p-8 rounded-3xl transition-all duration-500">
            <h3
              className="text-xl font-bold mb-3 bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent text-center"
              style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}
            >
              Unified Platform Management
            </h3>
            <p
              className="bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent text-sm text-center leading-relaxed"
              style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
            >
              Integrate multiple social media platforms into one place so you don't have to jump between apps. Manage everything efficiently with a single query.
            </p>
          </div>
        </div>
      </div>

      {/* Platform Integration Section */}
      <div id="platform" className="mt-32">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent mb-4 tracking-tight" style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}>
            CONNECT ALL YOUR PLATFORMS
          </h2>
          <p className="text-lg bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent max-w-2xl mx-auto font-medium" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
            Seamlessly integrate with all major social media and communication platforms from one unified dashboard so you don't have to jump from one to another.
          </p>
        </div>

        {/* <PlatformLogos /> */}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-16">
          {/* WhatsApp */}
          <div className="group fabric-card emerald-accent text-center p-6 rounded-xl transition-all duration-300">
            <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center mx-auto mb-4 transition-transform duration-300 group-hover:scale-110">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.465 3.488"/>
              </svg>
            </div>
            <h3 className="text-lg font-bold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent mb-2 tracking-wide" style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}>
              WHATSAPP
            </h3>
            <p className="text-sm bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent font-medium" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
              Automate WhatsApp Business messages and customer support
            </p>
          </div>

          {/* Twitter/X */}
          <div className="group fabric-card blue-accent text-center p-6 rounded-xl transition-all duration-300">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center mx-auto mb-4 transition-transform duration-300 group-hover:scale-110">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
              </svg>
            </div>
            <h3 className="text-lg font-bold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent mb-2 tracking-wide" style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}>
              TWITTER / X
            </h3>
            <p className="text-sm bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent font-medium" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
              Schedule tweets, engage with followers, and track trends
            </p>
          </div>

          {/* Instagram */}
          <div className="group fabric-card violet-accent text-center p-6 rounded-xl transition-all duration-300">
            <div className="w-12 h-12 bg-gradient-to-r from-pink-500 to-purple-500 rounded-lg flex items-center justify-center mx-auto mb-4 transition-transform duration-300 group-hover:scale-110">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
              </svg>
            </div>
            <h3 className="text-lg font-bold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent mb-2 tracking-wide" style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}>
              INSTAGRAM
            </h3>
            <p className="text-sm bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent font-medium" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
              Post stories, reels, and manage business accounts
            </p>
          </div>

          {/* LinkedIn */}
          <div className="group fabric-card blue-accent text-center p-6 rounded-xl transition-all duration-300">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg flex items-center justify-center mx-auto mb-4 transition-transform duration-300 group-hover:scale-110">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
            </div>
            <h3 className="text-lg font-bold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent mb-2 tracking-wide" style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}>
              LINKEDIN
            </h3>
            <p className="text-sm bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent font-medium" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
              Professional networking and B2B content automation
            </p>
          </div>
        </div>
      </div>

      <AutomationExamples />

      {/* Floating Elements */}
      <div className="absolute top-[10%] left-[10%] w-3 h-3 bg-purple-500/50 rounded-full animate-float-medium hidden lg:block"></div>
      <div className="absolute top-[25%] right-[15%] w-4 h-4 bg-pink-500/50 rounded-full animate-float-slow hidden lg:block"></div>
      <div className="absolute bottom-[20%] left-[20%] w-2 h-2 bg-purple-300/60 rounded-full animate-float-fast hidden lg:block"></div>
      <div className="absolute bottom-[10%] right-[10%] w-3 h-3 bg-pink-300/60 rounded-full animate-float-medium hidden lg:block"></div>
    </>
  );
};

export default FeatureGrid;
