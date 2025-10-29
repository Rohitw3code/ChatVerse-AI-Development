import React from 'react';

interface CustomAutomationButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
}

const CustomAutomationButton: React.FC<CustomAutomationButtonProps> = ({
  children,
  onClick,
  className = '',
  disabled = false,
}) => {
  // Add modern automation button CSS styles on component mount
  React.useEffect(() => {
    const existingStyle = document.getElementById('custom-automation-button-styles');
    if (existingStyle) return;

    const style = document.createElement('style');
    style.id = 'custom-automation-button-styles';
    style.textContent = `
      @keyframes gentle-glow {
        0%, 100% { 
          box-shadow: 
            0 4px 20px rgba(0, 0, 0, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }
        50% { 
          box-shadow: 
            0 8px 30px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(255, 255, 255, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
      }
      
      @keyframes subtle-pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.01); }
      }
      
      .custom-automation-btn {
        background: linear-gradient(135deg, 
          rgba(0, 0, 0, 0.95) 0%, 
          rgba(15, 15, 15, 0.9) 50%, 
          rgba(0, 0, 0, 0.95) 100%
        );
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(16px);
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }
      
      .custom-automation-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(
          135deg,
          rgba(255, 255, 255, 0.1) 0%,
          transparent 50%,
          rgba(255, 255, 255, 0.05) 100%
        );
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 1;
      }
      
      .custom-automation-btn:hover {
        transform: translateY(-2px);
        box-shadow: 
          0 12px 40px rgba(0, 0, 0, 0.6),
          0 0 0 1px rgba(255, 255, 255, 0.2),
          inset 0 1px 0 rgba(255, 255, 255, 0.15);
      }
      
      .custom-automation-btn:hover::before {
        opacity: 1;
      }
      
      .custom-automation-btn:active {
        transform: translateY(-1px) scale(0.98);
        transition: all 0.1s ease;
      }
      
      .custom-automation-content {
        position: relative;
        z-index: 2;
      }
      
      .automation-icon-container {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
      }
      
      .automation-icon-container:hover {
        background: rgba(0, 0, 0, 0.8);
        border-color: rgba(255, 255, 255, 0.3);
        transform: scale(1.05);
      }
    `;
    document.head.appendChild(style);
  }, []);

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        custom-automation-btn
        group relative font-medium rounded-xl
        focus:outline-none focus:ring-2 focus:ring-purple-500/30 focus:ring-offset-2 focus:ring-offset-transparent
        px-6 py-4 text-base sm:px-8 sm:py-5 lg:px-10 lg:py-6 sm:text-lg
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
    >
      <div className="custom-automation-content">
        {children}
      </div>
    </button>
  );
};

export default CustomAutomationButton;
