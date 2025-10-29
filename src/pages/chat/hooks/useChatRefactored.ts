import { useState } from "react";
import { useMessagesState } from "./useMessagesState";
import { useInterruptState } from "./useInterruptState";
import { useHistoryManagement } from "./useHistoryManagement";
import { useMessageSubmission } from "./useMessageSubmission";

export function useChatRefactored(chatId?: string, providerId?: string) {
  const [refetchCounter, setRefetchCounter] = useState(0);
  const [currentCredits, setCurrentCredits] = useState<number | null>(null);

  // Message state management
  const messageState = useMessagesState();
  
  // Interrupt state management
  const interruptState = useInterruptState();
  
  // History management
  const historyState = useHistoryManagement({
    providerId,
    chatId,
    clearMessages: messageState.clearMessages,
    updateMessages: messageState.updateMessages,
    handleInterruptUpdate: interruptState.handleInterruptUpdate
  });

  // Message submission handling
  const submissionState = useMessageSubmission({
    chatId,
    providerId,
    isInterruptResponse: interruptState.isInterruptResponse,
    lastInterruptType: interruptState.lastInterruptType,
    lastInputOptionContent: interruptState.lastInputOptionContent,
    addMessage: messageState.addMessage,
    updateMessages: messageState.updateMessages,
    setIsThinking: messageState.setIsThinking,
    setThinkingMessage: messageState.setThinkingMessage,
    handleThinkingState: messageState.handleThinkingState,
    handleInterruptUpdate: interruptState.handleInterruptUpdate,
    resetInterruptState: interruptState.resetInterruptState,
    setRefetchCounter,
    setCurrentCredits
  });

  return {
    messages: messageState.messages,
    isThinking: messageState.isThinking,
    thinkingMessage: messageState.thinkingMessage,
    isInitialLoading: historyState.isInitialLoading,
    isHistoryLoading: historyState.isHistoryLoading,
    refetchCounter,
    currentCredits,
    userInteracted: submissionState.userInteracted,
    loadMoreHistory: historyState.loadMoreHistory,
    submitMessage: submissionState.submitMessage,
  };
}