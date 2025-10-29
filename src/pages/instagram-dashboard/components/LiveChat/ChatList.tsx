import React from 'react';
import { Search } from 'lucide-react';
import type { ChatUser } from '../../../../types/types';

interface ChatListProps {
  chats: ChatUser[];
  filteredChats: ChatUser[];
  searchQuery: string;
  selectedChat: number;
  loading: boolean;
  chatLoading: boolean;
  onSearch: (query: string) => void;
  onChatSelect: (originalIndex: number, conversationId: string) => void;
}

const ChatList: React.FC<ChatListProps> = ({
  chats,
  filteredChats,
  searchQuery,
  selectedChat,
  loading,
  chatLoading,
  onSearch,
  onChatSelect,
}) => {
  return (
    <div className="h-full bg-[#1a1a1a] border border-[#262626] rounded-xl overflow-hidden flex flex-col shadow-lg">
      <div className="p-4 border-b border-[#262626] bg-gradient-to-r from-[#1a1a1a] to-[#1f1f1f]">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#8e8e8e]" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => onSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-[#0a0a0a] border border-[#262626] rounded-lg text-white placeholder-[#8e8e8e] focus:outline-none focus:border-[#fd1d1d] focus:ring-1 focus:ring-[#fd1d1d]/20 transition-all duration-200"
          />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-[#262626] scrollbar-track-transparent">
        {filteredChats.length === 0 && !loading ? (
          <div className="p-8 text-center">
            <p className="text-[#8e8e8e]">
              {searchQuery ? 'No conversations match your search' : 'No conversations found'}
            </p>
            <p className="text-sm text-[#666] mt-2">
              {searchQuery ? 'Try a different search term' : 'Start engaging with your audience to see conversations here'}
            </p>
          </div>
        ) : (
          filteredChats.map((chat) => {
            const originalIndex = chats.findIndex(c => c.id === chat.id);
            return (
              <div
                key={chat.id}
                onClick={() => onChatSelect(originalIndex, chat.conversationId)}
                className={`p-4 border-b border-[#262626] cursor-pointer transition-colors ${
                  selectedChat === originalIndex ? 'bg-[#262626]' : 'hover:bg-[#0a0a0a]'
                } ${chatLoading && selectedChat === originalIndex ? 'opacity-50' : ''}`}
              >
                <div className="flex items-center gap-3">
                  <div>
                    <img
                      src={chat.avatar}
                      alt={chat.name}
                      className="w-12 h-12 rounded-full object-cover"
                      onError={(e) => {
                        e.currentTarget.src = `https://ui-avatars.com/api/?name=${chat.name}`;
                      }}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-semibold text-white truncate">{chat.name}</h4>
                      <span className="text-xs text-[#8e8e8e]">{chat.time}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-[#8e8e8e] truncate">{chat.lastMessage}</p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default ChatList;