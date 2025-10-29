import React from 'react';
import { Bot, Target,Trash2, Reply, Image, BarChart3, Users, FileText, MessageSquare, Sparkles } from 'lucide-react';

interface CreateAutomationFormProps {
  onBack: () => void;
  onSelectAutomationType: (typeId: string) => void;
  platformAccount: {
    id: number;
    platform_user_id: string;
    username: string;
    profile_picture_url?: string;
  };
}

const automationTypes = [
  {
    id: 'ai-conversation',
    title: 'AI Conversation Engagement',
    description: 'Intelligent AI-powered conversations with your audience.',
    Icon: Bot,
    color: 'from-blue-500 to-purple-600',
    apiMethod: 'getAutomationConfig',
  },
  {
    id: 'trigger-messages',
    title: 'Trigger Messages on Keywords (DM)',
    description: 'Automatically respond to DMs when specific keywords are detected.',
    Icon: Target,
    color: 'from-green-500 to-teal-600',
    apiMethod: 'getDmKeywordReplyAutomations',
  },
  {
    id: 'reply-comment',
    title: 'Reply on Comments',
    description: 'Automatically respond to comments on your posts.',
    Icon: Reply,
    color: 'from-orange-500 to-red-600',
    apiMethod: 'getCommentReply',
  },
  {
    id: 'private-message',
    title: 'Direct Message (Who Comment on your post)',
    description: 'Send Message to a user when someone comment on your post',
    Icon: Image,
    color: 'from-pink-500 to-rose-600',
    apiMethod: 'getAllAutomations',
  },
{
  id: 'delete-comment',
  title: 'Delete Unwanted Comments',
  description: 'AI will automatically delete comments based on your conditions.',
  Icon: Trash2, // updated icon
  color: 'from-red-500 to-red-700', // updated color
  disabled: false,
  apiMethod: null,
},
  {
    id: 'comment-engagement',
    title: 'Comment Section Engagement',
    description: 'Engage actively in your comment sections.',
    Icon: Users,
    color: 'from-indigo-500 to-purple-600',
    disabled: true,
    apiMethod: null,
  },
  {
    id: 'message-summary',
    title: 'Message Summary',
    description: 'Get comprehensive summaries of your messages.',
    Icon: FileText,
    color: 'from-emerald-500 to-green-600',
    disabled: true,
    apiMethod: null,
  },
  {
    id: 'comment-classification',
    title: 'Comment Classification',
    description: 'Get classified comments for your brand analysis.',
    Icon: MessageSquare,
    color: 'from-yellow-500 to-orange-600',
    disabled: true,
    apiMethod: null,
  },
  {
    id: 'content-generation',
    title: 'Auto Content Generation',
    description: 'AI-powered content generation for your Instagram page.',
    Icon: Sparkles,
    color: 'from-violet-500 to-purple-600',
    disabled: true,
    apiMethod: null,
  },
];

const CreateAutomationForm: React.FC<CreateAutomationFormProps> = ({ onBack, onSelectAutomationType, platformAccount }) => {
  const handleCreateAutomation = (typeId: string) => {
    onSelectAutomationType(typeId);
  };

  return (
    <div className="p-3 sm:p-4 md:p-6 lg:p-8 bg-[#000000] min-h-screen text-neutral-200 font-sans">

      {/* Header section with responsive spacing */}
      <div className="mb-4 sm:mb-6">
        <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-white tracking-tight mb-2">Create New Automation</h1>
        <p className="text-neutral-500 text-xs sm:text-sm">Choose the type of automation you want to create for @{platformAccount.username}.</p>
      </div>

      {/* Automation types grid with responsive layout */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
        {automationTypes.map((type) => (
          <div
            key={type.id}
            onClick={() => !type.disabled && handleCreateAutomation(type.id)}
            className={`relative p-3 sm:p-4 bg-[#1a1a1a] border border-[#262626] rounded-lg flex flex-col items-start gap-2 sm:gap-3 transition-all duration-300
            ${type.disabled
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:border-red-500/50 hover:-translate-y-1 hover:shadow-xl hover:shadow-red-500/10 cursor-pointer'
            }`}
          >

            {/* Card content */}
            <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-gradient-to-r ${type.color} p-2.5 sm:p-3 flex items-center justify-center
                        ${!type.disabled && 'group-hover:scale-105 transition-transform duration-300'}`}>
              <type.Icon className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <h3 className="text-sm sm:text-base font-semibold text-white leading-tight">{type.title}</h3>
            <p className="text-xs text-neutral-200 leading-relaxed font-medium bg-gradient-to-r from-blue-100 via-purple-100 to-pink-100 bg-clip-text text-transparent drop-shadow-sm">
              {type.description}
            </p>
            {type.disabled && (
              <span className="mt-1 px-2 py-1 text-xs font-medium rounded-full bg-neutral-700 text-neutral-400">
                Coming Soon
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CreateAutomationForm;