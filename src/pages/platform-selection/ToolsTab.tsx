import React, { useEffect, useState } from 'react';
import { Plus, Search, ChevronDown, ChevronUp } from 'lucide-react';
import { PlatformAccount } from '../../types/types';
import { ConnectedAccountRow } from './ConnectedAccountRow';
import FabricButton from './components/FabricButton';

// Inject fabric button animations
const injectFabricAnimations = () => {
  const styleId = 'fabric-button-animations';
  if (document.getElementById(styleId)) return;
  
  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    @keyframes laser-sweep {
      0% { transform: translateX(-100%); }
      50% { transform: translateX(100%); }
      100% { transform: translateX(100%); }
    }
  `;
  document.head.appendChild(style);
};

// Assume productivityTools definition is passed as a prop or imported
// Assume platformIcons definition is passed as a prop or imported

interface ToolsTabProps {
  productivityTools: any[]; // Define a stricter type if possible
  connectedTools: PlatformAccount[];
  platformIcons: Record<string, React.ElementType>;
  connectingPlatform: string | null;
  handlePlatformConnect: (platformId: string) => void;
  handleAccountClick: (account: PlatformAccount) => void;
  activeTab: 'social' | 'tools';
  setActiveTab: (tab: 'social' | 'tools') => void;
  handleTalkToAiClick: () => void;
}

export const ToolsTab: React.FC<ToolsTabProps> = ({
  productivityTools,
  connectedTools,
  platformIcons,
  connectingPlatform,
  handlePlatformConnect,
  handleAccountClick,
  activeTab,
  setActiveTab,
  handleTalkToAiClick,
}) => {
  // Inject animations on mount
  useEffect(() => {
    injectFabricAnimations();
    
    // Inject card laser effect styles
    const styleId = 'tools-card-laser-styles';
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

  // Folding states
  const [isConnectedToolsOpen, setIsConnectedToolsOpen] = useState(true);
  const [isProductivityToolsOpen, setIsProductivityToolsOpen] = useState(true);

  return (
    <div className="space-y-6 md:space-y-8">
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

      <main className="grid grid-cols-1 xl:grid-cols-2 gap-8 md:gap-10 xl:gap-12">
        {/* Left Section - Connected Tools */}
        <section className="xl:col-span-1 order-2 xl:order-1">
          <div 
            className={`mb-5 cursor-pointer select-none transition-all duration-300 ${
              !isConnectedToolsOpen ? 'p-4 rounded-xl bg-gradient-to-r from-emerald-900/20 via-teal-900/20 to-cyan-900/20 border border-emerald-500/20 hover:border-emerald-500/40' : ''
            }`}
            onClick={() => setIsConnectedToolsOpen(!isConnectedToolsOpen)}
          >
            <h3 className="text-xl sm:text-2xl font-bold text-white mb-2 text-left flex items-center gap-2 group">
              <span className="text-2xl">🔧</span>
              <span>Connected Tools</span>
              {!isConnectedToolsOpen && (
                <span className="ml-2 px-3 py-1 text-xs font-semibold bg-emerald-500/20 text-emerald-300 rounded-full border border-emerald-500/30">
                  {connectedTools.length} Connected
                </span>
              )}
              {isConnectedToolsOpen ? (
                <ChevronUp className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors ml-auto" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors ml-auto" />
              )}
            </h3>
            {isConnectedToolsOpen && (
              <p className="text-sm text-gray-400 text-left">Ready for automation</p>
            )}
            {!isConnectedToolsOpen && (
              <p className="text-sm text-gray-500 text-left mt-1">Click to expand</p>
            )}
          </div>
          {isConnectedToolsOpen && (
            <>
              {connectedTools.length > 0 ? (
                <div className="bg-gradient-to-br from-black/70 via-gray-900/30 to-black/70 backdrop-blur-sm rounded-2xl overflow-hidden shadow-lg border border-gray-800/40 transition-all duration-300">
                  {connectedTools.map((account) => (
                    <ConnectedAccountRow
                      key={account.id}
                      account={account}
                      platformIcons={platformIcons}
                      onAccountClick={handleAccountClick}
                    />
                  ))}
                </div>
              ) : (
                <div className="bg-gradient-to-br from-black/70 via-gray-900/30 to-black/70 backdrop-blur-sm rounded-2xl p-8 text-center text-gray-400 border border-gray-800/40 transition-all duration-300">
                  <div className="w-14 h-14 mx-auto mb-4 bg-gradient-to-br from-gray-800 to-gray-900 rounded-full flex items-center justify-center">
                    <div className="w-7 h-7 text-gray-500">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                      </svg>
                    </div>
                  </div>
                  <h4 className="text-white font-semibold mb-2">No Tools Connected</h4>
                  <p className="text-sm">Connect tools to start automating</p>
                </div>
              )}
            </>
          )}
        </section>

        {/* Right Section - Available Productivity Tools */}
        <section className="xl:col-span-1 order-1 xl:order-2">
          <div 
            className={`mb-5 cursor-pointer select-none transition-all duration-300 ${
              !isProductivityToolsOpen ? 'p-4 rounded-xl bg-gradient-to-r from-amber-900/20 via-orange-900/20 to-red-900/20 border border-amber-500/20 hover:border-amber-500/40' : ''
            }`}
            onClick={() => setIsProductivityToolsOpen(!isProductivityToolsOpen)}
          >
            <h3 className="text-xl sm:text-2xl font-bold text-white mb-2 text-left flex items-center gap-2 group">
              <span className="text-2xl">⚡</span>
              <span>Productivity Tools</span>
              {!isProductivityToolsOpen && (
                <span className="ml-2 px-3 py-1 text-xs font-semibold bg-amber-500/20 text-amber-300 rounded-full border border-amber-500/30">
                  {productivityTools.length} Available
                </span>
              )}
              {isProductivityToolsOpen ? (
                <ChevronUp className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors ml-auto" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors ml-auto" />
              )}
            </h3>
            {isProductivityToolsOpen && (
              <p className="text-sm text-gray-400 text-left">Connect & automate</p>
            )}
            {!isProductivityToolsOpen && (
              <p className="text-sm text-gray-500 text-left mt-1">Click to expand</p>
            )}
          </div>
          
          {isProductivityToolsOpen && (
          <div className="space-y-2 transition-all duration-300">
            {productivityTools.map((platform) => {
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
                </div>
              );
            })}
            
            {/* Coming Soon Card */}
            <div className="bg-gradient-to-br from-slate-800/20 to-slate-700/20 backdrop-blur-sm rounded-xl border border-slate-600/20 p-6 text-center">
              <div className="w-12 h-12 mx-auto mb-3 bg-gradient-to-br from-emerald-800/30 to-emerald-900/30 rounded-full flex items-center justify-center">
                <Plus className="w-6 h-6 text-emerald-400" />
              </div>
              <h4 className="text-white font-semibold text-base mb-2">More Coming Soon</h4>
              <p className="text-gray-400 text-sm">New tools & integrations</p>
            </div>
          </div>
          )}
        </section>
      </main>
    </div>
  );
};