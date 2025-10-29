import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores';
import { 
  Menu, X, Sparkles, Zap, BarChart3, ArrowRight, 
  Rocket, Instagram, Twitter, Linkedin, 
  CheckCircle2, Clock, 
  TrendingUp, Lock, Boxes, Bot, Shield, Repeat, MessageSquare, 
  Send, Mail, Facebook, Code, ListChecks
} from 'lucide-react';
import PlatformLogos from './components/PlatformLogos';
import AutomationExamples from './components/AutomationExamples';
import chatverseLogo from './../../components/chatverse.svg';
import { supabase } from '../../lib/supabase';

function LandingPageNew2() {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const { user } = useAuthStore();
  const navigate = useNavigate();
  // Waitlist state
  const [waitlistEmail, setWaitlistEmail] = React.useState('');
  const [waitlistStatus, setWaitlistStatus] = React.useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [waitlistMessage, setWaitlistMessage] = React.useState<string | null>(null);

  const handleGetStarted = () => {
    if (user) {
      navigate('/platforms');
    } else {
      navigate('/get-started');
    }
  };

  const handleJoinWaitlist = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const email = waitlistEmail.trim();
    // simple email validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setWaitlistStatus('error');
      setWaitlistMessage('Please enter a valid email address.');
      return;
    }
    try {
      setWaitlistStatus('loading');
      setWaitlistMessage(null);
      const { error } = await supabase.from('waitlist').insert({ email });
      if (error) {
        // Unique violation (already subscribed)
        // Postgres unique_violation code
        // @ts-ignore
        if (error.code === '23505') {
          setWaitlistStatus('success');
          setWaitlistMessage("You're already on the waitlist. Thank you!");
        } else {
          setWaitlistStatus('error');
          setWaitlistMessage('Something went wrong. Please try again.');
          // eslint-disable-next-line no-console
          console.error('Waitlist insert error:', error);
        }
      } else {
        setWaitlistStatus('success');
        setWaitlistMessage('Thanks! You have been added to the waitlist.');
        setWaitlistEmail('');
      }
    } catch (err) {
      setWaitlistStatus('error');
      setWaitlistMessage('Network error. Please try again.');
      // eslint-disable-next-line no-console
      console.error('Waitlist exception:', err);
    }
  };
  
  const handleCreateAutomation = () => {
    if (!user) {
      // If user is not logged in, redirect to get started
      navigate('/get-started');
      return;
    }
    
    // Generate a new unique chat ID (same pattern as in chat.tsx)
    const newChatId = `chat_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    
    // Navigate to the new chat with user's ID as provider_id
    navigate(`/chat/${newChatId}?provider_id=${user.id}`);
  };

  // Query showcase state
  const queriesData = React.useMemo(() => [
    {
      text: 'Create and publish an Instagram post, then reply positively to all comments that have not yet received a response.',
      chips: [
        { label: 'Instagram Post', icon: <Instagram className="w-4 h-4" /> },
        { label: 'Auto-Reply', icon: <MessageSquare className="w-4 h-4" /> },
        { label: 'Positive Tone', icon: <Sparkles className="w-4 h-4" /> },
      ],
    },
    {
      text: 'Send a daily report at 12:00 AM to my Slack #general channel with comment counts and reel views.',
      chips: [
        { label: 'Daily 12 AM', icon: <Clock className="w-4 h-4" /> },
        { label: 'Reels Insights', icon: <BarChart3 className="w-4 h-4" /> },
        { label: 'Send to Slack', icon: <Send className="w-4 h-4" /> },
      ],
    },
    {
      text: 'When a Facebook Reel exceeds 100k views, post it to Instagram with the same caption and send the product link to users who comment "I want to buy product".',
      chips: [
        { label: 'Facebook Reels >100k', icon: <Facebook className="w-4 h-4" /> },
        { label: 'Cross-post to IG', icon: <Instagram className="w-4 h-4" /> },
        { label: 'DM Product Link', icon: <Mail className="w-4 h-4" /> },
      ],
    },
  ], []);

  const [qIndex, setQIndex] = React.useState(0);
  const [subIndex, setSubIndex] = React.useState(0);
  const [isDeleting, setIsDeleting] = React.useState(false);
  const [blink, setBlink] = React.useState(true);
  const [activeTab, setActiveTab] = React.useState('query');

  const currentQuery = queriesData[qIndex].text;
  const displayText = currentQuery.slice(0, subIndex);

  React.useEffect(() => {
    const id = setInterval(() => setBlink((b) => !b), 500);
    return () => clearInterval(id);
  }, []);

  React.useEffect(() => {
    if (!isDeleting && subIndex === currentQuery.length) {
      const hold = setTimeout(() => setIsDeleting(true), 1400);
      return () => clearTimeout(hold);
    }

    if (isDeleting && subIndex === 0) {
      setIsDeleting(false);
      setQIndex((i) => (i + 1) % queriesData.length);
      return;
    }

    const next = setTimeout(() => {
      setSubIndex((v) => v + (isDeleting ? -1 : 1));
    }, isDeleting ? 18 : 38);

    return () => clearTimeout(next);
  }, [subIndex, isDeleting, currentQuery.length, queriesData.length]);

  // Inject fabric styles
  React.useEffect(() => {
    const styleId = 'fabric-animations';
    if (document.getElementById(styleId)) return;

    const style = document.createElement('style');
    style.id = styleId;
    style.innerHTML = `
      @keyframes fabric-flow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }
      @keyframes laser-sweep {
        0% { transform: translateX(-100%) skewX(-15deg); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateX(200%) skewX(-15deg); opacity: 0; }
      }
      @keyframes laser-sweep-delayed {
        0% { transform: translateX(-100%) skewX(-15deg); opacity: 0; }
        50% { opacity: 0.6; }
        100% { transform: translateX(200%) skewX(-15deg); opacity: 0; }
      }
      .fabric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%),
                    repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(255,255,255,0.03) 2px, rgba(255,255,255,0.03) 4px),
                    repeating-linear-gradient(-45deg, transparent, transparent 2px, rgba(255,255,255,0.02) 2px, rgba(255,255,255,0.02) 4px);
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
      }
      .fabric-card::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: fabric-flow 8s ease-in-out infinite;
        opacity: 0;
        transition: opacity 0.3s;
      }
      .fabric-card:hover::before {
        opacity: 1;
      }
      .fabric-button {
        background: linear-gradient(135deg, #c2410c 0%, #ea580c 50%, #c2410c 100%),
                    repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(255,255,255,0.08) 2px, rgba(255,255,255,0.08) 4px);
        background-size: 200% 100%, 100% 100%;
        position: relative;
        overflow: hidden;
      }
      .fabric-button::before,
      .fabric-button::after {
        content: '';
        position: absolute;
        inset: 0;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s;
      }
      .fabric-button::before {
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        animation: laser-sweep 2s ease-in-out infinite;
      }
      .fabric-button::after {
        background: linear-gradient(90deg, transparent, rgba(251,146,60,0.6), transparent);
        animation: laser-sweep-delayed 2s ease-in-out infinite 0.3s;
      }
      .fabric-button:hover::before,
      .fabric-button:hover::after {
        opacity: 1;
      }
      .fabric-button:hover {
        animation: fabric-flow 3s ease-in-out infinite;
      }
    `;
    document.head.appendChild(style);

    return () => {
      const existingStyle = document.getElementById(styleId);
      if (existingStyle) existingStyle.remove();
    };
  }, []);

  // Automation examples
  const automationExamples = [
    {
      title: "Post & engage on Instagram",
      description: "Create a post, reply to comments with AI, and track engagement",
      icon: <Instagram className="w-5 h-5" />,
      color: "from-pink-500 to-purple-600"
    },
    {
      title: "Daily analytics reports",
      description: "Get insights from all platforms sent to Slack every morning",
      icon: <BarChart3 className="w-5 h-5" />,
      color: "from-blue-500 to-cyan-500"
    },
    {
      title: "Cross-platform publishing",
      description: "Share viral content across all your social accounts instantly",
      icon: <Zap className="w-5 h-5" />,
      color: "from-orange-500 to-red-500"
    },
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white relative overflow-hidden">
      {/* Animated gradient background */}
      <div className="fixed inset-0 bg-gradient-to-br from-[#0a0a0a] via-[#0f0f14] to-[#0a0a0a]" />
      
      {/* Grid pattern */}
      <div
        className="fixed inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(to right, #ffffff 1px, transparent 1px),
            linear-gradient(to bottom, #ffffff 1px, transparent 1px)
          `,
          backgroundSize: '64px 64px',
        }}
      />
      
      {/* Radial gradient overlay */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-orange-900/10 via-transparent to-transparent" />
      
      {/* Animated grain texture */}
      <div className="fixed inset-0 opacity-[0.015] mix-blend-overlay pointer-events-none"
        style={{
          backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 400 400\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'4\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\'/%3E%3C/svg%3E")',
        }}
      />

      {/* Navigation */}
      <nav className="relative z-50 pt-4 px-4 sm:px-6">
        <div className="max-w-6xl mx-auto">
          <div className="relative px-4 sm:px-6 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="relative group cursor-pointer">
                    <img src={chatverseLogo} alt="ChatVerse" className="w-9 h-9 transition-transform group-hover:scale-110" />
                  </div>
                  <div>
                    <span className="text-base font-bold text-white">ChatVerse</span>
                    <div className="text-[9px] text-orange-400 font-medium tracking-wider">AUTOMATION</div>
                  </div>
                </div>

                <div className="hidden md:flex items-center space-x-1">
                  <a href="#features" className="px-3 py-2 text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all duration-300">
                    Features
                  </a>
                  <a href="#how-it-works" className="px-3 py-2 text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all duration-300">
                    How it works
                  </a>
                  <a href="#platforms" className="px-3 py-2 text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all duration-300">
                    Platforms
                  </a>
                  
                  <div className="flex items-center space-x-2 ml-2 pl-2 border-l border-white/5">
                    {user ? (
                      <button 
                        onClick={() => navigate('/platforms')}
                        className="px-4 py-2 text-sm font-medium bg-white/8 hover:bg-white/12 rounded-xl text-white transition-all duration-300"
                      >
                        Dashboard
                      </button>
                    ) : (
                      <>
                        <button 
                          onClick={() => navigate('/get-started')}
                          className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white hover:bg-white/5 rounded-xl transition-all duration-300"
                        >
                          Login
                        </button>
                        <button 
                          onClick={() => navigate('/get-started')}
                          className="px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 rounded-xl text-sm font-semibold text-white transition-all duration-300 shadow-md shadow-orange-500/20"
                        >
                          Sign Up
                        </button>
                      </>
                    )}
                  </div>
                </div>

                <button className="md:hidden p-2 hover:bg-white/5 rounded-xl transition-all duration-300" onClick={() => setIsMenuOpen(!isMenuOpen)}>
                  {isMenuOpen ? <X className="w-5 h-5 text-white" /> : <Menu className="w-5 h-5 text-white" />}
                </button>
              </div>

            {/* Mobile dropdown with soft background */}
            {isMenuOpen && (
              <div className="md:hidden mt-4 pt-4 border-t border-white/5">
                <div 
                  className="flex flex-col space-y-1 p-3 rounded-2xl"
                  style={{
                    background: 'rgba(15, 15, 20, 0.9)',
                    backdropFilter: 'blur(16px)',
                    WebkitBackdropFilter: 'blur(16px)',
                  }}
                >
                  <a href="#features" className="px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all duration-300">Features</a>
                  <a href="#how-it-works" className="px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all duration-300">How it works</a>
                  <a href="#platforms" className="px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all duration-300">Platforms</a>
                  {user ? (
                    <button onClick={() => navigate('/platforms')} className="px-3 py-2 text-left text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all duration-300">
                      Dashboard
                    </button>
                  ) : (
                    <>
                      <button onClick={() => navigate('/get-started')} className="px-3 py-2 text-left text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all duration-300">
                        Login
                      </button>
                      <button onClick={() => navigate('/get-started')} className="mt-2 px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 rounded-xl text-center text-sm text-white font-medium transition-all duration-300 shadow-md shadow-orange-500/20">
                        Sign Up
                      </button>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </nav>

      <main className="relative z-10">
        {/* Hero Section */}
        <div className="max-w-5xl mx-auto px-6 pt-8 sm:pt-12 pb-16">
          <div className="text-center space-y-6">
            {/* Badges */}
            <div className="flex flex-col items-center gap-3">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-black/40 border border-orange-500/30 backdrop-blur-sm hover:border-orange-500/50 transition-all">
                <Sparkles className="w-4 h-4 text-orange-400" />
                <span className="text-sm font-medium text-white">No-code AI automation platform</span>
                <div className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />
              </div>
              
              {/* Alpha Testing Chip */}
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/30 backdrop-blur-sm group relative">
                <span className="text-xs font-medium text-yellow-400">⚠️ Alpha Testing</span>
                {/* Tooltip */}
                <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 w-64 px-3 py-2 bg-black/90 border border-yellow-500/20 rounded-lg text-xs text-gray-300 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 backdrop-blur-md">
                  This website is under development. You might face some issues.
                </div>
              </div>
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight leading-[1.1] px-4">
              <span className="block text-white">Build automations</span>
              <span className="block bg-gradient-to-r from-orange-400 via-orange-500 to-orange-400 bg-clip-text text-transparent">without code</span>
            </h1>

            {/* Subheadline */}
            <p className="max-w-2xl mx-auto text-lg sm:text-xl text-gray-400 leading-relaxed px-4">
              Forget n8n and Zapier. Create powerful automations for{' '}
              <span className="text-white font-medium">social media</span> and{' '}
              <span className="text-white font-medium">productivity tools</span> using just natural language.{' '}
              <span className="text-orange-400 font-medium">No coding. No APIs. Just queries.</span>
            </p>
            {/* Waitlist Form (moved above buttons) */}
            <div className="mt-4 sm:mt-6 px-4">
              {waitlistStatus === 'success' ? (
                <div className="max-w-xl mx-auto w-full">
                  <div className="px-4 py-3 rounded-xl bg-green-500/10 border border-green-500/30 text-green-300 text-sm text-center">
                    {waitlistMessage || 'Thanks! You have been added to the waitlist.'}
                  </div>
                </div>
              ) : (
                <>
                  {/* <p className="text-xs sm:text-sm text-yellow-400/90 text-center mb-2">
                    Please enter your email so that when our product is ready we will let you know. Right now it is under development and testing phase.
                  </p>
                  <form onSubmit={handleJoinWaitlist}>
                    <div className="max-w-xl mx-auto w-full">
                      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                        <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-xl bg-black/60 border border-orange-500/20 focus-within:border-orange-500/50 transition-colors">
                          <Mail className="w-4 h-4 text-orange-400 flex-shrink-0" />
                          <input
                            type="email"
                            value={waitlistEmail}
                            onChange={(e) => setWaitlistEmail(e.target.value)}
                            placeholder="Your email address"
                            className="w-full bg-transparent text-sm sm:text-base placeholder-gray-400 text-white outline-none"
                            disabled={waitlistStatus === 'loading'}
                            required
                          />
                        </div>
                        <button
                          type="submit"
                          disabled={waitlistStatus === 'loading'}
                          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold shadow-md shadow-orange-500/20 disabled:opacity-60 disabled:cursor-not-allowed"
                        >
                          {waitlistStatus === 'loading' ? 'Joining…' : 'Join Waitlist'}
                        </button>
                      </div>
                      {waitlistMessage && (
                        <p className={`${waitlistStatus === 'error' ? 'text-red-400' : 'text-green-400'} text-xs sm:text-sm mt-2 text-center`}>
                          {waitlistMessage}
                        </p>
                      )}
                    </div>
                  </form> */}
                </>
              )}
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 pt-4 px-4">
              <button
                onClick={handleCreateAutomation}
                className="group relative w-full sm:w-auto px-6 sm:px-10 py-3 sm:py-4 bg-gradient-to-r from-black via-zinc-900 to-black border-2 border-orange-500/30 hover:border-orange-500/60 text-white font-bold text-base sm:text-lg rounded-xl transition-all duration-300 hover:shadow-2xl hover:shadow-orange-500/30 hover:scale-105"
              >
                <span className="flex items-center justify-center gap-2 sm:gap-3 relative z-10">
                  <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-orange-400" />
                  Create AI Automation
                  <ArrowRight className="w-5 h-5 sm:w-6 sm:h-6 text-orange-400 group-hover:translate-x-1 transition-transform" />
                </span>
              </button>
              
              <button
                onClick={handleGetStarted}
                className="group relative w-full sm:w-auto px-6 sm:px-8 py-3 sm:py-4 bg-white/5 hover:bg-white/10 text-white font-semibold text-base sm:text-lg rounded-lg transition-all duration-200"
              >
                <span className="flex items-center justify-center gap-2">
                  <Rocket className="w-4 h-4 sm:w-5 sm:h-5" />
                  {user ? 'Go to Dashboard' : 'Start Building Free'}
                  <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5 group-hover:translate-x-1 transition-transform" />
                </span>
              </button>
            </div>

            

            {/* Social Proof / Stats */}
            <div className="flex flex-wrap items-center justify-center gap-8 pt-8 text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-500" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-500" />
                <span>Setup in 2 minutes</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-500" />
                <span>Works with 10+ platforms</span>
              </div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div id="features" className="max-w-6xl mx-auto px-6 py-24">
          <div className="text-center space-y-12">
            <div className="space-y-4">
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white">
                Automation as simple as typing
              </h2>
              <p className="text-lg text-gray-400 max-w-2xl mx-auto">
                Just describe what you want in plain English. Our AI understands, builds, and runs the automation for you.
              </p>
            </div>

            {/* Query & Data-Driven Showcase */}
            <div className="max-w-full sm:max-w-3xl mx-auto">
              {/* Tab Navigation */}
              <div className="flex items-center justify-center mb-8">
                <div className="relative p-1 bg-black/60 backdrop-blur-sm rounded-2xl border border-white/10">
                  <div className="flex space-x-1">
                    <button
                      onClick={() => setActiveTab('query')}
                      className={`relative px-4 sm:px-6 py-2 sm:py-3 rounded-xl text-xs sm:text-sm font-medium transition-all duration-300 ${activeTab === 'query' ? 'text-white' : 'text-gray-400'}`}
                    >
                      {activeTab === 'query' && (
                        <div className="absolute inset-0 bg-gradient-to-r from-orange-600 to-orange-500 rounded-xl" />
                      )}
                      <span className="relative z-10 flex items-center gap-2">
                        <Bot className="w-4 h-4" />
                        Query-Based
                      </span>
                    </button>
                    <button
                      onClick={() => setActiveTab('data')}
                      className={`relative px-4 sm:px-6 py-2 sm:py-3 rounded-xl text-xs sm:text-sm font-medium transition-all duration-300 ${activeTab === 'data' ? 'text-white' : 'text-gray-400'}`}
                    >
                      {activeTab === 'data' && (
                        <div className="absolute inset-0 bg-gradient-to-r from-orange-600 to-orange-500 rounded-xl" />
                      )}
                      <span className="relative z-10 flex items-center gap-2">
                        <BarChart3 className="w-4 h-4" />
                        Data-Driven
                      </span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Query-Based Tab */}
              {activeTab === 'query' && (
                <div className="p-[2px] rounded-2xl bg-gradient-to-r from-black/40 via-black/60 to-black/40 border border-orange-500/20 shadow-[0_0_60px_-12px_rgba(234,88,12,0.15)]">
                  <div className="fabric-card rounded-2xl backdrop-blur-sm bg-black" style={{backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.08) 1px, transparent 0), radial-gradient(circle at 3px 3px, rgba(255,255,255,0.04) 1px, transparent 0)', backgroundSize: '20px 20px, 40px 40px'}}>
                    <div className="flex items-center justify-between px-3 sm:px-4 py-3 border-b border-orange-500/10">
                      <div className="flex items-center gap-2 sm:gap-3">
                        <div className="w-6 h-6 sm:w-8 sm:h-8 rounded-lg bg-gradient-to-br from-orange-600 to-orange-500 flex items-center justify-center shadow-lg shadow-orange-500/30">
                          <Bot className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
                        </div>
                        <p className="text-xs sm:text-sm text-gray-300 font-medium">Ask in plain English — ChatVerse converts it into automation</p>
                      </div>
                      <div className="hidden sm:flex items-center gap-2 text-xs text-gray-400">
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-lg shadow-emerald-400/50" />
                        <span>Live preview</span>
                      </div>
                    </div>
                    <div className="px-3 sm:px-4 py-4 sm:py-5">
                      <div className="flex flex-col gap-3 sm:gap-4">
                        <div className="w-full">
                          <div className="fabric-card flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 rounded-xl bg-black border border-orange-500/20">
                            <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-orange-400 flex-shrink-0 animate-pulse" />
                            <div className="text-left text-sm sm:text-base text-gray-100 whitespace-pre-wrap break-words flex-1 min-h-[1.5rem] font-medium">
                              {displayText}
                              <span className={blink ? 'inline-block ml-1 align-middle h-4 sm:h-5 w-[2px] bg-orange-400 animate-pulse shadow-lg shadow-orange-400/50' : 'inline-block ml-1 align-middle h-4 sm:h-5 w-[2px] bg-orange-400 opacity-40'} />
                            </div>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-1.5 sm:gap-2 justify-center sm:justify-start">
                          {queriesData[qIndex].chips.map((c, i) => (
                            <div key={i} className="fabric-card inline-flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1 sm:py-1.5 rounded-full bg-black/80 border border-orange-500/20 hover:border-orange-500/40 transition-all">
                              <span className="opacity-80 text-gray-200 text-xs sm:text-sm">{c.icon}</span>
                              <span className="text-[10px] sm:text-xs text-gray-300 whitespace-nowrap font-medium">{c.label}</span>
                            </div>
                          ))}
                        </div>
                        <div className="grid grid-cols-3 gap-2 md:gap-3 mt-2">
                          <div className="fabric-card p-2 md:p-3 rounded-xl bg-black/80 border border-orange-500/20 flex items-center gap-2 hover:border-orange-500/40 transition-all group">
                            <div className="w-6 h-6 md:w-8 md:h-8 rounded-lg bg-gradient-to-br from-orange-600 to-orange-500 flex items-center justify-center flex-shrink-0 shadow-lg shadow-orange-500/30 group-hover:shadow-orange-500/50 transition-all">
                              <Code className="w-3 h-3 md:w-4 md:h-4 text-white" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-xs text-gray-300 font-medium">Parse</p>
                              <p className="text-[10px] text-gray-400">Understand</p>
                            </div>
                          </div>
                          <div className="fabric-card p-2 md:p-3 rounded-xl bg-black/80 border border-orange-500/20 flex items-center gap-2 hover:border-orange-500/40 transition-all group">
                            <div className="w-6 h-6 md:w-8 md:h-8 rounded-lg bg-gradient-to-br from-orange-500 to-orange-400 flex items-center justify-center flex-shrink-0 shadow-lg shadow-orange-500/30 group-hover:shadow-orange-500/50 transition-all">
                              <ListChecks className="w-3 h-3 md:w-4 md:h-4 text-white" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-xs text-gray-300 font-medium">Plan</p>
                              <p className="text-[10px] text-gray-400">Map tasks</p>
                            </div>
                          </div>
                          <div className="fabric-card p-2 md:p-3 rounded-xl bg-black/80 border border-orange-500/20 flex items-center gap-2 hover:border-orange-500/40 transition-all group">
                            <div className="w-6 h-6 md:w-8 md:h-8 rounded-lg bg-gradient-to-br from-orange-400 to-orange-300 flex items-center justify-center flex-shrink-0 shadow-lg shadow-orange-500/30 group-hover:shadow-orange-500/50 transition-all">
                              <Zap className="w-3 h-3 md:w-4 md:h-4 text-white" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-xs text-gray-300 font-medium">Run</p>
                              <p className="text-[10px] text-gray-400">Execute</p>
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={handleCreateAutomation}
                          className="fabric-button mt-4 w-full px-4 py-3 text-white font-bold text-sm rounded-lg transition-all shadow-lg shadow-orange-500/30 hover:shadow-orange-500/50 hover:-translate-y-0.5"
                        >
                          <span className="flex items-center justify-center gap-2 relative z-10">
                            <Rocket className="w-4 h-4" />
                            {user ? 'Go to Dashboard' : 'Try This Automation'}
                            <ArrowRight className="w-4 h-4" />
                          </span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Data-Driven Tab */}
              {activeTab === 'data' && (
                <div className="p-[2px] rounded-2xl bg-gradient-to-r from-black/40 via-black/60 to-black/40 border border-orange-500/20 shadow-[0_0_60px_-12px_rgba(234,88,12,0.15)]">
                  <div className="fabric-card rounded-2xl backdrop-blur-sm bg-black p-4 sm:p-6" style={{backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.08) 1px, transparent 0), radial-gradient(circle at 3px 3px, rgba(255,255,255,0.04) 1px, transparent 0)', backgroundSize: '20px 20px, 40px 40px'}}>
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-600 to-orange-500 flex items-center justify-center shadow-lg shadow-orange-500/30">
                        <BarChart3 className="w-4 h-4 text-white" />
                      </div>
                      <h3 className="text-base sm:text-lg font-semibold text-white">Automation Builder</h3>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Target Platform</label>
                        <select className="fabric-card w-full px-3 py-2 bg-black/80 border border-orange-500/20 rounded-lg text-white text-sm focus:outline-none focus:border-orange-500/60 transition-all hover:border-orange-500/40">
                          <option>Instagram</option>
                          <option>Twitter</option>
                          <option>LinkedIn</option>
                          <option>Facebook</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Content Template</label>
                        <textarea className="fabric-card w-full px-3 py-2 bg-black/80 border border-orange-500/20 rounded-lg text-white text-sm h-20 resize-none focus:outline-none focus:border-orange-500/60 transition-all hover:border-orange-500/40" placeholder="Check out our latest product launch! 🚀 #innovation #tech" readOnly />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">AI Model</label>
                        <div className="grid grid-cols-2 gap-2">
                          <div className="fabric-card p-3 bg-black/60 border border-orange-500/40 rounded-lg cursor-pointer hover:border-orange-500/70 hover:bg-black/80 transition-all group">
                            <div className="text-xs font-medium text-orange-300 group-hover:text-orange-200 transition-colors">GPT-4</div>
                            <div className="text-[10px] text-gray-400">Creative & Engaging</div>
                          </div>
                          <div className="fabric-card p-3 bg-black/60 border border-orange-500/20 rounded-lg cursor-pointer hover:border-orange-500/40 hover:bg-black/80 transition-all group">
                            <div className="text-xs font-medium text-gray-300 group-hover:text-white transition-colors">Claude</div>
                            <div className="text-[10px] text-gray-400">Professional Tone</div>
                          </div>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Schedule</label>
                        <div className="flex gap-2">
                          <input type="time" className="fabric-card flex-1 px-3 py-2 bg-black/80 border border-orange-500/20 rounded-lg text-white text-sm focus:outline-none focus:border-orange-500/60 transition-all hover:border-orange-500/40" defaultValue="14:30" />
                          <select className="fabric-card flex-1 px-3 py-2 bg-black/80 border border-orange-500/20 rounded-lg text-white text-sm focus:outline-none focus:border-orange-500/60 transition-all hover:border-orange-500/40">
                            <option>Daily</option>
                            <option>Weekly</option>
                            <option>Monthly</option>
                          </select>
                        </div>
                      </div>
                      <button 
                        onClick={handleCreateAutomation}
                        className="fabric-button w-full mt-6 px-4 py-3 text-white font-bold text-sm rounded-lg transition-all shadow-lg shadow-orange-500/30 hover:shadow-orange-500/50 hover:-translate-y-0.5"
                      >
                        <div className="flex items-center justify-center gap-2 relative z-10">
                          <Zap className="w-4 h-4" />
                          Deploy Automation
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
              )}

              <p className="mt-4 sm:mt-6 text-xs sm:text-sm text-gray-500 text-center">
                {activeTab === 'query' ? 'Examples rotate to demonstrate what ChatVerse can do — try your own on the next step' : 'Configure your automation with custom settings and see the preview in real-time'}
              </p>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div id="features" className="max-w-6xl mx-auto px-6 py-24">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white">
              Everything you need, nothing you don't
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              Built for creators, marketers, and teams who want powerful automation without the complexity
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {automationExamples.map((example, idx) => (
              <div 
                key={idx}
                className="fabric-card group rounded-2xl p-6 transition-all duration-300"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${example.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  {example.icon}
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{example.title}</h3>
                <p className="text-gray-400">{example.description}</p>
              </div>
            ))}
          </div>

          {/* Feature Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-16">
            <div className="fabric-card rounded-2xl p-8">
              <Lock className="w-10 h-10 text-blue-400 mb-4" />
              <h3 className="text-2xl font-bold text-white mb-3">Secure & Private</h3>
              <p className="text-gray-400 leading-relaxed">
                Your data is encrypted end-to-end. We never store your passwords or access tokens beyond what's needed for automation.
              </p>
            </div>

            <div className="fabric-card rounded-2xl p-8">
              <TrendingUp className="w-10 h-10 text-green-400 mb-4" />
              <h3 className="text-2xl font-bold text-white mb-3">AI-Powered Intelligence</h3>
              <p className="text-gray-400 leading-relaxed">
                Advanced AI models understand context, sentiment, and intent to make smart decisions for your automations.
              </p>
            </div>

            <div className="fabric-card rounded-2xl p-8">
              <Boxes className="w-10 h-10 text-purple-400 mb-4" />
              <h3 className="text-2xl font-bold text-white mb-3">10+ Platform Integrations</h3>
              <p className="text-gray-400 leading-relaxed">
                Connect Instagram, Facebook, Twitter, LinkedIn, Slack, Gmail, and more. All from one dashboard.
              </p>
            </div>

            <div className="fabric-card rounded-2xl p-8">
              <Clock className="w-10 h-10 text-orange-400 mb-4" />
              <h3 className="text-2xl font-bold text-white mb-3">Schedule & Automate</h3>
              <p className="text-gray-400 leading-relaxed">
                Set up recurring tasks, time-based triggers, or event-based automations that run 24/7 without manual intervention.
              </p>
            </div>
          </div>
        </div>

        {/* Platform Section */}
        <div id="platforms" className="max-w-6xl mx-auto px-6 py-24">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4">
              Connect all your platforms
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              Instagram, Facebook, Twitter, Slack, Gmail, Meet, WhatsApp, Calendar, LinkedIn, Crawler, and <span className="text-orange-400 font-semibold">200+ tools and apps</span> connect seamlessly
            </p>
          </div>

          <PlatformLogos />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
            <div className="fabric-card rounded-2xl p-8 transition-all">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">One-Click Setup</h3>
              <p className="text-gray-400">
                Connect all your accounts in seconds with our streamlined OAuth integration
              </p>
            </div>

            <div className="fabric-card rounded-2xl p-8 transition-all">
              <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Secure & Private</h3>
              <p className="text-gray-400">
                Enterprise-grade security with end-to-end encryption for all your data
              </p>
            </div>

            <div className="fabric-card rounded-2xl p-8 transition-all">
              <div className="w-12 h-12 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Real-Time Sync</h3>
              <p className="text-gray-400">
                Instant synchronization across all platforms with live updates and notifications
              </p>
            </div>
          </div>
        </div>

        {/* Automation Examples from Original */}
        <AutomationExamples />

        {/* No-Code Automation Section */}
        <div className="max-w-6xl mx-auto px-6 py-24">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-6">
              Automate your social presence with no code
            </h2>
            <p className="text-lg text-gray-400 max-w-4xl mx-auto leading-relaxed">
              Our intuitive automation tool allows you to streamline your social media workflow without writing a single line of code. Simply provide your queries or fill in the values manually to set up powerful automation flows.
            </p>
          </div>

          <div className="flex flex-col items-center justify-center my-16">
            <div className="flex items-center space-x-8">
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg">
                  <Bot className="w-8 h-8 text-white" />
                </div>
                <p className="mt-2 text-sm text-gray-400 font-medium">Query Input</p>
              </div>
              <ArrowRight className="w-10 h-10 text-gray-500" />
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg">
                  <Repeat className="w-8 h-8 text-white" />
                </div>
                <p className="mt-2 text-sm text-gray-400 font-medium">Automation Logic</p>
              </div>
              <ArrowRight className="w-10 h-10 text-gray-500" />
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-2xl flex items-center justify-center shadow-lg">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <p className="mt-2 text-sm text-gray-400 font-medium">Action Performed</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="fabric-card rounded-2xl p-8 transition-all">
              <h3 className="text-xl font-bold text-white mb-3 text-center">
                Query-Based Automation
              </h3>
              <p className="text-gray-400 text-sm text-center leading-relaxed">
                Simply give a query and let our AI handle the rest, from content creation to scheduling and posting across platforms.
              </p>
            </div>
            <div className="fabric-card rounded-2xl p-8 transition-all">
              <h3 className="text-xl font-bold text-white mb-3 text-center">
                Data Scraping & Reporting
              </h3>
              <p className="text-gray-400 text-sm text-center leading-relaxed">
                Scrape social media data and use it to create insightful reports, allowing AI to make informed decisions or send you daily email summaries.
              </p>
            </div>
            <div className="fabric-card rounded-2xl p-8 transition-all">
              <h3 className="text-xl font-bold text-white mb-3 text-center">
                Unified Platform Management
              </h3>
              <p className="text-gray-400 text-sm text-center leading-relaxed">
                Integrate multiple social media platforms into one place so you don't have to jump between apps. Manage everything efficiently with a single query.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="max-w-4xl mx-auto px-6 py-24">
          <div className="bg-gradient-to-r from-orange-500/10 to-orange-600/10 border border-orange-500/20 rounded-2xl p-12 text-center backdrop-blur-sm">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4">
              Ready to automate your workflow?
            </h2>
            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
              Join thousands of creators and teams who've automated their social media and productivity workflows
            </p>
            <button
              onClick={handleCreateAutomation}
              className="group inline-flex items-center gap-2 px-6 sm:px-10 py-3 sm:py-4 bg-gradient-to-r from-black via-zinc-900 to-black border-2 border-orange-500/30 hover:border-orange-500/60 text-white font-bold text-base sm:text-lg rounded-xl transition-all duration-300 hover:shadow-2xl hover:shadow-orange-500/30 hover:scale-105"
            >
              <span className="relative z-10 flex items-center gap-2">
                <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-orange-400" />
                Create Automation
                <ArrowRight className="w-5 h-5 sm:w-6 sm:h-6 text-orange-400 group-hover:translate-x-1 transition-transform" />
              </span>
            </button>
            <p className="text-sm text-gray-400 mt-4">Free plan available. No credit card required.</p>
          </div>
        </div>
      </main>
      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 bg-black/50 backdrop-blur-lg mt-24">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <img src={chatverseLogo} alt="ChatVerse" className="w-12 h-12" />
                <span className="text-xl font-bold text-white">ChatVerse</span>
              </div>
              <p className="text-sm text-gray-400">
                No-code AI automation platform for social media and productivity tools.
              </p>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#how-it-works" className="hover:text-white transition-colors">How it works</a></li>
                <li><a href="/pricing" className="hover:text-white transition-colors">Pricing</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="/privacy" className="hover:text-white transition-colors">Privacy</a></li>
                <li><a href="/terms" className="hover:text-white transition-colors">Terms</a></li>
              </ul>
            </div>
          </div>

          <div className="flex flex-col md:flex-row items-center justify-between border-t border-white/10 pt-8">
            <div className="text-sm text-gray-400">
              &copy; {new Date().getFullYear()} ChatVerse. All rights reserved.
            </div>
            <div className="flex items-center space-x-4 mt-6 md:mt-0">
              <a href="#" className="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center transition-all">
                <Instagram className="w-5 h-5 text-gray-400 hover:text-white" />
              </a>
              <a href="#" className="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center transition-all">
                <Twitter className="w-5 h-5 text-gray-400 hover:text-white" />
              </a>
              <a href="#" className="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center transition-all">
                <Linkedin className="w-5 h-5 text-gray-400 hover:text-white" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPageNew2;
