import { useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ApiMessage } from '../types';
import { useChatStream } from './useChatStream';
import { applyDelta, applyUpdate } from '../logic/streaming';
import { clearDuplicateTracking } from '../logic/message-processing';
import { makeInsufficientCreditsMessage } from '../logic/state-management';

interface UseMessageSubmissionProps {
  chatId?: string;
  providerId?: string;
  isInterruptResponse: boolean;
  lastInterruptType: string | null;
  lastInputOptionContent: string | null;
  addMessage: (message: ApiMessage) => void;
  updateMessages: (updater: (prev: ApiMessage[]) => ApiMessage[]) => void;
  setIsThinking: (thinking: boolean) => void;
  setThinkingMessage: (message: ApiMessage | null) => void;
  handleThinkingState: (data: any) => void;
  handleInterruptUpdate: (data: any) => void;
  resetInterruptState: () => void;
  setRefetchCounter: (updater: (prev: number) => number) => void;
  setCurrentCredits: (credits: number | null) => void;
}

export function useMessageSubmission({
  chatId,
  providerId,
  isInterruptResponse,
  lastInterruptType,
  lastInputOptionContent,
  addMessage,
  updateMessages,
  setIsThinking,
  setThinkingMessage,
  handleThinkingState,
  handleInterruptUpdate,
  resetInterruptState,
  setRefetchCounter,
  setCurrentCredits
}: UseMessageSubmissionProps) {
  const userInteracted = useRef<boolean>(false);
  const streamNodeMessageIndex = useRef<Record<string, number>>({});
  const [searchParams, setSearchParams] = useSearchParams();

  const { startStream, closeStream } = useChatStream({
    chatId,
    providerId,
    onDelta: (data) => {
      if (data.stream_type !== "messages") return;
      console.debug("[chat] onDelta received chunk:", {
        node: data.node,
        len: data.message?.length,
        preview: data.message?.slice?.(0, 120)
      });

      updateMessages((prev) =>
        applyDelta(
          prev,
          data,
          streamNodeMessageIndex.current,
          providerId!,
          chatId!
        )
      );
    },
    onUpdate: (data) => {
      const nodeName = data.node;
      if (!nodeName) return;

      updateMessages(prev => {
        const cleanedMessages = prev.filter(msg => msg.status !== 'streaming');
        console.debug("[chat] onUpdate received:", {
          node: data.node,
          type: data.type_,
          status: data.status,
          hasContent: data.current_messages?.some(m => !!m.content),
        });
        const { messages: updatedMessages, updated } = applyUpdate(cleanedMessages, data, streamNodeMessageIndex.current);

        handleThinkingState(data);

        if (updated) {
          handleInterruptUpdate(data);
        }

        return updated ? updatedMessages : prev;
      });
      userInteracted.current = true;
    },
    onError: (errorData) => {
      if (errorData.error === "Insufficient credits") {
        setCurrentCredits(errorData.current_credits);
        const errorMessage = makeInsufficientCreditsMessage(
          providerId!,
          chatId!,
          errorData
        );
        addMessage(errorMessage);
        userInteracted.current = true;
      }
    },
    onDone: () => {
      setIsThinking(false);
      setThinkingMessage(null);
      setRefetchCounter(c => c + 1);
      streamNodeMessageIndex.current = {};
      
      // Clean up any remaining streaming messages when stream is done
      updateMessages(prev => {
        const cleanedMessages = prev.filter(msg => msg.status !== 'streaming');
        if (cleanedMessages.length !== prev.length) {
          console.debug('[chat] Cleaned up remaining streaming messages on stream done');
        }
        return cleanedMessages;
      });
    }
  });

  const addUserMessage = (text: string) => {
    if (!providerId || !chatId) return;
    const userMessage: ApiMessage = {
      provider_id: providerId, 
      thread_id: chatId, 
      role: "human_message", 
      node: "input",
      status: "success",
      reason: "User input", 
      current_messages: [{ role: "human", content: text }], 
      type_: "human",
    };
    addMessage(userMessage);
    userInteracted.current = true;
  };

  const submitMessage = (text: string, additionalData?: any) => {
    const trimmedText = text.trim();
    if (!trimmedText) return;
    
    setIsThinking(true);
    setThinkingMessage(null);
    
    let messageToSend = trimmedText;
    let displayText = trimmedText;
    
    if (additionalData) {
      // For any interrupt with additionalData (from option buttons), send as JSON
      if (additionalData.type === 'input_option') {
        // For input_option, display the human response (selected option), not JSON
        displayText = trimmedText;
        messageToSend = JSON.stringify({
          modified_text: additionalData.modified_text || '',
          type: 'input_option',
          human_response: trimmedText
        });
      } else {
        // For other interrupt types, send as JSON with the text
        displayText = trimmedText;
        messageToSend = JSON.stringify({
          modified_text: '',
          type: additionalData.type || 'interrupt',
          human_response: trimmedText
        });
      }
      addUserMessage(displayText);
    } else if (isInterruptResponse && lastInterruptType) {
      // For interrupt response from ChatInput (not option buttons), send as JSON
      displayText = trimmedText;
      messageToSend = JSON.stringify({
        modified_text: lastInterruptType === 'input_option' ? (lastInputOptionContent || '') : '',
        type: lastInterruptType,
        human_response: trimmedText
      });
      addUserMessage(displayText);
    } else {
      // For regular messages (non-interrupt), send as plain text
      addUserMessage(trimmedText);
    }
    
    startStream(messageToSend, isInterruptResponse);
    if (isInterruptResponse) {
      resetInterruptState();
    }
  };

  // Handle authentication success
  const handleAuthSuccess = (lastMessage: ApiMessage | null) => {
    const authSuccessPlatform = searchParams.get('auth_success');
    if (authSuccessPlatform && lastMessage && lastMessage.data?.type === 'connect') {
      const confirmationMessage = `My ${authSuccessPlatform} account is connected. Please continue.`;
      addUserMessage(confirmationMessage);
      startStream(confirmationMessage, true);
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.delete('auth_success');
      setSearchParams(newSearchParams, { replace: true });
    }
  };

  const resetForNewChat = () => {
    clearDuplicateTracking();
    closeStream();
  };

  return {
    userInteracted,
    submitMessage,
    handleAuthSuccess,
    resetForNewChat
  };
}