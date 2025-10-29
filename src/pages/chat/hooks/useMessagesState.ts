import { useState } from 'react';
import { ApiMessage } from '../types';

export function useMessagesState() {
  const [messages, setMessages] = useState<ApiMessage[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [thinkingMessage, setThinkingMessage] = useState<ApiMessage | null>(null);

  const addMessage = (message: ApiMessage) => {
    setMessages(prev => [...prev, message]);
  };

  const updateMessages = (updater: (prev: ApiMessage[]) => ApiMessage[]) => {
    setMessages(updater);
  };

  const clearMessages = () => {
    setMessages([]);
    setIsThinking(false);
    setThinkingMessage(null);
  };

  const handleThinkingState = (data: any) => {
    const isInterrupt = data.type_ === 'interrupt';
    const thinking = !isInterrupt && data.next_node !== '__end__';
    setIsThinking(thinking);
    setThinkingMessage(thinking ? data : null);
  };

  const stopThinking = () => {
    setIsThinking(false);
    setThinkingMessage(null);
  };

  return {
    messages,
    isThinking,
    thinkingMessage,
    setMessages,
    setIsThinking,
    setThinkingMessage,
    addMessage,
    updateMessages,
    clearMessages,
    handleThinkingState,
    stopThinking
  };
}