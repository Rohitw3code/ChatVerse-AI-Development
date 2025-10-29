import React from 'react';
import { CheckCircle, Zap, Plus } from 'lucide-react';
import { PlatformAccount } from '../../types/types';

interface Platform {
  id: string;
  name: string;
  description: string;
  Icon: React.ElementType;
  gradient: string;
  comingSoon: boolean;
}

interface PlatformCardProps {
  platform: Platform;
  connectedAccounts: PlatformAccount[];
  connectingPlatform: string | null;
  onConnect: (platformId: string) => void;
}

export const PlatformCard: React.FC<PlatformCardProps> = ({ platform, connectedAccounts, connectingPlatform, onConnect }) => {
  const hasConnectedAccount = connectedAccounts.some(account => account.platform === platform.id);
  const isConnecting = connectingPlatform === platform.id;

  return (
    <div
      className={`group relative p-5 rounded-xl border transition-all duration-300 bg-white/[.02] backdrop-blur-sm flex flex-col text-left
        ${hasConnectedAccount ? 'border-green-500/30' : 'border-white/10'}
        ${platform.comingSoon ? 'opacity-60 cursor-not-allowed' : 'hover:border-white/20 hover:shadow-lg hover:shadow-purple-500/5 hover:-translate-y-1'}`}
    >
      {hasConnectedAccount && (
        <div className="absolute top-3 right-3 bg-green-500/20 p-1 rounded-full" title="Connected">
          <CheckCircle className="w-4 h-4 text-green-400" />
        </div>
      )}

      <div className="flex items-center gap-4 mb-3">
        <div className={`w-12 h-12 bg-gradient-to-br ${platform.gradient} rounded-lg flex items-center justify-center text-white shadow-md transition-transform group-hover:scale-105`}>
          <platform.Icon />
        </div>
        <h3 className="text-lg font-bold text-white">{platform.name}</h3>
      </div>

      <p className="text-sm text-gray-400 mb-4 flex-grow">{platform.description}</p>

      {!platform.comingSoon ? (
        <button
          onClick={() => onConnect(platform.id)}
          disabled={!!connectingPlatform}
          className={`w-full mt-auto flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all
            ${isConnecting ? 'bg-gray-600 cursor-wait' : 'bg-white/10 hover:bg-white/20 text-white'}
            ${hasConnectedAccount ? 'bg-green-500/20 hover:bg-green-500/30 text-green-300' : ''}`}
        >
          {isConnecting ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Connecting...</span>
            </>
          ) : (
            <>
              {hasConnectedAccount ? <Plus className="w-4 h-4" /> : <Zap className="w-4 h-4" />}
              <span>{hasConnectedAccount ? 'Add Another' : 'Connect'}</span>
            </>
          )}
        </button>
      ) : (
        <span className="text-xs font-semibold text-yellow-400 bg-yellow-400/10 px-3 py-1 rounded-full self-start mt-auto">
          Coming Soon
        </span>
      )}
    </div>
  );
};