import React, { useLayoutEffect, useRef, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, Plus, Sparkles } from 'lucide-react';

const SendIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>;

interface ChatInputProps {
  onSendMessage: (text: string) => void;
  isKeyboardOpen?: boolean;
  currentCredits?: number | null;
  isEnhanced?: boolean;
  onInputChange?: (text: string) => void;
  inputValue?: string;
}

export function ChatInput({ onSendMessage, isKeyboardOpen = false, currentCredits, isEnhanced = false, onInputChange, inputValue }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const navigate = useNavigate();

  // Sync with external input value if provided
  useEffect(() => {
    if (inputValue !== undefined && inputValue !== input) {
      setInput(inputValue);
      // Focus the textarea when external value is set
      if (inputValue && textareaRef.current) {
        textareaRef.current.focus();
        // Set cursor at the end
        const length = inputValue.length;
        textareaRef.current.setSelectionRange(length, length);
      }
    }
  }, [inputValue]);

  useLayoutEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const scrollHeight = textarea.scrollHeight;
      const maxHeight = 200;
      if (scrollHeight > maxHeight) {
        textarea.style.height = `${maxHeight}px`;
        textarea.style.overflowY = 'auto';
      } else {
        textarea.style.height = `${scrollHeight}px`;
        textarea.style.overflowY = 'hidden';
      }
    }
  }, [input]);

  const handleInputChange = (newValue: string) => {
    setInput(newValue);
    if (onInputChange) {
      onInputChange(newValue);
    }
  };

  const send = () => {
    onSendMessage(input);
    setInput("");
    if (onInputChange) {
      onInputChange("");
    }
  };

  const handleUpgrade = () => {
    navigate('/pricing');
  };

  const preventTouchDrag = (e: React.TouchEvent) => {
    if (isKeyboardOpen) {
      e.preventDefault();
    }
  };

  // Add animations
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
      }
      @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(234, 88, 12, 0.1), 0 0 40px rgba(234, 88, 12, 0.05); }
        50% { box-shadow: 0 0 25px rgba(234, 88, 12, 0.2), 0 0 50px rgba(234, 88, 12, 0.1); }
      }
      .shimmer-effect {
        background: linear-gradient(
          90deg,
          transparent,
          rgba(234, 88, 12, 0.1),
          transparent
        );
        background-size: 200% 100%;
        animation: shimmer 3s infinite;
      }
      .pulse-glow {
        animation: pulseGlow 3s ease-in-out infinite;
      }
    `;
    document.head.appendChild(style);
    return () => { document.head.removeChild(style); };
  }, []);

  return (
    <div className="flex-shrink-0 pt-2 pb-0" onTouchStart={preventTouchDrag} onTouchMove={preventTouchDrag}>
      {/* Main Input */}
      <div className={`relative rounded-2xl transition-all duration-300 ease-in-out ${
        isEnhanced 
          ? 'bg-gray-900/80 border border-gray-700/50 backdrop-blur-xl min-h-[140px] px-4 py-3 focus-within:border-orange-600/50 hover:border-gray-600/50' 
          : ''
      }`}>
        {/* Non-enhanced (compact) version with modern glass design */}
        {!isEnhanced && (
          <div className="relative group">
            {/* Gradient glow background */}
            <div className="absolute -inset-[1px] bg-gradient-to-r from-orange-600/20 via-orange-500/20 to-orange-600/20 rounded-2xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 blur-sm"></div>
            
            {/* Main container */}
            <div className="relative bg-gradient-to-br from-[#1a1a1a] via-[#151515] to-[#0a0a0a] backdrop-blur-xl border border-gray-700/50 group-focus-within:border-orange-600 rounded-2xl px-4 py-2.5 transition-all duration-300 shadow-lg shadow-black/20">
              {/* Shimmer overlay on focus */}
              <div className="absolute inset-0 rounded-2xl overflow-hidden opacity-0 group-focus-within:opacity-100 transition-opacity duration-300">
                <div className="shimmer-effect absolute inset-0"></div>
              </div>
              
              {/* Upgrade button */}
              {currentCredits !== null && currentCredits !== undefined && currentCredits <= 0 && (
                <button
                  type="button"
                  onClick={handleUpgrade}
                  aria-label="Upgrade Plan"
                  className="absolute -top-10 left-0 flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-600 text-white rounded-lg text-xs font-semibold transition-all duration-200 flex-shrink-0 z-10 shadow-lg shadow-orange-500/20 hover:shadow-orange-500/40"
                  title="Upgrade Plan"
                >
                  <Sparkles className="w-3 h-3" />
                  <span>Upgrade for credits</span>
                </button>
              )}
              
              {/* Textarea */}
              <div className="relative flex items-center gap-3">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => handleInputChange(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      if (input.trim()) send();
                    }
                  }}
                  placeholder="Message ChatVerse..."
                  className="flex-1 bg-transparent text-white placeholder:text-gray-500 border-none outline-none focus:ring-0 resize-none text-[15px] leading-6 min-h-[40px] max-h-[200px] py-2"
                  rows={1}
                  style={{ verticalAlign: 'middle' }}
                />
                
                {/* Action buttons */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  {/* Add platforms button */}
                  <button 
                    onClick={() => navigate('/platforms')}
                    className="group/btn w-9 h-9 rounded-xl flex items-center justify-center bg-gray-800/80 hover:bg-gray-700/80 border border-gray-700/50 hover:border-orange-600 cursor-pointer transition-all duration-200 hover:scale-105 active:scale-95" 
                    title="Add platforms"
                    aria-label="Add platforms"
                  >
                    <Plus size={18} className="text-gray-400 group-hover/btn:text-orange-500 transition-colors duration-200" />
                  </button>
                  
                  {/* Send button with gradient */}
                  <button 
                    onClick={send} 
                    className="relative w-9 h-9 rounded-xl flex items-center justify-center cursor-pointer transition-all duration-200 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 overflow-hidden group/send" 
                    title="Send message"
                    disabled={!input.trim()}
                    aria-label="Send"
                  >
                    {/* Gradient background */}
                    <div className={`absolute inset-0 bg-gradient-to-r transition-all duration-300 ${
                      !input.trim() 
                        ? 'from-gray-700 to-gray-600' 
                        : 'from-orange-600 via-orange-500 to-orange-600 group-hover/send:from-orange-500 group-hover/send:via-orange-400 group-hover/send:to-orange-500'
                    }`} style={{ backgroundSize: '200% 100%' }}></div>
                    
                    {/* Glow effect */}
                    {input.trim() && (
                      <div className="absolute inset-0 bg-gradient-to-r from-orange-400/0 via-white/20 to-orange-400/0 opacity-0 group-hover/send:opacity-100 transition-opacity duration-300"></div>
                    )}
                    
                    {/* Icon */}
                    <div className="relative z-10">
                      <SendIcon />
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Enhanced version (keep original for empty state) */}
        {isEnhanced && (
          <>
            {currentCredits !== null && currentCredits !== undefined && currentCredits <= 0 && (
              <button
                type="button"
                onClick={handleUpgrade}
                aria-label="Upgrade Plan"
                className="absolute top-3 left-3 flex items-center gap-1 px-3 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-md text-xs font-semibold transition-all duration-200 flex-shrink-0 z-10"
                title="Upgrade Plan"
              >
                <TrendingUp className="w-3 h-3" />
                <span className="hidden sm:inline">Upgrade</span>
              </button>
            )}
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => handleInputChange(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (input.trim()) send();
                }
              }}
              placeholder="Ask anything or type '/' for commands..."
              className="w-full text-white placeholder:text-gray-500 border-none outline-none focus:ring-0 resize-none bg-transparent text-[16px] leading-7 pr-24 pb-14 pt-1 min-h-[110px]"
              rows={1}
              style={{ verticalAlign: 'top' }}
            />
            <div className="absolute bottom-3 right-3 flex items-center gap-2">
              <button 
                onClick={() => navigate('/platforms')}
                className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-gray-700 hover:bg-gray-600 border border-gray-600 cursor-pointer transition-all duration-150 ease-in-out" 
                title="Add platforms"
                aria-label="Add platforms"
              >
                <Plus size={20} className="text-white" />
              </button>
              <button 
                onClick={send} 
                className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-orange-600 hover:bg-orange-700 cursor-pointer transition-all duration-150 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed" 
                title="Send message"
                disabled={!input.trim()}
                aria-label="Send"
              >
                <SendIcon />
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
