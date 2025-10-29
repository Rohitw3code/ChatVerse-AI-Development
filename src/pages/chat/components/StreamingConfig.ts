// Configuration for StreamingMessageBox behavior
export const STREAMING_CONFIG = {
  // Animation settings
  animation: {
    duration: 500, // ms - Duration for fold/unfold animations
    easing: 'ease-in-out', // CSS easing function
    scaleEffect: true, // Enable scale animation during closing
    fadeEffect: true, // Enable fade animation during closing
    slideEffect: true, // Enable slide up animation during closing
  },
  
  // Auto-removal settings
  autoRemoval: {
    enabled: true, // Enable automatic removal
    onNewMessage: true, // Remove when new message is added
    onStreamComplete: true, // Remove when streaming completes
    onStatusChange: true, // Remove when status changes from 'streaming'
    delay: 0, // ms - Optional delay before starting removal animation
  },
  
  // Visual settings
  visual: {
    showFoldButton: false, // Show manual fold/unfold button
    persistOnScroll: true, // Keep visible when user scrolls
    hideOnUserInteraction: false, // Hide when user clicks elsewhere
  },
  
  // Timeout settings
  timeout: {
    warningTime: 30000, // ms - Show warning after this time
    maxTime: 60000, // ms - Force remove after this time
    enabled: true,
  }
};

// Easy preset configurations
export const STREAMING_PRESETS = {
  // Default behavior - auto-remove with fold animation
  default: STREAMING_CONFIG,
  
  // Quick removal - faster animations
  quick: {
    ...STREAMING_CONFIG,
    animation: {
      ...STREAMING_CONFIG.animation,
      duration: 300,
    }
  },
  
  // Persistent - longer timeout, no auto-removal on new messages
  persistent: {
    ...STREAMING_CONFIG,
    autoRemoval: {
      ...STREAMING_CONFIG.autoRemoval,
      onNewMessage: false,
    },
    timeout: {
      ...STREAMING_CONFIG.timeout,
      warningTime: 60000,
      maxTime: 120000,
    }
  },
  
  // Manual - only manual control, no auto-removal
  manual: {
    ...STREAMING_CONFIG,
    autoRemoval: {
      enabled: false,
      onNewMessage: false,
      onStreamComplete: false,
      onStatusChange: false,
      delay: 0,
    },
    visual: {
      ...STREAMING_CONFIG.visual,
      showFoldButton: true,
    }
  }
};