import { ApiMessage } from "../../types";
import { TRACKED_TOOL_NODES } from "../../type/ToolExecution";
import { HumanMessage } from "../../role/HumanMessage";
import { AiMessage } from "../../role/AiMessage";
import { ToolMessage } from "../../role/ToolMessage";
import { StreamingMessage } from "../shared/StreamingMessage";
import { InterruptNode } from "../interactions/InterruptNode";

const HIDDEN_NODES = new Set([
  'starter_node', 'planner_node',
  'gmail_agent_node', 'instagram_agent_node',
  "research_agent_node","task_selection_node",
  'youtube_agent_node','youtube_manager_node',"search_agent_node","sheets_agent_node","gdoc_agent_node"
]);

interface MessageRendererProps {
  message: ApiMessage;
  onOptionClick: (option: string, additionalData?: any) => void;
  providerId: string;
  isClosing?: boolean;
  onAnimationComplete?: () => void;
}

export function MessageRenderer({ message, onOptionClick, providerId, isClosing, onAnimationComplete }: MessageRendererProps) {
  const isLastNode = message.next_node === '__end__' || message.next_node === 'end';

  // Priority: Show streaming messages for ALL nodes
  if (message.status === 'streaming') {
    return (
      <StreamingMessage
        message={message}
        isClosing={isClosing}
        onAnimationComplete={onAnimationComplete}
      />
    );
  }

  // Handle interrupt nodes
  if (message.type_ === "interrupt") {
    return (
      <InterruptNode
        message={message}
        onOptionClick={onOptionClick}
        providerId={providerId}
        isClosing={isClosing}
        onAnimationComplete={onAnimationComplete}
      />
    );
  }

  // Apply hidden nodes logic only for non-streaming, completed messages
  if (HIDDEN_NODES.has(message.node) && !isLastNode) {
    return null;
  }

  if (message.role === "human_message") {
    return <HumanMessage message={message} />;
  }

  const nodeName = message.node?.trim();
  if (message.type_ === "tool" && nodeName && TRACKED_TOOL_NODES.has(nodeName)) {
    return <ToolMessage message={message} />;
  }

  return <AiMessage message={message} />;
}

export default MessageRenderer;