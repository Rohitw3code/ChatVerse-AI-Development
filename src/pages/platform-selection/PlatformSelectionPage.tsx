import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Menu, X } from 'lucide-react';
import { API_CONFIG } from '../../config/api';
import { PlatformAccount } from '../../types/types';
import { useAuthStore, useUserStore } from '../../stores';
import { InstagramIcon, YouTubeIcon, MeetIcon, TwitterIcon, SlackIcon, GitHubIcon, RedditIcon, SheetsIcon, DocsIcon } from '../../assets/Icons';
import { GmailIcon } from '../../assets/GmailIcon';

// Import the new components
import { AppCard } from './AppCard';
import { InstagramCard } from './InstagramCard';
import { CreditDisplay } from '../../components/common/CreditDisplay';
import { UserApiService } from '../../api/user_api';

// Dynamic Background CSS Animations from Landing Page
const injectDynamicBackgroundStyles = () => {
  const styleId = 'dynamic-background-styles';
  if (document.getElementById(styleId)) return;
  
  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    .mouse-pull-bg {
      transition: transform 0.3s ease-out, filter 0.3s ease-out;
      will-change: transform, filter;
    }
    
    .platform-glow {
      box-shadow: 
        inset 0 0 20px rgba(0,0,0,0.8),
        0 0 40px rgba(0,0,0,0.6),
        0 0 80px rgba(0,0,0,0.4);
    }
  `;
  document.head.appendChild(style);
};

const PlatformSelectionPage: React.FC = () => {
  const { user, signOut } = useAuthStore();
  const { connectedAccounts, isLoading: userLoading, setSelectedPlatformAccount, fetchConnectedAccounts } = useUserStore();
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null);
  const [credits, setCredits] = useState<number | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
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

  // Fetch connected accounts when component mounts or user changes
  useEffect(() => {
    if (user?.id) {
      fetchConnectedAccounts(user.id);
    }
  }, [user?.id, fetchConnectedAccounts]);

  // Fetch credits when user changes
  useEffect(() => {
    const fetchCredits = async () => {
      if (user?.id) {
        try {
          const response = await UserApiService.getUserCredit(user.id);
          if (response.success) {
            setCredits(response.data.current_credits);
          }
        } catch (error) {
          console.error("Failed to fetch user credits:", error);
          setCredits(0);
        }
      }
    };
    fetchCredits();
  }, [user?.id]);

  // Refetch connected accounts when returning from OAuth flow
  useEffect(() => {
    const handleFocus = () => {
      if (user?.id && document.visibilityState === 'visible') {
        fetchConnectedAccounts(user.id);
      }
    };

    const handleVisibilityChange = () => {
      if (user?.id && document.visibilityState === 'visible') {
        fetchConnectedAccounts(user.id);
      }
    };

    window.addEventListener('focus', handleFocus);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      window.removeEventListener('focus', handleFocus);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [user?.id, fetchConnectedAccounts]);
    
  // Data Definitions - Social Media Apps
  const socialMediaApps = [
    { 
      id: 'instagram', 
      name: 'Instagram', 
      description: 'AI Integration - Connect your account, let AI automate your social presence', 
      Icon: InstagramIcon, 
      gradient: 'from-pink-500 via-red-500 to-yellow-500', 
      enabled: true
    },
  ];

  // Productivity Tools
  const productivityApps = [
    { 
      id: 'gmail', 
      name: 'Gmail', 
      description: 'AI-powered email automation and management', 
      Icon: GmailIcon, 
      gradient: 'from-red-500 to-yellow-500', 
      enabled: true
    },
    { 
      id: 'youtube', 
      name: 'YouTube', 
      description: 'Manage channel and video performance', 
      Icon: YouTubeIcon, 
      gradient: 'from-red-500 to-red-700', 
      enabled: true
    },
    { 
      id: 'meet', 
      name: 'Google Meet', 
      description: 'Schedule and manage video meetings', 
      Icon: MeetIcon, 
      gradient: 'from-blue-500 to-green-500', 
      enabled: false
    },
    { 
      id: 'twitter', 
      name: 'Twitter', 
      description: 'Schedule tweets and manage engagement', 
      Icon: TwitterIcon, 
      gradient: 'from-blue-400 to-blue-600', 
      enabled: false
    },
    { 
      id: 'slack', 
      name: 'Slack', 
      description: 'Automate team communication workflows', 
      Icon: SlackIcon, 
      gradient: 'from-purple-500 to-pink-500', 
      enabled: false
    },
    { 
      id: 'github', 
      name: 'GitHub', 
      description: 'Automate repository and issue management', 
      Icon: GitHubIcon, 
      gradient: 'from-gray-700 to-gray-900', 
      enabled: false
    },
    { 
      id: 'reddit', 
      name: 'Reddit', 
      description: 'Automate posts and community engagement', 
      Icon: RedditIcon, 
      gradient: 'from-orange-500 to-red-600', 
      enabled: false
    },
    { 
      id: 'sheets', 
      name: 'Google Sheets', 
      description: 'Automate data collection and reporting', 
      Icon: SheetsIcon, 
      gradient: 'from-green-500 to-teal-500', 
      enabled: true
    },
    { 
      id: 'docs', 
      name: 'Google Docs', 
      description: 'Automate document creation and editing', 
      Icon: DocsIcon, 
      gradient: 'from-blue-500 to-blue-700', 
      enabled: true
    },
  ];

  // Get connected accounts for each app
  const getAppConnectedAccounts = (appId: string) => {
    // Map frontend app IDs to backend platform IDs
    const platformMapping: { [key: string]: string } = {
      'sheets': 'google_sheets',
      // Add other mappings if needed
    };
    
    const backendPlatformId = platformMapping[appId] || appId;
    return connectedAccounts.filter((acc: PlatformAccount) => acc.platform === backendPlatformId);
  };

  // Handlers
  const handlePlatformConnect = (platform_name: string) => {
    if (!user) return;
    setConnectingPlatform(platform_name);
    try {
      const returnUrl = window.location.href;
      let loginUrl = '';
      if (platform_name === 'instagram') loginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.INSTAGRAM.LOGIN(user.id, returnUrl)}`;
      if (platform_name === 'gmail') loginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.GMAIL.LOGIN(user.id, returnUrl)}`;
      if (platform_name === 'youtube') loginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.YOUTUBE.LOGIN(user.id, returnUrl)}`;
      if (platform_name === 'sheets') loginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.GOOGLE_SHEETS.LOGIN(user.id, returnUrl)}`;
  if (platform_name === 'youtube') loginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.YOUTUBE.LOGIN(user.id, returnUrl)}`;
  if (platform_name === 'docs') loginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.GDOC.LOGIN(user.id, returnUrl)}`;
      if (platform_name === 'x') {
        console.log("Connecting X/Twitter for user: " + user.id);
        setConnectingPlatform(null); // Placeholder
        return;
      }
      window.location.href = loginUrl;
    } catch (error) {
      console.error(`Failed to initiate ${platform_name} connection:`, error);
      setConnectingPlatform(null);
    }
  };
  
  const handleAccountClick = (account: PlatformAccount) => {
    setSelectedPlatformAccount(account);
    // Route Sheets directly to Chat instead of an unused dashboard
    if (account.platform === 'google_sheets') {
      const newChatId = `chat_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
      navigate(`/chat/${newChatId}?provider_id=${account.provider_id}`);
      return;
    }
    navigate(`/${account.platform}`);
  };

  const handleLogout = async () => {
    try {
      await signOut();
      navigate('/');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  const handleAddCredits = () => {
    navigate('/pricing');
  };

  const handleViewInstagramDashboard = (account: PlatformAccount) => {
    setSelectedPlatformAccount(account);
    navigate('/instagram');
  };



  // Inject Dynamic Background Styles
  useEffect(() => {
    injectDynamicBackgroundStyles();
  }, []);

  // Loading State
  if (userLoading) {
    return (
      <div className="min-h-screen text-white relative overflow-hidden flex items-center justify-center" style={{ backgroundColor: '#0a0a0a' }}>
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
            transform: `translate(${(mousePosition.x - (typeof window !== 'undefined' ? window.innerWidth : 0) / 2) * 0.02}px, ${(mousePosition.y - (typeof window !== 'undefined' ? window.innerHeight : 0) / 2) * 0.02}px)`,
            '--mouse-x': `${typeof window !== 'undefined' ? (mousePosition.x / window.innerWidth) * 100 : 50}%`,
            '--mouse-y': `${typeof window !== 'undefined' ? (mousePosition.y / window.innerHeight) * 100 : 50}%`,
          } as React.CSSProperties}
        ></div>
        <div className="relative z-10">
          <div className="w-12 h-12 border-4 border-gray-800/40 border-t-gray-600 rounded-full animate-spin platform-glow"></div>
        </div>
      </div>
    );
  }

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
          transform: `translate(${(mousePosition.x - (typeof window !== 'undefined' ? window.innerWidth : 0) / 2) * 0.02}px, ${(mousePosition.y - (typeof window !== 'undefined' ? window.innerHeight : 0) / 2) * 0.02}px)`,
          '--mouse-x': `${typeof window !== 'undefined' ? (mousePosition.x / window.innerWidth) * 100 : 50}%`,
          '--mouse-y': `${typeof window !== 'undefined' ? (mousePosition.y / window.innerHeight) * 100 : 50}%`,
        } as React.CSSProperties}
      ></div>
      
      {/* removed cursor-following white light overlay */}

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
          transform: `translate(${(mousePosition.x - (typeof window !== 'undefined' ? window.innerWidth : 0) / 2) * 0.01}px, ${(mousePosition.y - (typeof window !== 'undefined' ? window.innerHeight : 0) / 2) * 0.01}px)`,
          transition: 'transform 0.2s ease-out',
        }}
      ></div>

      <div 
        className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-gray-900/20"
        style={{
          transform: `translate(${(mousePosition.x - (typeof window !== 'undefined' ? window.innerWidth : 0) / 2) * 0.005}px, ${(mousePosition.y - (typeof window !== 'undefined' ? window.innerHeight : 0) / 2) * 0.005}px)`,
          transition: 'transform 0.4s ease-out',
        }}
      ></div>
      
      {/* removed upward pull white light overlay */}

      <div className="relative z-10 p-4 sm:p-6 lg:p-8 font-sans" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
        {/* Top Navigation Bar - YC Style */}
        <nav className="relative z-50 border-b border-gray-800/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6">
            <div className="flex items-center justify-between h-16">
              {/* Left Section - Back & Brand */}
              <div className="flex items-center space-x-4 md:space-x-6">
                <Link to="/" className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors">
                  <ArrowLeft className="w-4 h-4" />
                  <span className="text-sm font-medium">Back</span>
                </Link>
                <div className="hidden sm:block w-px h-5 bg-gray-700"></div>
                <span className="text-lg font-bold text-white">ChatVerse</span>
              </div>

              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center space-x-3">
                <CreditDisplay
                  credits={credits || 0}
                  onAddCredits={handleAddCredits}
                  variant="compact"
                  showActions={true}
                />
                
                <div className="flex items-center space-x-2 px-3 py-1.5 bg-gray-800/50 rounded-md hover:bg-gray-800 transition-colors">
                  <User className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-300 max-w-[140px] truncate">{user?.email}</span>
                </div>
                
                <button
                  onClick={handleLogout}
                  className="px-4 py-1.5 bg-gray-800/50 rounded-md hover:bg-gray-800 transition-colors text-gray-300 hover:text-white text-sm font-medium"
                >
                  Logout
                </button>
              </div>

              {/* Mobile Menu Button */}
              <button 
                className="md:hidden p-2 -mr-2 text-gray-400 hover:text-white transition-colors" 
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              >
                {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
            
            {/* Mobile Menu Dropdown - YC Style */}
            {isMobileMenuOpen && (
              <div className="md:hidden border-t border-gray-800/50 bg-black">
                <div className="flex flex-col py-4 space-y-2">
                  {/* User Info */}
                  <div className="flex items-center space-x-3 px-4 py-2.5 text-sm text-gray-400">
                    <User className="w-4 h-4" />
                    <span className="truncate">{user?.email}</span>
                  </div>
                  
                  {/* Credits */}
                  <div className="px-4 py-2.5 flex items-center justify-between border-t border-b border-gray-800/50">
                    <span className="text-sm text-gray-400">Credits: <span className="text-white font-medium">{credits || 0}</span></span>
                    <button
                      onClick={() => {
                        handleAddCredits();
                        setIsMobileMenuOpen(false);
                      }}
                      className="px-3 py-1 bg-orange-500/10 hover:bg-orange-500/20 rounded text-xs text-orange-400 font-medium transition-colors border border-orange-500/20"
                    >
                      Add Credits
                    </button>
                  </div>
                  
                  {/* Logout */}
                  <button
                    onClick={() => {
                      handleLogout();
                      setIsMobileMenuOpen(false);
                    }}
                    className="mx-4 px-4 py-2 bg-gray-800/50 hover:bg-gray-800 rounded-md text-sm text-gray-300 hover:text-white transition-colors text-center font-medium"
                  >
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </nav>
        <div className="max-w-5xl mx-auto w-full pt-6 md:pt-12 px-4 sm:px-6">
          {/* Hero Section - YC Style */}
          <div className="mb-8 md:mb-10">
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-orange-500/10 rounded-md border border-orange-500/20">
                <div className="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
                <span className="text-xs font-medium text-orange-400 uppercase tracking-wide">
                  AI-Powered Automation
                </span>
              </div>

              <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white leading-tight">
                Use AI to Automate Your Digital World
              </h1>

              <p className="text-base sm:text-lg text-gray-400 max-w-2xl leading-relaxed">
                Connect your productivity and social media tools, let AI handle the rest. Build intelligent automations that work seamlessly across all your platforms.
              </p>
            </div>
          </div>

          {/* Social Media Section */}
          <div className="mb-10">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">Social Media</h2>
              <p className="text-sm text-gray-400">Connect your social media platforms and automate your presence</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {socialMediaApps.map((app) => (
                <InstagramCard
                  key={app.id}
                  app={app}
                  connectedAccounts={getAppConnectedAccounts(app.id)}
                  onConnect={handlePlatformConnect}
                  onViewDashboard={handleViewInstagramDashboard}
                  isConnecting={connectingPlatform === app.id}
                />
              ))}
            </div>
          </div>

          {/* Productivity Tools Section */}
          <div className="mb-8 md:mb-12">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">Productivity Tools</h2>
              <p className="text-sm text-gray-400">Integrate productivity apps to streamline your workflow</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {productivityApps.map((app) => (
                <AppCard
                  key={app.id}
                  app={app}
                  connectedAccounts={getAppConnectedAccounts(app.id)}
                  onConnect={handlePlatformConnect}
                  onAccountClick={handleAccountClick}
                  isConnecting={connectingPlatform === app.id}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default PlatformSelectionPage;