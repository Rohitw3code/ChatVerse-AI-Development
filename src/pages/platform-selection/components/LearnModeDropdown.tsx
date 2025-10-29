import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle, AlertCircle, ExternalLink } from 'lucide-react';

interface LearnModeDropdownProps {
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

const LearnModeDropdown: React.FC<LearnModeDropdownProps> = ({ platform }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div>
      {/* Toggle Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-3 md:px-4 py-2.5 md:py-3 transition-all duration-200 bg-slate-800/20 hover:bg-slate-800/40 border-t border-slate-600/30"
      >
        <div className="flex items-center gap-2 md:gap-3 min-w-0 flex-1">
          <div className="w-6 h-6 md:w-8 md:h-8 rounded-lg bg-blue-500/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0">
            <ExternalLink className="w-3 h-3 md:w-4 md:h-4 text-blue-400" />
          </div>
          <div className="text-left min-w-0 flex-1">
            <h4 className="text-white font-medium text-xs md:text-sm truncate">Setup Guide</h4>
            <p className="text-gray-400 text-xs hidden sm:block">Learn how to prepare your {platform.name} account</p>
          </div>
        </div>
        <div className="flex items-center gap-1 md:gap-2 flex-shrink-0">
          <span className="text-xs text-blue-400 font-medium hidden sm:inline">
            {isExpanded ? 'Hide' : 'Show'}
          </span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-blue-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-blue-400" />
          )}
        </div>
      </button>

      {/* Dropdown Content */}
      {isExpanded && (
        <div className="bg-gradient-to-br from-slate-900/60 to-slate-800/60 backdrop-blur-sm border-t border-slate-600/30">
          <div className="p-3 md:p-4 space-y-3 md:space-y-4">
            {/* Title & Description */}
            <div>
              <h5 className="text-base md:text-lg font-semibold text-white mb-2">{platform.requirements.title}</h5>
              <p className="text-gray-300 text-xs md:text-sm leading-relaxed">{platform.requirements.description}</p>
            </div>

            {/* Steps */}
            <div>
              <h6 className="text-xs md:text-sm font-semibold text-white mb-2 md:mb-3 flex items-center gap-2">
                <CheckCircle className="w-3 h-3 md:w-4 md:h-4 text-green-400" />
                Setup Steps
              </h6>
              <div className="space-y-2">
                {platform.requirements.steps.map((step, index) => (
                  <div key={index} className="flex gap-2 md:gap-3">
                    <div className="w-4 h-4 md:w-5 md:h-5 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-blue-400 text-xs font-medium">{index + 1}</span>
                    </div>
                    <p className="text-gray-300 text-xs md:text-sm leading-relaxed">{step}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Tips */}
            {platform.requirements.tips.length > 0 && (
              <div>
                <h6 className="text-xs md:text-sm font-semibold text-white mb-2 md:mb-3 flex items-center gap-2">
                  <ExternalLink className="w-3 h-3 md:w-4 md:h-4 text-blue-400" />
                  Pro Tips
                </h6>
                <div className="space-y-1.5 md:space-y-2">
                  {platform.requirements.tips.map((tip, index) => (
                    <div key={index} className="flex gap-2 p-2 rounded-lg bg-blue-500/5 border border-blue-500/20">
                      <div className="w-1 h-1 md:w-1.5 md:h-1.5 rounded-full bg-blue-400 flex-shrink-0 mt-1.5 md:mt-2"></div>
                      <p className="text-blue-100 text-xs leading-relaxed">{tip}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Warnings */}
            {platform.requirements.warnings && platform.requirements.warnings.length > 0 && (
              <div>
                <h6 className="text-xs md:text-sm font-semibold text-white mb-2 md:mb-3 flex items-center gap-2">
                  <AlertCircle className="w-3 h-3 md:w-4 md:h-4 text-yellow-400" />
                  Important Notes
                </h6>
                <div className="space-y-1.5 md:space-y-2">
                  {platform.requirements.warnings.map((warning, index) => (
                    <div key={index} className="flex gap-2 p-2 rounded-lg bg-yellow-500/5 border border-yellow-500/20">
                      <AlertCircle className="w-3 h-3 text-yellow-400 flex-shrink-0 mt-0.5" />
                      <p className="text-yellow-100 text-xs leading-relaxed">{warning}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default LearnModeDropdown;
