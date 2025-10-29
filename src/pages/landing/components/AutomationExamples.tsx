import React from 'react';
import { MessageCircle, Heart, Share2, User, Bot } from 'lucide-react';

const AutomationExamples = () => {
  const examples = [
    {
      platform: 'Instagram',
      originalComment: "Love this content! 😍 How do you stay so motivated?",
      aiResponse: "Thank you so much! 💫 I find motivation in connecting with amazing people like you. What keeps you inspired in your daily life?",
      engagement: { likes: 24, replies: 3 },
      timing: "2 minutes ago"
    },
    {
      platform: 'LinkedIn',
      originalComment: "Great insights on digital marketing trends. What's your take on AI integration?",
      aiResponse: "Thanks for the thoughtful question! AI is definitely reshaping how we approach marketing. I believe the key is finding the right balance between automation and authentic human connection. What's been your experience with AI tools?",
      engagement: { likes: 18, replies: 5 },
      timing: "5 minutes ago"
    },
    {
      platform: 'Twitter',
      originalComment: "This is exactly what I needed to hear today 🙏",
      aiResponse: "So glad this resonated with you! 🌟 Sometimes we all need that little reminder. Hope your day gets even better from here!",
      engagement: { likes: 31, replies: 2 },
      timing: "1 minute ago"
    }
  ];

  return (
    <div className="mt-24">
      <div className="text-center mb-12">
        <h2 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent mb-4 game-font">
          AI THAT RESPONDS LIKE YOU
        </h2>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto lego-font">
          Our AI learns your voice and responds to comments with authentic, engaging replies that build real connections
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {examples.map((example, index) => (
          <div
            key={index}
            className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6 hover:bg-white/8 transition-all duration-300 edge-holder glow-purple"
          >
            {/* Platform Header */}
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium text-gray-300 game-font">{example.platform}</span>
              <span className="text-xs text-gray-500 lego-font">{example.timing}</span>
            </div>

            {/* Original Comment */}
            <div className="mb-4">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1">
                  <div className="bg-white/5 rounded-lg p-3">
                    <p className="text-sm text-gray-300 lego-font">{example.originalComment}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Response */}
            <div className="mb-4">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1">
                  <div className="bg-gradient-to-r from-emerald-500/10 to-teal-500/10 rounded-lg p-3 border border-emerald-500/20">
                    <p className="text-sm text-gray-200 lego-font">{example.aiResponse}</p>
                    <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/10">
                      <div className="flex items-center space-x-4 text-xs text-gray-400 lego-font">
                        <div className="flex items-center space-x-1">
                          <Heart className="w-3 h-3" />
                          <span>{example.engagement.likes}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <MessageCircle className="w-3 h-3" />
                          <span>{example.engagement.replies}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Share2 className="w-3 h-3" />
                        </div>
                      </div>
                      <span className="text-xs text-emerald-400 font-medium game-font">AI GENERATED</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* AI Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
        <div className="text-center p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 edge-holder glow-blue">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center mx-auto mb-4">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2 game-font">VOICE LEARNING</h3>
          <p className="text-sm text-gray-400 lego-font">AI analyzes your writing style and tone to match your authentic voice</p>
        </div>
        
        <div className="text-center p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 edge-holder glow-emerald">
          <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center mx-auto mb-4">
            <MessageCircle className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2 game-font">CONTEXT AWARE</h3>
          <p className="text-sm text-gray-400 lego-font">Understands post content and comment context for relevant responses</p>
        </div>
        
        <div className="text-center p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 edge-holder glow-purple">
          <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mx-auto mb-4">
            <Heart className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2 game-font">ENGAGEMENT BOOST</h3>
          <p className="text-sm text-gray-400 lego-font">Increases response rates and builds stronger community connections</p>
        </div>
      </div>
    </div>
  );
};

export default AutomationExamples;