import { ApiMessage } from '../../types';
import { applyDelta, clearDuplicateTracking as clearDeltaDuplicates } from '../streaming/delta';
import { applyUpdate } from '../streaming/update';

// Helpers to decide display/update behavior
const isDisplayable = (m: ApiMessage) =>
  (m.current_messages?.some((x) => x.content) ?? false) || m.type_ === 'interrupt';

export type StreamIndex = Record<string, number>;

// Export function to clear duplicate tracking (useful when chat resets)
export function clearDuplicateTracking() {
    clearDeltaDuplicates();
}

export { applyDelta, applyUpdate, isDisplayable };