import React from 'react';

interface PlatformConnectButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
}

const PlatformConnectButton: React.FC<PlatformConnectButtonProps> = ({
  children,
  onClick,
  className = '',
  disabled = false,
}) => {
  // Add platform connect button CSS animations on component mount
  React.useEffect(() => {
    const existingStyle = document.getElementById('platform-connect-button-styles');
    if (existingStyle) return;

    const style = document.createElement('style');
    style.id = 'platform-connect-button-styles';
    style.textContent = `
      @keyframes platform-connect-glow {
        0%, 100% { 
          box-shadow: 
            0 0 20px rgba(75, 85, 99, 0.3),
            0 4px 16px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        50% { 
          box-shadow: 
            0 0 30px rgba(75, 85, 99, 0.4),
            0 6px 24px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
        }
      }
      
      @keyframes platform-border-flow {
        0% { box-shadow: 0 0 20px rgba(75, 85, 99, 0.3); }
        50% { box-shadow: 0 0 30px rgba(139, 92, 246, 0.4); }
        100% { box-shadow: 0 0 20px rgba(75, 85, 99, 0.3); }
      }
      
      .platform-connect-btn {
        background: 
          radial-gradient(circle at 20% 20%, rgba(75, 85, 99, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(55, 65, 81, 0.08) 0%, transparent 50%),
          linear-gradient(135deg, 
            rgba(15, 23, 42, 0.8) 0%, 
            rgba(30, 41, 59, 0.7) 30%, 
            rgba(51, 65, 85, 0.6) 70%, 
            rgba(15, 23, 42, 0.8) 100%
          );
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
      }
      
      .platform-connect-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
          repeating-linear-gradient(
            45deg,
            transparent 0px,
            transparent 3px,
            rgba(75, 85, 99, 0.03) 3px,
            rgba(75, 85, 99, 0.03) 6px
          );
        z-index: 1;
      }
      
      .platform-connect-btn:hover {
        background: 
          radial-gradient(circle at 20% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
          linear-gradient(135deg, 
            rgba(15, 23, 42, 0.9) 0%, 
            rgba(30, 41, 59, 0.8) 30%, 
            rgba(51, 65, 85, 0.7) 70%, 
            rgba(15, 23, 42, 0.9) 100%
          );
        animation: 
          platform-connect-glow 2s ease-in-out infinite,
          platform-border-flow 3s ease-in-out infinite;
        transform: translateY(-2px) scale(1.02);
      }
      
      .platform-connect-btn:active {
        transform: translateY(0px) scale(1);
      }
      
      .platform-connect-content {
        position: relative;
        z-index: 2;
      }
      
      .platform-icon-glow {
        transition: all 0.3s ease;
      }
      
      .platform-connect-btn:hover .platform-icon-glow {
        box-shadow: 
          0 0 20px rgba(139, 92, 246, 0.4),
          0 0 40px rgba(139, 92, 246, 0.2);
      }
    `;
    document.head.appendChild(style);
  }, []);

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        platform-connect-btn w-full
        group relative font-semibold rounded-xl transition-all duration-300 
        focus:outline-none focus:ring-2 focus:ring-purple-500/30
        p-5 text-left
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
    >
      <div className="platform-connect-content">
        {children}
      </div>
    </button>
  );
};

export default PlatformConnectButton;
