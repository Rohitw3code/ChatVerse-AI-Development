import React, { useEffect } from 'react';
import { useNavigate, Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import { useAuthStore, useUserStore, useAppStore } from '../../stores';
import { LayoutDashboard, Bot, CreditCard, MessageSquare, ArrowLeft } from 'lucide-react';
import Sidebar from './components/Sidebar';
import DashboardContent from './components/DashboardContent';
import AutomationContent from './components/Automation/AutomationContent';
import AllAutomationsDashboard from './components/Automation/AllAutomationsDashboard';
import BillingContent from './components/BillingContent';
import LiveChatContent from './components/LiveChat/LiveChatContent';
import CreateAutomationForm from './components/Automation/CreateAutomationForm';
import AIConversationEngagement from './components/Automation/AIConversationEngagement';
import TriggerMessages from './components/Automation/TriggerMessages';
import ReplyOnComment from './components/Automation/ReplyOnComment';
import PrivateMessage from './components/Automation/PrivateMessage';
import PlatformSelectionPage from '../platform-selection/PlatformSelectionPage';
import { InstagramIcon } from '../../assets/Icons';


const InstagramDashboard: React.FC = () => {
  const { signOut, user } = useAuthStore();
  const { selectedPlatformAccount, fetchConnectedAccounts } = useUserStore();
  const {
    activeTab,
    setActiveTab,
    sidebarCollapsed,
    setSidebarCollapsed,
    isMobile,
    setIsMobile,
    showMobileNav,
    setShowMobileNav,
    addNotification
  } = useAppStore();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
    { id: 'automation', label: 'Automation', icon: <Bot className="w-5 h-5" /> },
    { id: 'billing', label: 'Billing', icon: <CreditCard className="w-5 h-5" /> },
    { id: 'livechat', label: 'Live Chat', icon: <MessageSquare className="w-5 h-5" /> },
  ];

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const connected = urlParams.get('connected');

    if (connected === 'true') {
      addNotification({
        type: 'success',
        message: 'Instagram connected successfully! Your account is now ready for automation.'
      });
      window.history.replaceState({}, document.title, window.location.pathname);
      if (user?.id) {
        fetchConnectedAccounts(user.id);
      }
    }
  }, [addNotification, user?.id, fetchConnectedAccounts]);

  useEffect(() => {
    const path = location.pathname;
    if (path.includes('/automation') || path.includes('/create-automation')) {
      setActiveTab('automation');
    } else if (path.includes('/billing')) {
      setActiveTab('billing');
    } else if (path.includes('/livechat')) {
      setActiveTab('livechat');
    } else if (path === '/instagram' || path === '/instagram/') {
      setActiveTab('dashboard');
    }
  }, [location.pathname, setActiveTab]);

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 1024;
      setIsMobile(mobile);
      if (mobile) {
        setSidebarCollapsed(true);
        setShowMobileNav(false);
      } else {
        setSidebarCollapsed(false);
        setShowMobileNav(false);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [setIsMobile, setSidebarCollapsed, setShowMobileNav]);

  const handleLogout = async () => {
    try {
      await signOut();
      navigate('/');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  const toggleMobileNav = () => {
    setShowMobileNav(!showMobileNav);
  };

  const handleNavigateToTab = (tabId: string) => {
    setActiveTab(tabId);
    switch (tabId) {
      case 'dashboard':
        navigate('/instagram');
        break;
      case 'automation':
        navigate('/instagram/automation');
        break;
      case 'billing':
        navigate('/instagram/billing');
        break;
      case 'livechat':
        navigate('/instagram/livechat');
        break;
      default:
        navigate('/instagram');
    }
  };

  const handleCreateAutomationBack = () => {
    navigate('/instagram/create-automation');
  };

  const handleSelectAutomationType = (typeId: string) => {
    const routeMap: { [key: string]: string } = {
      'ai-conversation': '/instagram/create-automation/ai-conversation',
      'trigger-messages': '/instagram/create-automation/trigger-messages',
      'reply-comment': '/instagram/create-automation/reply-comment',
      'private-message': '/instagram/create-automation/private-message'
    };

    const route = routeMap[typeId];
    if (route) {
      navigate(route);
      setActiveTab('automation');
    } else {
      console.warn(`No route found for automation type: ${typeId}`);
    }
  };

  return (
    <div className="min-h-screen bg-[#000000] text-white">
      {!isMobile && (
        <Sidebar
          collapsed={sidebarCollapsed}
          setCollapsed={setSidebarCollapsed}
          platformAccount={selectedPlatformAccount || undefined}
          onLogout={handleLogout}
        />
      )}

      {isMobile && (
        <div className="fixed top-0 left-0 right-0 h-14 bg-[#0a0a0a] border-b border-[#262626] z-50 lg:hidden">
          <div className="flex items-center justify-between h-full px-4">
            <button
              onClick={toggleMobileNav}
              className="p-2 rounded-lg hover:bg-[#1a1a1a] transition-all duration-200 group"
            >
              <div className="flex flex-col gap-1">
                <div className={`w-5 h-0.5 bg-white transition-all duration-300 ${showMobileNav ? 'rotate-45 translate-y-1.5' : ''
                  }`}></div>
                <div className={`w-5 h-0.5 bg-white transition-all duration-300 ${showMobileNav ? 'opacity-0' : ''
                  }`}></div>
                <div className={`w-5 h-0.5 bg-white transition-all duration-300 ${showMobileNav ? '-rotate-45 -translate-y-1.5' : ''
                  }`}></div>
              </div>
            </button>

            <div className="flex items-center gap-2">
              <div className="w-7 h-7 bg-gradient-to-r from-[#833ab4] via-[#fd1d1d] to-[#fcb045] rounded-lg flex items-center justify-center p-1">
                <InstagramIcon />
              </div>
              <span className="text-white font-semibold text-base">Instagram</span>
            </div>

            <div className="flex items-center gap-2">
              {selectedPlatformAccount && (
                <div className="flex items-center gap-2">
                  <img
                    src={'https://images.pexels.com/photos/1040880/pexels-photo-1040880.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=2'}
                    alt="Profile"
                    className="w-7 h-7 rounded-full object-cover ring-2 ring-[#262626]"
                  />
                  <span className="text-white text-sm font-medium hidden sm:block">
                    @{selectedPlatformAccount.platform_username}
                  </span>
                </div>
              )}
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg hover:bg-[#1a1a1a] transition-colors duration-200 text-red-400 hover:text-red-300"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      <div className={`transition-all duration-300 ${isMobile
          ? 'pt-14'
          : sidebarCollapsed
            ? 'ml-16'
            : 'ml-64'
        }`}>
        {isMobile && showMobileNav && (
          <div
            className="fixed inset-0 bg-black/80 z-40 lg:hidden"
            onClick={() => setShowMobileNav(false)}
          />
        )}
        {isMobile && showMobileNav && (
          <div className="fixed top-14 left-0 h-full w-72 bg-[#0a0a0a] border-r border-[#262626] z-50 lg:hidden overflow-y-auto">
            <div className="p-4 border-b border-[#262626]">
              <div className="flex items-center justify-between">
                <h2 className="text-white font-semibold text-lg">Menu</h2>
                <button
                  onClick={() => setShowMobileNav(false)}
                  className="p-2 rounded-lg hover:bg-[#1a1a1a] transition-colors duration-200"
                >
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <nav className="p-4 space-y-2">
              {menuItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    handleNavigateToTab(item.id);
                    setShowMobileNav(false);
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${activeTab === item.id
                      ? 'bg-[#1a1a1a] text-white border border-[#262626]'
                      : 'text-[#8e8e8e] hover:text-white hover:bg-[#1a1a1a]'
                    }`}
                >
                  <span className="text-xl">{item.icon}</span>
                  <span className="font-medium">{item.label}</span>
                </button>
              ))}
            </nav>
          </div>
        )}

        <div className="p-4 sm:p-6 lg:p-8">
            <Link
                to="/platforms"
                className="group mb-6 inline-flex items-center gap-2 px-3 py-2 bg-white/5 backdrop-blur-sm rounded-lg border border-white/10 hover:border-white/20 transition-all duration-300"
            >
                <ArrowLeft className="w-4 h-4 text-gray-300 group-hover:text-white transition-colors" />
                <span className="font-medium text-gray-300 group-hover:text-white transition-colors text-sm">Back to Platforms</span>
            </Link>
          <Routes>
            <Route path="/" element={<DashboardContent platform_user_id={selectedPlatformAccount?.platform_user_id ?? ''} />} />
            <Route path="/automation" element={
              selectedPlatformAccount ?
                <AllAutomationsDashboard platformAccount={{
                  id: selectedPlatformAccount.id,
                  platform_user_id: selectedPlatformAccount.platform_user_id,
                  username: selectedPlatformAccount.platform_username,
                  profile_picture_url: undefined
                }} 
                onBack={handleCreateAutomationBack}
                onSelectAutomationType={handleSelectAutomationType}                
                /> :
                <PlatformSelectionPage />
            } />
            <Route path="/create-automation/*" element={
              selectedPlatformAccount ? (
                <Routes>
                  <Route index element={
                    <CreateAutomationForm
                      platformAccount={{
                        id: selectedPlatformAccount.id,
                        platform_user_id: selectedPlatformAccount.platform_user_id,
                        username: selectedPlatformAccount.platform_username,
                        profile_picture_url: undefined
                      }}
                      onBack={handleCreateAutomationBack}
                      onSelectAutomationType={handleSelectAutomationType}
                    />
                  } />
                  <Route path="ai-conversation" element={
                    <AIConversationEngagement
                      platformAccount={selectedPlatformAccount}
                      onBack={handleCreateAutomationBack}
                    />
                  } />
                  <Route path="trigger-messages" element={
                    <TriggerMessages
                      platformAccount={selectedPlatformAccount}
                      onBack={handleCreateAutomationBack}
                    />
                  } />
                  <Route path="reply-comment" element={
                    <ReplyOnComment
                      platformAccount={selectedPlatformAccount}
                      onBack={handleCreateAutomationBack}
                    />
                  } />
                  <Route path="private-message" element={
                    <PrivateMessage
                      platformAccount={selectedPlatformAccount}
                      onBack={handleCreateAutomationBack}
                    />
                  } />
                </Routes>
              ) : (
                <PlatformSelectionPage />
              )
            } />
            <Route path="/billing" element={<BillingContent />} />
            <Route path="/livechat" element={
              selectedPlatformAccount ?
                <LiveChatContent platformAccount={selectedPlatformAccount} /> :
                <PlatformSelectionPage />
            } />
            <Route path="*" element={<Navigate to="/instagram" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  );
};

export default InstagramDashboard;