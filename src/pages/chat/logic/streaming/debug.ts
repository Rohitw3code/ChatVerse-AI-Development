const debugState: { counters: Record<string, number> } = { counters: {} };

function isDebug(): boolean {
  try {
    if (typeof window === 'undefined') return false;
    return window.localStorage.getItem('chat.debug.stream') === '1';
  } catch {
    return false;
  }
}

export function dlog(event: string, payload: any) {
  if (!isDebug()) return;
  // Using console.debug to keep noise low; can be filtered in DevTools
  try {
    console.debug(`[chat-delta] ${event}`, payload);
  } catch {}
}

export function incChunk(node: string): number {
  const cur = debugState.counters[node] || 0;
  const next = cur + 1;
  debugState.counters[node] = next;
  return next;
}
