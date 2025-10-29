import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { ChatAgentApiService } from "../../../api/chatagent";
import { ApiMessage } from "../types";
import { useChatStream } from "./useChatStream";
import { processHistoryMessages, clearDuplicateTracking } from "../logic/message-processing";
import { applyDelta, applyUpdate } from "../logic/streaming";
import { makeInsufficientCreditsMessage } from "../logic/state-management";

export function useChat(chatId?: string, providerId?: string) {
  const [messages, setMessages] = useState<ApiMessage[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isInterruptResponse, setIsInterruptResponse] = useState(false);
  const [lastInterruptType, setLastInterruptType] = useState<string | null>(null);
  const [lastInputOptionContent, setLastInputOptionContent] = useState<string | null>(null);
  const [isThinking, setIsThinking] = useState(false);
  const [thinkingMessage, setThinkingMessage] = useState<ApiMessage | null>(null);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [refetchCounter, setRefetchCounter] = useState(0);
  const [currentCredits, setCurrentCredits] = useState<number | null>(null);

  const userInteracted = useRef<boolean>(false);
  const streamNodeMessageIndex = useRef<Record<string, number>>({});
  const [searchParams, setSearchParams] = useSearchParams();

  // History processing moved to ../logic/processHistory

  const { startStream, closeStream } = useChatStream({
    chatId,
    providerId,
    onDelta: (data) => {
      if (data.stream_type !== "messages") return;
      // Log received streaming chunk (per node)
      console.debug("[chat] onDelta received chunk:", {
        node: data.node,
        len: data.message?.length,
        preview: data.message?.slice?.(0, 120)
      });

      // console.log("\n\nset message : "+JSON.stringify(messages),"\n\n"); 

      setMessages((prev) =>
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
  
        setMessages(prev => {
          const cleanedMessages = prev.filter(msg => msg.status !== 'streaming');
          console.debug("[chat] onUpdate received:", {
            node: data.node,
            type: data.type_,
            status: data.status,
            hasContent: data.current_messages?.some(m => !!m.content),
          });
          const { messages: updatedMessages, updated } = applyUpdate(cleanedMessages, data, streamNodeMessageIndex.current);

          const isInterrupt = data.type_ === 'interrupt';
          const thinking = !isInterrupt && data.next_node !== '__end__';
          setIsThinking(thinking);
          setThinkingMessage(thinking ? data : null);

          if (updated) {
            if (isInterrupt) {
              setIsInterruptResponse(true);
              // Capture the interrupt type from data
              const iType = data.data?.type || null;
              setLastInterruptType(iType);
              if (iType === 'input_option') {
                const c = data.data?.data?.content ?? '';
                setLastInputOptionContent(c);
              }
            } else if (data.next_type !== 'human') {
              setIsInterruptResponse(false);
              setLastInterruptType(null);
              setLastInputOptionContent(null);
            }
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
        setMessages((prev) => [...prev, errorMessage]);
        userInteracted.current = true;
      }
    },
    onDone: () => {
      setIsThinking(false);
      setThinkingMessage(null);
      setRefetchCounter(c => c + 1);
      streamNodeMessageIndex.current = {};
      
      // Clean up any remaining streaming messages when stream is done
      setMessages(prev => {
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
      provider_id: providerId, thread_id: chatId, role: "human_message", node: "input",
      status: "success",
      reason: "User input", 
      current_messages: [{ role: "human", content: text }], 
      type_: "human",
    };
    setMessages(prev => [...prev, userMessage]);
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
      setIsInterruptResponse(false);
      setLastInterruptType(null);
    }
  };

  useEffect(() => {
    setMessages([]); setIsThinking(false); setThinkingMessage(null);
    setPage(1); setHasMore(true); userInteracted.current = false;
    clearDuplicateTracking(); // Clear duplicate tracking for new chat
    closeStream();

    if (!providerId || !chatId) { setIsInitialLoading(false); return; }

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
              setIsInterruptResponse(true);
              // Set the last interrupt type if it's an interrupt
              if (lastMessage.type_ === 'interrupt') {
                const lType = lastMessage.data?.type || null;
                setLastInterruptType(lType);
                if (lType === 'input_option') {
                  const c = lastMessage.data?.data?.content ?? '';
                  setLastInputOptionContent(c);
                }
              }
            } else {
              setIsInterruptResponse(false);
              setLastInterruptType(null);
              setLastInputOptionContent(null);
            }
            setMessages(processed);
          }
          setPage(2);
        } else {
          setHasMore(false);
        }
      } catch (e) {
        console.error("Failed to load initial history:", e);
      } finally {
        setIsInitialLoading(false);
        const authSuccessPlatform = searchParams.get('auth_success');
        if (authSuccessPlatform && lastMessage && lastMessage.data?.type === 'connect') {
          const confirmationMessage = `My ${authSuccessPlatform} account is connected. Please continue.`;
          addUserMessage(confirmationMessage);
          startStream(confirmationMessage, true);
          const newSearchParams = new URLSearchParams(searchParams);
          newSearchParams.delete('auth_success');
          setSearchParams(newSearchParams, { replace: true });
        }
      }
    };
    loadInitialHistory();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chatId, providerId, closeStream]);

  return {
    messages, page, hasMore, isThinking, thinkingMessage,
    isHistoryLoading, isInitialLoading, refetchCounter,
    currentCredits,
    userInteracted,
    loadMoreHistory: {
      set: setIsHistoryLoading,
      get: isHistoryLoading,
      process: async () => {
        if (isHistoryLoading || !hasMore || !providerId || !chatId) return 0;
        setIsHistoryLoading(true);
        try {
          const history = await ChatAgentApiService.getChatHistory(providerId, chatId, page, 30);
          if (history.length < 30) setHasMore(false);
          if (history.length > 0) {
            const processedHistory = processHistoryMessages(history);
            setMessages(prev => [...processedHistory, ...prev]);
            setPage(p => p + 1);
          }
          return history.length > 0 ? 1 : 0;
        } catch (error) { return 0; }
        finally { setIsHistoryLoading(false); }
      },
    },
    submitMessage,
  };
}