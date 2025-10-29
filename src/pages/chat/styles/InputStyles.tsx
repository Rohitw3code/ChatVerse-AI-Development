const InputStyles = () => (
  <style>{`
    /* Chat Input Container */
    .chat-input-container { padding: 1.5rem; }

    .chat-input-area {
      display: flex; 
      align-items: flex-end; 
      gap: 1rem; 
      background: var(--surface-primary);
      border-radius: 20px; 
      padding: 0.5rem; 
      padding-left: 1.5rem; 
      border: 1px solid var(--border-color); 
      transition: all 0.3s ease;
      min-height: 80px;
    }
    .chat-input-area:focus-within { 
      border-color: var(--violet-primary); 
      box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.2); 
    }
    
    .chat-input { 
      flex-grow: 1; 
      background: transparent; 
      border: none; 
      outline: none; 
      color: var(--white-primary); 
      font-size: 1rem; 
      line-height: 1.5;
      resize: none; 
      max-height: 200px;
      padding-top: 14px; 
      padding-bottom: 14px;
    }
    .chat-input::placeholder { color: var(--gray-medium); }
    
    .send-button { 
      background: var(--user-bubble-bg); 
      border: none; 
      border-radius: 50%; 
      width: 48px; 
      height: 48px;
      display: flex; 
      align-items: center; 
      justify-content: center; 
      cursor: pointer; 
      transition: all 0.2s ease;
      flex-shrink: 0; 
      margin-bottom: 2px;
    }
    .send-button:hover { transform: scale(1.1); }
    .send-button svg { fill: var(--white-primary); }
  `}</style>
);

export default InputStyles;