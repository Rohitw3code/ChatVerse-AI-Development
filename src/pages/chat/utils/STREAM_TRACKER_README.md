# Stream Tracker

A simple debugging utility to track how streaming text messages are processed and displayed in the chat interface.

## Purpose

This tracker helps identify issues with text streaming by logging:
1. **Raw messages** received from the server
2. **Text processing logic** (how chunks are combined)
3. **Final content** displayed in the UI

## Usage

### Enable Tracking
Open browser console and run:
```javascript
enableStreamTracker()
```
Or manually:
```javascript
localStorage.setItem('chat.stream.tracker', '1')
```

### Disable Tracking
Open browser console and run:
```javascript
disableStreamTracker()
```
Or manually:
```javascript
localStorage.removeItem('chat.stream.tracker')
```

## What Gets Logged

### 1. Raw Message Reception
```
[Stream Tracker] Raw message received: {
  node: "agent_node",
  streamType: "messages", 
  rawMessage: "Hello, I can help...",
  messageLength: 20,
  timestamp: "2025-01-12T10:30:00.000Z"
}
```

### 2. Delta Processing
```
[Stream Tracker] Delta received for node: agent_node {
  chunkNumber: 1,
  receivedText: "Hello, I can help...",
  receivedLength: 20,
  hasExistingMessage: false,
  existingIndex: undefined
}
```

### 3. Text Processing Logic
```
[Stream Tracker] ✅ Cumulative replace - new text contains current as prefix
[Stream Tracker] ➕ Append suffix { commonPrefixLength: 15, suffix: " you today", ... }
[Stream Tracker] ⏸️ Keep longer - current is longer and contains new text
```

### 4. Final Display Content
```
[Stream Tracker] 🖥️ Display Update - Node: agent_node {
  status: "streaming",
  contentLength: 25,
  contentPreview: "Hello, I can help you tod...",
  isStreaming: true,
  fullContent: "Hello, I can help you today"
}
```

## Troubleshooting Common Issues

### Duplicated Text
Look for logs showing:
- Multiple "Append suffix" operations on the same content
- Common prefix calculations that are incorrect

### Missing Text
Look for:
- "Keep longer" operations that might be preserving old content
- Raw messages that aren't being processed

### Out-of-Order Chunks
Look for:
- Timestamp sequences in raw message logs
- Chunk numbers that don't increment properly

## Implementation

The tracker is implemented across:
- `useChatStream.ts` - Logs raw SSE data
- `messageReducers.ts` - Logs text processing logic  
- `AiMessage.tsx` - Logs final display content
- `streamTracker.ts` - Utility functions

## Performance

The tracker only runs when explicitly enabled and has minimal performance impact when disabled.