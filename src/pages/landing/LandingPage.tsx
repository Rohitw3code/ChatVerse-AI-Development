import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores';
import { Menu, X, Sparkles, Zap, Users, BarChart3, Shield, ArrowRight, Star, Rocket, Instagram, Facebook, Twitter, Linkedin, Bot, Workflow, Brain, CheckCircle2, PlayCircle, Terminal, MessageSquare, Clock, TrendingUp, Lock, Boxes, Send, Mail, Globe, Code, ListChecks, Repeat } from 'lucide-react';
import PlatformLogos from './components/PlatformLogos';
import AutomationExamples from './components/AutomationExamples';
import chatverseLogo from './../../components/chatverse.svg'

function LandingPage() {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const handleGetStarted = () => {
    if (user) {
      navigate('/platforms');
    } else {
      navigate('/get-started');
    }
  };
  
  const handleLogout = async () => {
    const { signOut } = useAuthStore.getState();
    try {
      await signOut();
      navigate('/');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

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

      <nav className="relative z-50">
        <div className="max-w-6xl mx-auto px-6 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative group">
                <div className="w-10 h-10 bg-white/5 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/10 group-hover:border-white/20 transition-all duration-300">
                                    <img src={chatverseLogo} alt="ChatVerse Logo" className="w-full h-full" />
                </div>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-white rounded-full opacity-80"></div>
              </div>
              <span className="text-2xl font-bold text-white tracking-wide">ChatVerse.io</span>
            </div>

            <div className="hidden md:flex items-center space-x-8">
              <a href="#platform" className="relative group">
                <span className="text-gray-400 hover:text-white transition-all duration-300">Platform</span>
                <div className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-500"></div>
              </a>
              <div className="flex items-center space-x-4">
                {user ? (
                  <>
                    <button 
                      onClick={() => navigate('/platforms')}
                      className="px-4 py-2 text-gray-400 hover:text-white transition-all duration-300"
                    >
                      Dashboard
                    </button>
                    <button 
                      onClick={handleLogout}
                      className="px-6 py-2 bg-red-500/10 backdrop-blur-sm rounded-lg hover:bg-red-500/20 transition-all duration-300 border border-red-500/20 hover:border-red-500/40"
                    >
                      <span className="text-red-400">Logout</span>
                    </button>
                  </>
                ) : (
                  <>
                    <button 
                      onClick={() => navigate('/get-started')}
                      className="px-4 py-2 text-gray-400 hover:text-white transition-all duration-300"
                    >
                      Login
                    </button>
                    <button 
                      onClick={() => navigate('/get-started')}
                      className="px-6 py-2 bg-white/5 backdrop-blur-sm rounded-lg hover:bg-white/10 transition-all duration-300 border border-white/10 hover:border-white/20"
                    >
                      <span className="text-white">Sign Up</span>
                    </button>
                  </>
                )}
              </div>
            </div>

            <button className="md:hidden transition-transform duration-200" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

          {isMenuOpen && (
            <div className="md:hidden absolute top-full left-0 right-0 bg-black/90 backdrop-blur-lg border border-white/20 rounded-lg mt-2 mx-6 p-4">
              <div className="flex flex-col space-y-4">
                <a href="#platform" className="text-gray-400 hover:text-white transition-all duration-300">
                  Platform
                </a>
                {user ? (
                  <>
                    <button 
                      onClick={() => navigate('/platforms')}
                      className="text-left text-gray-400 hover:text-white transition-all duration-300"
                    >
                      Dashboard
                    </button>
                    <button 
                      onClick={handleLogout}
                      className="px-6 py-2 bg-red-500/10 backdrop-blur-sm rounded-lg text-center border border-red-500/20 hover:bg-red-500/20 transition-all duration-300"
                    >
                      <span className="text-red-400">Logout</span>
                    </button>
                  </>
                ) : (
                  <>
                    <button 
                      onClick={() => navigate('/get-started')}
                      className="text-left text-gray-400 hover:text-white transition-all duration-300"
                    >
                      Login
                    </button>
                    <button 
                      onClick={() => navigate('/get-started')}
                      className="px-6 py-2 bg-white/10 backdrop-blur-sm rounded-lg text-center border border-white/20 hover:bg-white/20 transition-all duration-300"
                    >
                      Sign Up
                    </button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </nav>
        {/* The rest of the JSX for LandingPage remains the same */}
        <main className="relative overflow-hidden py-12 sm:py-20 lg:py-24">
        <div className="relative z-10 max-w-6xl mx-auto px-6">
          <div className="text-center space-y-16">
            <div className="space-y-8">
              <div className="inline-flex items-center space-x-3 bg-gradient-to-r from-purple-800/30 to-pink-800/30 backdrop-blur-sm rounded-full px-4 sm:px-6 py-2 sm:py-3 border border-purple-500/40 hover:border-purple-500/60 transition-all duration-300 group animate-fade-in-down">
                <Star className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-300 animate-sparkle" />
                <span className="text-xs sm:text-sm font-medium bg-gradient-to-r from-gray-300 to-white bg-clip-text text-transparent">
                  INTELLIGENT SOCIAL MEDIA AUTOMATION
                </span>
                <div className="w-2 h-2 bg-green-400 rounded-full animate-ping opacity-80"></div>
              </div>

              <div className="relative">
                <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-black leading-none tracking-wider">
                  <div className="relative inline-block">
                    <span
                      className="bg-gradient-to-r from-white via-pink-500 to-red-500 bg-clip-text text-transparent"
                      style={{
                        fontFamily: 'Playfair Display, Georgia, serif',
                        fontWeight: '900',
                        letterSpacing: '0.05em',
                      }}
                    >
                      CHAT-VERSE
                    </span>
                  </div>
                </h1>

                <div className="mt-6 sm:mt-8">
                  <h2
                    className="text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl font-light tracking-wide bg-gradient-to-r from-gray-200 to-gray-400 bg-clip-text text-transparent px-4 sm:px-0"
                    style={{ fontFamily: 'Playfair Display, Georgia, serif' }}
                  >
                    Transform Your Social Presence with <span className="font-semibold bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent">AI-Powered Automation</span>
                  </h2>
                </div>
              </div>

              <div className="max-w-4xl mx-auto px-4 sm:px-0">
                <p
                  className="text-base sm:text-lg md:text-xl lg:text-2xl leading-relaxed font-light text-gray-400"
                  style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
                >
                  Revolutionize your social media strategy with ChatVerse.
                  <span className="font-medium bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent">
                    {' '}Create, schedule, and engage
                  </span>{' '}
                  across all platforms using natural language commands. Let AI handle the complexity while you focus on growing your brand.
                </p>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6 px-4 sm:px-0">
              <button
                onClick={handleGetStarted}
                className="group relative w-full sm:w-auto px-8 sm:px-12 py-3 sm:py-4 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-lg font-semibold text-base sm:text-lg transition-all duration-300 hover:from-purple-700 hover:to-pink-600 shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 hover:scale-[1.02] overflow-hidden transform-gpu"
                style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent -skew-x-12 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>

                <span className="flex items-center justify-center space-x-2 sm:space-x-3 relative z-10">
                  <Zap className="w-4 h-4 sm:w-5 sm:h-5 text-white group-hover:rotate-6 transition-transform duration-300" />
                  <span className="font-semibold tracking-wide">
                    {user ? 'Go to Dashboard' : 'Get Started Free'}
                  </span>
                  <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5 text-white group-hover:translate-x-1 transition-transform duration-300" />
                </span>
              </button>

              <button
                className="group relative w-full sm:w-auto px-6 sm:px-8 py-3 sm:py-4 bg-transparent border border-white/20 rounded-lg font-medium text-base sm:text-lg transition-all duration-300 hover:bg-white/10 hover:border-white/40 overflow-hidden text-gray-300 hover:text-white hover:shadow-md hover:shadow-white/5"
                style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
                onClick={() => {
                  const el = document.getElementById('query-showcase');
                  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }}
              >
                <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <span className="flex items-center justify-center space-x-2 sm:space-x-3 relative z-10">
                  <Globe className="w-4 h-4 sm:w-5 sm:h-5 text-gray-300 group-hover:text-white transition-colors duration-300" />
                  <span>Watch Demo</span>
                </span>
              </button>
            </div>
            <section id="query-showcase" className="mx-auto max-w-4xl w-full px-4 sm:px-0">
              <div className="flex items-center justify-center mb-8">
                <div className="relative p-1 bg-black/40 backdrop-blur-sm rounded-2xl border border-white/20">
                  <div className="flex space-x-1">
                    <button
                      onClick={() => setActiveTab('query')}
                      className={`relative px-6 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${activeTab === 'query'
                        ? 'text-white'
                        : 'text-gray-400 hover:text-gray-300'
                        }`}
                    >
                      {activeTab === 'query' && (
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/80 to-pink-600/80 rounded-xl border border-purple-500/40 shadow-lg shadow-purple-500/25" />
                      )}
                      <span className="relative z-10 flex items-center gap-2">
                        <Bot className="w-4 h-4" />
                        Query-Based
                      </span>
                    </button>
                    <button
                      onClick={() => setActiveTab('data')}
                      className={`relative px-6 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${activeTab === 'data'
                        ? 'text-white'
                        : 'text-gray-400 hover:text-gray-300'
                        }`}
                    >
                      {activeTab === 'data' && (
                        <div className="absolute inset-0 bg-gradient-to-r from-cyan-600/80 to-blue-600/80 rounded-xl border border-cyan-500/40 shadow-lg shadow-cyan-500/25" />
                      )}
                      <span className="relative z-10 flex items-center gap-2">
                        <BarChart3 className="w-4 h-4" />
                        Data-Driven
                      </span>
                    </button>
                  </div>
                </div>
              </div>
              {activeTab === 'query' && (
                <div className="p-[2px] rounded-2xl bg-gradient-to-r from-purple-900/40 via-fuchsia-800/30 to-pink-800/30 shadow-[0_0_60px_-12px_rgba(168,85,247,0.25)]">
                  <div
                    className="rounded-2xl backdrop-blur-sm border border-gray-800"
                    style={{
                      backgroundColor: '#0a0a0a',
                      backgroundImage: `
            radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0),
            radial-gradient(circle at 3px 3px, rgba(255,255,255,0.08) 1px, transparent 0),
            radial-gradient(circle at 5px 5px, rgba(255,255,255,0.04) 1px, transparent 0)
          `,
                      backgroundSize: '20px 20px, 40px 40px, 60px 60px',
                    }}
                  >
                    <div className="flex items-center justify-between px-3 sm:px-4 py-3 border-b border-gray-800">
                      <div className="flex items-center gap-2 sm:gap-3">
                        <div className="w-6 h-6 sm:w-8 sm:h-8 rounded-lg bg-gradient-to-br from-purple-700 to-pink-600 flex items-center justify-center">
                          <Bot className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
                        </div>
                        <p className="text-xs sm:text-sm text-gray-300" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                          Ask in plain English — ChatVerse converts it into automation
                        </p>
                      </div>

                      <div className="hidden sm:flex items-center gap-2 text-xs text-gray-400">
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" aria-hidden="true" />
                        <span>Live preview</span>
                      </div>
                    </div>
                    <div className="px-3 sm:px-4 py-4 sm:py-5">
                      <div className="flex flex-col gap-3 sm:gap-4">
                        <div className="w-full">
                          <div className="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 rounded-xl bg-black/70 border border-gray-800">
                            <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-pink-400 flex-shrink-0" />

                            <div
                              aria-live="polite"
                              className="text-left text-sm sm:text-base md:text-lg text-gray-100 whitespace-pre-wrap break-words flex-1 min-h-[1.5rem]"
                              style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
                            >
                              {displayText}
                              <span
                                className={
                                  blink
                                    ? 'inline-block ml-1 align-middle h-4 sm:h-5 w-[1px] bg-gray-100 animate-pulse'
                                    : 'inline-block ml-1 align-middle h-4 sm:h-5 w-[1px] bg-gray-100 opacity-40'
                                }
                              />
                            </div>

                            <button
                              onClick={handleGetStarted}
                              className="hidden md:inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 border border-transparent hover:from-purple-700 hover:to-pink-700 transition-all text-sm flex-shrink-0"
                            >
                              <Rocket className="w-4 h-4 text-white" />
                              {user ? 'Dashboard' : 'Generate'}
                            </button>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-1.5 sm:gap-2 justify-center sm:justify-start">
                          {queriesData[qIndex].chips.map((c, i) => (
                            <div
                              key={i}
                              className="group inline-flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1 sm:py-1.5 rounded-full bg-black/70 border border-gray-800 hover:border-gray-600 transition-all"
                            >
                              <span className="opacity-80 text-gray-200 text-xs sm:text-sm">{c.icon}</span>
                              <span className="text-[10px] sm:text-xs text-gray-300 whitespace-nowrap" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                                {c.label}
                              </span>
                            </div>
                          ))}
                        </div>
                        <div className="mt-2 sm:mt-1">
                          <div className="sm:hidden flex flex-col gap-2">
                            <div className="p-2 rounded-lg bg-black/70 border border-gray-800 flex items-center gap-2">
                              <div className="w-6 h-6 rounded-md bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center flex-shrink-0">
                                <Code className="w-3 h-3 text-white" />
                              </div>
                              <div className="flex-1">
                                <p className="text-xs text-gray-300 font-medium">Parse</p>
                                <p className="text-[10px] text-gray-400">Understand intent</p>
                              </div>
                            </div>

                            <div className="p-2 rounded-lg bg-black/70 border border-gray-800 flex items-center gap-2">
                              <div className="w-6 h-6 rounded-md bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center flex-shrink-0">
                                <ListChecks className="w-3 h-3 text-white" />
                              </div>
                              <div className="flex-1">
                                <p className="text-xs text-gray-300 font-medium">Plan</p>
                                <p className="text-[10px] text-gray-400">Map tasks & checks</p>
                              </div>
                            </div>

                            <div className="p-2 rounded-lg bg-black/70 border border-gray-800 flex items-center gap-2">
                              <div className="w-6 h-6 rounded-md bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center flex-shrink-0">
                                <Zap className="w-3 h-3 text-white" />
                              </div>
                              <div className="flex-1">
                                <p className="text-xs text-gray-300 font-medium">Run</p>
                                <p className="text-[10px] text-gray-400">Post · Reply · Notify</p>
                              </div>
                            </div>
                          </div>
                          <div className="hidden sm:grid grid-cols-3 gap-2 md:gap-3">
                            <div className="p-2 md:p-3 rounded-xl bg-black/70 border border-gray-800 flex items-center gap-2 md:gap-3">
                              <div className="w-6 h-6 md:w-8 md:h-8 rounded-lg bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center flex-shrink-0">
                                <Code className="w-3 h-3 md:w-4 md:h-4 text-white" />
                              </div>
                              <div className="min-w-0">
                                <p className="text-xs text-gray-300 font-medium">Parse</p>
                                <p className="text-[10px] text-gray-400 truncate">Understand intent</p>
                              </div>
                            </div>

                            <div className="p-2 md:p-3 rounded-xl bg-black/70 border border-gray-800 flex items-center gap-2 md:gap-3">
                              <div className="w-6 h-6 md:w-8 md:h-8 rounded-lg bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center flex-shrink-0">
                                <ListChecks className="w-3 h-3 md:w-4 md:h-4 text-white" />
                              </div>
                              <div className="min-w-0">
                                <p className="text-xs text-gray-300 font-medium">Plan</p>
                                <p className="text-[10px] text-gray-400 truncate">Map tasks & checks</p>
                              </div>
                            </div>

                            <div className="p-2 md:p-3 rounded-xl bg-black/70 border border-gray-800 flex items-center gap-2 md:gap-3">
                              <div className="w-6 h-6 md:w-8 md:h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center flex-shrink-0">
                                <Zap className="w-3 h-3 md:w-4 md:h-4 text-white" />
                              </div>
                              <div className="min-w-0">
                                <p className="text-xs text-gray-300 font-medium">Run</p>
                                <p className="text-[10px] text-gray-400 truncate">Post · Reply · Notify</p>
                              </div>
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={handleGetStarted}
                          className="sm:hidden w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 border border-transparent hover:from-purple-700 hover:to-pink-700 transition-all text-sm font-medium shadow-lg shadow-purple-500/25"
                        >
                          <Rocket className="w-4 h-4 text-white" />
                          {user ? 'Go to Dashboard' : 'Try ChatVerse Now'}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {activeTab === 'data' && (
                <div className="p-[2px] rounded-2xl bg-gradient-to-r from-blue-900/40 via-cyan-800/30 to-teal-800/30 shadow-[0_0_60px_-12px_rgba(6,182,212,0.25)]">

                  <section className="mx-auto max-w-6xl w-full px-4 sm:px-6 mt-16 sm:mt-24">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
                      <div className="order-2 lg:order-1">
                        <div className="p-[2px] rounded-2xl bg-gradient-to-r from-blue-900/40 via-cyan-800/30 to-teal-800/30 shadow-[0_0_60px_-12px_rgba(6,182,212,0.25)]">
                          <div
                            className="rounded-2xl backdrop-blur-sm border border-gray-800 p-4 sm:p-6"
                            style={{
                              backgroundColor: '#0a0a0a',
                              backgroundImage: `
                          radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0),
                          radial-gradient(circle at 3px 3px, rgba(255,255,255,0.08) 1px, transparent 0)
                        `,
                              backgroundSize: '20px 20px, 40px 40px',
                            }}
                          >
                            <div className="flex items-center gap-3 mb-6">
                              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-600 to-blue-700 flex items-center justify-center">
                                <BarChart3 className="w-4 h-4 text-white" />
                              </div>
                              <h3 className="text-lg font-semibold text-white" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                                Automation Builder
                              </h3>
                            </div>
                            <div className="space-y-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                                  Target Platform
                                </label>
                                <div className="relative">
                                  <select className="w-full px-3 py-2 bg-black/70 border border-gray-700 rounded-lg text-white text-sm focus:border-cyan-500 focus:outline-none transition-colors">
                                    <option>Instagram</option>
                                    <option>Twitter</option>
                                    <option>LinkedIn</option>
                                    <option>Facebook</option>
                                  </select>
                                </div>
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                                  Content Template
                                </label>
                                <textarea
                                  className="w-full px-3 py-2 bg-black/70 border border-gray-700 rounded-lg text-white text-sm h-20 resize-none focus:border-cyan-500 focus:outline-none transition-colors"
                                  placeholder="Check out our latest product launch! 🚀 #innovation #tech"
                                  readOnly
                                />
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                                  AI Model
                                </label>
                                <div className="grid grid-cols-2 gap-2">
                                  <div className="p-3 bg-gradient-to-br from-purple-900/30 to-pink-900/30 border border-purple-700/50 rounded-lg cursor-pointer hover:border-purple-600 transition-colors">
                                    <div className="text-xs font-medium text-purple-300">GPT-4</div>
                                    <div className="text-[10px] text-gray-400">Creative & Engaging</div>
                                  </div>
                                  <div className="p-3 bg-black/70 border border-gray-700 rounded-lg cursor-pointer hover:border-gray-600 transition-colors">
                                    <div className="text-xs font-medium text-gray-300">Claude</div>
                                    <div className="text-[10px] text-gray-400">Professional Tone</div>
                                  </div>
                                </div>
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                                  Schedule
                                </label>
                                <div className="flex gap-2">
                                  <input
                                    type="time"
                                    className="flex-1 px-3 py-2 bg-black/70 border border-gray-700 rounded-lg text-white text-sm focus:border-cyan-500 focus:outline-none transition-colors"
                                    defaultValue="14:30"
                                  />
                                  <select className="flex-1 px-3 py-2 bg-black/70 border border-gray-700 rounded-lg text-white text-sm focus:border-cyan-500 focus:outline-none transition-colors">
                                    <option>Daily</option>
                                    <option>Weekly</option>
                                    <option>Monthly</option>
                                  </select>
                                </div>
                              </div>
                              <button className="w-full mt-6 px-4 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 rounded-lg text-white font-medium text-sm hover:from-cyan-700 hover:to-blue-700 transition-all shadow-lg shadow-cyan-500/25">
                                <div className="flex items-center justify-center gap-2">
                                  <Zap className="w-4 h-4" />
                                  Deploy Automation
                                </div>
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="order-1 lg:order-2">
                        <div className="text-center mb-6">
                          <h3 className="text-lg font-semibold text-white mb-2" style={{ fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif' }}>
                            Live Preview
                          </h3>
                          <p className="text-sm text-gray-400" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                            See how your automation looks across devices
                          </p>
                        </div>
                        <div className="flex flex-col sm:flex-row gap-6 justify-center items-start">
                          <div className="flex-1 max-w-[200px] mx-auto sm:mx-0">
                            <div className="relative">
                              <div className="w-full h-[320px] bg-gradient-to-b from-gray-900 to-black rounded-[24px] border-4 border-gray-700 p-3 shadow-2xl">
                                <div className="w-full h-full bg-black rounded-[16px] overflow-hidden relative">
                                  <div className="flex justify-between items-center px-3 py-1 bg-gray-900">
                                    <div className="text-[8px] text-white">9:41</div>
                                    <div className="flex gap-1">
                                      <div className="w-3 h-2 bg-white rounded-sm opacity-60"></div>
                                      <div className="w-1 h-2 bg-white rounded-sm"></div>
                                    </div>
                                  </div>
                                  <div className="p-3 space-y-3">
                                    <div className="flex items-center gap-2">
                                      <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>
                                      <div className="text-[10px] text-white font-medium">your_brand</div>
                                    </div>
                                    <div className="w-full h-24 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                                      <Rocket className="w-6 h-6 text-white" />
                                    </div>
                                    <div className="text-[8px] text-gray-300 leading-tight">
                                      Check out our latest product launch! 🚀 #innovation #tech
                                    </div>
                                  </div>
                                </div>
                              </div>
                              <div className="text-center mt-2">
                                <div className="text-xs text-gray-400" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>Mobile View</div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="mt-6 grid grid-cols-3 gap-3">
                          <div className="text-center p-3 bg-black/30 rounded-lg border border-gray-800">
                            <div className="w-2 h-2 bg-green-400 rounded-full mx-auto mb-1 animate-pulse"></div>
                            <div className="text-[10px] text-gray-400">Connected</div>
                          </div>
                          <div className="text-center p-3 bg-black/30 rounded-lg border border-gray-800">
                            <div className="w-2 h-2 bg-blue-400 rounded-full mx-auto mb-1"></div>
                            <div className="text-[10px] text-gray-400">Scheduled</div>
                          </div>
                          <div className="text-center p-3 bg-black/30 rounded-lg border border-gray-800">
                            <div className="w-2 h-2 bg-purple-400 rounded-full mx-auto mb-1"></div>
                            <div className="text-[10px] text-gray-400">AI Ready</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </section>
                </div>
              )}
              <p className="mt-4 sm:mt-6 text-xs sm:text-sm text-gray-500 text-center px-4 sm:px-0" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                {activeTab === 'query'
                  ? 'Examples rotate to demonstrate what ChatVerse can do — try your own on the next step'
                  : 'Configure your automation with custom settings and see the preview in real-time'
                }
              </p>
            </section>
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
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mt-12 sm:mt-20 px-4 sm:px-0">
              <div className="group p-6 bg-gradient-to-br from-white/8 to-white/4 backdrop-blur-sm rounded-2xl border border-white/20 hover:border-violet-500/40 transition-all duration-500 hover:shadow-2xl hover:shadow-violet-500/10 hover:transform hover:scale-105">
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

              <div className="group p-6 bg-gradient-to-br from-white/8 to-white/4 backdrop-blur-sm rounded-2xl border border-white/20 hover:border-blue-500/40 transition-all duration-500 hover:shadow-2xl hover:shadow-blue-500/10 hover:transform hover:scale-105">
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

              <div className="group p-6 bg-gradient-to-br from-white/8 to-white/4 backdrop-blur-sm rounded-2xl border border-white/20 hover:border-emerald-500/40 transition-all duration-500 hover:shadow-2xl hover:shadow-emerald-500/10 hover:transform hover:scale-105">
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

              <div className="group p-6 bg-gradient-to-br from-white/8 to-white/4 backdrop-blur-sm rounded-2xl border border-white/20 hover:border-orange-500/40 transition-all duration-500 hover:shadow-2xl hover:shadow-orange-500/10 hover:transform hover:scale-105">
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
            <div className="mt-24 pt-16 border-t border-white/10">
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
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
                <div className="p-8 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-3xl border border-white/20 hover:border-purple-500/40 transition-all duration-500 group">
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
                <div className="p-8 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-3xl border border-white/20 hover:border-blue-500/40 transition-all duration-500 group">
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
                <div className="p-8 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-3xl border border-white/20 hover:border-emerald-500/40 transition-all duration-500 group">
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

            <div id="platform" className="mt-32">
              <div className="text-center mb-12">
                <h2 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent mb-4 tracking-tight game-font">
                  CONNECT ALL YOUR PLATFORMS
                </h2>
                <p className="text-lg bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent max-w-2xl mx-auto font-medium lego-font">
                  Seamlessly integrate with all major social media and communication platforms from one unified dashboard so you don't have to jump from one to another.
                </p>
              </div>

              <PlatformLogos />

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-16">
                <div className="text-center p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:bg-white/10 transition-all duration-300 group edge-holder glow-blue">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center mx-auto mb-4 transition-transform duration-300">
                    <Zap className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-bold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent mb-2 tracking-wide game-font">
                    ONE-CLICK SETUP
                  </h3>
                  <p className="text-sm bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent font-medium lego-font">
                    Connect all your accounts in seconds with our streamlined OAuth integration
                  </p>
                </div>

                <div className="text-center p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:bg-white/10 transition-all duration-300 group edge-holder glow-emerald">
                  <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center mx-auto mb-4 transition-transform duration-300">
                    <Shield className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-bold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent mb-2 tracking-wide game-font">
                    SECURE & PRIVATE
                  </h3>
                  <p className="text-sm bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent font-medium lego-font">
                    Enterprise-grade security with end-to-end encryption for all your data
                  </p>
                </div>

                <div className="text-center p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:bg-white/10 transition-all duration-300 group md:col-span-2 lg:col-span-1 edge-holder glow-cyan">
                  <div className="w-12 h-12 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg flex items-center justify-center mx-auto mb-4 transition-transform duration-300">
                    <BarChart3 className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-bold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent mb-2 tracking-wide game-font">
                    REAL-TIME SYNC
                  </h3>
                  <p className="text-sm bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent font-medium lego-font">
                    Instant synchronization across all platforms with live updates and notifications
                  </p>
                </div>
              </div>
            </div>

            <AutomationExamples />
          </div>
        </div>

        <div className="absolute top-[10%] left-[10%] w-3 h-3 bg-purple-500/50 rounded-full animate-float-medium hidden lg:block"></div>
        <div className="absolute top-[25%] right-[15%] w-4 h-4 bg-pink-500/50 rounded-full animate-float-slow hidden lg:block"></div>
        <div className="absolute bottom-[20%] left-[20%] w-2 h-2 bg-purple-300/60 rounded-full animate-float-fast hidden lg:block"></div>
        <div className="absolute bottom-[10%] right-[10%] w-3 h-3 bg-pink-300/60 rounded-full animate-float-medium hidden lg:block"></div>
      </main>

      <footer className="relative z-10 border-t border-white/10 bg-black/50 backdrop-blur-lg mt-24">
        <div className="max-w-6xl mx-auto px-6 py-12 text-gray-400">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center border border-white/10">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <span className="text-2xl font-bold text-white tracking-wide">Chat-Verse</span>
              </div>
              <p className="text-sm">Intelligent social media automation to connect, automate, and engage across all platforms.</p>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="#" className="hover:text-white transition-colors duration-200">
                    Documentation
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors duration-200">
                    Pricing
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors duration-200">
                    Help Center
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors duration-200">
                    Blog
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="/privacy" className="hover:text-white transition-colors duration-200" target="_blank">
                    Privacy Policy
                  </a>
                </li>
                <li>
                  <a href="/terms" className="hover:text-white transition-colors duration-200" target="_blank">
                    Terms & Conditions
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors duration-200">
                    Disclaimer
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div className="mt-12 flex flex-col md:flex-row items-center justify-between border-t border-white/10 pt-8">
            <div className="text-sm">&copy; {new Date().getFullYear()} ChatVerse. All rights reserved.</div>
            <div className="flex items-center space-x-4 mt-6 md:mt-0">
              <a href="#" className="w-8 h-8 rounded-full bg-white/5 backdrop-blur-sm flex items-center justify-center hover:bg-white/10 transition-all duration-300">
                <Instagram className="w-4 h-4 text-gray-400 hover:text-white" />
              </a>
              <a href="#" className="w-8 h-8 rounded-full bg-white/5 backdrop-blur-sm flex items-center justify-center hover:bg-white/10 transition-all duration-300">
                <Facebook className="w-4 h-4 text-gray-400 hover:text-white" />
              </a>
              <a href="#" className="w-8 h-8 rounded-full bg-white/5 backdrop-blur-sm flex items-center justify-center hover:bg-white/10 transition-all duration-300">
                <Twitter className="w-4 h-4 text-gray-400 hover:text-white" />
              </a>
              <a href="#" className="w-8 h-8 rounded-full bg-white/5 backdrop-blur-sm flex items-center justify-center hover:bg-white/10 transition-all duration-300">
                <Linkedin className="w-4 h-4 text-gray-400 hover:text-white" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;