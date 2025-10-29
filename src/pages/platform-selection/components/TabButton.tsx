import React from 'react';

interface TabButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  active?: boolean;
  className?: string;
  disabled?: boolean;
}

const TabButton: React.FC<TabButtonProps> = ({
  children,
  onClick,
  active = false,
  className = '',
  disabled = false,
}) => {
  // Add tab button CSS animations on component mount
  React.useEffect(() => {
    const existingStyle = document.getElementById('tab-button-styles');
    if (existingStyle) return;

    const style = document.createElement('style');
    style.id = 'tab-button-styles';
    style.textContent = `
      @keyframes tab-glow {
        0%, 100% { 
          box-shadow: 
            0 0 15px rgba(139, 92, 246, 0.2),
            0 0 30px rgba(139, 92, 246, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        50% { 
          box-shadow: 
            0 0 25px rgba(139, 92, 246, 0.3),
            0 0 50px rgba(139, 92, 246, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
        }
      }
      
      @keyframes tab-secondary-glow {
        0%, 100% { 
          box-shadow: 
            0 0 15px rgba(59, 130, 246, 0.2),
            0 0 30px rgba(59, 130, 246, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        50% { 
          box-shadow: 
            0 0 25px rgba(59, 130, 246, 0.3),
            0 0 50px rgba(59, 130, 246, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
        }
      }
      
      .tab-btn-active-primary {
        background: 
          radial-gradient(circle at 30% 30%, rgba(139, 92, 246, 0.2) 0%, transparent 60%),
          linear-gradient(135deg, 
            rgba(15, 23, 42, 0.9) 0%, 
            rgba(30, 41, 59, 0.8) 50%, 
            rgba(51, 65, 85, 0.7) 100%
          );
        animation: tab-glow 3s ease-in-out infinite;
      }
      
      .tab-btn-active-secondary {
        background: 
          radial-gradient(circle at 30% 30%, rgba(59, 130, 246, 0.2) 0%, transparent 60%),
          linear-gradient(135deg, 
            rgba(15, 23, 42, 0.9) 0%, 
            rgba(30, 41, 59, 0.8) 50%, 
            rgba(51, 65, 85, 0.7) 100%
          );
        animation: tab-secondary-glow 3s ease-in-out infinite;
      }
      
      .tab-btn-inactive {
        background: 
          radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.05) 0%, transparent 60%),
          linear-gradient(135deg, transparent 0%, rgba(0, 0, 0, 0.2) 100%);
        backdrop-filter: blur(8px);
      }
      
      .tab-btn-inactive:hover {
        background: 
          radial-gradient(circle at 30% 30%, rgba(139, 92, 246, 0.1) 0%, transparent 60%),
          linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%);
        box-shadow: 
          0 0 20px rgba(139, 92, 246, 0.2),
          0 4px 16px rgba(0, 0, 0, 0.3);
      }
    `;
    document.head.appendChild(style);
  }, []);

  const getButtonClasses = () => {
    if (active) {
      return 'tab-btn-active-primary';
    }
    return 'tab-btn-inactive';
  };


  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${getButtonClasses()}
        group relative font-semibold rounded-xl transition-all duration-300 
        transform hover:scale-[1.02] focus:outline-none focus:ring-2 
        focus:ring-purple-500/30 px-4 py-2.5 text-sm sm:px-6 sm:py-3 sm:text-base
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
    >
      <span className="relative z-10 flex items-center justify-center gap-3 text-white">
        {children}
      </span>
    </button>
  );
};

export const SecondaryTabButton: React.FC<TabButtonProps> = ({
  children,
  onClick,
  active = false,
  className = '',
  disabled = false,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${active ? 'tab-btn-active-secondary' : 'tab-btn-inactive'}
        group relative font-semibold rounded-xl transition-all duration-300 
        transform hover:scale-[1.02] focus:outline-none focus:ring-2 
        focus:ring-blue-500/30 px-4 py-2.5 text-sm sm:px-6 sm:py-3 sm:text-base
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
    >
      <span className="relative z-10 flex items-center justify-center gap-3 text-white">
        {children}
      </span>
    </button>
  );
};

export default TabButton;
