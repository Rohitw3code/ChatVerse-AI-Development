import { useState } from 'react';

export function useInterruptState() {
  const [isInterruptResponse, setIsInterruptResponse] = useState(false);
  const [lastInterruptType, setLastInterruptType] = useState<string | null>(null);
  const [lastInputOptionContent, setLastInputOptionContent] = useState<string | null>(null);

  const handleInterruptUpdate = (data: any) => {
    const isInterrupt = data.type_ === 'interrupt';
    
    if (isInterrupt) {
      setIsInterruptResponse(true);
      // Capture the interrupt type from data
      const iType = data.data?.type || null;
      setLastInterruptType(iType);
      if (iType === 'input_option') {
        const c = data.data?.data?.content ?? '';
        setLastInputOptionContent(c);
      }
    } else if (data.next_type !== 'human') {
      setIsInterruptResponse(false);
      setLastInterruptType(null);
      setLastInputOptionContent(null);
    }
  };

  const resetInterruptState = () => {
    setIsInterruptResponse(false);
    setLastInterruptType(null);
    setLastInputOptionContent(null);
  };

  return {
    isInterruptResponse,
    lastInterruptType,
    lastInputOptionContent,
    setIsInterruptResponse,
    handleInterruptUpdate,
    resetInterruptState
  };
}