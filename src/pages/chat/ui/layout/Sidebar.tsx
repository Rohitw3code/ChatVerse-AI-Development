import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatAgentApiService } from '../../../../api/chatagent';
import { UserApiService } from '../../../../api/user_api';
import { useAuthStore } from '../../../../stores/authStore';
import { useUserStore } from '../../../../stores/userStore';
import { Trash2, MoreHorizontal, Edit3, Plus, MessageSquare, ChevronLeft, List, Search, ArrowLeft } from 'lucide-react';

interface ChatItem {
  id: string;
  title: string;
}

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onNewChat?: () => void;
  onSelectChat?: (chatId: string) => void;
  currentChatId?: string;
  isExpanded?: boolean;
  onToggleExpanded?: () => void;
  onBack?: () => void;
  providerId: string;
  refetchCounter?: number;
  onOpenAutomations?: () => void;
}

export function Sidebar({
  isOpen, onToggle, onNewChat, onSelectChat, currentChatId,
  isExpanded = true, onToggleExpanded, onBack, providerId, refetchCounter, onOpenAutomations
}: SidebarProps) {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { userProfile } = useUserStore();
  const [chatHistory, setChatHistory] = useState<ChatItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [creditBalance, setCreditBalance] = useState<number | null>(null);
  const [imageError, setImageError] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Helper function to get user display info
  const getUserInfo = () => {
    const displayName = userProfile?.full_name || user?.name || user?.email?.split('@')[0] || 'User';
    const profileImage = userProfile?.profile_picture || user?.avatar;
    
    // Generate initials from the display name
    const initials = displayName
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2) || 'U';
    
    return { displayName, profileImage, initials };
  };

  // Reset image error when user data changes
  useEffect(() => {
    setImageError(false);
  }, [user?.avatar, userProfile?.profile_picture]);

  // Handle mobile detection and window resize
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    
    // Check on mount
    checkMobile();
    
    // Add resize listener
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    if (providerId) {
      setIsLoading(true);
      ChatAgentApiService.getThreads(providerId)
        .then(threads => {
          const formattedThreads = threads.map((thread: any) => ({
            id: thread.thread_id,
            title: thread.name || `Chat ${thread.thread_id.substring(0, 8)}`
          }));
          setChatHistory(formattedThreads);
        })
        .catch(error => console.error("Failed to fetch chat history:", error))
        .finally(() => setIsLoading(false));
    }
  }, [providerId, isOpen, refetchCounter]);

  // Fetch credit balance
  useEffect(() => {
    if (providerId) {
      UserApiService.getUserCredit(providerId)
        .then(response => {
          if (response.success && response.data) {
            setCreditBalance(response.data.current_credits);
          }
        })
        .catch(error => console.error("Failed to fetch credit balance:", error));
    }
  }, [providerId]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpenMenuId(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAction = (action?: () => void) => {
    if (action) action();
    if (window.innerWidth < 1024) onToggle();
  };

  const handleToggleMenu = (e: React.MouseEvent, chatId: string) => {
    e.stopPropagation();
    setOpenMenuId(openMenuId === chatId ? null : chatId);
  };

  const handleRenameStart = (e: React.MouseEvent, chat: ChatItem) => {
    e.stopPropagation();
    setRenamingId(chat.id);
    setRenameValue(chat.title);
    setOpenMenuId(null);
  };

  const handleRenameSubmit = (chatId: string) => {
    if (!renameValue.trim()) return;
    setChatHistory(prev => prev.map(chat => chat.id === chatId ? { ...chat, title: renameValue } : chat));
    setRenamingId(null);
  };

  const handleDeleteChat = async (e: React.MouseEvent, chatIdToDelete: string) => {
    e.stopPropagation();
    setOpenMenuId(null);
    if (window.confirm("Are you sure you want to delete this chat?")) {
      try {
        await ChatAgentApiService.deleteThread(chatIdToDelete);
        setChatHistory(prev => prev.filter(chat => chat.id !== chatIdToDelete));
        if (currentChatId === chatIdToDelete && onNewChat) onNewChat();
      } catch (error) { console.error("Error deleting chat:", error); }
    }
  };

  const sidebarClasses = `
    fixed top-0 left-0 h-[100dvh] bg-[#0d0e12]/90 backdrop-blur-lg border-r border-white/10 lg:border-r-0 z-[1200]
    shadow-[0_10px_30px_rgba(0,0,0,0.55)] transition-all duration-300 ease-in-out flex flex-col p-3
    ${isExpanded ? 'w-[var(--sidebar-width-expanded)]' : 'w-[var(--sidebar-width-collapsed)]'}
    max-lg:-translate-x-full ${isOpen ? 'max-lg:translate-x-0' : ''}
  `;

  const filteredChats = chatHistory.filter(c => c.title.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <>
      <div className={`fixed inset-0 bg-black/50 backdrop-blur-sm z-[1100] lg:hidden
        transition-opacity ease-in-out duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
          onClick={onToggle}
      />
      <aside className={sidebarClasses}>
        <div className="flex items-center justify-between mb-3">
          <button className="bg-white/5 hover:bg-white/10 rounded-md w-9 h-9 flex items-center justify-center cursor-pointer text-white transition-colors" onClick={onBack || onToggle} title={onBack ? 'Back to platforms' : 'Close sidebar'}>
            <ArrowLeft size={18} />
          </button>
          {isExpanded && (
            <button className="flex items-center gap-3 flex-grow py-2.5 px-4 bg-violet-600/15 hover:bg-violet-600/25 rounded-full text-violet-100 text-sm font-medium cursor-pointer transition-colors duration-200 ml-2" onClick={() => handleAction(onNewChat)} title="New chat">
              <Plus size={18} /> <span>New chat</span>
            </button>
          )}
        </div>

        {/* Credit Display - Only show when expanded */}
        {isExpanded && (
          <div className="mb-3">
            <div className="bg-white/5 hover:bg-white/[0.07] border border-white/10 rounded-xl p-3 transition-all duration-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 bg-gradient-to-br from-amber-400 to-amber-600 rounded-full flex items-center justify-center shadow-sm">
                    <span className="text-sm font-bold text-white">★</span>
                  </div>
                  <div>
                    <div className="text-[11px] text-slate-400 font-medium">Credits</div>
                    <div className="text-sm font-semibold text-white">
                      {creditBalance !== null ? creditBalance.toLocaleString() : '...'}
                    </div>
                  </div>
                </div>
                <button 
                  onClick={() => navigate('/pricing')} 
                  className="px-3 py-1.5 bg-violet-600 hover:bg-violet-500 rounded-lg text-xs font-medium text-white transition-colors duration-200"
                >
                  Add
                </button>
              </div>
            </div>
          </div>
        )}

        {isExpanded && (
          <div className="mb-3">
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search chats"
                className="w-full pl-9 pr-3 py-2.5 bg-white/5 border-none rounded-full text-sm text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500/40"
              />
            </div>
          </div>
        )}

        {/* Automations Button - Only show when expanded */}
        {isExpanded && (
          <div className="mb-4">
            <button className="w-full flex items-center gap-3 py-2.5 px-4 bg-white/5 hover:bg-white/10 rounded-full text-white text-sm font-medium cursor-pointer transition-colors duration-200" onClick={() => handleAction(onOpenAutomations)}>
              <List size={18} /> <span>Automations List</span>
            </button>
          </div>
        )}

        {/* New Chat Button for collapsed state */}
        {!isExpanded && (
          <div className="mb-4 flex flex-col gap-3">
            <button className="w-10 h-10 rounded-full justify-center p-0 m-0 flex-grow-0 flex-shrink-0 flex items-center bg-violet-600/15 hover:bg-violet-600/25 text-violet-100 transition-colors duration-200" onClick={() => handleAction(onNewChat)} title="New chat">
              <Plus size={18} />
            </button>
          </div>
        )}

        {/* Threads List - Only show when expanded */}
        {isExpanded && (
          <div className="flex-1 overflow-y-auto sidebar-scroll">
            <h3 className="text-slate-400 text-xs tracking-wide mb-2 px-3">RECENT</h3>
            {isLoading ? (
              <div className="flex items-center justify-center gap-3 p-4 text-slate-500">
                <div className="w-4 h-4 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin"></div>
                <span className="text-sm">Loading...</span>
              </div>
            ) : (
              filteredChats.map((chat) => (
                <div key={chat.id} className={`group flex items-center gap-3 py-2.5 px-3 mb-1 rounded-xl cursor-pointer transition-colors duration-150 whitespace-nowrap justify-between relative ${currentChatId === chat.id ? 'bg-violet-500/15 ring-1 ring-inset ring-violet-500/30' : 'hover:bg-white/5'}`} onClick={() => handleAction(() => onSelectChat && onSelectChat(chat.id))} title={chat.title}>
                  <div className="flex items-center gap-3 overflow-hidden flex-grow">
                    <MessageSquare size={18} className={`${currentChatId === chat.id ? 'text-violet-400' : 'text-slate-400'} flex-shrink-0`} />
                    {renamingId === chat.id ? (
                      <input type="text" value={renameValue} onChange={(e) => setRenameValue(e.target.value)} onBlur={() => handleRenameSubmit(chat.id)} onKeyDown={(e) => e.key === 'Enter' && handleRenameSubmit(chat.id)} className="bg-white/5 border-none text-white py-1.5 px-2 rounded-md text-sm w-full focus:outline-none focus:ring-2 focus:ring-violet-500/40" autoFocus onClick={(e) => e.stopPropagation()} />
                    ) : (
                      <div className="text-white text-[13px] font-normal overflow-hidden text-ellipsis whitespace-nowrap flex-grow">{chat.title}</div>
                    )}
                  </div>
                  <div className="hidden group-hover:block">
                    <button onClick={(e) => handleToggleMenu(e, chat.id)} className="p-1 text-slate-400 hover:text-white"><MoreHorizontal size={16} /></button>
                  </div>
                  {openMenuId === chat.id && (
                    <div className="absolute right-4 top-11 bg-[#141417] rounded-lg p-2 z-[110] w-36 shadow-[0_8px_24px_rgba(0,0,0,0.5)]" ref={menuRef} onClick={e => e.stopPropagation()}>
                      <button onClick={(e) => handleRenameStart(e, chat)} className="flex items-center gap-2 w-full p-2 text-left rounded-md text-sm text-white hover:bg-white/5"><Edit3 size={14} /> Rename</button>
                      <button onClick={(e) => handleDeleteChat(e, chat.id)} className="flex items-center gap-2 w-full p-2 text-left rounded-md text-sm text-red-300 hover:bg-red-900/30"><Trash2 size={14} /> Delete</button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* Spacer for collapsed state to push user section to bottom */}
        {!isExpanded && <div className="flex-1"></div>}

        <div className="pt-3">
          <div className="flex items-center gap-3 p-2.5 rounded-xl cursor-pointer transition-colors duration-150 whitespace-nowrap overflow-hidden hover:bg-white/5">
            {!imageError && getUserInfo().profileImage ? (
              <img 
                src={getUserInfo().profileImage} 
                alt={getUserInfo().displayName} 
                className="w-7 h-7 rounded-full object-cover flex-shrink-0"
                onError={() => setImageError(true)}
              />
            ) : (
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-violet-700 flex items-center justify-center text-white font-semibold text-xs flex-shrink-0">
                {getUserInfo().initials}
              </div>
            )}
            {isExpanded && (
              <div className="text-white text-sm truncate">
                {getUserInfo().displayName}
              </div>
            )}
          </div>
          <div className="flex items-center gap-3 p-2.5 rounded-xl cursor-pointer transition-colors duration-150 whitespace-nowrap overflow-hidden hover:bg-white/5" onClick={() => {
            // On mobile (below lg breakpoint), close the sidebar instead of just collapsing
            if (isMobile && isExpanded) {
              onToggle();
            } else {
              onToggleExpanded && onToggleExpanded();
            }
          }} title={isMobile ? (isExpanded ? 'Close sidebar' : 'Expand') : (isExpanded ? 'Collapse' : 'Expand')}>
            <button className="bg-transparent border-none cursor-pointer p-0 flex items-center text-slate-400">
              <ChevronLeft size={18} style={{ transform: isExpanded ? 'rotate(0deg)' : 'rotate(180deg)', transition: 'transform 0.3s' }} />
            </button>
            {isExpanded && <div className="text-white text-sm">{isMobile ? 'Close' : (isExpanded ? 'Collapse' : 'Expand')}</div>}
          </div>
        </div>
      </aside>
    </>
  );
}