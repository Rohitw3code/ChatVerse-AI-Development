
import { ApiMessage } from "../../types";
import { MessageRenderer } from "./MessageRenderer";
import { Thinking } from '../shared/Thinking';
import { useStreamingManager } from '../../components/useStreamingManager';

interface MessageListProps {
  messages: ApiMessage[];
  isInitialLoading: boolean;
  isHistoryLoading: boolean;
  isThinking: boolean;
  thinkingMessage: ApiMessage | null;
  onOptionClick: (option: string, additionalData?: any) => void;
  providerId: string;
}

export function MessageList({
  messages, isInitialLoading, isHistoryLoading, isThinking,
  thinkingMessage, onOptionClick, providerId
}: MessageListProps) {
  const { isMessageClosing, handleAnimationComplete } = useStreamingManager({ messages });
  if (isInitialLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="w-8 h-8 border-4 rounded-full animate-spin border-surface-secondary border-t-violet-primary"></div>
      </div>
    );
  }

  return (
    <>
      {isHistoryLoading && (
        <div className="flex justify-center p-4">
          <div className="w-6 h-6 border-2 rounded-full animate-spin border-surface-secondary border-t-violet-primary"></div>
        </div>
      )}
      {messages.map((m, i) => (
        <MessageRenderer 
          key={m.id || `${m.node}-${i}`} 
          message={m} 
          onOptionClick={onOptionClick} 
          providerId={providerId}
          isClosing={m.id ? isMessageClosing(m.id) : false}
          onAnimationComplete={m.id ? () => handleAnimationComplete(m.id!) : undefined}
        />
      ))}
      {isThinking && <Thinking message={thinkingMessage} />}
    </>
  );
}