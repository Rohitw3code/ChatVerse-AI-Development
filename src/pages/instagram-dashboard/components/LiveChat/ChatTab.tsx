import React, { useState, useEffect } from 'react';
import { RefreshCw, AlertCircle } from 'lucide-react';
import { InstagramApiService } from '../../../../api/instagram_api';
import { PlatformAccount, ChatUser, ChatMessage } from '../../../../types/types';
import ChatList from './ChatList';
import Messages from './Messages';

interface ChatTabProps {
  platformAccount: PlatformAccount;
}

const ChatTab: React.FC<ChatTabProps> = ({ platformAccount }) => {
  const [message, setMessage] = useState('');
  const [selectedChat, setSelectedChat] = useState(0);
  const [chats, setChats] = useState<ChatUser[]>([]);
  const [filteredChats, setFilteredChats] = useState<ChatUser[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [messagesError, setMessagesError] = useState<string | null>(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);

  const fetchConversations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await InstagramApiService.getConversations(platformAccount.platform_user_id);

      if (response.success && response.data?.data) {
        const transformedChats: ChatUser[] = response.data.data.map((conv) => {
          const otherParticipant = conv.participants.data.find(p => p.id !== platformAccount.platform_user_id) || conv.participants.data[0];
          return {
            id: otherParticipant.id,
            name: otherParticipant.username.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            username: `@${otherParticipant.username}`,
            avatar: `https://ui-avatars.com/api/?name=${otherParticipant.username.charAt(0)}`,
            lastMessage: 'Click to load messages...',
            time: '',
            unread: 0,
            online: false,
            conversationId: conv.id
          };
        });

        setChats(transformedChats);
        setFilteredChats(transformedChats);
        
        // Auto-select the first chat when conversations are loaded
        if (transformedChats.length > 0) {
          setSelectedChat(0);
          setChatLoading(true);
          fetchMessages(transformedChats[0].conversationId);
        }
      } else {
        setError(response.message || 'Failed to fetch conversations');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load conversations. Please try again.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const fetchMessages = async (conversationId: string) => {
    if (!conversationId) return;
    setMessagesLoading(true);
    setMessagesError(null);
    try {
      const response = await InstagramApiService.getMessages(conversationId, platformAccount.platform_user_id);
      if (response.success && response.data?.messages) {
        const transformedMessages: ChatMessage[] = response.data.messages.map((msg) => ({
          id: msg.id,
          sender: msg.from.username,
          message: msg.message,
          time: new Date(msg.created_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isOwn: msg.from.id === platformAccount.platform_user_id,
          created_time: msg.created_time
        })).sort((a, b) => new Date(a.created_time).getTime() - new Date(b.created_time).getTime());
        setMessages(transformedMessages);
      } else {
        setMessagesError(response.message || 'Failed to fetch messages');
      }
    } catch (err: any) {
      setMessagesError(err.message || 'Failed to load messages. Please try again.');
    } finally {
      setMessagesLoading(false);
      setChatLoading(false);
    }
  };

  const sendMessage = async () => {
    const messageText = message.trim();
    const recipientId = chats[selectedChat]?.id;
    if (!messageText || !recipientId) return;

    setSendingMessage(true);
    setSendError(null);
    try {
      const payload = {
        recipient_id: recipientId,
        message: messageText,
        platform_user_id: platformAccount.platform_user_id
      };
      const response = await InstagramApiService.sendMessage(payload);

      if (response.success) {
        const newMessage: ChatMessage = {
          id: response.data.message_id || `temp-${Date.now()}`,
          sender: 'You',
          message: messageText,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isOwn: true,
          created_time: new Date().toISOString()
        };
        setMessages(prev => [...prev, newMessage]);
        setMessage('');
      } else {
        setSendError(response.message || 'Failed to send message');
      }
    } catch (err: any) {
      setSendError(err.message || 'Failed to send message. Please try again.');
    } finally {
      setSendingMessage(false);
    }
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    const filtered = query ? chats.filter(c => c.name.toLowerCase().includes(query.toLowerCase())) : chats;
    setFilteredChats(filtered);
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchConversations();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleChatSelect = (originalIndex: number, conversationId: string) => {
    setSelectedChat(originalIndex);
    setMessages([]);
    setChatLoading(true);
    fetchMessages(conversationId);
  };

  useEffect(() => {
    if (platformAccount?.id) {
        fetchConversations();
    }
  }, [platformAccount]);

  return (
    <>
      {/* Header - Refresh button removed as requested */}
      {/* <div className="flex items-center justify-between p-4 bg-gradient-to-r from-[#1a1a1a] to-[#1f1f1f] border border-[#262626] rounded-xl shadow-lg mb-4">
        <div>
          <h2 className="text-lg font-semibold text-white">Conversations</h2>
          <p className="text-sm text-[#8e8e8e]">Manage your Instagram direct messages</p>
        </div>
        Refresh button commented out as requested
        <button
          onClick={handleRefresh}
          disabled={refreshing || loading}
          className="flex items-center gap-2 px-4 py-2 bg-[#262626] hover:bg-[#333] text-white rounded-lg transition-all duration-200 disabled:opacity-50 hover:scale-105 shadow-md"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span className="text-sm font-medium">Refresh</span>
        </button>        
      </div> */}

      {error && (
        <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-lg flex items-center gap-3 mb-4 backdrop-blur-sm">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <span className="text-red-300">{error}</span>
        </div>
      )}

      <div className="flex flex-col xl:flex-row gap-4 h-[calc(100vh-240px)] min-h-[600px]">
        <div className="w-full xl:w-80 flex-shrink-0">
          <ChatList
            chats={chats}
            filteredChats={filteredChats}
            searchQuery={searchQuery}
            selectedChat={selectedChat}
            loading={loading}
            chatLoading={chatLoading}
            onSearch={handleSearch}
            onChatSelect={handleChatSelect}
          />
        </div>
        <div className="flex-1 min-w-0">
          <Messages
            selectedChat={selectedChat}
            chats={chats}
            messages={messages}
            message={message}
            messagesLoading={messagesLoading}
            messagesError={messagesError}
            sendError={sendError}
            sendingMessage={sendingMessage}
            onMessageChange={setMessage}
            onSendMessage={sendMessage}
            onKeyPress={handleKeyPress}
            onDismissSendError={() => setSendError(null)}
          />
        </div>
      </div>
    </>
  );
};

export default ChatTab;