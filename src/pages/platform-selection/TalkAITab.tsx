import React from 'react';
import { ArrowRight, Brain, Plus, Sparkles, Workflow, MessageSquare, Settings } from 'lucide-react';
import { PlatformAccount } from '../../types/types';
import { CreditDisplay } from '../../components/common/CreditDisplay';
import { useNavigate } from 'react-router-dom';
import FabricButton from './components/FabricButton';

interface TalkAITabProps {
  connectedAccounts: PlatformAccount[];
  onTalkToAiClick: () => void;
  credits: number | null;
}

export const TalkAITab: React.FC<TalkAITabProps> = ({ connectedAccounts, onTalkToAiClick, credits }) => {
  const navigate = useNavigate();

  const handleAddCredits = () => {
    navigate('/pricing');
  };

  const handleUpgrade = () => {
    navigate('/pricing');
  };
  
  const fabricBackgroundStyle = "bg-black bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]";

  const FeatureCard = ({ icon, title, description, accentColor, actionText }: { icon: React.ReactNode; title: string; description: string; accentColor: string; actionText: string; }) => {
    const accentStyle = {
      '--accent-color': accentColor,
    } as React.CSSProperties;

    return (
      <div style={accentStyle} className={`group relative p-6 rounded-2xl border border-white/10 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 overflow-hidden ${fabricBackgroundStyle}`}>
        <div className="absolute inset-0 bg-gradient-to-br from-[var(--accent-color)]/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        <div className="absolute top-0 left-0 w-24 h-24 bg-[var(--accent-color)]/5 rounded-full blur-2xl opacity-0 group-hover:opacity-50 transition-opacity duration-300"></div>
        
        <div className="relative z-10">
          <div className="w-14 h-14 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
            {icon}
          </div>
          <h3 className="text-white font-bold text-xl mb-3">{title}</h3>
          <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
          <div className="mt-4 flex items-center text-[var(--accent-color)] text-sm font-medium">
            <span>{actionText}</span>
            <ArrowRight className="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full bg-black">
      <main className="relative z-10 max-w-6xl mx-auto">
        {/* Enhanced Hero Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          {/* Main Hero Content */}
          <div className={`lg:col-span-2 relative rounded-2xl border border-white/10 shadow-2xl shadow-black/40 overflow-hidden ${fabricBackgroundStyle}`}>
            <div className="absolute top-0 right-0 w-48 h-48 bg-gray-800/20 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 left-0 w-32 h-32 bg-gray-800/20 rounded-full blur-2xl"></div>
            
            <div className="relative z-10 p-8 lg:p-12">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center shadow-xl">
                  <Brain className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h2 className="text-white font-bold text-3xl lg:text-4xl leading-tight">
                    ChatVerse AI
                  </h2>
                  <p className="text-gray-400 font-medium">Query-Based Automation</p>
                </div>
              </div>
              
              <p className="text-gray-300 text-lg leading-relaxed mb-8 max-w-2xl">
                Transform natural language queries into powerful automation workflows. Connect your platforms and let AI handle the complexity.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <FabricButton
                  onClick={onTalkToAiClick}
                  variant="primary"
                  size="large"
                  className="shadow-lg"
                >
                  <MessageSquare className="w-5 h-5" />
                  Start Conversation
                  <ArrowRight className="w-5 h-5" />
                </FabricButton>
                
                <FabricButton
                  variant="outline"
                  size="large"
                  className="text-gray-300 hover:text-white"
                >
                  <Settings className="w-5 h-5" />
                  View Examples
                </FabricButton>
              </div>
            </div>
          </div>

          {/* Credit Display Card */}
          <div className="lg:col-span-1">
            <CreditDisplay
              credits={credits || 0}
              onAddCredits={handleAddCredits}
              onUpgrade={handleUpgrade}
              variant="card"
              className={`h-full border border-white/10 ${fabricBackgroundStyle}`}
            />
          </div>
        </div>
        
        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          <FeatureCard
            icon={<Plus className="w-7 h-7 text-green-400" />}
            title="Connect Platforms"
            description="Link your social media and tools to enable cross-platform automation workflows."
            accentColor="#34d399" // green-400
            actionText="Get Started"
          />
          <FeatureCard
            icon={<Sparkles className="w-7 h-7 text-blue-400" />}
            title="Smart Automation"
            description="Describe what you want in plain English and watch AI create sophisticated workflows."
            accentColor="#60a5fa" // blue-400
            actionText="Try Now"
          />
          <FeatureCard
            icon={<Workflow className="w-7 h-7 text-purple-400" />}
            title="Manage Workflows"
            description="Monitor, edit, and optimize your automations with real-time insights and controls."
            accentColor="#a78bfa" // purple-400
            actionText="View Dashboard"
          />
        </div>

        {/* Connected Accounts Summary */}
        {connectedAccounts.length > 0 && (
          <div className={`rounded-2xl border border-white/10 p-6 ${fabricBackgroundStyle}`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-bold text-lg">Connected Accounts</h3>
              <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-medium">
                {connectedAccounts.length} Connected
              </span>
            </div>
            <p className="text-gray-400 text-sm mb-4">
              Your connected platforms are ready for AI-powered automation. Start a conversation to create workflows.
            </p>
            <div className="flex flex-wrap gap-2">
              {connectedAccounts.slice(0, 5).map((account) => (
                <div key={account.id} className="flex items-center gap-2 px-3 py-2 bg-white/5 rounded-lg border border-white/10">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-white text-sm font-medium capitalize">{account.platform}</span>
                </div>
              ))}
              {connectedAccounts.length > 5 && (
                <div className="flex items-center gap-2 px-3 py-2 bg-white/5 rounded-lg border border-white/10">
                  <span className="text-gray-400 text-sm">+{connectedAccounts.length - 5} more</span>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};