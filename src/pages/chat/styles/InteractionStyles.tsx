const InteractionStyles = () => (
  <style>{`
    /* Thinking Animation */
    .thinking-text { 
      display: flex; 
      align-items: center; 
      gap: 8px; 
      font-weight: 500; 
      color: var(--violet-light); 
    }
    .dot { 
      height: 8px; 
      width: 8px; 
      background: var(--violet-primary); 
      border-radius: 50%; 
      animation: pulse 1.4s infinite ease-in-out both; 
    }
    @keyframes pulse { 
      0%, 80%, 100% { transform: scale(0); } 
      40% { transform: scale(1.0); } 
    }
    
    /* Details Toggle */
    .details-button {
      background: none; 
      border: none; 
      color: var(--gray-medium); 
      cursor: pointer; 
      padding: 8px 0;
      font-size: 0.8rem; 
      font-weight: 500; 
      transition: color 0.2s ease;
    }
    .details-button:hover { color: var(--violet-light); }
    .details-content { 
      overflow: hidden; 
      transition: max-height 0.3s ease-out, opacity 0.3s ease-out; 
    }
    
    /* Interrupt Components */
    .interrupt-title { 
      font-weight: 600; 
      margin-bottom: 12px; 
      color: var(--violet-light); 
    }
    .interrupt-content { 
      white-space: pre-wrap; 
      font-family: inherit; 
      margin: 0; 
      color: var(--white-primary); 
      line-height: 1.5; 
    }
    .interrupt-options { 
      margin-top: 16px; 
      display: flex; 
      gap: 12px; 
      flex-wrap: wrap; 
    }
    .interrupt-button {
      padding: 10px 16px; 
      border: 1px solid var(--violet-primary); 
      border-radius: 20px; 
      cursor: pointer;
      background-color: transparent; 
      color: var(--violet-primary); 
      transition: all 0.3s ease;
      font-weight: 500; 
      font-size: 0.9rem;
    }
    .interrupt-button:hover { 
      background: var(--user-bubble-bg); 
      color: var(--white-primary); 
      transform: translateY(-2px); 
    }

    /* Connect Button */
    .connect-button {
      display: inline-flex; 
      align-items: center; 
      gap: 0.75rem; 
      padding: 12px 20px;
      border-radius: 50px; 
      font-weight: 600; 
      font-size: 1rem;
      cursor: pointer; 
      text-decoration: none; 
      transition: all 0.2s ease;
      margin-top: 1rem; 
      background: #2a2a2a; 
      color: white;
      border: 1px solid var(--border-color);
    }
    .connect-button:hover {
      transform: translateY(-2px); 
      border-color: var(--violet-light);
    }
    .connect-button svg {
      width: 24px !important; 
      height: 24px !important;
    }
  `}</style>
);

export default InteractionStyles;