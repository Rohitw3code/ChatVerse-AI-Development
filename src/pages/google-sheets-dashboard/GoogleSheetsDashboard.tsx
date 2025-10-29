import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Menu, X, FileSpreadsheet, Plus, ExternalLink, Calendar, TrendingUp } from 'lucide-react';
import { useAuthStore } from '../../stores';
import { API_CONFIG } from '../../config/api';
import { CreditDisplay } from '../../components/common/CreditDisplay';
import { UserApiService } from '../../api/user_api';
import { SheetsIcon } from '../../assets/Icons';

interface Spreadsheet {
  id: string;
  name: string;
  createdTime?: string;
  modifiedTime?: string;
  webViewLink?: string;
}

const GoogleSheetsDashboard: React.FC = () => {
  const { user, signOut } = useAuthStore();
  const [spreadsheets, setSpreadsheets] = useState<Spreadsheet[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [credits, setCredits] = useState<number | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  // Fetch user's spreadsheets
  useEffect(() => {
    const fetchSpreadsheets = async () => {
      if (!user?.id) return;
      
      try {
        setIsLoading(true);
        const response = await fetch(
          `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.GOOGLE_SHEETS.SPREADSHEETS(user.id)}`,
          {
            method: 'GET',
            headers: API_CONFIG.HEADERS,
          }
        );

        if (response.ok) {
          const data = await response.json();
          if (data.success && data.spreadsheets) {
            setSpreadsheets(data.spreadsheets);
          } else {
            console.warn('No spreadsheets found or user not authenticated');
            setSpreadsheets([]);
          }
        } else if (response.status === 401) {
          console.warn('User not authenticated with Google Sheets');
          setSpreadsheets([]);
        } else {
          console.error('Failed to fetch spreadsheets');
          setSpreadsheets([]);
        }
      } catch (error) {
        console.error('Error fetching spreadsheets:', error);
        setSpreadsheets([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSpreadsheets();
  }, [user?.id]);

  // Fetch user credits
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

  const handleConnectSheets = () => {
    if (!user?.id) return;
    const returnUrl = window.location.href;
    const loginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.GOOGLE_SHEETS.LOGIN(user.id, returnUrl)}`;
    window.location.href = loginUrl;
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getTimeAgo = (dateString?: string) => {
    if (!dateString) return 'Unknown';
    const now = new Date();
    const date = new Date(dateString);
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return formatDate(dateString);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen text-white relative overflow-hidden flex items-center justify-center" style={{ backgroundColor: '#0a0a0a' }}>
        <div className="relative z-10">
          <div className="w-12 h-12 border-4 border-gray-800/40 border-t-gray-600 rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-400">Loading your spreadsheets...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden" style={{ backgroundColor: '#0a0a0a' }}>
      {/* Background */}
      <div className="absolute inset-0" style={{
        backgroundColor: '#0a0a0a',
        backgroundImage: `
          radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0),
          radial-gradient(circle at 3px 3px, rgba(255,255,255,0.08) 1px, transparent 0)
        `,
        backgroundSize: '20px 20px, 40px 40px'
      }}></div>

      <div className="relative z-10 p-4 sm:p-6 lg:p-8 font-sans" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
        {/* Top Navigation Bar */}
        <nav className="relative z-50 border-b border-gray-800/50">
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
                  <SheetsIcon className="w-6 h-6 text-green-500" />
                  <span className="text-lg font-bold text-white">Google Sheets</span>
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

        <div className="max-w-6xl mx-auto w-full pt-6 md:pt-12 px-4 sm:px-6">
          {/* Header Section */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">Your Spreadsheets</h1>
                <p className="text-gray-400">Manage and automate your Google Sheets data</p>
              </div>
              
              {spreadsheets.length > 0 && (
                <button
                  onClick={handleConnectSheets}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white font-medium transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span className="hidden sm:inline">Refresh Connection</span>
                  <span className="sm:hidden">Refresh</span>
                </button>
              )}
            </div>
          </div>

          {/* Content */}
          {spreadsheets.length === 0 ? (
            // Empty State
            <div className="text-center py-12">
              <div className="mb-6">
                <FileSpreadsheet className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No spreadsheets found</h3>
                <p className="text-gray-400 mb-6 max-w-md mx-auto">
                  Connect your Google Sheets account to view and manage your spreadsheets, or create your first spreadsheet to get started.
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={handleConnectSheets}
                  className="flex items-center justify-center space-x-2 px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg text-white font-medium transition-colors"
                >
                  <SheetsIcon className="w-5 h-5" />
                  <span>Connect Google Sheets</span>
                </button>
                
                <a
                  href="https://sheets.google.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center space-x-2 px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg text-white font-medium transition-colors"
                >
                  <Plus className="w-5 h-5" />
                  <span>Create New Sheet</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          ) : (
            // Spreadsheets Grid
            <div>
              <div className="mb-6 flex items-center justify-between">
                <p className="text-sm text-gray-400">
                  Found {spreadsheets.length} spreadsheet{spreadsheets.length !== 1 ? 's' : ''}
                </p>
                <a
                  href="https://sheets.google.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1 text-sm text-green-400 hover:text-green-300 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>Create New</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {spreadsheets.map((sheet) => (
                  <div
                    key={sheet.id}
                    className="bg-gray-900/50 border border-gray-800 rounded-lg p-6 hover:bg-gray-900/70 transition-all duration-200 hover:border-gray-700"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                          <FileSpreadsheet className="w-5 h-5 text-green-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="text-white font-medium truncate">{sheet.name}</h3>
                        </div>
                      </div>
                      
                      {sheet.webViewLink && (
                        <a
                          href={sheet.webViewLink}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-gray-400 hover:text-white transition-colors"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                    
                    <div className="space-y-2 text-sm text-gray-400">
                      <div className="flex items-center space-x-2">
                        <Calendar className="w-4 h-4" />
                        <span>Modified {getTimeAgo(sheet.modifiedTime)}</span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="w-4 h-4" />
                        <span>Created {formatDate(sheet.createdTime)}</span>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-gray-800">
                      <div className="flex space-x-2">
                        {sheet.webViewLink && (
                          <a
                            href={sheet.webViewLink}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-1 py-2 px-3 bg-green-600/20 hover:bg-green-600/30 rounded text-green-400 text-center text-sm font-medium transition-colors"
                          >
                            Open Sheet
                          </a>
                        )}
                        
                        <button
                          className="py-2 px-3 bg-gray-800 hover:bg-gray-700 rounded text-gray-300 text-sm font-medium transition-colors"
                          onClick={() => {
                            // Future: Add automation configuration
                            console.log('Configure automation for:', sheet.id);
                          }}
                        >
                          Automate
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GoogleSheetsDashboard;