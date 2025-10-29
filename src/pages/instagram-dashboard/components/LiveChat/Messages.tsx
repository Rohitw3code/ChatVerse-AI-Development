import React, { useEffect, useRef } from 'react';
import {
  Send,
  MoreVertical,
  Phone,
  Video,
  Paperclip,
  Smile,
  AlertCircle
} from 'lucide-react';
import type { ChatUser, ChatMessage } from '../../../../types/types';

interface MessagesProps {
  selectedChat: number;
  chats: ChatUser[];
  messages: ChatMessage[];
  message: string;
  messagesLoading: boolean;
  messagesError: string | null;
  sendError: string | null;
  sendingMessage: boolean;
  onMessageChange: (message: string) => void;
  onSendMessage: () => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
  onDismissSendError: () => void;
}

const Messages: React.FC<MessagesProps> = ({
  selectedChat,
  chats,
  messages,
  message,
  messagesLoading,
  messagesError,
  sendError,
  sendingMessage,
  onMessageChange,
  onSendMessage,
  onKeyPress,
  onDismissSendError,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div className="h-full bg-[#1a1a1a] border border-[#262626] rounded-xl flex flex-col shadow-lg">
      {chats[selectedChat] ? (
        <>
          <div className="p-4 border-b border-[#262626] flex flex-col gap-1 bg-gradient-to-r from-[#1a1a1a] to-[#1f1f1f]">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <img
                    src={chats[selectedChat]?.avatar}
                    alt={chats[selectedChat]?.name}
                    className="w-12 h-12 rounded-full object-cover ring-2 ring-[#262626]"
                  />
                  <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-[#1a1a1a]"></div>
                </div>
                <div>
                  <h4 className="text-base font-semibold text-white">{chats[selectedChat]?.name}</h4>
                  <p className="text-sm text-[#8e8e8e]">{chats[selectedChat]?.username}</p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button className="p-2 text-[#8e8e8e] hover:text-white hover:bg-[#262626] rounded-lg transition-all duration-200">
                  <Phone className="w-5 h-5" />
                </button>
                <button className="p-2 text-[#8e8e8e] hover:text-white hover:bg-[#262626] rounded-lg transition-all duration-200">
                  <Video className="w-5 h-5" />
                </button>
                <button className="p-2 text-[#8e8e8e] hover:text-white hover:bg-[#262626] rounded-lg transition-all duration-200">
                  <MoreVertical className="w-5 h-5" />
                </button>
              </div>
            </div>
            {messagesLoading && (
              <div className="h-1 w-full bg-gradient-to-r from-[#fd1d1d] via-[#fd1d1d]/70 to-transparent animate-pulse rounded-full mt-2" />
            )}
          </div>

          <div className="flex-1 p-4 overflow-y-auto space-y-4 scrollbar-thin scrollbar-thumb-[#262626] scrollbar-track-transparent">
            {messagesError && (
              <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-lg flex items-center gap-3 backdrop-blur-sm">
                <AlertCircle className="w-5 h-5 text-red-400" />
                <span className="text-red-300">{messagesError}</span>
              </div>
            )}
            {sendError && (
              <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-lg flex items-center gap-3 backdrop-blur-sm">
                <AlertCircle className="w-5 h-5 text-red-400" />
                <span className="text-red-300">{sendError}</span>
                <button
                  onClick={onDismissSendError}
                  className="ml-auto text-red-300 hover:text-red-200 p-1 hover:bg-red-500/20 rounded transition-all duration-200"
                >
                  ×
                </button>
              </div>
            )}
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.isOwn ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2 duration-300`}
              >
                <div
                  className={`max-w-[85%] sm:max-w-[75%] lg:max-w-[65%] px-4 py-3 rounded-2xl shadow-sm ${
                    msg.isOwn
                      ? 'bg-gradient-to-r from-[#fd1d1d] to-[#e01717] text-white'
                      : 'bg-[#262626] text-white border border-[#333]'
                  }`}
                >
                  <p className="text-sm leading-relaxed">{msg.message}</p>
                  <p
                    className={`text-xs mt-2 ${
                      msg.isOwn ? 'text-white/70' : 'text-[#8e8e8e]'
                    }`}
                  >
                    {msg.time}
                  </p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 border-t border-[#262626] bg-gradient-to-r from-[#1a1a1a] to-[#1f1f1f]">
            <div className="flex items-center gap-3">
              <button className="p-2 text-[#8e8e8e] hover:text-white hover:bg-[#262626] rounded-lg transition-all duration-200">
                <Paperclip className="w-5 h-5" />
              </button>
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => onMessageChange(e.target.value)}
                  onKeyPress={onKeyPress}
                  placeholder="Type a message..."
                  disabled={sendingMessage}
                  className="w-full px-4 py-3 pr-12 bg-[#0a0a0a] border border-[#262626] rounded-full text-white placeholder-[#8e8e8e] focus:outline-none focus:border-[#fd1d1d] focus:ring-1 focus:ring-[#fd1d1d]/20 transition-all duration-200"
                />
                <button className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 text-[#8e8e8e] hover:text-white hover:bg-[#262626] rounded transition-all duration-200">
                  <Smile className="w-5 h-5" />
                </button>
              </div>
              <button
                onClick={onSendMessage}
                disabled={sendingMessage || !message.trim()}
                className="p-3 bg-gradient-to-r from-[#fd1d1d] to-[#e01717] text-white rounded-full hover:shadow-lg hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none"
              >
                {sendingMessage ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-[#8e8e8e] mb-2">No conversation selected</p>
            <p className="text-sm text-[#666]">Select a conversation to start chatting</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Messages;
