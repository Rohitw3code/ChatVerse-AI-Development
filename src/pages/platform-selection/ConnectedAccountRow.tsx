import React, { useEffect } from 'react';
import { ArrowRight, CheckCircle } from 'lucide-react';
import { PlatformAccount } from '../../types/types';

interface ConnectedAccountRowProps {
  account: PlatformAccount;
  platformIcons: Record<string, React.ElementType>;
  onAccountClick: (account: PlatformAccount) => void;
}

export const ConnectedAccountRow: React.FC<ConnectedAccountRowProps> = ({ account, platformIcons, onAccountClick }) => {
  const PlatformIcon = platformIcons[account.platform];

  // Inject account row laser effect styles
  useEffect(() => {
    const styleId = 'account-row-laser-styles';
    if (document.getElementById(styleId)) return;

    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      @keyframes account-laser-sweep {
        0% { transform: translateX(-100%) skewX(-15deg); opacity: 0; }
        50% { opacity: 0.4; }
        100% { transform: translateX(200%) skewX(-15deg); opacity: 0; }
      }
      
      .account-row-laser {
        position: relative;
        overflow: hidden;
      }
      
      .account-row-laser::before {
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
        z-index: 2;
        pointer-events: none;
      }
      
      .account-row-laser:hover::before {
        animation: account-laser-sweep 1s ease-out;
      }
    `;
    document.head.appendChild(style);
  }, []);

  return (
    <div
      className="account-row-laser p-5 sm:p-6 flex items-center justify-between gap-4 hover:bg-gradient-to-r hover:from-gray-900/60 hover:via-gray-800/40 hover:to-gray-900/60 transition-all duration-300 cursor-pointer group border-b border-gray-800/30 last:border-b-0 hover:scale-[1.01] hover:shadow-md hover:shadow-white/5"
      onClick={() => onAccountClick(account)}
    >
      <div className="flex items-center gap-4 min-w-0 relative z-10">
        <div className="relative flex-shrink-0">
          <img 
            src={`https://placehold.co/48x48/1a1a1a/ffffff?text=${account.platform_username.charAt(0).toUpperCase()}`} 
            alt="Profile" 
            className="w-12 h-12 rounded-full object-cover border-2 border-gray-700 group-hover:border-gray-500 transition-all duration-300 shadow-lg group-hover:shadow-white/10 group-hover:scale-105" 
          />
          <div className="absolute -bottom-1 -right-1 bg-gradient-to-br from-gray-800 to-black rounded-full p-1 border-2 border-gray-700 group-hover:border-gray-500 transition-all duration-300">
            <div className="w-4 h-4 text-white group-hover:scale-110 transition-transform duration-300">
              {PlatformIcon && <PlatformIcon />}
            </div>
          </div>
        </div>
        <div className="min-w-0">
          <div className="font-semibold text-white text-base truncate group-hover:text-gray-100 transition-colors" title={account.platform_username}>
            {account.platform === 'gmail' ? account.platform_username : `@${account.platform_username}`}
          </div>
          <div className="text-sm text-gray-400 capitalize group-hover:text-gray-300 transition-colors">{account.platform}</div>
        </div>
      </div>
      <div className="flex items-center gap-3 text-sm flex-shrink-0 relative z-10">
        <div className="flex items-center gap-1.5 text-green-400 bg-gradient-to-r from-green-900/30 to-emerald-900/30 px-3 py-1.5 rounded-full border border-green-800/40 group-hover:border-green-700/60 transition-all duration-300 group-hover:shadow-md group-hover:shadow-green-500/10">
          <CheckCircle className="w-4 h-4" />
          <span className="hidden sm:inline">Connected</span>
        </div>
        <ArrowRight className="w-5 h-5 text-gray-500 group-hover:text-white transition-all duration-300 group-hover:translate-x-1" />
      </div>
    </div>
  );
};