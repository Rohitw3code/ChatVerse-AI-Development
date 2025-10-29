import { ApiMessage } from "../../types";
import { StreamingMessageBox } from "../../components/StreamingMessageBox";

interface StreamingMessageProps {
  message: ApiMessage;
  isClosing?: boolean;
  onAnimationComplete?: () => void;
}

export function StreamingMessage({ message, isClosing, onAnimationComplete }: StreamingMessageProps) {
  if (message.status !== 'streaming') {
    return null;
  }

  // Show "ChatVerse Thinking" for any streaming operation
  return (
    <div className="flex justify-start mb-5">
      <StreamingMessageBox 
        message={message} 
        isClosing={isClosing}
        onAnimationComplete={onAnimationComplete}
      />
    </div>
  );
}
