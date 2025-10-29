import { useEffect, useState, useCallback } from 'react';
import { ApiMessage } from '../types';
import { STREAMING_PRESETS } from './StreamingConfig';

interface UseStreamingManagerProps {
  messages: ApiMessage[];
  config?: keyof typeof STREAMING_PRESETS;
}

export function useStreamingManager({ messages, config = 'default' }: UseStreamingManagerProps) {
  const [closingMessages, setClosingMessages] = useState<Set<string>>(new Set());
  const streamingConfig = STREAMING_PRESETS[config];
  
  // Track streaming messages
  const streamingMessages = messages.filter(msg => msg.status === 'streaming');
  const streamingMessageIds = new Set(streamingMessages.map(msg => msg.id || ''));
  
  // Handle auto-removal when new non-streaming messages are added
  useEffect(() => {
    if (!streamingConfig.autoRemoval.enabled || !streamingConfig.autoRemoval.onNewMessage) {
      return;
    }

    const nonStreamingMessages = messages.filter(msg => msg.status !== 'streaming');
    const latestMessage = nonStreamingMessages[nonStreamingMessages.length - 1];
    
    // Only close streaming messages if there's actually a NEW non-streaming message
    // Added check to prevent immediate closure on component mount
    if (latestMessage && streamingMessages.length > 0 && nonStreamingMessages.length > 1) {
      const delay = streamingConfig.autoRemoval.delay;
      
      console.log('Auto-removing streaming messages due to new message:', latestMessage);
      setTimeout(() => {
        streamingMessages.forEach(msg => {
          if (msg.id) {
            setClosingMessages(prev => new Set(prev).add(msg.id!));
          }
        });
      }, delay);
    }
  }, [messages.length, streamingConfig.autoRemoval.enabled, streamingConfig.autoRemoval.onNewMessage, streamingConfig.autoRemoval.delay]);

  // Handle auto-removal when streaming completes
  useEffect(() => {
    if (!streamingConfig.autoRemoval.enabled || !streamingConfig.autoRemoval.onStreamComplete) {
      return;
    }

    // Check if any previously streaming messages are now completed
    const completedMessageIds = new Set<string>();
    messages.forEach(msg => {
      if (msg.id && msg.status !== 'streaming' && streamingMessageIds.has(msg.id)) {
        completedMessageIds.add(msg.id);
      }
    });

    if (completedMessageIds.size > 0) {
      const delay = streamingConfig.autoRemoval.delay;
      setTimeout(() => {
        setClosingMessages(prev => {
          const newClosing = new Set(prev);
          completedMessageIds.forEach(id => newClosing.add(id));
          return newClosing;
        });
      }, delay);
    }
  }, [messages, streamingConfig.autoRemoval.enabled, streamingConfig.autoRemoval.onStreamComplete, streamingConfig.autoRemoval.delay]);

  // Clean up closed messages
  const handleAnimationComplete = useCallback((messageId: string) => {
    setClosingMessages(prev => {
      const newClosing = new Set(prev);
      newClosing.delete(messageId);
      return newClosing;
    });
  }, []);

  // Check if a message is closing
  const isMessageClosing = useCallback((messageId: string) => {
    return closingMessages.has(messageId);
  }, [closingMessages]);

  // Manual close function
  const closeMessage = useCallback((messageId: string) => {
    setClosingMessages(prev => new Set(prev).add(messageId));
  }, []);

  // Close all streaming messages
  const closeAllStreaming = useCallback(() => {
    streamingMessages.forEach(msg => {
      if (msg.id) {
        setClosingMessages(prev => new Set(prev).add(msg.id!));
      }
    });
  }, [streamingMessages]);

  return {
    isMessageClosing,
    handleAnimationComplete,
    closeMessage,
    closeAllStreaming,
    streamingCount: streamingMessages.length,
    closingCount: closingMessages.size,
  };
}