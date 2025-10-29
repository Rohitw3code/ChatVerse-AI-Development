import { ApiMessage } from '../../types';
import { StreamIndex } from '../message-processing/messageReducers';
import { dlog } from './debug';

// Helpers to decide display/update behavior
const isDisplayable = (m: ApiMessage) =>
  (m.current_messages?.some((x) => x.content) ?? false) ||
  m.type_ === 'interrupt';

// Track last processed content to avoid duplicates
const lastProcessedContent: Record<string, string> = {};

// Handle "updates" or "custom" events to finalize or insert messages
export function applyUpdate(
  prev: ApiMessage[],
  data: ApiMessage,
  nodeIndex: StreamIndex
): { messages: ApiMessage[]; updated: boolean; clearStreamingIndex?: boolean } {
  const nodeName = data.node;
  if (!nodeName) return { messages: prev, updated: false };

  const newMessages = [...prev];
  const streamingIdx = nodeIndex[nodeName];
  let updated = false;

  // Clear duplicate tracking for this node when finalizing
  if (data.status === 'success' || data.status === 'failed') {
    const nodeKey = `${nodeName}-${data.provider_id}-${data.thread_id}`;
    delete lastProcessedContent[nodeKey];
  }

  if (streamingIdx !== undefined && newMessages[streamingIdx]) {
    // Check if the existing message is a streaming message
    const streamingMessage = newMessages[streamingIdx];
    const isStreamingMessage = streamingMessage.status === 'streaming';
    
    // Enhanced removal conditions for streaming messages
    const shouldRemoveStreaming = isStreamingMessage && (
      // Remove when stream type changes to updates or custom
      data.stream_type === 'updates' || 
      data.stream_type === 'custom' ||
      // Remove when streaming explicitly stops
      data.status === 'success' ||
      data.status === 'failed' ||
      data.status === 'completed' ||
      // Remove when next_node indicates end of streaming
      data.next_node === '__end__' ||
      data.next_node === 'end'
    );

    if (shouldRemoveStreaming) {
      // Immediately remove the streaming message when streaming stops
      dlog('update.remove.streaming', {
        node: nodeName,
        type: data.type_,
        status: data.status,
        streamType: data.stream_type,
        reason: 'streaming_stopped'
      });
      newMessages.splice(streamingIdx, 1);
      delete nodeIndex[nodeName];
      
      // Adjust all indices in nodeIndex that are greater than the removed index
      Object.keys(nodeIndex).forEach(key => {
        if (nodeIndex[key] > streamingIdx) {
          nodeIndex[key]--;
        }
      });
      
      updated = true;
      
      // If the update data is displayable, add it as a new message
      if (isDisplayable(data)) {
        newMessages.push(data);
      }
    } else if (isDisplayable(data)) {
      dlog('update.replace.streaming', {
        node: nodeName,
        type: data.type_,
        status: data.status,
      });
      newMessages[streamingIdx] = data;
      delete nodeIndex[nodeName];
      updated = true;
    }
  } else if (
    data.type_ === 'tool' &&
    (data.status === 'success' || data.status === 'failed')
  ) {
    const toolExecIndex = newMessages.findIndex(
      (m) =>
        m.node === nodeName &&
        m.type_ === 'tool' &&
        m.status !== 'success' &&
        m.status !== 'failed'
    );
    if (toolExecIndex !== -1) {
      dlog('update.replace.toolFinalize', {
        node: nodeName,
        status: data.status,
      });
      newMessages[toolExecIndex] = data;
      updated = true;
    }
  } else if (isDisplayable(data)) {
    const isAlreadyPresent = data.id
      ? newMessages.some((m) => m.id === data.id)
      : false;
    if (!isAlreadyPresent) {
      dlog('update.insert.displayable', {
        node: nodeName,
        type: data.type_,
      });
      newMessages.push(data);
      updated = true;
    }
  }

  return { messages: updated ? newMessages : prev, updated };
}
