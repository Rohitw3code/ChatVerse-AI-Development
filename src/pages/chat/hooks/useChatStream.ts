import { useRef, useCallback } from "react";
import { ChatAgentApiService } from "../../../api/chatagent";
import { ApiMessage } from "../types";

interface ChatStreamProps {
  chatId?: string;
  providerId?: string;
  onDelta: (data: ApiMessage) => void;
  onUpdate: (data: ApiMessage) => void;
  onError: (error: any) => void;
  onDone: () => void;
}

export function useChatStream({ chatId, providerId, onDelta, onUpdate, onError, onDone }: ChatStreamProps) {
  const streamRef = useRef<EventSource | null>(null);

  const startStream = useCallback((userText: string, isHumanResponse: boolean = false) => {
    if (!providerId || !chatId) return;
    if (streamRef.current) {
      streamRef.current.close();
    }

    const es = ChatAgentApiService.sendMessageStream({
      message: userText,
      chat_id: chatId,
      provider_id: providerId,
      human_response: isHumanResponse,
    });
    streamRef.current = es;

    es.addEventListener("delta", (evt: MessageEvent) => {
      // Raw SSE payload for debugging
      try {
        const raw = typeof evt.data === 'string' ? evt.data : String(evt.data);
      } catch { /* ignore logging errors */ }
      try {
        const data: ApiMessage = JSON.parse(evt.data);
        
        // Always log raw stream data for debugging
        if (data.stream_type === "messages" && data.message) {
          console.log(`[Text Chunk] RAW RECEIVED from server:`, data.message);
          console.log(`[Text Chunk] Node: ${data.node}, Length: ${data.message.length}`);
        }
                
        if (data.stream_type === "messages") {
          onDelta(data);
        } else if (data.stream_type === "updates" || data.stream_type === "custom") {
          onUpdate(data);
        }

      } catch (e) {
        console.error("Error processing stream delta:", e);
      }
    });

    es.addEventListener("error", (evt: MessageEvent) => {
      console.log("[chat-stream] error event received", {
        isTrusted: evt.isTrusted,
        type: evt.type,
        data: evt.data,
        target: evt.target,
        eventData: evt
      });
      try {
        if (evt.data) {
          const errorData = JSON.parse(evt.data);
          console.log("[chat-stream] parsed error data:", errorData);
          onError(errorData);
        } else {
          console.log("[chat-stream] error event has no data");
          onError({ error: "Stream error", isTrusted: evt.isTrusted });
        }
      } catch (e) {
        console.log("[chat-stream] error parsing error data:", e);
        onError(e);
      }
      closeStream();
    });

    es.addEventListener("done", () => {
      console.debug("[chat-stream] done event received");
      onDone();
      closeStream();
    });

    const closeStream = () => {
      if (streamRef.current) {
        streamRef.current.close();
        streamRef.current = null;
      }
    };
  }, [chatId, providerId, onDelta, onUpdate, onError, onDone]);

  const closeStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.close();
      streamRef.current = null;
    }
  }, []);

  return { startStream, closeStream };
}