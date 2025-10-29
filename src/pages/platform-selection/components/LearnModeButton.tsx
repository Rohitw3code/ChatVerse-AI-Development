import React from 'react';
import { BookOpen } from 'lucide-react';

interface LearnModeButtonProps {
  onClick: () => void;
  className?: string;
}

const LearnModeButton: React.FC<LearnModeButtonProps> = ({ onClick, className = '' }) => {
  return (
    <button
      onClick={onClick}
      className={`
        group relative px-3 py-2 rounded-lg transition-all duration-200 
        bg-gradient-to-r from-blue-500/10 to-purple-500/10 
        hover:from-blue-500/20 hover:to-purple-500/20
        border border-blue-500/20 hover:border-blue-500/30
        backdrop-blur-sm hover:scale-105
        ${className}
      `}
    >
      <div className="flex items-center gap-2">
        <BookOpen className="w-4 h-4 text-blue-400 group-hover:text-blue-300 transition-colors" />
        <span className="text-blue-400 group-hover:text-blue-300 text-sm font-medium transition-colors">
          Learn Mode
        </span>
      </div>
    </button>
  );
};

export default LearnModeButton;
