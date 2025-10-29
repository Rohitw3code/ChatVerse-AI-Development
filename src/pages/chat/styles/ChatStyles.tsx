const ChatStyles = () => (
  <style>{`
    /* Chat Container */
    .chat-container {
      display: flex;
      flex-direction: column;
      height: 100vh;
      width: 100%;
      max-width: 1100px;
      margin: 0 auto;
      position: relative;
    }

    /* Message List */
    .message-list { 
      display: none; 
      flex-grow: 1; 
      overflow-y: auto; 
      padding: 1.5rem; 
    }
    
    .message-list::-webkit-scrollbar { width: 5px; }
    .message-list::-webkit-scrollbar-track { background: transparent; }
    .message-list::-webkit-scrollbar-thumb {
      background-color: var(--violet-primary);
      border-radius: 4px;
      border: 1px solid var(--background-primary);
    }
    .message-list::-webkit-scrollbar-thumb:hover { background-color: var(--violet-dark); }

    /* Message Items */
    .message-item { display: flex; margin-bottom: 1.5rem; position: relative; }
    .message-item.user { justify-content: flex-end; }
    .message-item.ai { justify-content: flex-start; }
    
    .message-bubble { max-width: 80%; padding: 0.75rem 1.25rem; border-radius: 20px; line-height: 1.6; }
    
    .message-item.user .message-bubble { 
      background: var(--user-bubble-bg); 
      color: var(--white-primary); 
      border-bottom-right-radius: 4px; 
    }
    .message-item.ai .message-bubble { 
      background: var(--ai-bubble-bg); 
      color: var(--white-primary); 
      border-bottom-left-radius: 4px; 
    }

    /* Empty State */
    .chat-container.is-empty { 
      justify-content: center; 
      align-items: center; 
      gap: 2rem; 
      padding: 2rem; 
    }
    .chat-container.is-empty .empty-state-content { display: block; }
    .chat-container.is-empty .chat-input-container { 
      border-top: none; 
      padding: 0; 
      width: 100%; 
      max-width: 600px; 
    }
    .chat-container:not(.is-empty) .message-list { display: block; }
  `}</style>
);

export default ChatStyles;