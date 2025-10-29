import React from 'react';
import ReactMarkdown from 'react-markdown';

type MarkdownProps = {
  children: string | null | undefined;
  className?: string;
};

// Custom Markdown renderer that avoids <pre> and <code> tags to prevent overflow
// and ensures content wraps within the message container.
export function Markdown({ children, className }: MarkdownProps) {
  if (!children) return null;

  // Map markdown elements to non-pre/code HTML to keep wrapping behavior
  const components: any = {
    // Remove <pre> wrapper entirely
    pre: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    // Render inline and block code without using <code>
    code: ({ inline, children }: { inline?: boolean; children: React.ReactNode }) => {
      if (inline) {
        return (
          <span className="px-1 py-0.5 rounded bg-gray-700/50 whitespace-normal break-words font-mono text-[0.9em] leading-snug">
            {children}
          </span>
        );
      }
      // Block code rendered as a normal div that wraps
      return (
        <div className="rounded-md bg-gray-800/60 p-3 whitespace-pre-wrap break-words font-mono text-sm leading-snug m-0">
          {String(children)}
        </div>
      );
    },
    // Ensure paragraphs and list items have minimal spacing and preserve newlines similar to notepad
    p: ({ children }: { children: React.ReactNode }) => (
      <p className="whitespace-pre-wrap break-words m-0 leading-snug">{children}</p>
    ),
    li: ({ children }: { children: React.ReactNode }) => (
      <li className="whitespace-pre-wrap break-words my-0 leading-snug">{children}</li>
    ),
    ul: ({ children }: { children: React.ReactNode }) => (
      <ul className="pl-5 m-0 leading-snug list-disc">{children}</ul>
    ),
    ol: ({ children }: { children: React.ReactNode }) => (
      <ol className="pl-5 m-0 leading-snug list-decimal">{children}</ol>
    ),
    blockquote: ({ children }: { children: React.ReactNode }) => (
      <blockquote className="m-0 pl-3 border-l border-gray-600 leading-snug">{children}</blockquote>
    ),
    h1: ({ children }: { children: React.ReactNode }) => (
      <h1 className="text-xl font-semibold my-1 leading-snug">{children}</h1>
    ),
    h2: ({ children }: { children: React.ReactNode }) => (
      <h2 className="text-lg font-semibold my-1 leading-snug">{children}</h2>
    ),
    h3: ({ children }: { children: React.ReactNode }) => (
      <h3 className="text-base font-semibold my-1 leading-snug">{children}</h3>
    ),
    h4: ({ children }: { children: React.ReactNode }) => (
      <h4 className="text-base font-semibold my-1 leading-snug">{children}</h4>
    ),
    hr: () => (
      <hr className="my-1 border-gray-700" />
    ),
  };

  return (
    <div className={`${className || ''} overflow-hidden max-w-full`}>
      <ReactMarkdown components={components}>
        {children}
      </ReactMarkdown>
    </div>
  );
}

export default Markdown;
