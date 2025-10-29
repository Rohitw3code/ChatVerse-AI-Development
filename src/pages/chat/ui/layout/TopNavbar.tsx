// React import not required with new JSX transform

const MenuIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4 6h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
    <path d="M4 12h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
    <path d="M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
  </svg>
);
const PlusIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M19 11H13V5H11V11H5V13H11V19H13V13H19V11Z" />
  </svg>
);

interface TopNavbarProps {
  onMobileMenuClick: () => void;
  leftOffset?: number;
  onNewChat?: () => void;
}

export function TopNavbar({ onMobileMenuClick, leftOffset = 0, onNewChat }: TopNavbarProps) {
  return (
    <header className="fixed top-0 right-0 z-[1000] flex items-center justify-between py-1 px-2 bg-background-primary/70 backdrop-blur-md lg:hidden" style={{ left: leftOffset }}>
      <div className="flex items-center gap-2">
        <button
          className="w-8 h-8 rounded-md flex items-center justify-center text-white hover:bg-white/10 transition-colors"
          onClick={onMobileMenuClick}
          aria-label="Toggle sidebar"
        >
          <MenuIcon />
        </button>
      </div>
      <div className="flex items-center gap-2">
        <button
          className="w-8 h-8 rounded-md flex items-center justify-center text-white hover:bg-white/10 transition-colors"
          onClick={() => onNewChat && onNewChat()}
          aria-label="New chat"
          title="New chat"
        >
          <PlusIcon />
        </button>
      </div>
    </header>
  );
}