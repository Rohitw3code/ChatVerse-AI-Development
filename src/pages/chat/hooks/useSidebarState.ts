import { useEffect, useState } from 'react';

interface UseSidebarStateProps {
  isSidebarExpanded: boolean;
}

export function useSidebarState({ isSidebarExpanded }: UseSidebarStateProps) {
  const [leftOffset, setLeftOffset] = useState(0);

  useEffect(() => {
    const computeLeft = () => {
      const isLg = window.innerWidth >= 1024; 
      if (!isLg) return 0;
      const root = getComputedStyle(document.documentElement);
      const exp = parseInt(root.getPropertyValue('--sidebar-width-expanded')) || 220;
      const col = parseInt(root.getPropertyValue('--sidebar-width-collapsed')) || 70;
      return isSidebarExpanded ? exp : col;
    };
    const handler = () => setLeftOffset(computeLeft());
    handler();
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, [isSidebarExpanded]);

  return { leftOffset };
}