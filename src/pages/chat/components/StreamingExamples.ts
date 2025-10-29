import { STREAMING_PRESETS } from './StreamingConfig';

// Example of how to easily alter streaming behavior
export const StreamingExamples = {
  // Quick removal - for fast interactions
  quickMode: () => {
    console.log('Using quick mode - faster animations');
    return 'quick' as keyof typeof STREAMING_PRESETS;
  },

  // Persistent mode - for important processes
  persistentMode: () => {
    console.log('Using persistent mode - longer visibility');
    return 'persistent' as keyof typeof STREAMING_PRESETS;
  },

  // Manual control - for debugging or demo
  manualMode: () => {
    console.log('Using manual mode - user controlled');
    return 'manual' as keyof typeof STREAMING_PRESETS;
  },

  // Default mode - balanced behavior
  defaultMode: () => {
    console.log('Using default mode - auto-removal');
    return 'default' as keyof typeof STREAMING_PRESETS;
  }
};

// How to use different configurations:
// <StreamingMessageBox message={msg} config="quick" />
// <StreamingMessageBox message={msg} config="persistent" />
// <StreamingMessageBox message={msg} config="manual" />
// <StreamingMessageBox message={msg} config="default" />

// How to customize in MessageList:
// const streamingConfig = StreamingExamples.quickMode();
// <MessageList messages={messages} streamingConfig={streamingConfig} ... />

export default StreamingExamples;