import React, { useState, useEffect } from 'react';
import { ChevronDown, CheckCircle, Lock } from 'lucide-react';
import { PlatformAccount } from '../../types/types';

interface AppCardProps {
  app: {
    id: string;
    name: string;
    description: string;
    Icon: React.ElementType;
    gradient: string;
    enabled: boolean;
  };
  connectedAccounts: PlatformAccount[];
  onConnect: (appId: string) => void;
  onAccountClick: (account: PlatformAccount) => void;
  isConnecting: boolean;
}

export const AppCard: React.FC<AppCardProps> = ({
  app,
  connectedAccounts,
  onConnect,
  onAccountClick,
  isConnecting,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const isConnected = connectedAccounts.length > 0;
  
  // Inject laser effect styles
  useEffect(() => {
    const styleId = 'app-card-laser-styles';
    if (document.getElementById(styleId)) return;

    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      @keyframes app-card-laser-sweep {
        0% { transform: translateX(-100%) skewX(-15deg); opacity: 0; }
        50% { opacity: 0.4; }
        100% { transform: translateX(200%) skewX(-15deg); opacity: 0; }
      }
      
      .app-card-laser {
        position: relative;
        overflow: hidden;
      }
      
      .app-card-laser::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(
          90deg,
          transparent,
          rgba(255, 255, 255, 0.1),
          transparent
        );
        transform: translateX(-100%) skewX(-15deg);
        z-index: 1;
        pointer-events: none;
      }
      
      .app-card-laser:hover::before {
        animation: app-card-laser-sweep 1s ease-out;
      }
    `;
    document.head.appendChild(style);
  }, []);

  return (
    <div className={`app-card-laser border border-gray-800 rounded-lg overflow-hidden bg-gray-900/30 backdrop-blur-sm transition-all duration-300 ${
      app.enabled ? 'hover:border-gray-700 hover:shadow-lg hover:shadow-white/5' : 'opacity-60'
    }`}>
      <div className="p-4">
        {/* App Header */}
        <div className="flex items-start gap-3 mb-3">
          <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${app.gradient} flex items-center justify-center flex-shrink-0 shadow-md relative`}>
            <app.Icon />
            {!app.enabled && (
              <div className="absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center">
                <Lock className="w-5 h-5 text-gray-400" />
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="text-white font-semibold text-sm">{app.name}</h4>
              {!app.enabled && (
                <span className="px-2 py-0.5 bg-gray-700/50 text-gray-400 rounded text-xs font-medium">
                  Soon
                </span>
              )}
            </div>
            <p className="text-gray-500 text-xs line-clamp-2">{app.description}</p>
          </div>
        </div>

        {/* Connection Status / Action */}
        {app.enabled ? (
          <>
            {isConnected ? (
              <div className="space-y-2">
                {/* Connected Status Button */}
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="w-full flex items-center justify-between p-2.5 bg-green-900/20 hover:bg-green-900/30 rounded-lg border border-green-800/40 hover:border-green-700/60 transition-all duration-300 group"
                >
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="text-sm text-green-400 font-medium">
                      {connectedAccounts.length === 1 
                        ? connectedAccounts[0].platform_username 
                        : `${connectedAccounts.length} Connected`}
                    </span>
                  </div>
                  <ChevronDown className={`w-4 h-4 text-green-400 transition-transform duration-200 ${
                    isExpanded ? 'rotate-180' : ''
                  }`} />
                </button>

                {/* Dropdown - Connected Accounts */}
                {isExpanded && (
                  <div className="space-y-1 pl-2 border-l-2 border-gray-800">
                    {connectedAccounts.map((account) => (
                      <button
                        key={account.id}
                        onClick={() => onAccountClick(account)}
                        className="w-full text-left p-2 rounded hover:bg-gray-800/50 transition-colors group/account"
                      >
                        <div className="flex items-center gap-2">
                          <img 
                            src={`https://placehold.co/32x32/1a1a1a/ffffff?text=${account.platform_username.charAt(0).toUpperCase()}`}
                            alt={account.platform_username}
                            className="w-6 h-6 rounded-full border border-gray-700"
                          />
                          <div className="flex-1 min-w-0">
                            <div className="text-sm text-white truncate group-hover/account:text-gray-200">
                              {account.platform === 'gmail' ? account.platform_username : `@${account.platform_username}`}
                            </div>
                          </div>
                          <svg className="w-4 h-4 text-gray-600 group-hover/account:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={() => onConnect(app.id)}
                disabled={isConnecting}
                className="w-full p-2.5 bg-gray-800/50 hover:bg-gray-800 rounded-lg border border-gray-700 hover:border-gray-600 transition-all duration-300 text-white text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isConnecting ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-gray-600 border-t-white rounded-full animate-spin"></div>
                    <span>Connecting...</span>
                  </div>
                ) : (
                  'Connect'
                )}
              </button>
            )}
          </>
        ) : (
          <div className="p-2.5 bg-gray-800/30 rounded-lg border border-gray-800/50 text-center">
            <span className="text-xs text-gray-500">Coming Soon</span>
          </div>
        )}
      </div>
    </div>
  );
};
