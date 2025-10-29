import { useEffect, useRef, useLayoutEffect } from 'react';
import { ApiMessage } from '../types';

interface UseScrollManagementProps {
  messages: ApiMessage[];
  isInitialLoading: boolean;
  isHistoryLoading: boolean;
  keyboardOffset: number;
  inputHeight: number;
  loadMoreHistory: {
    get: boolean;
    process: () => Promise<number>;
  };
  userInteracted: React.MutableRefObject<boolean>;
  messageListRef: React.RefObject<HTMLDivElement>;
}

export function useScrollManagement({
  messages,
  isInitialLoading,
  isHistoryLoading,
  keyboardOffset,
  inputHeight,
  loadMoreHistory,
  userInteracted,
  messageListRef
}: UseScrollManagementProps) {
  const prevScrollHeightRef = useRef<number>(0);

  // Handle scroll to load more history
  useEffect(() => {
    const handleScroll = async () => {
      if (messageListRef.current && messageListRef.current.scrollTop === 0 && !loadMoreHistory.get) {
        prevScrollHeightRef.current = messageListRef.current.scrollHeight;
        await loadMoreHistory.process();
      }
    };
    const element = messageListRef.current;
    element?.addEventListener('scroll', handleScroll);
    return () => element?.removeEventListener('scroll', handleScroll);
  }, [loadMoreHistory]);

  // Handle auto-scroll on new messages
  useLayoutEffect(() => {
    const list = messageListRef.current;
    if (!list) return;
    if (userInteracted.current) {
        list.scrollTop = list.scrollHeight;
        userInteracted.current = false;
    } else if (prevScrollHeightRef.current > 0) {
      list.scrollTop = list.scrollHeight - prevScrollHeightRef.current;
      prevScrollHeightRef.current = 0;
    } else if(!isHistoryLoading && !isInitialLoading){
      list.scrollTop = list.scrollHeight;
    }
  }, [messages, isInitialLoading, isHistoryLoading]);

  // Handle scroll adjustment for keyboard/input changes
  useEffect(() => {
    const list = messageListRef.current;
    if (!list) return;
    const delta = list.scrollHeight - (list.scrollTop + list.clientHeight);
    if (delta < 40) {
      list.scrollTop = list.scrollHeight;
    }
  }, [keyboardOffset, inputHeight]);

  // No return needed since we use the passed ref
}