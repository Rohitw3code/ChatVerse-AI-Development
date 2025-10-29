import React, { useState, useEffect } from 'react';
import { ChevronDown, CheckCircle, ExternalLink } from 'lucide-react';
import { PlatformAccount } from '../../types/types';

interface InstagramCardProps {
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
  onViewDashboard: (account: PlatformAccount) => void;
  isConnecting: boolean;
}

export const InstagramCard: React.FC<InstagramCardProps> = ({
  app,
  connectedAccounts,
  onConnect,
  onViewDashboard,
  isConnecting,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const isConnected = connectedAccounts.length > 0;
  
  // Inject laser effect styles
  useEffect(() => {
    const styleId = 'instagram-card-laser-styles';
    if (document.getElementById(styleId)) return;

    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      @keyframes instagram-card-laser-sweep {
        0% { transform: translateX(-100%) skewX(-15deg); opacity: 0; }
        50% { opacity: 0.5; }
        100% { transform: translateX(200%) skewX(-15deg); opacity: 0; }
      }
      
      .instagram-card-laser {
        position: relative;
        overflow: hidden;
      }
      
      .instagram-card-laser::before {
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
      
      .instagram-card-laser:hover::before {
        animation: instagram-card-laser-sweep 1.2s ease-out;
      }
    `;
    document.head.appendChild(style);
  }, []);

  return (
    <div className={`instagram-card-laser border border-gray-800 rounded-lg overflow-hidden bg-gray-900/30 backdrop-blur-sm transition-all duration-300 ${
      app.enabled ? 'hover:border-gray-700 hover:shadow-lg hover:shadow-white/5' : 'opacity-60'
    }`}>
      <div className="p-5">
        {/* App Header */}
        <div className="flex items-start gap-4 mb-4">
          <div className={`w-14 h-14 rounded-lg bg-gradient-to-br ${app.gradient} flex items-center justify-center flex-shrink-0 shadow-lg`}>
            <app.Icon />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-white font-bold text-base mb-1">{app.name}</h4>
            <p className="text-gray-400 text-sm leading-relaxed">{app.description}</p>
          </div>
        </div>

        {/* Connection Status / Action */}
        {app.enabled ? (
          <>
            {isConnected ? (
              <div className="space-y-3">
                {/* Connected Status Button */}
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="w-full flex items-center justify-between p-3 bg-green-900/20 hover:bg-green-900/30 rounded-lg border border-green-800/40 hover:border-green-700/60 transition-all duration-300 group"
                >
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="text-sm text-green-400 font-medium">
                      {connectedAccounts.length === 1 
                        ? `@${connectedAccounts[0].platform_username}` 
                        : `${connectedAccounts.length} Accounts Connected`}
                    </span>
                  </div>
                  <ChevronDown className={`w-4 h-4 text-green-400 transition-transform duration-200 ${
                    isExpanded ? 'rotate-180' : ''
                  }`} />
                </button>

                {/* Dropdown - Connected Accounts */}
                {isExpanded && connectedAccounts.length > 1 && (
                  <div className="space-y-2 pl-2 border-l-2 border-gray-800">
                    {connectedAccounts.map((account) => (
                      <div
                        key={account.id}
                        className="p-2 rounded hover:bg-gray-800/50 transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <img 
                            src={`https://placehold.co/28x28/1a1a1a/ffffff?text=${account.platform_username.charAt(0).toUpperCase()}`}
                            alt={account.platform_username}
                            className="w-6 h-6 rounded-full border border-gray-700"
                          />
                          <span className="text-sm text-white">@{account.platform_username}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* View Instagram Dashboard Button */}
                <button
                  onClick={() => onViewDashboard(connectedAccounts[0])}
                  className="w-full flex items-center justify-center gap-2 p-3 bg-gradient-to-r from-pink-500/20 via-purple-500/20 to-yellow-500/20 hover:from-pink-500/30 hover:via-purple-500/30 hover:to-yellow-500/30 rounded-lg border border-pink-500/40 hover:border-pink-500/60 transition-all duration-300 group"
                >
                  <ExternalLink className="w-4 h-4 text-pink-400 group-hover:text-pink-300" />
                  <span className="text-sm text-pink-400 group-hover:text-pink-300 font-semibold">
                    View Instagram Dashboard
                  </span>
                </button>
              </div>
            ) : (
              <button
                onClick={() => onConnect(app.id)}
                disabled={isConnecting}
                className="w-full p-3 bg-gradient-to-r from-pink-500/10 to-yellow-500/10 hover:from-pink-500/20 hover:to-yellow-500/20 rounded-lg border border-pink-500/40 hover:border-pink-500/60 transition-all duration-300 text-white text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isConnecting ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-gray-600 border-t-white rounded-full animate-spin"></div>
                    <span>Connecting...</span>
                  </div>
                ) : (
                  'Connect Instagram Account'
                )}
              </button>
            )}
          </>
        ) : (
          <div className="p-3 bg-gray-800/30 rounded-lg border border-gray-800/50 text-center">
            <span className="text-xs text-gray-500">Coming Soon</span>
          </div>
        )}
      </div>
    </div>
  );
};
