const ComponentStyles = () => (
  <style>{`
    .main-content {
      display: flex;
      flex-direction: column;
      height: 100vh;
      max-height: 100vh;
      overflow: hidden;
      background-color: #0a0a0a;
      background-image:
        radial-gradient(circle at 1px 1px, rgba(255,255,255,0.1) 1px, transparent 0),
        radial-gradient(circle at 3px 3px, rgba(255,255,255,0.06) 1px, transparent 0),
        radial-gradient(circle at 5px 5px, rgba(255,255,255,0.03) 1px, transparent 0);
      background-size: 20px 20px, 40px 40px, 60px 60px;
    }

    /* Top Navbar */
    .top-navbar {
      position: sticky;
      top: 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1rem 1.5rem;
      background: rgba(10, 10, 10, 0.8);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      z-index: 10;
      flex-shrink: 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .top-navbar-left {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .brand-logo {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: var(--white-primary);
    }
    .brand-logo svg {
      color: var(--violet-primary);
    }
    .brand-logo h1 {
      font-size: 1.25rem;
      font-weight: 500;
      margin: 0;
    }

    .top-navbar-right {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .automations-button {
      background-color: var(--surface-primary);
      color: var(--white-primary);
      border: 1px solid var(--border-color);
      padding: 0.5rem 1.25rem;
      border-radius: 50px;
      cursor: pointer;
      font-weight: 500;
      transition: all 0.2s ease;
    }
    .automations-button:hover {
      background-color: var(--surface-secondary);
      border-color: var(--violet-primary);
    }

    .user-profile-button {
      background: var(--surface-primary);
      border: 1px solid var(--border-color);
      border-radius: 50%;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--gray-medium);
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .user-profile-button:hover {
      color: var(--white-primary);
      border-color: var(--violet-primary);
    }

    /* Empty State */
    .empty-state-content {
      display: none;
      text-align: center;
    }
    .empty-state-content h1 {
      font-size: 3.5rem;
      font-weight: 500;
      background: -webkit-linear-gradient(45deg, var(--white-primary), var(--violet-light));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin: 0;
    }
    .empty-state-content p {
      color: var(--gray-medium);
      font-size: 1.25rem;
      margin-top: 0.5rem;
      margin-bottom: 2rem;
    }

    .example-queries { 
      display: grid; 
      grid-template-columns: 1fr 1fr; 
      gap: 1rem; 
      width: 100%; 
      max-width: 700px; 
    }
    .example-query {
      background: var(--surface-primary); 
      border: 1px solid var(--border-color); 
      border-radius: 16px;
      padding: 1.25rem; 
      cursor: pointer; 
      transition: all 0.25s ease; 
      text-align: left;
    }
    .example-query:hover { 
      transform: translateY(-4px); 
      border-color: var(--violet-primary); 
      box-shadow: var(--shadow-lg); 
    }
    .example-query h3 { 
      color: var(--violet-light); 
      font-size: 0.9rem; 
      font-weight: 600; 
      margin: 0 0 0.5rem 0; 
    }
    .example-query p { 
      color: var(--white-primary); 
      font-size: 1rem; 
      margin: 0; 
      line-height: 1.4; 
    }
    
    .chat-container {
      flex-grow: 1;
      min-height: 0;
    }
    
    .message-list {
        min-height: 0;
    }
    
    .chat-container.is-empty .empty-state-content {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
      height: 100%;
      padding-bottom: 15vh;
    }

    .empty-state-logo {
      width: 80px;
      height: 80px;
      margin-bottom: 1.5rem;
      animation: float 3s ease-in-out infinite;
    }

    .empty-state-title {
      font-size: 1.75rem;
      font-weight: 500;
      color: var(--white-primary);
      margin-bottom: 2rem;
    }
    
    .empty-state-content .chat-input-container {
      padding: 0;
      width: 100%;
      max-width: 700px;
    }

    .chat-input-container {
      padding: 1rem 1.5rem 2rem 1.5rem;
      width: 100%;
      max-width: 800px;
      margin: 0 auto;
      flex-shrink: 0;
    }
    .chat-input-area {
      padding: 0.75rem;
      padding-left: 1.75rem;
      min-height: 80px;
      height: auto;
      gap: 0.75rem;
      border-radius: 20px;
      align-items: flex-end;
    }
    .chat-input {
      font-size: 1.1rem;
      height: auto;
      padding-top: 22px;
      padding-bottom: 22px;
    }
    .send-button {
      width: 56px;
      height: 56px;
      flex-shrink: 0;
    }

    @keyframes float {
      0% { transform: translateY(0px); }
      50% { transform: translateY(-10px); }
      100% { transform: translateY(0px); }
    }
    
    @media (max-width: 768px) {
      .brand-logo h1 { display: none; }
      .automations-button {
        padding: 0.5rem 0.75rem;
        font-size: 0.875rem;
      }
      .top-navbar { padding: 0.75rem 1rem; }
      .empty-state-title { font-size: 1.5rem; }
      .empty-state-content .chat-input-container {
          width: 90%;
      }
    }
  `}</style>
);

export default ComponentStyles;