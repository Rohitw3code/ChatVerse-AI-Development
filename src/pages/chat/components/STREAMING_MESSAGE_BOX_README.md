# Streaming Message Box Implementation

## Overview

This implementation adds a dedicated streaming message box component that displays real-time streaming messages with a fixed-height scrollable container and shadow effects. The box automatically appears when streaming begins and is removed when streaming completes.

## Features

### Visual Design
- **Black Theme**: Pure black background (`bg-black`) for clean appearance
- **Shadow Effects**: Enhanced shadow with `shadow-xl shadow-black/50` for depth
- **Clean Border**: Gray-colored border (`border-gray-700/50`) without animations
- **ChatVerse Branding**: "ChatVerse Thinking" title with animated dots
- **Hidden Scrollbar**: Completely invisible scrollbar for clean look
- **Scroll Indicator**: Shows "More content" when user scrolls up (gray theme)

### Enhanced Autoscroll Functionality
- **Smooth Scrolling**: CSS `scroll-smooth` class and `scrollBehavior: 'smooth'`
- **Smart Auto-scroll**: Only auto-scrolls when user is at bottom or content is new
- **MutationObserver**: Watches for DOM changes and auto-scrolls accordingly
- **Scroll Position Tracking**: Detects if user has scrolled up manually
- **Hidden Scrollbar**: Complete scrollbar removal with CSS classes
- **Content Overflow**: Black-themed bottom fade effect indicates more content below

### Temporary Display & Auto-Removal
- **Stream Type Detection**: Vanishes when `stream_type` changes to `"updates"` or `"custom"`
- **Status-Based Removal**: Removes when status becomes `"success"`, `"failed"`, or `"completed"`
- **End Node Detection**: Removes when `next_node` is `"__end__"` or `"end"`
- **Safety Cleanup**: Automatic cleanup in `onDone` callback removes any lingering streaming messages
- **Timeout Warning**: 30-second warning for long-running streams

### Animation Effects
- **Pulsing Dots**: Three violet dots with staggered animation delays (0s, 0.3s, 0.6s)
- **Border Glow**: Subtle animated gradient border that pulses
- **Waiting State**: Animated ping dot when waiting for content

## Vanishing Logic

The streaming message box vanishes (is removed) when the next stream type is "updates" or "custom". This is implemented in the `applyUpdate` function:

```typescript
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
  // Remove the streaming message immediately
  newMessages.splice(streamingIdx, 1);
  delete nodeIndex[nodeName];
  
  // Adjust indices for consistency
  Object.keys(nodeIndex).forEach(key => {
    if (nodeIndex[key] > streamingIdx) {
      nodeIndex[key]--;
    }
  });
  
  // Add new displayable content if available
  if (isDisplayable(data)) {
    newMessages.push(data);
  }
}
```

This ensures:
- ✅ Streaming boxes are removed when streaming phase ends
- ✅ No orphaned streaming messages remain
- ✅ Clean transition to final content display
- ✅ Proper index management for message array

## Implementation Details

### Files Modified

1. **`MessageRenderer.tsx`**
   - Added import for `StreamingMessageBox`
   - Added logic to detect streaming messages (`message.status === 'streaming'`)
   - Routes streaming AI messages to the new component

2. **`StreamingMessageBox.tsx`** (New Component)
   - Fixed-height scrollable container (144px)
   - Auto-scroll functionality using `useRef` and `useEffect`
   - Enhanced visual design with gradients and animations
   - Responsive layout with max-width constraint

### Detection Logic

The streaming detection has **PRIORITY** over hidden nodes logic:
```typescript
// PRIORITY: Show streaming messages for ALL nodes (even hidden ones)
if (message.status === 'streaming' && message.role === "ai_message") {
  return <StreamingMessageBox message={message} />;
}

// Apply hidden nodes logic only for non-streaming, completed messages
if (HIDDEN_NODES.has(message.node) && !isLastNode) {
  return null;
}
```

This ensures that users see "ChatVerse Thinking" for every streaming operation, including normally hidden nodes like:
- `planner_node`, `research_agent_node`, `gmail_agent_node`
- `instagram_manager_node`, `youtube_agent_node`, etc.

### Auto-Removal Mechanism

The streaming message box is automatically removed when:

1. **Stream Type Changes**: When `stream_type` changes from `"messages"` to `"updates"` or `"custom"`
2. **Stream Completion**: When streaming completes and status changes to final state

This is handled by the modified `applyUpdate` function in `update.ts`, which specifically detects when a streaming message receives an update or custom stream type and immediately removes the streaming box from the message array.

## How It Works

### Stream Lifecycle

1. **Stream Start**: 
   - `applyDelta` creates message with `status: 'streaming'`
   - `MessageRenderer` detects streaming status **BEFORE** checking hidden nodes
   - `StreamingMessageBox` renders for **ALL** nodes (including hidden ones)
   - Users see "ChatVerse Thinking" for every streaming operation

2. **Stream Progress**:
   - New content chunks are appended to `current_messages[0].content`
   - Component auto-scrolls to show latest content
   - Visual indicators show active streaming

3. **Stream End**:
   - When `stream_type` changes to `"updates"` or `"custom"`, streaming message is immediately removed
   - `applyUpdate` detects streaming messages receiving update/custom stream types
   - Streaming message is spliced from message array
   - Node indices are adjusted to maintain consistency
   - If update data is displayable, it's added as a new regular message

### Content Handling & Autoscroll

- **Content Display**: Uses `ReactMarkdown` for proper formatting
- **Smart Autoscroll**: 
  ```typescript
  // Only auto-scroll if user is at bottom or content is new
  const shouldAutoScroll = isScrolledToBottom || !content;
  if (shouldAutoScroll) {
    scrollElement.scrollTo({
      top: scrollElement.scrollHeight,
      behavior: 'smooth'
    });
  }
  ```
- **MutationObserver**: Watches for DOM changes and triggers smooth scroll
- **Scroll Tracking**: Detects scroll position and shows indicators
- **Visual Feedback**: "More content" indicator when user scrolls up
- **Empty State**: Shows animated waiting indicator

## CSS Classes Used

### Layout & Positioning
- `flex justify-start mb-5` - Message alignment
- `relative max-w-[80%]` - Container positioning
- `h-36 overflow-y-auto` - Fixed scrollable area

### Visual Effects
- `bg-gradient-to-br from-[#1f1f1f] to-[#1a1a1a]` - Background gradient
- `shadow-xl shadow-black/50` - Enhanced shadow
- `border border-violet-500/30` - Violet border
- `backdrop-blur-sm` - Subtle backdrop blur

### Animations
- `animate-pulse` - Pulsing effects on dots and border
- `animate-ping` - Waiting state indicator
- Custom animation delays via inline styles

## Browser Compatibility

- **Webkit Browsers** (Chrome, Edge, Safari): Custom scrollbar styling
- **Firefox**: Fallback scrollbar styling via `scrollbarWidth` and `scrollbarColor`
- **Mobile**: Responsive design with touch-friendly scrolling

## Performance Considerations

- Uses `useRef` to avoid unnecessary re-renders during auto-scroll
- `useEffect` dependency on `message.current_messages` for efficient updates
- Minimal DOM manipulation with CSS-based animations
- Fixed height prevents layout thrashing during content updates

## Customization Options

### Colors
- Violet theme can be changed by updating `violet-` classes
- Background gradients in `from-[#1f1f1f] to-[#1a1a1a]`
- Border and shadow colors in `border-violet-500/30`

### Dimensions
- Height: Change `h-36` (144px) to desired fixed height
- Width: Modify `max-w-[80%]` constraint
- Padding: Adjust `py-4 px-4` for internal spacing

### Animations
- Animation delays in `style={{ animationDelay: '0.3s' }}`
- Pulse speed via CSS animation duration
- Fade effect height in `h-6` bottom gradient

This implementation provides a polished, user-friendly streaming experience that clearly indicates when content is being streamed and automatically handles the transition to final content display.

## 🎬 **NEW: Folding Animation & Auto-Removal System**

### Enhanced Features Added:

#### 🎭 **Folding Animation**
- **Smooth Closing**: Animated fade, scale, and slide effects
- **Configurable Duration**: Customizable animation timing (default: 500ms)
- **Multiple Effects**: Combine fade, scale, and slide animations
- **CSS Transitions**: Hardware-accelerated animations

#### ⚡ **Auto-Removal System**
- **Smart Triggers**: Automatically closes when:
  - New non-streaming messages are added
  - Streaming status changes to completed
  - Stream ends or times out
- **Configurable Delay**: Optional delay before starting removal animation
- **Manual Control**: Optional close button for user control

#### 🛠️ **Easy Configuration**
```typescript
// Quick mode - fast animations
<StreamingMessageBox message={msg} config="quick" />

// Persistent mode - longer visibility
<StreamingMessageBox message={msg} config="persistent" />

// Manual mode - user controlled
<StreamingMessageBox message={msg} config="manual" />

// Default mode - balanced behavior (default)
<StreamingMessageBox message={msg} config="default" />
```

#### 📊 **Configuration Presets**
- **`default`**: Auto-remove with 500ms fold animation
- **`quick`**: Fast 300ms animations for rapid interactions
- **`persistent`**: Longer timeout, no auto-remove on new messages
- **`manual`**: User-controlled with close button, no auto-removal

The streaming message box now features sophisticated folding animations and intelligent auto-removal! ✨