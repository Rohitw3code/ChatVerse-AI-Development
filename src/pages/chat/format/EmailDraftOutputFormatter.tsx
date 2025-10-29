
interface EmailDraftOutputFormatterProps {
  toolOutput: {
    output: { 
        subject: string;
        body: string;
    };
    type: string;
    show: boolean;
  };
}

// Helper function to detect if content is HTML
const isHtmlContent = (content: string): boolean => {
  const htmlTagPattern = /<\/?[a-z][\s\S]*>/i;
  return htmlTagPattern.test(content);
};

// Helper function to sanitize HTML and remove center alignment
const sanitizeHtmlAlignment = (html: string): string => {
  let sanitized = html;
  
  // Remove text-align: center from inline styles
  sanitized = sanitized.replace(/text-align\s*:\s*center\s*;?/gi, 'text-align: left;');
  
  // Remove align="center" attributes
  sanitized = sanitized.replace(/align\s*=\s*["']center["']/gi, 'align="left"');
  
  // Remove center tags
  sanitized = sanitized.replace(/<center>/gi, '<div style="text-align: left;">');
  sanitized = sanitized.replace(/<\/center>/gi, '</div>');
  
  return sanitized;
};

export const EmailDraftOutputFormatter = ({ toolOutput }: EmailDraftOutputFormatterProps) => {
    const { output } = toolOutput;

    if (!output || typeof output.subject === 'undefined' || typeof output.body === 'undefined') {
      return <pre className="p-3 text-xs bg-black border border-red-800 rounded-md text-red-400">{JSON.stringify(output, null, 2)}</pre>;
    }
  
    const isHtml = isHtmlContent(output.body);
  
    return (
      <div className="w-full max-w-3xl rounded-lg border border-slate-700/40 bg-[#1a1a1a] overflow-hidden shadow-lg">
        {/* Gmail-style Header */}
        <div className="px-2 py-2 sm:px-3 sm:py-2 md:px-4 md:py-2.5 border-b border-slate-700/40 bg-[#151515] flex items-center justify-between">
          <div className="flex items-center gap-1.5 sm:gap-2">
            <div className="flex items-center justify-center w-5 h-5 sm:w-5.5 sm:h-5.5 md:w-6 md:h-6 rounded-md bg-red-600">
              <svg className="w-3 h-3 sm:w-3.5 sm:h-3.5 md:w-3.5 md:h-3.5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
              </svg>
            </div>
            <span className="text-xs font-medium text-slate-300">Draft</span>
          </div>
          <button 
            onClick={() => navigator.clipboard.writeText(`Subject: ${output.subject}\n\n${output.body}`)}
            className="flex items-center gap-1 sm:gap-1.5 px-2 py-1 sm:px-2.5 sm:py-1.5 md:px-3 text-xs font-medium text-slate-300 hover:text-white bg-slate-800/50 hover:bg-slate-700/50 rounded-md transition-all border border-slate-700/40"
          >
            <svg className="w-3 h-3 sm:w-3.5 sm:h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <span className="hidden xs:inline">Copy</span>
          </button>
        </div>

        {/* Email Content - Gmail Style */}
        <div className="px-2 py-2 sm:px-3 sm:py-2.5 md:px-4 md:py-3 space-y-2 sm:space-y-2.5 md:space-y-3 bg-[#1a1a1a] overflow-hidden">
          {/* Subject */}
          <div className="overflow-hidden">
            <div className="text-xs text-slate-500 mb-1 sm:mb-1.5 font-medium">Subject</div>
            <div className="text-sm sm:text-base font-semibold text-white break-words overflow-wrap-anywhere">
              {output.subject}
            </div>
          </div>

          {/* Separator */}
          <div className="border-t border-slate-700/40"></div>

          {/* Body */}
          <div className="overflow-hidden">
            <div className="text-xs text-slate-500 mb-1 sm:mb-1.5 font-medium">Message</div>
            {isHtml ? (
              <div 
                className="text-xs sm:text-sm leading-relaxed text-slate-300 break-words email-html-content text-left overflow-hidden"
                dangerouslySetInnerHTML={{ __html: sanitizeHtmlAlignment(output.body) }}
                style={{
                  wordBreak: 'break-word',
                  overflowWrap: 'break-word',
                  textAlign: 'left'
                }}
              />
            ) : (
              <div className="text-xs sm:text-sm leading-relaxed text-slate-300 whitespace-pre-wrap break-words text-left overflow-hidden">
                {output.body}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };