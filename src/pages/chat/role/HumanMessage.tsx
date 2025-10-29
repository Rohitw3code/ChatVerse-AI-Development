import { Markdown } from '../ui/components/Markdown';
import { ApiMessage } from "../types";

interface HumanMessageProps {
  message: ApiMessage;
}

export function HumanMessage({ message }: HumanMessageProps) {
  const rawContent = message.current_messages?.[0]?.content || '';
  let content = rawContent;
  
  // If backend echoed a JSON payload, display only the human_response field
  if (typeof rawContent === 'string' && rawContent.trim().startsWith('{')) {
    try {
      const obj = JSON.parse(rawContent);
      if (obj && typeof obj === 'object' && 'human_response' in obj) {
        content = obj.human_response ?? rawContent;
      }
    } catch {
      // not JSON, leave as-is
    }
  }
  
  return (
    <div className="flex justify-end mb-5">
      <div className="max-w-[80%] py-3 px-4 rounded-2xl rounded-br-md bg-[#373737] text-white break-words leading-snug">
        <div className="max-w-none space-y-1">
          <Markdown>{content}</Markdown>
        </div>
      </div>
    </div>
  );
}