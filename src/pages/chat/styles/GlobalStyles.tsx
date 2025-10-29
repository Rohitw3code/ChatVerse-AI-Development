const GlobalStyles = () => (
  <style>{`
    :root {
      --sidebar-width-expanded: 250px;
      --sidebar-width-collapsed: 80px;
      --background-primary: #0a0a0a;
      --surface-primary: #1a1a1a;
      --surface-secondary: #2a2a2a;
      --violet-primary: #8b5cf6;
      --violet-dark: #6d28d9;
      --violet-light: #c4b5fd;
      --white-primary: #ffffff;
      --gray-medium: #64748b;
      --border-color: #374151;
      --success-color: #22c55e;
      --user-bubble-bg: linear-gradient(135deg, var(--violet-primary), var(--violet-dark));
      --ai-bubble-bg: var(--surface-primary);
      --shadow-lg: 0 10px 15px -3px rgba(139, 92, 246, 0.1), 0 4px 6px -2px rgba(139, 92, 246, 0.05);
    }
    
    * { box-sizing: border-box; }
    
    body {
      background-color: var(--background-primary);
      color: var(--white-primary);
      font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      margin: 0;
      overflow-x: hidden;
    }

    /* Layout Styles */
    .app-layout { display: flex; height: 100vh; position: relative; }
    .main-content {
      flex: 1;
      transition: margin-left 0.3s ease;
      min-width: 0;
      display: flex;
      justify-content: center;
    }

    /* Mobile Responsive */
    @media (min-width: 1024px) {
      .main-content.sidebar-expanded { margin-left: var(--sidebar-width-expanded); }
      .main-content.sidebar-collapsed { margin-left: var(--sidebar-width-collapsed); }
    }
    @media (max-width: 1023px) {
      .main-content { margin-left: 0 !important; }
      .mobile-header { display: flex; align-items: center; padding: 1rem; }
      .mobile-menu-button { background: none; border: none; cursor: pointer; }
    }
  `}</style>
);

export default GlobalStyles;