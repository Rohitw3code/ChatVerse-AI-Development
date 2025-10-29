import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Zap, 
  Settings, 
  CreditCard, 
  MessageCircle, 
  ChevronLeft,
  ChevronRight,
  LogOut
} from 'lucide-react';
import { useAppStore } from '../../../stores';
import { PlatformAccount } from '../../../types/types';

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  platformAccount: PlatformAccount | undefined;
  onLogout: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  collapsed, 
  setCollapsed,
  platformAccount,
  onLogout
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { setActiveTab } = useAppStore();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/instagram' },
    { id: 'automation', label: 'Automation', icon: Zap, path: '/instagram/automation' },
    { id: 'livechat', label: 'Live Chat', icon: MessageCircle, path: '/instagram/livechat' },
    { id: 'billing', label: 'Billing', icon: CreditCard, path: '/instagram/billing' },
    { id: 'settings', label: 'Settings', icon: Settings, path: '/instagram/settings' },
  ];

  const getCurrentTab = () => {
    const path = location.pathname;
    
    if (path.includes('/automation') || path.includes('/create-automation')) {
      return 'automation';
    }

    if (path === '/instagram' || path === '/instagram/') {
        return 'dashboard';
    }
    
    const menuItem = menuItems.find(item => path.startsWith(item.path) && item.path !== '/instagram');
    return menuItem ? menuItem.id : 'dashboard';
  };

  const activeTab = getCurrentTab();

  const handleNavigation = (item: typeof menuItems[0]) => {
    navigate(item.path);
    setActiveTab(item.id);
  };

  const instagramUser = {
    username: platformAccount?.platform_username || 'Unknown',
    profileImage: 'https://images.pexels.com/photos/1040880/pexels-photo-1040880.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=2',
    fullName: platformAccount?.platform_username || 'Unknown User'
  };

  return (
    <>
      <div className={`hidden lg:flex flex-col fixed left-0 top-0 h-full bg-[#0a0a0a] border-r border-[#262626] transition-all duration-300 z-40 ${
        collapsed ? 'w-16' : 'w-64'
      }`}>
        
        <div className="p-4 border-b border-[#262626]">
          <div className={`flex items-center gap-3 ${collapsed ? 'justify-center' : ''}`}>
            <div className="relative flex-shrink-0">
              <img
                src={instagramUser.profileImage}
                alt="Profile"
                className="w-10 h-10 rounded-full object-cover ring-2 ring-[#262626]"
              />
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-[#0a0a0a]"></div>
            </div>
            
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <h3 className="text-white font-semibold text-sm truncate">
                  {instagramUser.fullName}
                </h3>
                <p className="text-[#8e8e8e] text-xs truncate">
                  @{instagramUser.username}
                </p>
              </div>
            )}
            
            {!collapsed && (
                <button
                onClick={() => setCollapsed(!collapsed)}
                className="p-1.5 rounded-lg hover:bg-[#1a1a1a] transition-colors duration-200 text-[#8e8e8e] hover:text-white"
                >
                    <ChevronLeft className="w-4 h-4" />
                </button>
            )}
          </div>
        </div>

        <nav className="flex-grow p-2 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => handleNavigation(item)}
                title={collapsed ? item.label : ''}
                className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200 group ${
                    collapsed ? 'justify-center' : ''
                } ${
                  isActive
                    ? 'bg-[#1a1a1a] text-white border border-[#262626]'
                    : 'text-[#8e8e8e] hover:text-white hover:bg-[#1a1a1a]'
                }`}
              >
                <Icon className={`w-5 h-5 flex-shrink-0 ${
                  isActive ? 'text-white' : 'text-[#8e8e8e] group-hover:text-white'
                }`} />
                
                {!collapsed && (
                  <span className="font-medium text-sm truncate">
                    {item.label}
                  </span>
                )}
                
                {isActive && !collapsed && (
                  <div className="w-1.5 h-1.5 bg-white rounded-full ml-auto flex-shrink-0"></div>
                )}
              </button>
            );
          })}
        </nav>

        <div className="p-2">
          <button
            onClick={onLogout}
            title={collapsed ? 'Logout' : ''}
            className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200 group text-red-400 hover:text-red-300 hover:bg-red-500/10 ${
                collapsed ? 'justify-center' : ''
            }`}
          >
            <LogOut className="w-5 h-5 flex-shrink-0" />
            {!collapsed && (
              <span className="font-medium text-sm truncate">
                Logout
              </span>
            )}
          </button>
        </div>

        {!collapsed && (
          <div className="p-4">
             <div className="p-1 bg-gradient-to-r from-[#833ab4] via-[#fd1d1d] to-[#fcb045] rounded-lg">
                <div className="bg-[#1a1a1a] rounded-md p-3 text-center">
                    <div className="flex items-center justify-center gap-2 mb-1">
                        <svg viewBox="0 0 24 24" className="w-5 h-5 text-white" fill="currentColor">
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                        </svg>
                        <span className="text-white font-semibold text-sm">Instagram</span>
                    </div>
                    <p className="text-[#8e8e8e] text-xs">Connected & Active</p>
                </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Sidebar;