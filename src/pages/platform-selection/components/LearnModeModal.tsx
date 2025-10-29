import React from 'react';
import { X, CheckCircle, AlertCircle, ExternalLink } from 'lucide-react';

interface LearnModeModalProps {
  isOpen: boolean;
  onClose: () => void;
  platform: {
    id: string;
    name: string;
    requirements: {
      title: string;
      description: string;
      steps: string[];
      tips: string[];
      warnings?: string[];
    };
  };
}

const LearnModeModal: React.FC<LearnModeModalProps> = ({ isOpen, onClose, platform }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 backdrop-blur-xl"
        style={{
          background: `linear-gradient(135deg, 
            rgba(0, 0, 0, 0.8) 0%, 
            rgba(15, 15, 23, 0.9) 50%, 
            rgba(0, 0, 0, 0.8) 100%)
          `
        }}
        onClick={onClose}
      ></div>
      
      {/* Modal */}
      <div 
        className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl border border-white/10 shadow-2xl"
        style={{
          background: `linear-gradient(135deg, 
            rgba(20, 20, 25, 0.95) 0%, 
            rgba(30, 30, 35, 0.9) 50%, 
            rgba(20, 20, 25, 0.95) 100%)
          `,
          backdropFilter: 'blur(20px)'
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div>
            <h2 className="text-2xl font-bold text-white">Setup Guide</h2>
            <p className="text-gray-400 mt-1">Learn how to prepare your {platform.name} account</p>
          </div>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center transition-all duration-200 hover:scale-105"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Title & Description */}
          <div>
            <h3 className="text-xl font-semibold text-white mb-2">{platform.requirements.title}</h3>
            <p className="text-gray-300">{platform.requirements.description}</p>
          </div>

          {/* Steps */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-400" />
              Setup Steps
            </h4>
            <div className="space-y-3">
              {platform.requirements.steps.map((step, index) => (
                <div key={index} className="flex gap-3">
                  <div className="w-6 h-6 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-400 text-sm font-medium">{index + 1}</span>
                  </div>
                  <p className="text-gray-300 leading-relaxed">{step}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Tips */}
          {platform.requirements.tips.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <ExternalLink className="w-5 h-5 text-blue-400" />
                Pro Tips
              </h4>
              <div className="space-y-2">
                {platform.requirements.tips.map((tip, index) => (
                  <div key={index} className="flex gap-3 p-3 rounded-xl bg-blue-500/5 border border-blue-500/20">
                    <div className="w-2 h-2 rounded-full bg-blue-400 flex-shrink-0 mt-2"></div>
                    <p className="text-blue-100 text-sm leading-relaxed">{tip}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Warnings */}
          {platform.requirements.warnings && platform.requirements.warnings.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-yellow-400" />
                Important Notes
              </h4>
              <div className="space-y-2">
                {platform.requirements.warnings.map((warning, index) => (
                  <div key={index} className="flex gap-3 p-3 rounded-xl bg-yellow-500/5 border border-yellow-500/20">
                    <AlertCircle className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
                    <p className="text-yellow-100 text-sm leading-relaxed">{warning}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-white/10">
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 hover:text-white transition-all duration-200 font-medium"
            >
              Got it!
            </button>
            <button
              onClick={onClose}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-medium transition-all duration-200 hover:scale-105"
            >
              Start Setup
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearnModeModal;
