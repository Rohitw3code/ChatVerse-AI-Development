interface ToolOutputFormatterProps {
  toolOutput: {
    output: any;
    type: string;
    show: boolean;
  };
}

export const ToolOutputFormatter = ({ toolOutput }: ToolOutputFormatterProps) => {
  if (!toolOutput || !toolOutput.output) {
    return null;
  }

  switch (toolOutput.type) {    
    default:
      return (
        <pre className="w-full whitespace-pre-wrap break-words text-xs leading-6 bg-[#0c0c0c] border border-slate-700 rounded-lg p-4 text-slate-200 overflow-hidden">
          {JSON.stringify(toolOutput.output, null, 2)}
        </pre>
      );
  }
};