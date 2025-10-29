import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  useChat, 
  useViewport, 
  useScrollManagement, 
  useSidebarState, 
  useInputPositioning, 
  useBodyScrollLock 
} from "./hooks";
import { Sidebar, TopNavbar } from "./ui/layout";
import { EmptyState, MessageList } from "./ui/messages";
import { ChatInput } from "./ui/input";
import "./utils/streamTracker"; // Initialize stream tracker utilities

export default function Chat() {
  const navigate = useNavigate();
  const { chatId } = useParams<{ chatId: string }>();
  const providerId = new URLSearchParams(window.location.search).get('provider_id') || '';

  const {
    messages, isThinking, thinkingMessage, isInitialLoading, isHistoryLoading,
    refetchCounter, userInteracted, loadMoreHistory, submitMessage, currentCredits
  } = useChat(chatId, providerId);

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);
  
  // Custom hooks for UI management
  const { keyboardOffset } = useViewport();
  const { leftOffset } = useSidebarState({ isSidebarExpanded });
  const { inputHeight, inputCenterLeft, inputContainerRef, messageListRef } = useInputPositioning({
    isSidebarExpanded,
    leftOffset,
    isSidebarOpen
  });
  useScrollManagement({
    messages,
    isInitialLoading,
    isHistoryLoading,
    keyboardOffset,
    inputHeight,
    loadMoreHistory,
    userInteracted,
    messageListRef
  });
  
  // Use body scroll lock
  useBodyScrollLock();

  const handleNewChat = () => {
    if (!providerId) return;
    const newChatId = `chat_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    navigate(`/chat/${newChatId}?provider_id=${providerId}`);
  };

  const handleSelectChat = (selectedChatId: string) => {
    if (!providerId) return;
    navigate(`/chat/${selectedChatId}?provider_id=${providerId}`);
  };

  const handleBack = () => {
    navigate('/platforms');
  };

  const isEmptyState = messages.length === 0 && !isThinking && !isInitialLoading && !loadMoreHistory.get;

  return (
    <div className="flex h-[100dvh] relative bg-[#0a0a0a] text-white">
      <Sidebar 
        isOpen={isSidebarOpen} onToggle={() => setIsSidebarOpen(!isSidebarOpen)} onNewChat={handleNewChat}
        onSelectChat={handleSelectChat} currentChatId={chatId} isExpanded={isSidebarExpanded}
        onToggleExpanded={() => setIsSidebarExpanded(!isSidebarExpanded)}
        providerId={providerId} refetchCounter={refetchCounter} onBack={handleBack}
      />
      <TopNavbar onMobileMenuClick={() => setIsSidebarOpen(true)} leftOffset={leftOffset} onNewChat={handleNewChat} />
      <main 
        className={`relative flex-1 flex flex-col h-[100dvh] max-h-[100dvh] overflow-hidden transition-[margin-left] duration-300 ease-in-out ${isSidebarExpanded ? 'lg:ml-[220px]' : 'lg:ml-[70px]'}`}
        style={{ overscrollBehaviorY: 'none' }}
      >
        <div className="flex flex-col flex-1 h-full">
          <div
            className="flex-1 min-h-0 overflow-y-auto scrollbar-thin scrollbar-track-transparent scrollbar-thumb-violet-primary w-full"
            ref={messageListRef}
            style={{ overscrollBehaviorY: 'contain', WebkitOverflowScrolling: 'touch' as any }}
          >
            <div className="w-full max-w-[900px] mx-auto px-5 pt-12 lg:pt-4" style={{ paddingBottom: `${inputHeight + keyboardOffset + 8}px` }}>
              {isEmptyState ? (
                <EmptyState onSendMessage={submitMessage} />
              ) : (
                <MessageList
                  messages={messages}
                  isInitialLoading={isInitialLoading}
                  isHistoryLoading={isHistoryLoading}
                  isThinking={isThinking}
                  thinkingMessage={thinkingMessage}
                  onOptionClick={submitMessage}
                  providerId={providerId}
                />
              )}
            </div>
          </div>
          {!isEmptyState && (
            <div
              ref={inputContainerRef}
              className="w-full max-w-[900px] mx-auto px-5"
              style={{ position: 'fixed', zIndex: 20, left: inputCenterLeft != null ? `${inputCenterLeft}px` : `calc(50% + ${Math.max(0, leftOffset) / 2}px)`, transform: 'translateX(-50%)', bottom: `${keyboardOffset + 8}px`, paddingBottom: 0, touchAction: 'none', overscrollBehavior: 'none' }}
            >
              <ChatInput onSendMessage={submitMessage} isKeyboardOpen={keyboardOffset > 0} currentCredits={currentCredits} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
