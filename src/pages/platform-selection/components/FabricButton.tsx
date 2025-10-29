import React from 'react';

interface FabricButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'selected';
  size?: 'small' | 'medium' | 'large';
  className?: string;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  fullWidth?: boolean;
}

const FabricButton: React.FC<FabricButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'medium',
  className = '',
  disabled = false,
  type = 'button',
  fullWidth = false,
}) => {
  // Add fabric design CSS animations on component mount
  React.useEffect(() => {
    const existingStyle = document.getElementById('platform-fabric-button-styles');
    if (existingStyle) return;

    const style = document.createElement('style');
    style.id = 'platform-fabric-button-styles';
    style.textContent = `
      @keyframes fabric-flow {
        0% { background-position: 0% 0%, 0% 0%, 0% 0%; }
        50% { background-position: 100% 50%, 50% 100%, 25% 75%; }
        100% { background-position: 200% 100%, 100% 200%, 50% 150%; }
      }
      
      @keyframes fabric-flow-reverse {
        0% { background-position: 200% 100%, 100% 200%, 50% 150%; }
        50% { background-position: 100% 50%, 50% 100%, 25% 75%; }
        100% { background-position: 0% 0%, 0% 0%, 0% 0%; }
      }
      
      @keyframes laser-sweep {
        0% { transform: translateX(-100%) skewX(-15deg); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateX(100%) skewX(-15deg); opacity: 0; }
      }
      
      @keyframes laser-sweep-delayed {
        0% { transform: translateX(-100%) skewX(-15deg); opacity: 0; }
        25% { opacity: 0; }
        75% { opacity: 1; }
        100% { transform: translateX(100%) skewX(-15deg); opacity: 0; }
      }
      
      .platform-fabric-btn-primary {
        background: 
          radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 50%),
          repeating-linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.08) 0px,
            rgba(255, 255, 255, 0.08) 1px,
            transparent 1px,
            transparent 8px
          ),
          repeating-linear-gradient(
            -45deg,
            rgba(255, 255, 255, 0.04) 0px,
            rgba(255, 255, 255, 0.04) 1px,
            transparent 1px,
            transparent 12px
          ),
          linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #0a0a0a 100%);
        background-size: 200% 200%, 150% 150%, 16px 16px, 24px 24px, 100% 100%;
        background-blend-mode: overlay, multiply, normal, normal, normal;
      }
      
      .platform-fabric-btn-primary:hover {
        animation: fabric-flow 3s ease-in-out infinite;
        box-shadow: 
          0 0 30px rgba(255, 255, 255, 0.2),
          0 8px 32px rgba(0, 0, 0, 0.4),
          inset 0 1px 0 rgba(255, 255, 255, 0.2);
      }
      
      .platform-fabric-btn-secondary {
        background: 
          radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.08) 0%, transparent 50%),
          repeating-linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.12) 0px,
            rgba(255, 255, 255, 0.12) 1px,
            transparent 1px,
            transparent 8px
          ),
          repeating-linear-gradient(
            -45deg,
            rgba(255, 255, 255, 0.06) 0px,
            rgba(255, 255, 255, 0.06) 1px,
            transparent 1px,
            transparent 12px
          ),
          linear-gradient(135deg, #ffffff 0%, #f5f5f5 50%, #e5e5e5 100%);
        background-size: 200% 200%, 150% 150%, 16px 16px, 24px 24px, 100% 100%;
        background-blend-mode: overlay, multiply, normal, normal, normal;
      }
      
      .platform-fabric-btn-secondary:hover {
        animation: fabric-flow-reverse 3s ease-in-out infinite;
        box-shadow: 
          0 0 30px rgba(0, 0, 0, 0.3),
          0 8px 32px rgba(0, 0, 0, 0.2),
          inset 0 1px 0 rgba(255, 255, 255, 0.3);
      }
      
      .platform-fabric-btn-outline {
        background: 
          radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.05) 0%, transparent 60%),
          repeating-linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.04) 0px,
            rgba(255, 255, 255, 0.04) 1px,
            transparent 1px,
            transparent 6px
          ),
          linear-gradient(135deg, transparent 0%, rgba(0, 0, 0, 0.2) 100%);
        background-size: 150% 150%, 12px 12px, 100% 100%;
      }
      
      .platform-fabric-btn-outline:hover {
        background: 
          radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.1) 0%, transparent 60%),
          repeating-linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.08) 0px,
            rgba(255, 255, 255, 0.08) 1px,
            transparent 1px,
            transparent 6px
          ),
          linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.05) 100%);
        box-shadow: 
          0 0 20px rgba(255, 255, 255, 0.2),
          0 4px 16px rgba(0, 0, 0, 0.3);
      }
      
      .platform-fabric-btn-selected {
        background: 
          radial-gradient(circle at 20% 20%, rgba(249, 115, 22, 0.2) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(234, 88, 12, 0.15) 0%, transparent 50%),
          repeating-linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.1) 0px,
            rgba(255, 255, 255, 0.1) 1px,
            transparent 1px,
            transparent 8px
          ),
          repeating-linear-gradient(
            -45deg,
            rgba(255, 255, 255, 0.06) 0px,
            rgba(255, 255, 255, 0.06) 1px,
            transparent 1px,
            transparent 12px
          ),
          linear-gradient(135deg, #ea580c 0%, #f97316 50%, #fb923c 100%);
        background-size: 200% 200%, 150% 150%, 16px 16px, 24px 24px, 100% 100%;
        background-blend-mode: overlay, multiply, normal, normal, normal;
      }
      
      .platform-fabric-btn-selected:hover {
        animation: fabric-flow 3s ease-in-out infinite;
        box-shadow: 
          0 0 30px rgba(249, 115, 22, 0.4),
          0 8px 32px rgba(234, 88, 12, 0.3),
          inset 0 1px 0 rgba(255, 255, 255, 0.3);
      }
      
      .laser-effect {
        position: relative;
        overflow: hidden;
      }
      
      .laser-effect::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(
          90deg,
          transparent,
          rgba(255, 255, 255, 0.4),
          transparent
        );
        transform: translateX(-100%) skewX(-15deg);
        transition: transform 0.6s;
        z-index: 1;
      }
      
      .laser-effect:hover::before {
        animation: laser-sweep 1.5s ease-out;
      }
      
      .laser-effect::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(
          90deg,
          transparent,
          rgba(255, 255, 255, 0.2),
          transparent
        );
        transform: translateX(-100%) skewX(-15deg);
        z-index: 1;
      }
      
      .laser-effect:hover::after {
        animation: laser-sweep-delayed 1.5s ease-out;
      }
    `;
    document.head.appendChild(style);
  }, []);

  const getSizeClasses = () => {
    switch (size) {
      case 'small':
        return 'px-3 py-2 text-sm sm:px-4 sm:py-2';
      case 'large':
        return 'px-6 py-3 text-base sm:px-8 sm:py-4 lg:px-10 lg:py-5 sm:text-lg';
      default:
        return 'px-4 py-2.5 text-sm sm:px-6 sm:py-3 sm:text-base';
    }
  };

  const getVariantClasses = () => {
    switch (variant) {
      case 'secondary':
        return 'platform-fabric-btn-secondary border-black/30 hover:border-black/50 shadow-lg hover:shadow-black/25';
      case 'outline':
        return 'platform-fabric-btn-outline border-gray-700/50 hover:border-gray-600/70 shadow-lg hover:shadow-white/10';
      case 'selected':
        return 'platform-fabric-btn-selected border-orange-500/50 hover:border-orange-400/70 shadow-lg shadow-orange-500/20 hover:shadow-orange-500/30';
      default:
        return 'platform-fabric-btn-primary border-gray-700/50 hover:border-gray-600/70 shadow-lg hover:shadow-black/25';
    }
  };

  const getTextColor = () => {
    if (variant === 'secondary') return 'text-black';
    if (variant === 'selected') return 'text-white font-bold';
    return 'text-white';
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        group relative font-semibold rounded-2xl transition-all duration-300 
        transform hover:scale-105 focus:outline-none focus:ring-4 
        ${variant === 'secondary' ? 'focus:ring-black/20' : 'focus:ring-gray-500/20'}
        laser-effect border-2 
        ${getSizeClasses()} 
        ${getVariantClasses()} 
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
    >
      <span className={`relative z-10 flex items-center justify-center gap-3 ${getTextColor()}`}>
        {children}
      </span>
    </button>
  );
};

export default FabricButton;
