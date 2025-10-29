import { ApiMessage } from '../../types';
import { StreamIndex } from '../message-processing/messageReducers';
import { dlog, incChunk } from './debug';

// Track last processed content to avoid duplicates
const lastProcessedContent: Record<string, string> = {};

// Handle "delta" events (stream_type: messages) to append partial content
export function applyDelta(
  prev: ApiMessage[],
  data: ApiMessage,
  nodeIndex: StreamIndex,
  providerId: string,
  chatId: string
): ApiMessage[] {
  const nodeName = data.node;
  if (!nodeName) return prev;

  const newMessages = [...prev];
  const idx = nodeIndex[nodeName];

  // Always use raw chunk text as-is (show exact data, even if it's JSON)
  const text = (data.message ?? '').toString();

  console.log("\n\n TEXT[] : "+text);

  const displayText = text;

  const chunkNo = incChunk(nodeName);

  // Check for duplicate content at the node level
  const nodeKey = `${nodeName}-${providerId}-${chatId}`;
  const lastContent = lastProcessedContent[nodeKey];
  if (lastContent === text) {
    return prev; // Return unchanged messages
  }
  lastProcessedContent[nodeKey] = text;

  dlog('delta.in', {
    node: nodeName,
    chunkNo,
    textLen: text.length,
    textPreview: text.slice(0, 120),
    hasIndex: idx !== undefined,
  });

  if (idx !== undefined && newMessages[idx]) {
    const msg = newMessages[idx];
    // Only update if it's actually a streaming message with the same node to prevent updating previous messages
    if (msg.status === 'streaming' && msg.node === nodeName && msg.current_messages?.[0]?.content !== undefined) {
      const curr = msg.current_messages[0].content || '';
      const finalContent = curr + text;
      msg.current_messages[0].content = finalContent;
      dlog('delta.update', {
        node: nodeName,
        chunkNo,
        prevLen: curr.length,
        newLen: finalContent.length,
      });
      return newMessages;
    } else {
      // If the message at this index is not a streaming message for this node, clear the index
      dlog('delta.invalidIndex', {
        node: nodeName,
        indexNode: msg.node,
        indexStatus: msg.status,
        clearing: true,
      });
      delete nodeIndex[nodeName];
    }
  }

  const newMessage: ApiMessage = {
    id: `streaming-${nodeName}-${Date.now()}`,
    role: 'ai_message',
    node: nodeName,
    status: 'streaming',
    current_messages: [
      {
        role: 'ai',
        content: displayText,
      },
    ],
    provider_id: providerId!,
    thread_id: chatId!,
    type_: 'agent',
  };

  newMessages.push(newMessage);
  nodeIndex[nodeName] = newMessages.length - 1;
  dlog('delta.newMessage', {
    node: nodeName,
    chunkNo,
    contentLen: newMessage.current_messages?.[0]?.content?.length ?? 0,
  });
  return newMessages;
}

// Export function to clear duplicate tracking (useful when chat resets)
export function clearDuplicateTracking() {
  Object.keys(lastProcessedContent).forEach((key) => {
    delete lastProcessedContent[key];
  });
}
