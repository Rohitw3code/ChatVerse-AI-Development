import { useEffect } from 'react';

export function useBodyScrollLock() {
  useEffect(() => {
    const prevBodyOverflow = document.body.style.overflow;
    const prevHtmlOverflow = document.documentElement.style.overflow;
    const prevHtmlOverscroll = (document.documentElement.style as any).overscrollBehaviorY;
    
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
    (document.documentElement.style as any).overscrollBehaviorY = 'none';
    window.scrollTo(0, 0);
    
    return () => {
      document.body.style.overflow = prevBodyOverflow;
      document.documentElement.style.overflow = prevHtmlOverflow;
      (document.documentElement.style as any).overscrollBehaviorY = prevHtmlOverscroll;
    };
  }, []);
}