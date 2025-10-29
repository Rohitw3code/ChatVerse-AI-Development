import { useEffect, useState } from 'react';

export function useViewport() {
  const [keyboardOffset, setKeyboardOffset] = useState<number>(0);

  useEffect(() => {
    const updateKeyboardOffset = () => {
      const vv = (window as any).visualViewport as VisualViewport | undefined;
      if (!vv) {
        setKeyboardOffset(0);
        return;
      }
      const offset = Math.max(0, (window.innerHeight - (vv.height ?? window.innerHeight)) - (vv.offsetTop ?? 0));
      setKeyboardOffset(offset);
    };

    updateKeyboardOffset();
    const vv = (window as any).visualViewport as VisualViewport | undefined;
    vv?.addEventListener('resize', updateKeyboardOffset);
    vv?.addEventListener('scroll', updateKeyboardOffset);
    window.addEventListener('orientationchange', updateKeyboardOffset);

    return () => {
      vv?.removeEventListener('resize', updateKeyboardOffset);
      vv?.removeEventListener('scroll', updateKeyboardOffset);
      window.removeEventListener('orientationchange', updateKeyboardOffset);
    };
  }, []);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [keyboardOffset]);

  return { keyboardOffset };
}