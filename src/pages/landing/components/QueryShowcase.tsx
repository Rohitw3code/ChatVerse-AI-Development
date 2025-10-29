import React from 'react';
import { Bot, BarChart3, Sparkles, Rocket, Zap, Brain, Code, ListChecks, Instagram, Facebook, MessageSquare, Clock, Send, Mail } from 'lucide-react';
import { useAuthStore } from '../../../stores';
import FabricButton from './FabricButton';

interface QueryShowcaseProps {
  handleGetStarted: () => void;
  handleUseAI: () => void;
}

const QueryShowcase: React.FC<QueryShowcaseProps> = ({ handleGetStarted, handleUseAI }) => {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = React.useState('query');

  const queriesData = React.useMemo(() => [
    {
      text: 'Create and publish an Instagram post, then reply positively to all comments that have not yet received a response.',
      chips: [
        { label: 'Instagram Post', icon: <Instagram className="w-4 h-4" /> },
        { label: 'Auto-Reply', icon: <MessageSquare className="w-4 h-4" /> },
        { label: 'Positive Tone', icon: <Sparkles className="w-4 h-4" /> },
      ],
    },
    {
      text: 'Send a daily report at 12:00 AM to my Slack #general channel with comment counts and reel views.',
      chips: [
        { label: 'Daily 12 AM', icon: <Clock className="w-4 h-4" /> },
        { label: 'Reels Insights', icon: <BarChart3 className="w-4 h-4" /> },
        { label: 'Send to Slack', icon: <Send className="w-4 h-4" /> },
      ],
    },
    {
      text: 'When a Facebook Reel exceeds 100k views, post it to Instagram with the same caption and send the product link to users who comment "I want to buy product".',
      chips: [
        { label: 'Facebook Reels >100k', icon: <Facebook className="w-4 h-4" /> },
        { label: 'Cross-post to IG', icon: <Instagram className="w-4 h-4" /> },
        { label: 'DM Product Link', icon: <Mail className="w-4 h-4" /> },
      ],
    },
  ], []);

  const [qIndex, setQIndex] = React.useState(0);
  const [subIndex, setSubIndex] = React.useState(0);
  const [isDeleting, setIsDeleting] = React.useState(false);
  const [blink, setBlink] = React.useState(true);

  const currentQuery = queriesData[qIndex].text;
  const displayText = currentQuery.slice(0, subIndex);

  React.useEffect(() => {
    const id = setInterval(() => setBlink((b) => !b), 500);
    return () => clearInterval(id);
  }, []);

  React.useEffect(() => {
    if (!isDeleting && subIndex === currentQuery.length) {
      const hold = setTimeout(() => setIsDeleting(true), 1400);
      return () => clearTimeout(hold);
    }

    if (isDeleting && subIndex === 0) {
      setIsDeleting(false);
      setQIndex((i) => (i + 1) % queriesData.length);
      return;
    }

    const next = setTimeout(() => {
      setSubIndex((v) => v + (isDeleting ? -1 : 1));
    }, isDeleting ? 18 : 38);

    return () => clearTimeout(next);
  }, [subIndex, isDeleting, currentQuery.length, queriesData.length]);

  return (
    <section id="query-showcase" className="mx-auto max-w-4xl w-full px-4 sm:px-0 mt-24">
      <div className="flex items-center justify-center mb-8">
        <div className="relative p-1 backdrop-blur-sm rounded-2xl border border-white/15" style={{
          background: `
            repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
            repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
            linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%)
          `,
          backgroundSize: '40px 40px, 40px 40px, 100% 100%'
        }}>
          <div className="flex space-x-1">
            <button
              onClick={() => setActiveTab('query')}
              className={`relative px-6 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${activeTab === 'query'
                ? 'text-white'
                : 'text-gray-400 hover:text-gray-300'
                }`}
            >
              {activeTab === 'query' && (
                <div className="absolute inset-0 rounded-xl border-2 shadow-lg" style={{
                  background: `
                    repeating-linear-gradient(45deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 1px, transparent 1px, transparent 20px),
                    repeating-linear-gradient(-45deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 20px),
                    linear-gradient(135deg, rgba(40,40,40,0.8) 0%, rgba(30,30,30,0.6) 100%)
                  `,
                  backgroundSize: '44px 44px, 44px 44px, 100% 100%',
                  borderColor: 'rgba(139, 92, 246, 0.6)',
                  boxShadow: '0 0 20px rgba(139, 92, 246, 0.3)'
                }} />
              )}
              <span className="relative z-10 flex items-center gap-2">
                <Bot className="w-4 h-4" />
                Query-Based
              </span>
            </button>
            <button
              onClick={() => setActiveTab('data')}
              className={`relative px-6 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${activeTab === 'data'
                ? 'text-white'
                : 'text-gray-400 hover:text-gray-300'
                }`}
            >
              {activeTab === 'data' && (
                <div className="absolute inset-0 rounded-xl border-2 shadow-lg" style={{
                  background: `
                    repeating-linear-gradient(45deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 1px, transparent 1px, transparent 20px),
                    repeating-linear-gradient(-45deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 20px),
                    linear-gradient(135deg, rgba(40,40,40,0.8) 0%, rgba(30,30,30,0.6) 100%)
                  `,
                  backgroundSize: '44px 44px, 44px 44px, 100% 100%',
                  borderColor: 'rgba(6, 182, 212, 0.6)',
                  boxShadow: '0 0 20px rgba(6, 182, 212, 0.3)'
                }} />
              )}
              <span className="relative z-10 flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                Data-Driven
              </span>
            </button>
          </div>
        </div>
      </div>

      {activeTab === 'query' && (
        <div className="p-[2px] rounded-2xl bg-gradient-to-r from-purple-900/40 via-fuchsia-800/30 to-pink-800/30 shadow-[0_0_60px_-12px_rgba(168,85,247,0.25)]">
          <div
            className="rounded-2xl backdrop-blur-sm border border-gray-800"
            style={{
              background: `
                repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
                repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
                linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%)
              `,
              backgroundSize: '40px 40px, 40px 40px, 100% 100%'
            }}
          >
            <div className="flex items-center justify-between px-3 sm:px-4 py-3 border-b border-gray-800">
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="w-6 h-6 sm:w-8 sm:h-8 rounded-lg bg-gradient-to-br from-purple-700 to-pink-600 flex items-center justify-center">
                  <Bot className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
                </div>
                <p className="text-xs sm:text-sm text-gray-300" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                  Ask in plain English — ChatVerse converts it into automation
                </p>
              </div>

              <div className="hidden sm:flex items-center gap-2 text-xs text-gray-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" aria-hidden="true" />
                <span>Live preview</span>
              </div>
            </div>
            <div className="px-3 sm:px-4 py-4 sm:py-5">
              <div className="flex flex-col gap-3 sm:gap-4">
                <div className="w-full">
                  <div className="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 rounded-xl border border-white/15" style={{
                    background: `
                      repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
                      repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
                      linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%)
                    `,
                    backgroundSize: '40px 40px, 40px 40px, 100% 100%'
                  }}>
                    <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-pink-400 flex-shrink-0" />

                    <div
                      aria-live="polite"
                      className="text-left text-sm sm:text-base md:text-lg text-gray-100 whitespace-pre-wrap break-words flex-1 min-h-[1.5rem]"
                      style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
                    >
                      {displayText}
                      <span
                        className={
                          blink
                            ? 'inline-block ml-1 align-middle h-4 sm:h-5 w-[1px] bg-gray-100 animate-pulse'
                            : 'inline-block ml-1 align-middle h-4 sm:h-5 w-[1px] bg-gray-100 opacity-40'
                        }
                      />
                    </div>

                    <FabricButton
                      onClick={handleGetStarted}
                      variant="primary"
                      size="small"
                      className="hidden md:inline-flex flex-shrink-0"
                    >
                      <Rocket className="w-4 h-4" />
                      {user ? 'Dashboard' : 'Generate'}
                    </FabricButton>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1.5 sm:gap-2 justify-center sm:justify-start">
                  {queriesData[qIndex].chips.map((c, i) => (
                    <div
                      key={i}
                      className="group inline-flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1 sm:py-1.5 rounded-full border border-white/15 hover:border-white/25 transition-all"
                      style={{
                        background: `
                          repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
                          repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
                          linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%)
                        `,
                        backgroundSize: '40px 40px, 40px 40px, 100% 100%'
                      }}
                    >
                      <span className="opacity-80 text-gray-200 text-xs sm:text-sm">{c.icon}</span>
                      <span className="text-[10px] sm:text-xs text-gray-300 whitespace-nowrap" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                        {c.label}
                      </span>
                    </div>
                  ))}
                </div>
                <div className="mt-2 sm:mt-1">
                  <div className="sm:hidden flex flex-col gap-2">
                    <div className="p-2 rounded-lg border border-white/15 flex items-center gap-2" style={{
                      background: `
                        repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
                        repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
                        linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%)
                      `,
                      backgroundSize: '40px 40px, 40px 40px, 100% 100%'
                    }}>
                      <div className="w-6 h-6 rounded-md bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center flex-shrink-0">
                        <Code className="w-3 h-3 text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-300 font-medium">Parse</p>
                        <p className="text-[10px] text-gray-400">Understand intent</p>
                      </div>
                    </div>

                    <div className="p-2 rounded-lg border border-white/15 flex items-center gap-2" style={{
                      background: `
                        repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
                        repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
                        linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%)
                      `,
                      backgroundSize: '40px 40px, 40px 40px, 100% 100%'
                    }}>
                      <div className="w-6 h-6 rounded-md bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center flex-shrink-0">
                        <ListChecks className="w-3 h-3 text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-300 font-medium">Plan</p>
                        <p className="text-[10px] text-gray-400">Map tasks & checks</p>
                      </div>
                    </div>

                    <div className="p-2 rounded-lg border border-white/15 flex items-center gap-2" style={{
                      background: `
                        repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
                        repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
                        linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%)
                      `,
                      backgroundSize: '40px 40px, 40px 40px, 100% 100%'
                    }}>
                      <div className="w-6 h-6 rounded-md bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center flex-shrink-0">
                        <Zap className="w-3 h-3 text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-300 font-medium">Run</p>
                        <p className="text-[10px] text-gray-400">Post · Reply · Notify</p>
                      </div>
                    </div>
                  </div>
                  <div className="hidden sm:grid grid-cols-3 gap-2 md:gap-3">
                    <div className="p-2 md:p-3 rounded-xl border border-white/15 flex items-center gap-2 md:gap-3" style={{
                      background: `
                        repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
                        repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
                        linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%)
                      `,
                      backgroundSize: '40px 40px, 40px 40px, 100% 100%'
                    }}>
                      <div className="w-6 h-6 md:w-8 md:h-8 rounded-lg bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center flex-shrink-0">
                        <Code className="w-3 h-3 md:w-4 md:h-4 text-white" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs text-gray-300 font-medium">Parse</p>
                        <p className="text-[10px] text-gray-400 truncate">Understand intent</p>
                      </div>
                    </div>

                    <div className="p-2 md:p-3 rounded-xl border border-white/15 flex items-center gap-2 md:gap-3" style={{
                      background: `
                        repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
                        repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
                        linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%)
                      `,
                      backgroundSize: '40px 40px, 40px 40px, 100% 100%'
                    }}>
                      <div className="w-6 h-6 md:w-8 md:h-8 rounded-lg bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center flex-shrink-0">
                        <ListChecks className="w-3 h-3 md:w-4 md:h-4 text-white" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs text-gray-300 font-medium">Plan</p>
                        <p className="text-[10px] text-gray-400 truncate">Map tasks & checks</p>
                      </div>
                    </div>

                    <div className="p-2 md:p-3 rounded-xl border border-white/15 flex items-center gap-2 md:gap-3" style={{
                      background: `
                        repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
                        repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
                        linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%)
                      `,
                      backgroundSize: '40px 40px, 40px 40px, 100% 100%'
                    }}>
                      <div className="w-6 h-6 md:w-8 md:h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center flex-shrink-0">
                        <Zap className="w-3 h-3 md:w-4 md:h-4 text-white" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs text-gray-300 font-medium">Run</p>
                        <p className="text-[10px] text-gray-400 truncate">Post · Reply · Notify</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="sm:hidden w-full flex flex-col gap-4">
                  <FabricButton
                    onClick={handleGetStarted}
                    variant="primary"
                    size="medium"
                    className="w-full"
                  >
                    <Zap className="w-4 h-4" />
                    {user ? 'Go to Dashboard' : 'Try ChatVerse Now'}
                  </FabricButton>
                  <FabricButton
                    onClick={handleUseAI}
                    variant="secondary"
                    size="medium"
                    className="w-full"
                  >
                    <Brain className="w-4 h-4" />
                    Use AI for Automations
                  </FabricButton>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'data' && (
        <div className="p-[2px] rounded-2xl bg-gradient-to-r from-blue-900/40 via-cyan-800/30 to-teal-800/30 shadow-[0_0_60px_-12px_rgba(6,182,212,0.25)]">
          <section className="mx-auto max-w-5xl w-full px-4 sm:px-6 mt-16 sm:mt-24">
            <div className="flex justify-center">
              <div className="w-full max-w-md">
                <div className="p-[2px] rounded-2xl bg-gradient-to-r from-blue-900/40 via-cyan-800/30 to-teal-800/30 shadow-[0_0_60px_-12px_rgba(6,182,212,0.25)]">
                  <div
                    className="rounded-2xl backdrop-blur-sm border border-gray-800 p-4 sm:p-6"
                    style={{
                      background: `
                        repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
                        repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
                        linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%)
                      `,
                      backgroundSize: '40px 40px, 40px 40px, 100% 100%'
                    }}
                  >
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-600 to-blue-700 flex items-center justify-center">
                        <BarChart3 className="w-4 h-4 text-white" />
                      </div>
                      <h3 className="text-lg font-semibold text-white" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                        Automation Builder
                      </h3>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                          Target Platform
                        </label>
                        <div className="relative">
                          <select className="w-full px-3 py-2 bg-black/70 border border-gray-700 rounded-lg text-white text-sm focus:border-cyan-500 focus:outline-none transition-colors">
                            <option>Instagram</option>
                            <option>Twitter</option>
                            <option>LinkedIn</option>
                            <option>Facebook</option>
                          </select>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                          Content Template
                        </label>
                        <textarea
                          className="w-full px-3 py-2 bg-black/70 border border-gray-700 rounded-lg text-white text-sm h-20 resize-none focus:border-cyan-500 focus:outline-none transition-colors"
                          placeholder="Check out our latest product launch! 🚀 #innovation #tech"
                          readOnly
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                          AI Model
                        </label>
                        <div className="grid grid-cols-2 gap-2">
                          <div className="p-3 bg-gradient-to-br from-purple-900/30 to-pink-900/30 border border-purple-700/50 rounded-lg cursor-pointer hover:border-purple-600 transition-colors">
                            <div className="text-xs font-medium text-purple-300">GPT-4</div>
                            <div className="text-[10px] text-gray-400">Creative & Engaging</div>
                          </div>
                          <div className="p-3 bg-black/70 border border-gray-700 rounded-lg cursor-pointer hover:border-gray-600 transition-colors">
                            <div className="text-xs font-medium text-gray-300">Claude</div>
                            <div className="text-[10px] text-gray-400">Professional Tone</div>
                          </div>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                          Schedule
                        </label>
                        <div className="flex gap-2">
                          <input
                            type="time"
                            className="flex-1 px-3 py-2 bg-black/70 border border-gray-700 rounded-lg text-white text-sm focus:border-cyan-500 focus:outline-none transition-colors"
                            defaultValue="14:30"
                          />
                          <select className="flex-1 px-3 py-2 bg-black/70 border border-gray-700 rounded-lg text-white text-sm focus:border-cyan-500 focus:outline-none transition-colors">
                            <option>Daily</option>
                            <option>Weekly</option>
                            <option>Monthly</option>
                          </select>
                        </div>
                      </div>
                      <FabricButton 
                        variant="secondary"
                        size="medium"
                        className="w-full mt-6"
                      >
                        <Zap className="w-4 h-4" />
                        Deploy Automation
                      </FabricButton>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      )}

      <p className="mt-4 sm:mt-6 text-xs sm:text-sm text-gray-500 text-center px-4 sm:px-0" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
        {activeTab === 'query'
          ? 'Examples rotate to demonstrate what ChatVerse can do — try your own on the next step'
          : 'Configure your automation with custom settings and see the preview in real-time'
        }
      </p>
    </section>
  );
};

export default QueryShowcase;
