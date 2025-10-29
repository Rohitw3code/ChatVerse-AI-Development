import { Markdown } from '../ui/components/Markdown';
import { ApiMessage } from "../types";

interface AiMessageProps {
  message: ApiMessage;
}

export function AiMessage({ message }: AiMessageProps) {
  const isLastNode = message.next_node === '__end__' || message.next_node === 'end';

  return (
    <div className="flex justify-start mb-5 w-full">
      <div className="max-w-[80%] py-3 px-4 rounded-2xl rounded-bl-md leading-snug text-white bg-[#1a1a1a] overflow-hidden">
        <div className="max-w-none break-words overflow-wrap-anywhere space-y-1">
          {message.current_messages && message.current_messages.length > 0
            ? message.current_messages.map((cm, idx) => (
                <Markdown key={idx}>{cm.content}</Markdown>
              ))
            : message.reason && !isLastNode && <div>Final Answer</div>
          }
        </div>
      </div>
    </div>
  );
}