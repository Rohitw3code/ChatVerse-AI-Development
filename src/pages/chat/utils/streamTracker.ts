/**
 * Simple Stream Tracker Utility
 * 
 * This utility helps track streaming text messages to debug any issues
 * with text appending logic during streaming.
 * 
 * Usage:
 * - To enable tracking: localStorage.setItem('chat.stream.tracker', '1')
 * - To disable tracking: localStorage.removeItem('chat.stream.tracker')
 * 
 * The tracker logs:
 * 1. Raw messages received from the server
 * 2. Text processing logic (cumulative replace, append, etc.)
 * 3. Final content displayed in the UI
 */

export function isStreamTrackerEnabled(): boolean {
  try {
    if (typeof window === 'undefined') return false;
    return window.localStorage.getItem('chat.stream.tracker') === '1';
  } catch {
    return true; // Default to enabled during development
  }
}

export function streamLog(message: string, data?: any) {
  if (isStreamTrackerEnabled()) {
    console.log(message, data || '');
  }
}

export function enableStreamTracker() {
  try {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('chat.stream.tracker', '1');
      console.log('✅ Stream tracker enabled. Refresh the page to see detailed streaming logs.');
    }
  } catch (e) {
    console.error('Failed to enable stream tracker:', e);
  }
}

export function disableStreamTracker() {
  try {
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem('chat.stream.tracker');
      console.log('❌ Stream tracker disabled.');
    }
  } catch (e) {
    console.error('Failed to disable stream tracker:', e);
  }
}

// Make functions available globally for easy console access
if (typeof window !== 'undefined') {
  (window as any).enableStreamTracker = enableStreamTracker;
  (window as any).disableStreamTracker = disableStreamTracker;
}