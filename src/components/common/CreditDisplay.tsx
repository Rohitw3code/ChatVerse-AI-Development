import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Coins, Plus, TrendingUp } from 'lucide-react';

interface CreditDisplayProps {
  credits: number;
  onAddCredits?: () => void;
  onUpgrade?: () => void;
  showActions?: boolean;
  variant?: 'compact' | 'full' | 'card';
  className?: string;
}

export const CreditDisplay: React.FC<CreditDisplayProps> = ({
  credits = 150, // Mock default value
  onAddCredits,
  onUpgrade,
  showActions = true,
  variant = 'full',
  className = ''
}) => {
  const navigate = useNavigate();

  const handleUpgradeClick = () => {
    if (onUpgrade) {
      onUpgrade();
    } else {
      navigate('/pricing');
    }
  };
  const getCreditStatus = () => {
    if (credits >= 100) return { color: 'text-green-400', bgColor: 'bg-green-500/20', borderColor: 'border-green-500/30' };
    if (credits >= 50) return { color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', borderColor: 'border-yellow-500/30' };
    return { color: 'text-red-400', bgColor: 'bg-red-500/20', borderColor: 'border-red-500/30' };
  };

  const status = getCreditStatus();

  if (variant === 'compact') {
    return (
      <div className={`flex items-center gap-2 px-3 py-2 bg-white/5 backdrop-blur-sm rounded-lg border border-white/10 ${className}`}>
        <Coins className={`w-4 h-4 ${status.color}`} />
        <span className="font-medium text-white text-sm">{credits}</span>
        {showActions && onAddCredits && (
          <button
            onClick={onAddCredits}
            className="ml-1 p-1 hover:bg-white/10 rounded transition-colors"
            title="Add Credits"
          >
            <Plus className="w-3 h-3 text-gray-400 hover:text-white" />
          </button>
        )}
      </div>
    );
  }

  if (variant === 'card') {
    return (
      <div className={`relative p-6 rounded-2xl bg-gradient-to-br from-gray-900/50 to-gray-800/30 border ${status.borderColor} backdrop-blur-sm ${className}`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 ${status.bgColor} rounded-xl flex items-center justify-center`}>
              <Coins className={`w-6 h-6 ${status.color}`} />
            </div>
            <div>
              <h3 className="text-white font-bold text-lg">Available Credits</h3>
              <p className="text-gray-400 text-sm">For AI automations</p>
            </div>
          </div>
        </div>
        
        <div className="mb-6">
          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-3xl font-bold text-white">{credits}</span>
            <span className="text-gray-400 text-sm">credits</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                credits >= 100 ? 'bg-green-500' : credits >= 50 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${Math.min((credits / 200) * 100, 100)}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {credits < 50 ? 'Low credits - consider adding more' : 
             credits < 100 ? 'Moderate credits available' : 'Good credit balance'}
          </p>
        </div>

        {showActions && (
          <div className="flex gap-3">
            {onAddCredits && (
              <button
                onClick={onAddCredits}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-all duration-200 hover:scale-105"
              >
                <Plus className="w-4 h-4" />
                Add Credits
              </button>
            )}
            <button
              onClick={handleUpgradeClick}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-xl font-medium transition-all duration-200 hover:scale-105"
            >
              <TrendingUp className="w-4 h-4" />
              Upgrade
            </button>
          </div>
        )}
      </div>
    );
  }

  // Full variant (default)
  return (
    <div className={`flex items-center gap-4 p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 ${className}`}>
      <div className={`w-10 h-10 ${status.bgColor} rounded-lg flex items-center justify-center`}>
        <Coins className={`w-5 h-5 ${status.color}`} />
      </div>
      <div className="flex-1">
        <div className="flex items-baseline gap-2">
          <span className="text-xl font-bold text-white">{credits}</span>
          <span className="text-gray-400 text-sm">credits available</span>
        </div>
        <p className="text-xs text-gray-500">
          {credits < 50 ? 'Low balance' : credits < 100 ? 'Moderate balance' : 'Good balance'}
        </p>
      </div>
      {showActions && (
        <div className="flex gap-2">
          {onAddCredits && (
            <button
              onClick={onAddCredits}
              className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add
            </button>
          )}
          <button
            onClick={handleUpgradeClick}
            className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg text-sm font-medium transition-colors"
          >
            <TrendingUp className="w-4 h-4" />
            Upgrade
          </button>
        </div>
      )}
    </div>
  );
};
