import { useState, useEffect } from 'react';
import { ChatAgentApiService } from '../../../api/chatagent';
import { ApiMessage } from '../types';
import { processHistoryMessages } from '../logic/message-processing';

interface UseHistoryManagementProps {
  providerId?: string;
  chatId?: string;
  clearMessages: () => void;
  updateMessages: (updater: (prev: ApiMessage[]) => ApiMessage[]) => void;
  handleInterruptUpdate: (data: any) => void;
}

export function useHistoryManagement({
  providerId,
  chatId,
  clearMessages,
  updateMessages,
  handleInterruptUpdate
}: UseHistoryManagementProps) {
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);

  // Load initial history
  useEffect(() => {
    clearMessages();
    setPage(1);
    setHasMore(true);

    if (!providerId || !chatId) {
      setIsInitialLoading(false);
      return;
    }

    const loadInitialHistory = async () => {
      setIsInitialLoading(true);
      let lastMessage: ApiMessage | null = null;
      try {
        const threads = await ChatAgentApiService.getThreads(providerId);
        if (threads.some((t: any) => t.thread_id === chatId)) {
          const history = await ChatAgentApiService.getChatHistory(providerId, chatId, 1, 30);
          if (history.length < 30) setHasMore(false);
          if (history && history.length > 0) {
            const processed = processHistoryMessages(history);
            lastMessage = processed[processed.length - 1];
            if (lastMessage && lastMessage.next_type === 'human') {
              handleInterruptUpdate(lastMessage);
            }
            updateMessages(() => processed);
          }
          setPage(2);
        } else {
          setHasMore(false);
        }
      } catch (e) {
        console.error("Failed to load initial history:", e);
      } finally {
        setIsInitialLoading(false);
      }
    };
    
    loadInitialHistory();
  }, [chatId, providerId, clearMessages, updateMessages, handleInterruptUpdate]);

  const loadMoreHistory = async () => {
    if (isHistoryLoading || !hasMore || !providerId || !chatId) return 0;
    setIsHistoryLoading(true);
    try {
      const history = await ChatAgentApiService.getChatHistory(providerId, chatId, page, 30);
      if (history.length < 30) setHasMore(false);
      if (history.length > 0) {
        const processedHistory = processHistoryMessages(history);
        updateMessages(prev => [...processedHistory, ...prev]);
        setPage(p => p + 1);
      }
      return history.length > 0 ? 1 : 0;
    } catch (error) {
      return 0;
    } finally {
      setIsHistoryLoading(false);
    }
  };

  return {
    page,
    hasMore,
    isHistoryLoading,
    isInitialLoading,
    loadMoreHistory: {
      set: setIsHistoryLoading,
      get: isHistoryLoading,
      process: loadMoreHistory,
    }
  };
}