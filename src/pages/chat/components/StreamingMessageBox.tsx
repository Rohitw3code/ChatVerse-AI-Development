import { useEffect, useRef, useState } from 'react';
import { Markdown } from '../ui/components/Markdown';
import { ApiMessage } from '../types';
import { STREAMING_PRESETS } from './StreamingConfig';

interface StreamingMessageBoxProps {
  message: ApiMessage;
  isClosing?: boolean;
  onAnimationComplete?: () => void;
  config?: keyof typeof STREAMING_PRESETS;
}

export function StreamingMessageBox({ message, isClosing = false, onAnimationComplete, config = 'default' }: StreamingMessageBoxProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const content = message.current_messages?.[0]?.content || '';
  const [isScrolledToBottom, setIsScrolledToBottom] = useState(true);
  const streamingConfig = STREAMING_PRESETS[config];

  useEffect(() => {
    if (scrollRef.current) {
      const scrollElement = scrollRef.current;
      const shouldAutoScroll = isScrolledToBottom || !content;
      
      if (shouldAutoScroll) {
        scrollElement.scrollTo({
          top: scrollElement.scrollHeight,
          behavior: 'smooth'
        });
      }
    }
  }, [message.current_messages, isScrolledToBottom, content]);

  useEffect(() => {
    const scrollElement = scrollRef.current;
    if (scrollElement) {
      const observer = new MutationObserver(() => {
        scrollElement.scrollTo({
          top: scrollElement.scrollHeight,
          behavior: 'smooth'
        });
      });

      observer.observe(scrollElement, {
        childList: true,
        subtree: true,
        characterData: true
      });

      return () => observer.disconnect();
    }
  }, []);

  useEffect(() => {
    if (isClosing && onAnimationComplete) {
      const timer = setTimeout(() => {
        onAnimationComplete();
      }, streamingConfig.animation.duration);
      return () => clearTimeout(timer);
    }
  }, [isClosing, onAnimationComplete, streamingConfig.animation.duration]);

  useEffect(() => {
    const scrollElement = scrollRef.current;
    if (!scrollElement) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = scrollElement;
      const isAtBottom = Math.abs(scrollHeight - clientHeight - scrollTop) < 5;
      setIsScrolledToBottom(isAtBottom);
    };

    scrollElement.addEventListener('scroll', handleScroll);
    return () => scrollElement.removeEventListener('scroll', handleScroll);
  }, []);

  const animationClasses = isClosing ? 'animate-fold-up' : 'animate-unfold-down';

  return (
    <div
      className={`relative overflow-hidden rounded-lg border border-gray-700/50 bg-gray-800/20 backdrop-blur-sm my-2 w-full max-w-[70%] sm:max-w-[65%] md:max-w-[60%] lg:max-w-[55%] ${animationClasses}`}
      style={{ animationDuration: `${streamingConfig.animation.duration}ms` }}
      onAnimationEnd={() => {
        if (isClosing && onAnimationComplete) {
          onAnimationComplete();
        }
      }}
    >
      <div className="absolute top-0 left-0 w-full h-4 bg-gradient-to-b from-gray-800/50 to-transparent pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-full h-4 bg-gradient-to-t from-gray-800/50 to-transparent pointer-events-none" />
      
      <div
        ref={scrollRef}
        className="max-h-[180px] sm:max-h-[160px] lg:max-h-[140px] overflow-y-auto p-3 text-sm text-gray-300 scrollbar-none"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        <div className="flex items-center text-gray-400 mb-2">
          <div className="thinking-dots mr-3">
            <span />
            <span />
            <span />
          </div>
          {message.node && <span className="font-mono text-xs opacity-70">{message.node}...</span>}
        </div>
        
        {content && (
          <div className="max-w-none break-words text-gray-300 leading-snug space-y-1">
            <Markdown>{content}</Markdown>
          </div>
        )}
      </div>
    </div>
  );
}