import React, { useState } from "react";
import { ApiMessage } from "../types";

const nodeDescriptions: { [key: string]: string } = {
  starter_node: "Analyzing request...",
  planner_node: "Creating a step-by-step plan...",
  gmail_agent_node: "Accessing Gmail agent... ",
  research_agent_node: " Conducting research...",
  gdoc_agent_node: "Accessing Google Docs agent...",
  sheets_agent_node: "Accessing Google Sheets agent...",
  final_answer_node: "Generating final answer...",
  task_selection_node: "Selecting the best approach for your task..."
};

interface ThinkingProps {
  message: ApiMessage | null;
}

export function Thinking({ message }: ThinkingProps) {
  const [isOpen, setIsOpen] = useState(false);
  const thinkingText = (message?.node && nodeDescriptions[message.node]) || "Thinking...";

  const detailsClasses = isOpen
    ? 'max-h-[500px] opacity-100'
    : 'max-h-0 opacity-0';

  return (
    <div className="flex justify-start mb-5">
      <div className="max-w-[80%] py-3 px-4 rounded-2xl rounded-bl-md leading-relaxed text-white bg-[#1a1a1a]">
        <div className="flex items-center gap-1.5 font-medium text-violet-300">
          <span>{thinkingText}</span>
          <span className="animate-bounce w-1.5 h-1.5 bg-violet-500 rounded-full" style={{ animationDelay: '0s' }}></span>
          <span className="animate-bounce w-1.5 h-1.5 bg-violet-500 rounded-full" style={{ animationDelay: '0.15s' }}></span>
          <span className="animate-bounce w-1.5 h-1.5 bg-violet-500 rounded-full" style={{ animationDelay: '0.3s' }}></span>
        </div>
        {message?.current_messages && (
          <div className="mt-2">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="bg-transparent border-none text-slate-500 cursor-pointer py-1.5 text-xs font-medium transition-colors duration-200 ease-in-out hover:text-violet-300"
            >
              {isOpen ? 'Hide Details' : 'Show Details'}
            </button>
            <div className={`overflow-hidden transition-all duration-300 ease-out ${detailsClasses}`}>
              <pre className="whitespace-pre-wrap break-all m-0 text-slate-200 font-mono text-xs bg-black p-2.5 rounded-lg border border-slate-700 mt-1">
                {JSON.stringify(message.current_messages, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}