import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, CheckCircle, XCircle, Shield, Settings, User, Menu, X } from 'lucide-react';
import { useAuthStore, useUserStore } from '../../stores';
import { PlatformAccount } from '../../types/types';
import { GmailIcon } from '../../assets/GmailIcon';
import { CreditDisplay } from '../../components/common/CreditDisplay';
import { UserApiService } from '../../api/user_api';

// Permission mapping from backend scopes to user-friendly descriptions
const PERMISSION_MAP: Record<string, { 
  name: string; 
  description: string; 
  icon: React.ElementType;
  color: string;
}> = {
  'https://www.googleapis.com/auth/gmail.readonly': {
    name: 'View your email messages and settings',
    description: 'Allows ChatVerse to read your emails, view your settings, filters, and labels',
    icon: Mail,
    color: 'text-blue-400'
  },
  'https://www.googleapis.com/auth/gmail.send': {
    name: 'Send email on your behalf', 
    description: 'Allows ChatVerse to send emails that appear to come from your email address',
    icon: Settings,
    color: 'text-green-400'
  }
};

const GmailDashboard: React.FC = () => {
  const { user, signOut } = useAuthStore();
  const { connectedAccounts, isLoading, fetchConnectedAccounts } = useUserStore();
  const [credits, setCredits] = useState<number | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  // Get Gmail account from connected accounts
  const gmailAccount = connectedAccounts.find(
    (account: PlatformAccount) => account.platform === 'gmail'
  );

  // Fetch connected accounts when component mounts
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

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-gray-800/40 border-t-gray-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!gmailAccount) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center space-y-4">
          <XCircle className="w-16 h-16 text-red-400 mx-auto" />
          <h2 className="text-2xl font-bold">Gmail Account Not Found</h2>
          <p className="text-gray-400">Please connect your Gmail account first.</p>
          <Link
            to="/platforms"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Platforms
          </Link>
        </div>
      </div>
    );
  }

  const grantedPermissions = gmailAccount.scopes || [];
  const allPossiblePermissions = Object.keys(PERMISSION_MAP);

  return (
    <div className="min-h-screen bg-black text-white" style={{ backgroundColor: '#0a0a0a' }}>
      {/* Background */}
      <div
        className="absolute inset-0"
        style={{
          backgroundColor: '#0a0a0a',
          backgroundImage: `
            radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0),
            radial-gradient(circle at 3px 3px, rgba(255,255,255,0.08) 1px, transparent 0)
          `,
          backgroundSize: '20px 20px, 40px 40px',
        }}
      ></div>

      <div className="relative z-10">
        {/* Top Navigation */}
        <nav className="border-b border-gray-800/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6">
            <div className="flex items-center justify-between h-16">
              {/* Left Section */}
              <div className="flex items-center space-x-4 md:space-x-6">
                <Link to="/platforms" className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors">
                  <ArrowLeft className="w-4 h-4" />
                  <span className="text-sm font-medium">Back to Platforms</span>
                </Link>
                <div className="hidden sm:block w-px h-5 bg-gray-700"></div>
                <div className="flex items-center space-x-3">
                  <GmailIcon className="w-8 h-8" />
                  <span className="text-lg font-bold text-white">Gmail Dashboard</span>
                </div>
              </div>

              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center space-x-3">
                <CreditDisplay
                  credits={credits || 0}
                  onAddCredits={handleAddCredits}
                  variant="compact"
                  showActions={true}
                />
                
                <div className="flex items-center space-x-2 px-3 py-1.5 bg-gray-800/50 rounded-md">
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
            
            {/* Mobile Menu Dropdown */}
            {isMobileMenuOpen && (
              <div className="md:hidden border-t border-gray-800/50 bg-black">
                <div className="flex flex-col py-4 space-y-2">
                  <div className="flex items-center space-x-3 px-4 py-2.5 text-sm text-gray-400">
                    <User className="w-4 h-4" />
                    <span className="truncate">{user?.email}</span>
                  </div>
                  
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

        <div className="max-w-4xl mx-auto p-6 space-y-8">
          {/* Account Information */}
          <div className="bg-gray-900/50 rounded-xl border border-gray-800/50 p-6">
            <div className="flex items-center space-x-4 mb-6">
              <div className="relative">
                <img 
                  src={`https://placehold.co/64x64/1a1a1a/ffffff?text=${gmailAccount.platform_username.charAt(0).toUpperCase()}`}
                  alt="Gmail Profile"
                  className="w-16 h-16 rounded-full border-2 border-gray-700"
                />
                <div className="absolute -bottom-1 -right-1 bg-gray-800 rounded-full p-1 border-2 border-gray-700">
                  <GmailIcon className="w-6 h-6" />
                </div>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{gmailAccount.platform_username}</h2>
                <p className="text-gray-400">Connected on {new Date(gmailAccount.connected_at).toLocaleDateString()}</p>
              </div>
              <div className="ml-auto">
                <div className="flex items-center gap-2 text-green-400 bg-green-900/30 px-3 py-1.5 rounded-full border border-green-800/40">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-sm font-medium">Connected</span>
                </div>
              </div>
            </div>
          </div>

          {/* Permissions Section */}
          <div className="bg-gray-900/50 rounded-xl border border-gray-800/50 p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Shield className="w-6 h-6 text-blue-400" />
              <h3 className="text-xl font-bold text-white">Gmail Permissions</h3>
            </div>
            
            <div className="space-y-4">
              <p className="text-gray-400 text-sm mb-6">
                These are the permissions you granted to ChatVerse when connecting your Gmail account:
              </p>

              {/* Granted Permissions */}
              <div className="space-y-3">
                {grantedPermissions.length > 0 ? (
                  grantedPermissions.map((scope) => {
                    const permission = PERMISSION_MAP[scope];
                    if (!permission) return null;

                    const IconComponent = permission.icon;
                    return (
                      <div
                        key={scope}
                        className="flex items-start space-x-4 p-4 bg-green-900/20 border border-green-800/30 rounded-lg"
                      >
                        <div className="flex-shrink-0 mt-0.5">
                          <CheckCircle className="w-5 h-5 text-green-400" />
                        </div>
                        <div className="flex-grow">
                          <div className="flex items-center space-x-2 mb-2">
                            <IconComponent className={`w-4 h-4 ${permission.color}`} />
                            <h4 className="font-semibold text-white">{permission.name}</h4>
                          </div>
                          <p className="text-sm text-gray-400">{permission.description}</p>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-center py-8">
                    <XCircle className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-400">No permissions data available</p>
                  </div>
                )}
              </div>

              {/* Not Granted Permissions */}
              {allPossiblePermissions.some(scope => !grantedPermissions.includes(scope)) && (
                <div className="mt-8">
                  <h4 className="text-lg font-semibold text-white mb-4">Available Permissions (Not Granted)</h4>
                  <div className="space-y-3">
                    {allPossiblePermissions
                      .filter(scope => !grantedPermissions.includes(scope))
                      .map((scope) => {
                        const permission = PERMISSION_MAP[scope];
                        if (!permission) return null;

                        const IconComponent = permission.icon;
                        return (
                          <div
                            key={scope}
                            className="flex items-start space-x-4 p-4 bg-gray-800/30 border border-gray-700/50 rounded-lg opacity-60"
                          >
                            <div className="flex-shrink-0 mt-0.5">
                              <XCircle className="w-5 h-5 text-gray-500" />
                            </div>
                            <div className="flex-grow">
                              <div className="flex items-center space-x-2 mb-2">
                                <IconComponent className="w-4 h-4 text-gray-500" />
                                <h4 className="font-semibold text-gray-300">{permission.name}</h4>
                              </div>
                              <p className="text-sm text-gray-500">{permission.description}</p>
                            </div>
                          </div>
                        );
                      })}
                  </div>
                </div>
              )}
            </div>

            {/* Security Note */}
            <div className="mt-6 p-4 bg-blue-900/20 border border-blue-800/30 rounded-lg">
              <div className="flex items-start space-x-3">
                <Shield className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-blue-400 mb-1">Security Note</h4>
                  <p className="text-sm text-gray-300">
                    You can always review and modify these permissions in your{' '}
                    <a 
                      href="https://myaccount.google.com/permissions" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300 underline"
                    >
                      Google Account settings
                    </a>
                    . ChatVerse only uses these permissions for the features you've authorized.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-gray-900/50 rounded-xl border border-gray-800/50 p-6">
            <h3 className="text-xl font-bold text-white mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                className="p-4 bg-blue-600/20 border border-blue-500/30 rounded-lg hover:bg-blue-600/30 transition-colors"
                onClick={() => {
                  // Navigate to chat or automation setup
                  const newChatId = `chat_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
                  navigate(`/chat/${newChatId}?provider_id=${gmailAccount.provider_id}`);
                }}
              >
                <Mail className="w-6 h-6 text-blue-400 mb-2" />
                <h4 className="font-semibold text-white mb-1">Start AI Chat</h4>
                <p className="text-sm text-gray-400">Create intelligent email automations</p>
              </button>
              
              <button
                className="p-4 bg-gray-700/20 border border-gray-600/30 rounded-lg hover:bg-gray-700/30 transition-colors"
                onClick={() => window.open('https://myaccount.google.com/permissions', '_blank')}
              >
                <Settings className="w-6 h-6 text-gray-400 mb-2" />
                <h4 className="font-semibold text-white mb-1">Manage Permissions</h4>
                <p className="text-sm text-gray-400">Review access in Google Account</p>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GmailDashboard;