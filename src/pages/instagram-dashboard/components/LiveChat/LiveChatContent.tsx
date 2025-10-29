import React, { useState } from 'react';
import { Brain, Bot, Sparkles } from 'lucide-react';
import TrainTabContent from './TrainTabContent';
import ChatTab from './ChatTab';
import PublishTab from './PublishTab';
import { PlatformAccount } from '../../../../types/types';

interface LiveChatContentProps {
  platformAccount: PlatformAccount;
}

const LiveChatContent: React.FC<LiveChatContentProps> = ({ platformAccount }) => {
  const [activeTab, setActiveTab] = useState<'chat' | 'train' | 'publish'>('chat');

  const tabContent = {
    chat: {
      title: 'AI Chat Assistant',
      description: 'Engage with your audience using intelligent AI responses powered by advanced language models.',
      icon: <Bot className="w-5 h-5" />
    },
    train: {
      title: 'Knowledge Training',
      description: 'Train your AI with custom knowledge bases, documents, and data sources for personalized responses.',
      icon: <Brain className="w-5 h-5" />
    },
    publish: {
      title: 'Deploy & Monitor',
      description: 'Publish your trained AI assistant and monitor its performance across all platforms.',
      icon: <Sparkles className="w-5 h-5" />
    }
  };

  const currentTabContent = tabContent[activeTab];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Enhanced Header */}
      <div className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl border border-slate-700/50 shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-cyan-600/10"></div>
        <div className="relative p-8 lg:p-12">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
            <div className="flex-1 space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg">
                  {currentTabContent.icon}
                </div>
                <div>
                  <h1 className="text-3xl lg:text-4xl font-bold text-white mb-1">
                    {currentTabContent.title}
                  </h1>
                  <div className="flex items-center gap-2 text-blue-400">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium">AI-Powered Platform</span>
                  </div>
                </div>
              </div>

              <p className="text-slate-300 text-lg leading-relaxed max-w-2xl">
                {currentTabContent.description}
              </p>

              <div className="flex items-center gap-6 pt-2">
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span>Real-time responses</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                  <span>Multi-platform support</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                  <span>24/7 availability</span>
                </div>
              </div>
            </div>

            {/* Enhanced Tab Navigation */}
            <div className="lg:flex-shrink-0">
              <div className="flex items-center gap-3 p-2 bg-slate-800/50 backdrop-blur-sm border border-slate-600/50 rounded-xl shadow-lg">
                {(['chat', 'train', 'publish'] as const).map(tab => {
                  const tabInfo = tabContent[tab];
                  const isActive = activeTab === tab;

                  return (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`group relative flex items-center gap-3 px-6 py-4 rounded-lg text-sm font-semibold transition-all duration-300 min-w-[140px] justify-center ${
                        isActive
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/25'
                          : 'text-slate-300 hover:text-white hover:bg-slate-700/50 hover:shadow-md'
                      }`}
                    >
                      <div className={`transition-all duration-300 ${isActive ? 'scale-110' : 'group-hover:scale-105'}`}>
                        {tabInfo.icon}
                      </div>
                      <span className="capitalize font-medium">{tab}</span>
                      {isActive && (
                        <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-white rounded-full"></div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 shadow-xl">
        {activeTab === 'chat' ? (
          <ChatTab platformAccount={platformAccount} />
        ) : activeTab === 'train' ? (
          <TrainTabContent platformAccount={platformAccount} />
        ) : (
          <PublishTab platformAccount={platformAccount} />
        )}
      </div>
    </div>
  );
};

export default LiveChatContent;