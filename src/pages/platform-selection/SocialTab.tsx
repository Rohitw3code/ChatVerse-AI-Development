import React, { useState, useEffect } from 'react';
import { Search, ChevronDown, ChevronUp } from 'lucide-react';
import { PlatformAccount } from '../../types/types';
import { ConnectedAccountRow } from './ConnectedAccountRow';
import LearnModeDropdown from './components/LearnModeDropdown';
import FabricButton from './components/FabricButton';

interface SocialTabProps {
  socialPlatforms: any[];
  connectedSocialAccounts: PlatformAccount[];
  platformIcons: Record<string, React.ElementType>;
  connectingPlatform: string | null;
  handlePlatformConnect: (platformId: string) => void;
  handleAccountClick: (account: PlatformAccount) => void;
  activeTab: 'social' | 'tools';
  setActiveTab: (tab: 'social' | 'tools') => void;
  handleTalkToAiClick: () => void;
}

export const SocialTab: React.FC<SocialTabProps> = ({
  socialPlatforms,
  connectedSocialAccounts,
  platformIcons,
  connectingPlatform,
  handlePlatformConnect,
  handleAccountClick,
  activeTab,
  setActiveTab,
  handleTalkToAiClick,
}) => {
  // Folding states
  const [isConnectedAccountsOpen, setIsConnectedAccountsOpen] = useState(true);
  const [isSocialPlatformsOpen, setIsSocialPlatformsOpen] = useState(true);

  // Inject card laser effect styles
  useEffect(() => {
    const styleId = 'platform-card-laser-styles';
    if (document.getElementById(styleId)) return;

    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      @keyframes card-laser-sweep {
        0% { transform: translateX(-100%) skewX(-15deg); opacity: 0; }
        50% { opacity: 0.6; }
        100% { transform: translateX(200%) skewX(-15deg); opacity: 0; }
      }
      
      .platform-card-laser {
        position: relative;
        overflow: hidden;
      }
      
      .platform-card-laser::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(
          90deg,
          transparent,
          rgba(255, 255, 255, 0.15),
          transparent
        );
        transform: translateX(-100%) skewX(-15deg);
        z-index: 1;
        pointer-events: none;
      }
      
      .platform-card-laser:hover::before {
        animation: card-laser-sweep 1.2s ease-out;
      }
    `;
    document.head.appendChild(style);
  }, []);

  return (
    <div className="space-y-8">
      {/* Tab Navigation with Create Button */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        {/* Tabs */}
        <div className="inline-flex gap-2 p-1 bg-gray-900/50 rounded-lg border border-gray-800/50">
          <FabricButton
            onClick={() => setActiveTab('social')}
            variant={activeTab === 'social' ? 'selected' : 'outline'}
            size="small"
            className="!rounded-lg"
          >
            Social
          </FabricButton>
          <FabricButton
            onClick={() => setActiveTab('tools')}
            variant={activeTab === 'tools' ? 'selected' : 'outline'}
            size="small"
            className="!rounded-lg"
          >
            Tools
          </FabricButton>
        </div>
        
        {/* Create Automation Button */}
        <FabricButton
          onClick={handleTalkToAiClick}
          variant="secondary"
          size="small"
        >
          <Search className="w-4 h-4" />
          <span>Create Automation</span>
        </FabricButton>
      </div>

      <main className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Section - Connected Social Accounts */}
        <section>
          <div 
            className="mb-4 cursor-pointer select-none flex items-center justify-between group"
            onClick={() => setIsConnectedAccountsOpen(!isConnectedAccountsOpen)}
          >
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold text-white">Connected Accounts</h3>
              {!isConnectedAccountsOpen && connectedSocialAccounts.length > 0 && (
                <span className="px-2 py-0.5 text-xs font-medium bg-gray-800 text-gray-300 rounded">
                  {connectedSocialAccounts.length}
                </span>
              )}
            </div>
            {isConnectedAccountsOpen ? (
              <ChevronUp className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
            )}
          </div>

          {isConnectedAccountsOpen && (
            <>
              {connectedSocialAccounts.length > 0 ? (
                <div className="space-y-2">
                  {connectedSocialAccounts.map((account) => (
                    <ConnectedAccountRow
                      key={account.id}
                      account={account}
                      platformIcons={platformIcons}
                      onAccountClick={handleAccountClick}
                    />
                  ))}
                </div>
              ) : (
                <div className="border border-gray-800 rounded-lg p-8 text-center">
                  <div className="w-12 h-12 mx-auto mb-3 bg-gray-900 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                  </div>
                  <h4 className="text-white font-medium mb-1 text-sm">No connected accounts</h4>
                  <p className="text-sm text-gray-500">Connect platforms to get started</p>
                </div>
              )}
            </>
          )}
        </section>

        {/* Right Section - Available Social Platforms */}
        <section>
          <div 
            className="mb-4 cursor-pointer select-none flex items-center justify-between group"
            onClick={() => setIsSocialPlatformsOpen(!isSocialPlatformsOpen)}
          >
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold text-white">Available Platforms</h3>
              {!isSocialPlatformsOpen && (
                <span className="px-2 py-0.5 text-xs font-medium bg-gray-800 text-gray-300 rounded">
                  {socialPlatforms.length}
                </span>
              )}
            </div>
            {isSocialPlatformsOpen ? (
              <ChevronUp className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
            )}
          </div>
          
          {isSocialPlatformsOpen && (
          <div className="space-y-2">
            {socialPlatforms.map((platform) => {
              return (
                <div key={platform.id} className="border border-gray-800 rounded-lg hover:border-gray-700 transition-all duration-300 overflow-hidden platform-card-laser bg-gray-900/30 backdrop-blur-sm hover:shadow-lg hover:shadow-white/5">
                  <button
                    onClick={() => handlePlatformConnect(platform.id)}
                    disabled={connectingPlatform === platform.id || platform.comingSoon}
                    className={`relative w-full p-4 flex items-center gap-4 hover:bg-gray-900/50 transition-all duration-300 ${
                      platform.comingSoon ? 'opacity-50 cursor-not-allowed' : 'hover:scale-[1.01]'
                    }`}
                  >
                    <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${platform.gradient} flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:scale-110 shadow-md`}>
                      <platform.Icon className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0 text-left relative z-10">
                      <div className="flex items-center gap-2 mb-0.5">
                        <h4 className="text-white font-medium text-sm">{platform.name}</h4>
                        {platform.comingSoon && (
                          <span className="px-2 py-0.5 bg-yellow-500/10 text-yellow-500 rounded text-xs font-medium border border-yellow-500/30">
                            Soon
                          </span>
                        )}
                      </div>
                      <p className="text-gray-500 text-xs line-clamp-1">{platform.description}</p>
                    </div>
                    <div className="flex-shrink-0 relative z-10">
                      {connectingPlatform === platform.id ? (
                        <div className="w-4 h-4 border-2 border-gray-600 border-t-white rounded-full animate-spin"></div>
                      ) : (
                        <svg className="w-4 h-4 text-gray-600 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      )}
                    </div>
                  </button>
                  
                  {/* Learn Mode Dropdown */}
                  {platform.requirements && (
                    <LearnModeDropdown platform={platform} />
                  )}
                </div>
              );
            })}
          </div>
          )}
        </section>
      </main>
    </div>
  );
};