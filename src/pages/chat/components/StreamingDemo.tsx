import { useState } from 'react';
import { StreamingMessageBox } from './StreamingMessageBox';
import { ApiMessage } from '../types';

/**
 * Demo component to test StreamingMessageBox functionality
 * This simulates streaming behavior for development/testing purposes
 */
export function StreamingDemo() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<ApiMessage | null>(null);
  const [currentContent, setCurrentContent] = useState('');

  const sampleStreamText = `# AI Response

This is a sample streaming response that demonstrates how the StreamingMessageBox component works.

## Features
- **Real-time streaming**: Content appears progressively
- **Auto-scroll**: Automatically scrolls to show new content
- **Fixed height**: Container maintains consistent height
- **Visual indicators**: Shows streaming status with animated dots

## Technical Details
The streaming works by:
1. Creating a message with \`status: 'streaming'\`
2. Progressively updating the \`current_messages[0].content\`
3. Auto-scrolling to the bottom as content arrives
4. Replacing with final message when complete

## Benefits
- Better user experience with immediate feedback
- Prevents layout shifts with fixed container height
- Clear visual indication of streaming status
- Smooth transition to final content

This is the end of the sample streaming content.`;

  const startStreaming = () => {
    setIsStreaming(true);
    setCurrentContent('');

    // Create initial streaming message
    const initialMessage: ApiMessage = {
      id: `demo-streaming-${Date.now()}`,
      role: 'ai_message',
      node: 'demo_node',
      status: 'streaming',
      current_messages: [
        {
          role: 'ai',
          content: '',
        },
      ],
      provider_id: 'demo',
      thread_id: 'demo-thread',
      type_: 'agent',
    };

    setStreamingMessage(initialMessage);

    // Simulate streaming by adding text progressively
    const words = sampleStreamText.split(' ');
    let wordIndex = 0;

    const streamInterval = setInterval(() => {
      if (wordIndex < words.length) {
        const newContent = words.slice(0, wordIndex + 1).join(' ');
        setCurrentContent(newContent);
        
        // Update the streaming message
        setStreamingMessage(prev => prev ? {
          ...prev,
          current_messages: [
            {
              role: 'ai',
              content: newContent,
            },
          ],
        } : null);

        wordIndex++;
      } else {
        // Streaming complete
        clearInterval(streamInterval);
        setTimeout(() => {
          setIsStreaming(false);
          setStreamingMessage(null);
        }, 1000); // Show complete message for 1 second before hiding
      }
    }, 100); // Add a word every 100ms
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-4">StreamingMessageBox Demo</h2>
        <button
          onClick={startStreaming}
          disabled={isStreaming}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            isStreaming
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-violet-600 text-white hover:bg-violet-700'
          }`}
        >
          {isStreaming ? 'Streaming...' : 'Start Demo Streaming'}
        </button>
      </div>

      <div className="bg-gray-900 rounded-lg p-4 min-h-[300px]">
        <h3 className="text-lg font-semibold text-white mb-4">Chat Messages</h3>
        
        {/* Show streaming message box when streaming */}
        {isStreaming && streamingMessage && (
          <StreamingMessageBox message={streamingMessage} />
        )}

        {/* Show final message when streaming is complete */}
        {!isStreaming && currentContent && (
          <div className="flex justify-start mb-5">
            <div className="max-w-[80%] py-3 px-4 rounded-2xl rounded-bl-md leading-relaxed text-white bg-[#1a1a1a]">
              <div className="prose prose-sm prose-invert max-w-none">
                <div>{currentContent}</div>
              </div>
            </div>
          </div>
        )}

        {!isStreaming && !currentContent && (
          <div className="text-gray-400 text-center py-8">
            Click "Start Demo Streaming" to see the StreamingMessageBox in action
          </div>
        )}
      </div>

      <div className="mt-6 text-sm text-gray-400">
        <h4 className="font-semibold mb-2">How it works:</h4>
        <ul className="list-disc list-inside space-y-1">
          <li>Creates a message with <code className="bg-gray-800 px-1 rounded">status: 'streaming'</code></li>
          <li>Shows StreamingMessageBox with fixed height and animated indicators</li>
          <li>Progressively updates content and auto-scrolls</li>
          <li>Removes streaming box when status changes (simulated after completion)</li>
        </ul>
      </div>
    </div>
  );
}