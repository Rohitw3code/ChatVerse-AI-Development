import { ApiMessage } from "../../types";

// Normalize and merge tool messages within fetched history
export function processHistoryMessages(history: any[]): ApiMessage[] {
  const parseRawMessage = (rawMsg: any): ApiMessage | null => {
    try {
      const { type, ...rest } = rawMsg;
      return {
        ...rest,
        type_: type,
        id: rawMsg.id,
        current_messages:
          typeof rawMsg.current_messages === "string"
            ? JSON.parse(rawMsg.current_messages)
            : rawMsg.current_messages,
        tool_output:
          typeof rawMsg.tool_output === "string"
            ? JSON.parse(rawMsg.tool_output)
            : rawMsg.tool_output,
        params:
          typeof rawMsg.params === "string"
            ? JSON.parse(rawMsg.params)
            : rawMsg.params,
        usage:
          typeof rawMsg.usage === "string"
            ? JSON.parse(rawMsg.usage)
            : rawMsg.usage,
        data:
          typeof rawMsg.data === "string"
            ? JSON.parse(rawMsg.data)
            : rawMsg.data,
      } as ApiMessage;
    } catch (e) {
      return null;
    }
  };

  const reversedHistory = [...history].reverse();
  const processed: ApiMessage[] = [];

  for (const rawMsg of reversedHistory) {
    const msg = parseRawMessage(rawMsg);
    if (!msg) continue;

    // Skip messages with no current_messages or empty content
    if (!msg.current_messages || msg.current_messages.length === 0) {
      continue;
    }

    // Skip messages where all current_messages have empty/null content
    const hasValidContent = msg.current_messages.some(
      (cm) => cm.content && cm.content.trim() !== ''
    );
    
    if (!hasValidContent) {
      continue;
    }

    if (
      msg.type_ === "tool" &&
      (msg.status === "success" || msg.status === "failed")
    ) {
      const index = processed.findIndex(
        (m) =>
          m.node === msg.node &&
          m.type_ === "tool" &&
          m.status !== "success" &&
          m.status !== "failed"
      );
      if (index !== -1) {
        processed[index] = msg;
      } else {
        processed.push(msg);
      }
    } else {
      processed.push(msg);
    }
  }

  return processed;
}
