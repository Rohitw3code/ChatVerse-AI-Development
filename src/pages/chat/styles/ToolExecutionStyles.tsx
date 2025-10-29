const ToolExecutionStyles = () => (
  <style>{`
    /* Tool Execution Container */
    .tool-execution-container {
      position: relative;
      display: flex; 
      flex-direction: column; 
      gap: 8px;
      padding: 16px; 
      border-radius: 16px; 
      max-width: 500px; 
      width: 100%;
      background: var(--surface-primary); 
      border: 1px solid var(--border-color);
      box-shadow: inset 0 1px 2px 0 rgba(255, 255, 255, 0.05);
      animation: slideUpFadeIn 0.5s ease-out;
      transition: background-color 0.2s ease;
    }
    .tool-execution-container.is-finished { cursor: pointer; }
    .tool-execution-container.is-finished:hover { 
      background-color: var(--surface-secondary); 
    }
    .tool-execution-container.success { 
      animation: border-flash-success 1.2s ease-out; 
    }
    
    /* Tool Content */
    .tool-main-content { display: flex; gap: 16px; align-items: center; }
    .tool-icon { 
      flex-shrink: 0; 
      padding: 8px; 
      background: rgba(139, 92, 246, 0.1); 
      border-radius: 10px; 
    }
    .tool-content { flex-grow: 1; }
    .tool-header { 
      display: flex; 
      align-items: center; 
      justify-content: space-between; 
      font-weight: 600; 
      color: var(--white-primary); 
    }
    .tool-header-info { 
      display: flex; 
      align-items: center; 
      gap: 10px; 
    }
    
    /* Tool Status Indicators */
    .spinner { 
      width: 18px; 
      height: 18px; 
      border: 2px solid rgba(139, 92, 246, 0.2); 
      border-top-color: var(--violet-primary);
      border-radius: 50%; 
      animation: spin 1s linear infinite;
    }
    .success-icon { width: 18px; height: 18px; }
    .success-icon svg { 
      stroke: var(--success-color); 
      animation: draw-check 0.4s 0.2s forwards; 
    }

    .tool-status { 
      font-size: 0.85rem; 
      color: var(--gray-medium); 
      margin-top: 6px; 
      font-weight: 500; 
      transition: color 0.3s ease; 
    }
    .tool-execution-container.success .tool-status { 
      color: var(--success-color); 
    }

    /* Dropdown */
    .dropdown-chevron { 
      color: var(--gray-medium); 
      transition: transform 0.3s ease-out; 
    }
    .dropdown-chevron.open { transform: rotate(180deg); }

    .tool-output-dropdown {
      background-color: #000;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      margin-top: 12px;
      padding: 12px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      animation: fadeIn 0.3s ease;
    }
    .tool-output-pre { 
      white-space: pre-wrap; 
      word-break: break-all; 
      margin: 0; 
      color: #e2e8f0; 
      font-family: 'JetBrains Mono', monospace; 
      font-size: 0.8rem; 
    }

    /* Animations */
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes slideUpFadeIn { 
      from { opacity: 0; transform: translateY(10px); } 
      to { opacity: 1; transform: translateY(0); } 
    }
    @keyframes fadeIn { 
      from { opacity: 0; transform: scale(0.95); } 
      to { opacity: 1; transform: scale(1); } 
    }
    @keyframes draw-check { to { stroke-dashoffset: 0; } }
    @keyframes border-flash-success {
      0% { border-color: var(--border-color); }
      30% { 
        border-color: var(--success-color); 
        box-shadow: 0 0 15px rgba(34, 197, 94, 0.3), inset 0 1px 2px 0 rgba(255, 255, 255, 0.05); 
      }
      100% { 
        border-color: var(--border-color); 
        box-shadow: inset 0 1px 2px 0 rgba(255, 255, 255, 0.05); 
      }
    }
  `}</style>
);

export default ToolExecutionStyles;