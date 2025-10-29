import { useEffect, useRef, useState } from 'react';
import { FileText, TrendingUp, Briefcase, Search, ChevronDown } from 'lucide-react';
import { ChatInput } from '../input/ChatInput';

interface EmptyStateProps {
  onSendMessage: (text: string) => void;
  currentCredits?: number | null;
}

export function EmptyState({ onSendMessage, currentCredits }: EmptyStateProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const chatInputRef = useRef<HTMLDivElement>(null);
  const [inputValue, setInputValue] = useState("");

  // Scroll to show ChatInput on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      if (chatInputRef.current) {
        chatInputRef.current.scrollIntoView({ behavior: 'auto', block: 'center' });
      }
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  const suggestions = [
    {
      icon: <FileText size={20} />,
      title: 'Draft and send email',
      prompt: 'Draft a professional email to my team about tomorrow\'s meeting and send it to john@company.com'
    },
    {
      icon: <TrendingUp size={20} />,
      title: 'Get Instagram insights',
      prompt: 'Fetch my Instagram account insights and show me engagement stats and top performing posts from the last 7 days.'
    },
    {
      icon: <Briefcase size={20} />,
      title: 'Search jobs and email results',
      prompt: 'Find AI/ML engineer jobs in San Francisco and email me a summary with the top 5 opportunities.'
    },
    {
      icon: <Search size={20} />,
      title: 'YouTube channel analytics',
      prompt: 'Get my YouTube channel analytics including top videos, views, and demographics for the last 30 days.'
    },
  ];

  const quickChips = [
    'Read my unread emails from today',
    'Show YouTube video performance metrics',
    'Get Instagram follower growth stats',
    'Search for remote software jobs in Berlin',
    'Draft email about project deadline',
    'Check my Gmail inbox for important messages',
  ];

  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes bounceDown {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(8px); }
      }
      @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }
      @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
      }
      .bounce-down { animation: bounceDown 2s ease-in-out infinite; }
      .fade-in-up { animation: fadeInUp 0.6s ease-out forwards; }
      .gradient-shift { animation: gradientShift 3s ease infinite; }
    `;
    document.head.appendChild(style);
    return () => { document.head.removeChild(style); };
  }, []);

  const handleScrollToSuggestions = () => {
    const suggestionsElement = document.getElementById('suggestions-section');
    if (suggestionsElement) {
      suggestionsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleSuggestionClick = (prompt: string) => {
    setInputValue(prompt);
    // Scroll to the input
    if (chatInputRef.current) {
      chatInputRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  return (
    <div ref={scrollContainerRef} className="w-full h-full flex flex-col">
      {/* Main Section - ChatInput at 2/3 position */}
      <div className="flex-1 flex flex-col justify-center" style={{ paddingTop: 'calc(100vh / 6)' }}>
        <div className="max-w-[800px] mx-auto w-full px-4 fade-in-up">
          {/* Greeting Text - Left Aligned */}
          <div className="mb-8 text-left">
            <h1 className="text-3xl md:text-5xl font-bold mb-3 bg-gradient-to-r from-white via-purple-200 to-blue-200 bg-clip-text text-transparent gradient-shift" style={{ backgroundSize: '200% 200%' }}>
              Hey, ready to build?
            </h1>
            <p className="text-base md:text-lg text-gray-400 leading-relaxed">
              Ask anything. Create workflows. Automate tasks. Let's get started.
            </p>
          </div>

          {/* Enhanced ChatInput */}
          <div ref={chatInputRef} className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 rounded-2xl opacity-20 blur-xl group-hover:opacity-30 transition-opacity duration-500"></div>
            <div className="relative">
              <ChatInput 
                onSendMessage={onSendMessage} 
                currentCredits={currentCredits}
                isEnhanced={true}
                inputValue={inputValue}
                onInputChange={setInputValue}
              />
            </div>
          </div>

          {/* Scroll Down Indicator */}
          <div 
            className="mt-12 flex flex-col items-center gap-2 cursor-pointer opacity-60 hover:opacity-100 transition-opacity"
            onClick={handleScrollToSuggestions}
          >
            <p className="text-sm text-gray-500 font-medium">Try these examples</p>
            <div className="bounce-down">
              <ChevronDown size={32} className="text-purple-400" strokeWidth={2.5} />
            </div>
          </div>
        </div>
      </div>

      {/* Suggestions Section - Scrollable */}
      <div id="suggestions-section" className="max-w-[900px] mx-auto w-full px-4 pb-12 mt-24">
        <h2 className="text-xl md:text-2xl font-semibold text-white mb-6 text-left">
          Popular workflows
        </h2>

        {/* Suggestion Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-8">
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={() => handleSuggestionClick(s.prompt)}
              className="group relative flex items-start gap-4 rounded-xl p-5 text-left bg-gradient-to-br from-gray-800/40 to-gray-900/40 hover:from-gray-800/60 hover:to-gray-900/60 transition-all duration-300 border border-gray-700/50 hover:border-purple-500/50 backdrop-blur-sm"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className="w-11 h-11 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600 text-white flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                {s.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-white font-semibold text-[15px] mb-1">{s.title}</div>
                <div className="text-gray-400 text-[13px] leading-relaxed line-clamp-2">
                  {s.prompt}
                </div>
              </div>
              <div className="absolute top-3 right-3 w-2 h-2 rounded-full bg-purple-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </button>
          ))}
        </div>

        {/* Quick Chips */}
        <div className="flex flex-wrap gap-2">
          {quickChips.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSuggestionClick(q)}
              className="px-4 py-2 rounded-full text-[13px] text-white bg-gray-800/50 hover:bg-purple-600/30 transition-all duration-300 border border-gray-700/50 hover:border-purple-500/50 backdrop-blur-sm"
            >
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}