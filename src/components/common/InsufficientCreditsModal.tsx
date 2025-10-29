import React, { useEffect } from 'react';
import { X, AlertTriangle, Coins, Plus, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface InsufficientCreditsModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentCredits: number;
  message?: string;
}

const InsufficientCreditsModal: React.FC<InsufficientCreditsModalProps> = ({
  isOpen,
  onClose,
  currentCredits,
  message = "Your current credits are below zero. Please add credits to continue."
}) => {
  const navigate = useNavigate();

  // Close modal on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  // Inject fabric animation styles
  useEffect(() => {
    if (isOpen) {
      const style = document.createElement('style');
      style.textContent = `
        @keyframes fabric-flow {
          0% { background-position: 0% 0%, 0% 0%; }
          50% { background-position: 100% 100%, -100% -100%; }
          100% { background-position: 0% 0%, 0% 0%; }
        }
        
        @keyframes laser-sweep {
          0% { transform: translateX(-100%) skewX(-15deg); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateX(400%) skewX(-15deg); opacity: 0; }
        }
        
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
          50% { box-shadow: 0 0 30px rgba(239, 68, 68, 0.5); }
        }
      `;
      document.head.appendChild(style);
      return () => {
        document.head.removeChild(style);
      };
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleAddCredits = () => {
    onClose();
    navigate('/pricing');
  };

  const handleUpgrade = () => {
    onClose();
    navigate('/pricing');
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity"
          onClick={onClose}
        />
        
        {/* Modal */}
        <div className="relative w-full max-w-md transform transition-all">
          <div 
            className="relative bg-gradient-to-br from-gray-900/95 to-black/95 backdrop-blur-lg rounded-2xl shadow-2xl border border-red-500/30 overflow-hidden"
            style={{
              background: `
                linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(0, 0, 0, 0.95) 100%),
                repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(239, 68, 68, 0.1) 2px, rgba(239, 68, 68, 0.1) 4px),
                repeating-linear-gradient(-45deg, transparent, transparent 2px, rgba(239, 68, 68, 0.05) 2px, rgba(239, 68, 68, 0.05) 4px)
              `,
              backgroundSize: '100% 100%, 20px 20px, 20px 20px',
              animation: 'fabric-flow 8s ease-in-out infinite'
            }}
          >
            {/* Laser sweep effect */}
            <div 
              className="absolute inset-0 bg-gradient-to-r from-transparent via-red-500/20 to-transparent"
              style={{
                animation: 'laser-sweep 3s ease-in-out infinite'
              }}
            />
            
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-red-500/20">
              <div className="flex items-center gap-3">
                <div 
                  className="w-12 h-12 bg-red-500/20 rounded-xl flex items-center justify-center border border-red-500/30"
                  style={{ animation: 'pulse-glow 2s ease-in-out infinite' }}
                >
                  <AlertTriangle className="w-6 h-6 text-red-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Insufficient Credits</h3>
                  <p className="text-sm text-red-400">Action required</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {/* Content */}
            <div className="p-6">
              {/* Current Credits Display */}
              <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
                <div className="flex items-center gap-3 mb-2">
                  <Coins className="w-5 h-5 text-red-400" />
                  <span className="text-white font-medium">Current Balance</span>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-red-400">{currentCredits}</span>
                  <span className="text-gray-400 text-sm">credits</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2 mt-2">
                  <div 
                    className="h-2 rounded-full bg-red-500 transition-all duration-300"
                    style={{ width: currentCredits < 0 ? '0%' : `${Math.min((Math.abs(currentCredits) / 100) * 100, 100)}%` }}
                  />
                </div>
              </div>

              {/* Error Message */}
              <div className="mb-6">
                <p className="text-gray-300 text-sm leading-relaxed">
                  {message}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col gap-3">
                <button
                  onClick={handleAddCredits}
                  className="relative flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl font-medium transition-all duration-200 hover:scale-105 overflow-hidden group"
                >
                  {/* Fabric texture background */}
                  <div 
                    className="absolute inset-0 opacity-20"
                    style={{
                      background: `
                        repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(255, 255, 255, 0.1) 2px, rgba(255, 255, 255, 0.1) 4px),
                        repeating-linear-gradient(-45deg, transparent, transparent 2px, rgba(255, 255, 255, 0.05) 2px, rgba(255, 255, 255, 0.05) 4px)
                      `,
                      backgroundSize: '12px 12px, 12px 12px'
                    }}
                  />
                  
                  {/* Laser sweep on hover */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -translate-x-full group-hover:translate-x-full transition-transform duration-700 skew-x-12" />
                  
                  <Plus className="w-5 h-5 relative z-10" />
                  <span className="relative z-10">Add Credits Now</span>
                </button>
                
                <button
                  onClick={handleUpgrade}
                  className="relative flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-xl font-medium transition-all duration-200 hover:scale-105 overflow-hidden group"
                >
                  {/* Fabric texture background */}
                  <div 
                    className="absolute inset-0 opacity-20"
                    style={{
                      background: `
                        repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(255, 255, 255, 0.1) 2px, rgba(255, 255, 255, 0.1) 4px),
                        repeating-linear-gradient(-45deg, transparent, transparent 2px, rgba(255, 255, 255, 0.05) 2px, rgba(255, 255, 255, 0.05) 4px)
                      `,
                      backgroundSize: '12px 12px, 12px 12px'
                    }}
                  />
                  
                  {/* Laser sweep on hover */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -translate-x-full group-hover:translate-x-full transition-transform duration-700 skew-x-12" />
                  
                  <TrendingUp className="w-5 h-5 relative z-10" />
                  <span className="relative z-10">Upgrade Plan</span>
                </button>
                
                <button
                  onClick={onClose}
                  className="px-6 py-3 text-gray-400 hover:text-white border border-gray-600 hover:border-gray-500 rounded-xl font-medium transition-all duration-200 hover:bg-white/5"
                >
                  Continue Later
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InsufficientCreditsModal;
