import { useEffect, useRef, useState } from 'react';

interface UseInputPositioningProps {
  isSidebarExpanded: boolean;
  leftOffset: number;
  isSidebarOpen: boolean;
}

export function useInputPositioning({ 
  isSidebarExpanded, 
  leftOffset, 
  isSidebarOpen 
}: UseInputPositioningProps) {
  const [inputHeight, setInputHeight] = useState<number>(96);
  const [inputCenterLeft, setInputCenterLeft] = useState<number | null>(null);
  const inputContainerRef = useRef<HTMLDivElement>(null);
  const messageListRef = useRef<HTMLDivElement>(null);

  // Track input height changes
  useEffect(() => {
    if (!inputContainerRef.current) return;
    const el = inputContainerRef.current;
    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const h = Math.ceil(entry.contentRect.height);
        if (h > 0) setInputHeight(h);
      }
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Calculate input center position
  useEffect(() => {
    const computeCenter = () => {
      const el = messageListRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      setInputCenterLeft(rect.left + rect.width / 2);
    };
    
    computeCenter();
    window.addEventListener('resize', computeCenter);
    window.addEventListener('orientationchange', computeCenter as any);
    let ro: ResizeObserver | null = null;
    if (typeof ResizeObserver !== 'undefined' && messageListRef.current) {
      ro = new ResizeObserver(() => computeCenter());
      ro.observe(messageListRef.current);
    }

    const timeoutId = window.setTimeout(computeCenter, 350);
    return () => {
      window.removeEventListener('resize', computeCenter);
      window.removeEventListener('orientationchange', computeCenter as any);
      ro?.disconnect();
      window.clearTimeout(timeoutId);
    };
  }, [isSidebarExpanded, leftOffset, isSidebarOpen]);

  return {
    inputHeight,
    inputCenterLeft,
    inputContainerRef,
    messageListRef
  };
}