import React from 'react';
import { Settings, Camera, Mic, ImageIcon, Heart } from 'lucide-react';
import UserProfileImage from "../../../../assets/UserProfileImage.png"



const CommentReplyPreview = ({ trigger, platformAccount, selectedPost }: any) => {
  const defaultPostImage =
    'https://placehold.co/600x400/121212/444?text=No+Post+Selected';


  const getReplyText = () => {
    if (trigger.replyType === 'custom') {
      return trigger.customMessage || 'Your static reply will appear here.';
    } else {
      return (
        trigger.systemPrompt ||
        'AI will generate a reply based on this system prompt.'
      );
    }
  };

  const getTriggerCondition = () => {
    const aiContext =
      trigger.context || trigger.whenToTrigger?.context || '';
    const keywords =
      trigger.keywords?.length ? trigger.keywords.join(', ') : '';

    if (keywords && aiContext) {
      return `Comment contains: "${keywords}" AND AI decision based on: "${aiContext}"`;
    } else if (keywords) {
      return `Comment contains: "${keywords}"`;
    } else if (aiContext) {
      return `AI decision based on: "${aiContext}"`;
    } else {
      return 'No trigger condition defined.';
    }
  };

  return (
    <div className="flex flex-col flex-grow bg-white dark:bg-neutral-900 text-xs overflow-hidden">
      {/* Post Preview */}
      <div className="flex-shrink-0 border-b border-neutral-200 dark:border-neutral-800 p-2">
        <div className="flex items-center gap-2">
          <img
            src={UserProfileImage}
            alt="Profile"
            className="w-7 h-7 rounded-full object-cover"
          />
          <span className="font-semibold text-[12px]">
            {platformAccount.username}
          </span>
        </div>
        <div className="w-full bg-neutral-100 dark:bg-neutral-800 min-h-[110px] max-h-[140px] flex items-center justify-center overflow-hidden rounded-md mt-2">
          {trigger.postSelectionType === 'SPECIFIC' && selectedPost ? (
            <img
              src={selectedPost.imageUrl}
              alt="Selected Post"
              className="w-full h-full object-cover"
            />
          ) : (
            <img
              src={defaultPostImage}
              alt="Default Post"
              className="w-full h-full object-cover"
            />
          )}
        </div>
      </div>

      {/* Comments */}
      <div className="flex-grow px-3 py-2 overflow-y-auto no-scrollbar">
        {/* Main Comment */}
        <div className="flex items-start gap-2">
          <img
            src={UserProfileImage}
            alt="User"
            className="w-8 h-8 rounded-full object-cover"
          />
          <div className="flex flex-col flex-grow">
            <div className="flex items-center gap-1 text-[12px]">
              <span className="font-semibold">random_user123</span>
              <span className="text-neutral-500 dark:text-neutral-400">5h</span>
              <span>🙌</span>
            </div>
            <p className="text-[12px] mt-0.5">Hello</p>
            <div className="flex gap-3 text-[11px] text-neutral-500 dark:text-neutral-400 mt-1">
              <button>Reply</button>
              <button>Hide</button>
              <button>See translation</button>
            </div>
          </div>
          <div className="flex flex-col items-center text-neutral-500 dark:text-neutral-400">
            <Heart size={14} className="mb-0.5" />
            <span className="text-[10px]">1</span>
          </div>
        </div>

        {/* Reply */}
        <div className="flex items-start gap-2 mt-3 ml-10">
          <img
            src={UserProfileImage}
            alt="AI"
            className="w-6 h-6 rounded-full object-cover"
          />
          <div className="flex flex-col flex-grow">
            <div className="flex items-center gap-1 text-[12px]">
              <span className="font-semibold">{platformAccount.platform_username}</span>
              <span className="text-neutral-500 dark:text-neutral-400">48s</span>
            </div>
            <p className="text-[12px] mt-0.5">{getReplyText()}</p>
            <p className="text-[10px] italic text-neutral-500 dark:text-neutral-400 mt-1">
              This reply will trigger when: {getTriggerCondition()}
            </p>
            <div className="flex gap-3 text-[11px] text-neutral-500 dark:text-neutral-400 mt-1">
              <button>Reply</button>
              <button>See translation</button>
            </div>
          </div>
          <div className="flex flex-col items-center text-neutral-500 dark:text-neutral-400">
            <Heart size={14} />
          </div>
        </div>
      </div>

      {/* Reaction Bar */}
      <div className="px-3 py-2 border-t border-neutral-200 dark:border-neutral-800 flex items-center gap-3">
        {['❤️', '🙌', '🔥', '👏', '😢', '😍', '😮', '😂'].map((emoji, i) => (
          <span key={i} className="text-lg cursor-pointer">
            {emoji}
          </span>
        ))}
      </div>
    </div>
  );
};

const DirectMessagePreview = ({ trigger }: any) => {
  const renderMessageContent = () => {
    const { messageType, messageContent } = trigger;
    const { text, imageUrl, buttons } = messageContent;
    switch (messageType) {
      case 'text':
        return (
          <div className="bg-neutral-100 dark:bg-neutral-800 self-start rounded-2xl rounded-bl-sm px-3 py-2 max-w-[75%] break-words">
            {text || 'Your text message...'}
          </div>
        );
      case 'image':
        return (
          <div className="self-start max-w-[70%] rounded-2xl overflow-hidden">
            <img
              src={
                imageUrl
              }
              alt="Preview"
              className="w-full h-auto object-cover"
            />
          </div>
        );
      case 'button_template':
        return (
          <div className="bg-neutral-100 dark:bg-neutral-800 self-start rounded-2xl max-w-[75%] border border-neutral-200 dark:border-neutral-700">
            <div className="px-3 py-2 break-words">
              {text || 'Your message with buttons...'}
            </div>
            {buttons?.map((btn: any, i: number) => (
              <div
                key={i}
                className="border-t border-neutral-200 dark:border-neutral-700 text-center text-blue-500 font-semibold py-2"
              >
                {btn.text || 'Button'}
              </div>
            ))}
          </div>
        );
      case 'quick_replies':
        return (
          <div className="flex flex-col items-start max-w-[75%]">
            {text && (
              <div className="bg-neutral-100 dark:bg-neutral-800 rounded-2xl rounded-bl-sm px-3 py-2 break-words mb-2">
                {text}
              </div>
            )}
            {/* Choose one option label */}
            <span className="text-[11px] text-neutral-500 dark:text-neutral-400 mb-1 ml-1">
              Choose one option
            </span>
            {/* Scrollable bubble container */}
            <div className="flex gap-2 overflow-x-auto no-scrollbar pb-1">
              {buttons?.map((btn: any, i: number) => {
                const payload = btn.payload && btn.payload.trim() !== '' ? btn.payload : 'default_payload';
                return (
                  <div
                    key={i}
                    className="bg-blue-500 text-white text-sm px-4 py-1.5 rounded-full whitespace-nowrap cursor-pointer hover:opacity-90"
                    data-payload={payload}
                  >
                    {btn.text || 'Quick Reply'}
                  </div>
                );
              })}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col flex-grow bg-white dark:bg-neutral-900">
      <div className="flex-grow p-4 flex flex-col-reverse gap-3 overflow-y-auto no-scrollbar">
        <div className="flex items-end gap-2.5">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-orange-400 flex-shrink-0 self-end"></div>
          {renderMessageContent()}
        </div>
        <div className="flex items-end gap-2.5 justify-end">
          <div className="bg-blue-500 text-white rounded-2xl rounded-br-sm px-3 py-2 max-w-[75%] break-words">
            {trigger.triggerType === 'keyword'
              ? trigger.keywords?.[0] || 'keyword'
              : trigger.aiContext?.split(' ')[0] || 'AI context'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default function InstagramPreview({
  type,
  trigger,
  platformAccount,
  selectedPost,
}: any) {
  const [activeTab, setActiveTab] = React.useState<'comment' | 'dm'>(type || 'comment');
  
  // Update activeTab when type prop changes
  React.useEffect(() => {
    if (type) {
      setActiveTab(type);
    }
  }, [type]);

  return (
    <div className="relative w-full max-w-[320px] aspect-[9/16] mx-auto flex justify-center items-center">
      {/* Phone Frame */}
      <div className="bg-black dark:bg-neutral-950 rounded-[2.5rem] p-2 shadow-[0_0_50px_rgba(0,0,0,0.8)] border border-neutral-700 w-full h-full flex flex-col overflow-hidden relative">
        {/* Inner screen */}
        <div className="bg-white dark:bg-neutral-900 rounded-[2rem] border border-neutral-200 dark:border-neutral-800 w-full h-full flex flex-col overflow-hidden relative">
          {/* Camera Notch */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-28 h-5 bg-black dark:bg-neutral-950 rounded-b-xl z-20" />

          {/* Top Bar */}
          <div className="flex items-center justify-between px-4 py-2 bg-white dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800">
            <div className="flex items-center gap-3">
              <div className="font-bold text-sm text-black dark:text-neutral-200">
                {platformAccount.username}
              </div>
            </div>
            <Settings size={20} className="text-neutral-800 dark:text-neutral-200" />
          </div>

          {/* Main Content */}
          {activeTab === 'comment' ? (
            <CommentReplyPreview
              trigger={trigger}
              platformAccount={platformAccount}
              selectedPost={selectedPost}
            />
          ) : (
            <DirectMessagePreview
              trigger={trigger}
              platformAccount={platformAccount}
            />
          )}

          

          {/* Bottom Input */}
          <div className="p-3 bg-white dark:bg-neutral-900 border-t border-neutral-200 dark:border-neutral-800 flex-shrink-0">
            <div className="flex items-center bg-neutral-100 dark:bg-neutral-800 rounded-full px-3 py-2">
              <Camera size={20} className="text-neutral-500 dark:text-neutral-400" />
              <input
                type="text"
                placeholder={`Comment as ${platformAccount.username}...`}
                className="flex-grow bg-transparent mx-3 focus:outline-none text-sm text-black dark:text-white placeholder-neutral-500 dark:placeholder-neutral-400"
              />
              <Mic size={20} className="text-neutral-500 dark:text-neutral-400 mr-2" />
              <ImageIcon size={20} className="text-neutral-500 dark:text-neutral-400" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
