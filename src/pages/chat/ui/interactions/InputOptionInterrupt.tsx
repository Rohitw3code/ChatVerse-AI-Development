import { useState, useRef, useEffect, useMemo } from 'react';
import { ApiMessage } from "../../types";
import { GmailIcon } from "../shared/platforms";
import { ChatAgentApiService } from "../../../../api/chatagent";

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

interface InputOptionInterruptProps {
    messageData: ApiMessage['data'];
    onOptionClick: (option: string, additionalData?: any) => void;
    message?: ApiMessage;
}

export function InputOptionInterrupt({ messageData, onOptionClick, message }: InputOptionInterruptProps) {
    const { title, content, options } = messageData?.data || {};
    const [isEditing, setIsEditing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const contentRef = useRef<HTMLPreElement>(null);
    const gmailBodyRef = useRef<HTMLDivElement>(null);
    const [gmailDraft, setGmailDraft] = useState<{ to: string; subject: string; body: string } | null>(null);

    // Try to parse content as JSON to support structured previews
    const parsedContent = useMemo(() => {
        if (!content) return null;
        if (typeof content === 'object') return content as any;
        if (typeof content === 'string') {
            try { return JSON.parse(content); } catch { return null; }
        }
        return null;
    }, [content]);

    const isGmailPreview = parsedContent && parsedContent.type === 'send_gmail';
    // Initialize or refresh gmailDraft when parsedContent changes to send_gmail
    useEffect(() => {
        if (isGmailPreview) {
            setGmailDraft({
                to: parsedContent.to || '',
                subject: parsedContent.subject || '',
                body: parsedContent.body || '',
            });
        } else {
            setGmailDraft(null);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isGmailPreview, parsedContent?.to, parsedContent?.subject, parsedContent?.body]);


    const displayTextContent = useMemo(() => {
        if (typeof content === 'string') return content;
        if (!content) return '';
        try { return JSON.stringify(content, null, 2); } catch { return String(content); }
    }, [content]);

    useEffect(() => {
        if (isEditing && contentRef.current) {
            contentRef.current.focus();
            // Move cursor to end
            const range = document.createRange();
            const selection = window.getSelection();
            range.selectNodeContents(contentRef.current);
            range.collapse(false);
            selection?.removeAllRanges();
            selection?.addRange(range);
        }
    }, [isEditing]);

    const handleEditToggle = () => {
        if (isEditing) {
            // When saving (toggling from edit mode to view mode)
            handleSave();
        }
        setIsEditing(!isEditing);
    };

    const handleSave = async () => {
        if (!message || !message.id || !message.thread_id || !message.query_id) {
            console.error("Missing required message identifiers for update");
            return;
        }

        setIsSaving(true);
        try {
            // Prepare the updated data based on the message type
            let updatedData: any;

            if (isGmailPreview) {
                // For Gmail, construct the updated JSON structure
                updatedData = {
                    title: title || "Do you want to send this email?",
                    content: {
                        type: 'send_gmail',
                        to: gmailDraft?.to ?? parsedContent.to ?? '',
                        subject: gmailDraft?.subject ?? parsedContent.subject ?? '',
                        body: gmailBodyRef.current ? gmailBodyRef.current.innerText : (gmailDraft?.body ?? parsedContent.body ?? ''),
                    },
                    options: options || ["Yes", "No"]
                };
            } else {
                // For other content types
                const editedText = contentRef.current?.textContent || (typeof content === 'string' ? content : JSON.stringify(content)) || '';
                updatedData = {
                    title: title,
                    content: editedText,
                    options: options
                };
            }

            // Call the update API
            await ChatAgentApiService.updateMessageData({
                id: typeof message.id === 'string' ? parseInt(message.id, 10) : message.id,
                thread_id: message.thread_id,
                query_id: message.query_id,
                data: {
                    name: messageData?.name,
                    type: messageData?.type,
                    data: updatedData
                },
                merge: false  // Replace the data entirely
            });

            console.log("Message data updated successfully");
        } catch (error) {
            console.error("Failed to update message data:", error);
        } finally {
            setIsSaving(false);
        }
    };

    // When entering edit mode for Gmail, seed the body and place caret at end without resetting on each keystroke
    useEffect(() => {
        if (isEditing && isGmailPreview && gmailBodyRef.current) {
            const bodyText = gmailDraft?.body ?? parsedContent.body ?? '';
            // Only set once to avoid moving caret on each render
            if (gmailBodyRef.current.innerText !== bodyText) {
                gmailBodyRef.current.innerText = bodyText;
            }
            // Place caret at end
            const range = document.createRange();
            range.selectNodeContents(gmailBodyRef.current);
            range.collapse(false);
            const sel = window.getSelection();
            sel?.removeAllRanges();
            sel?.addRange(range);
        }
    }, [isEditing, isGmailPreview]);

    const handleOptionClick = (option: string) => {
        // For Gmail preview (structured JSON), always send the original JSON string as modified_text
        let editedText = '';
        if (isGmailPreview) {
            const current = {
                type: 'send_gmail',
                to: gmailDraft?.to ?? parsedContent.to ?? '',
                subject: gmailDraft?.subject ?? parsedContent.subject ?? '',
                body: gmailBodyRef.current ? gmailBodyRef.current.innerText : (gmailDraft?.body ?? parsedContent.body ?? ''),
            };
            editedText = JSON.stringify(current);
        } else {
            editedText = (contentRef.current?.textContent || (typeof content === 'string' ? content : JSON.stringify(content)) || '');
        }
        onOptionClick(option, { 
            modified_text: editedText,
            human_response: option,
            type: 'input_option'
        });
    };

    if (!options) return null;

    return (
        <div className="max-w-none">
            {title && <div className="font-medium mb-3 text-violet-200 text-[15px]">{title}</div>}
            {content && (
                <div className="group">
                    {isGmailPreview ? (
                        isEditing ? (
                            <div className="w-full sm:max-w-[600px] md:max-w-[650px] rounded-xl border border-violet-500/20 bg-[#0f0f0f] p-3 sm:p-4 md:p-5 text-white shadow-lg shadow-violet-500/5">
                                <div className="flex items-center gap-2 sm:gap-2.5 mb-3 sm:mb-4 pb-2 sm:pb-3 border-b border-violet-500/10">
                                    <GmailIcon />
                                    <span className="text-sm font-semibold text-violet-300">Compose</span>
                                </div>
                                <label className="block text-[11px] text-gray-400 mb-1.5 font-medium uppercase tracking-wide">To</label>
                                <input
                                    type="text"
                                    value={gmailDraft?.to ?? ''}
                                    placeholder="recipient@example.com"
                                    onChange={(e) => setGmailDraft((d) => ({ ...(d ?? { to: '', subject: '', body: '' }), to: e.target.value }))}
                                    className="w-full mb-3 sm:mb-4 px-0 py-2 bg-transparent border-b border-violet-500/20 text-sm outline-none focus:border-violet-500/60 rounded-none placeholder:text-gray-600 transition-colors"
                                />
                                <label className="block text-[11px] text-gray-400 mb-1.5 font-medium uppercase tracking-wide">Subject</label>
                                <input
                                    type="text"
                                    value={gmailDraft?.subject ?? ''}
                                    placeholder="Subject"
                                    onChange={(e) => setGmailDraft((d) => ({ ...(d ?? { to: '', subject: '', body: '' }), subject: e.target.value }))}
                                    className="w-full mb-3 sm:mb-4 px-0 py-2 bg-transparent border-b border-violet-500/20 text-sm outline-none focus:border-violet-500/60 rounded-none placeholder:text-gray-600 transition-colors"
                                />
                                <label className="block text-[11px] text-gray-400 mb-1.5 font-medium uppercase tracking-wide">Body</label>
                                <div
                                    ref={gmailBodyRef}
                                    contentEditable
                                    suppressContentEditableWarning
                                    className="min-h-[120px] sm:min-h-[140px] md:min-h-[160px] bg-transparent p-0 text-xs sm:text-sm whitespace-pre-wrap leading-relaxed outline-none"
                                    onInput={(e) => {
                                        const text = (e.target as HTMLDivElement).innerText;
                                        setGmailDraft((d) => ({ ...(d ?? { to: '', subject: '', body: '' }), body: text }));
                                    }}
                                />
                            </div>
                        ) : (
                            <div className="w-full sm:max-w-[600px] md:max-w-[650px] rounded-xl border border-violet-500/20 bg-[#0f0f0f] p-3 sm:p-4 md:p-5 text-white shadow-lg shadow-violet-500/5">
                                <div className="flex items-center gap-2 sm:gap-2.5 mb-2 sm:mb-3 pb-2 sm:pb-3 border-b border-violet-500/10">
                                    <GmailIcon />
                                    <span className="text-sm font-semibold text-violet-300">Gmail Preview</span>
                                </div>
                                <div className="text-xs text-gray-300 mb-1.5"><span className="text-gray-500 font-medium">To:</span> <span className="text-gray-200">{gmailDraft?.to ?? parsedContent.to ?? '-'}</span></div>
                                <div className="text-xs text-gray-300 mb-3 sm:mb-4"><span className="text-gray-500 font-medium">Subject:</span> <span className="text-gray-200">{gmailDraft?.subject ?? parsedContent.subject ?? '-'}</span></div>
                                {isHtmlContent(gmailDraft?.body ?? parsedContent.body ?? '') ? (
                                    <div 
                                        className="rounded bg-transparent p-0 text-xs sm:text-sm leading-relaxed text-gray-200 email-html-content text-left"
                                        dangerouslySetInnerHTML={{ __html: sanitizeHtmlAlignment(gmailDraft?.body ?? parsedContent.body ?? '') }}
                                        style={{
                                            wordBreak: 'break-word',
                                            overflowWrap: 'break-word',
                                            textAlign: 'left'
                                        }}
                                    />
                                ) : (
                                    <div className="rounded bg-transparent p-0 text-xs sm:text-sm whitespace-pre-wrap leading-relaxed text-gray-200 text-left">
                                        {gmailDraft?.body ?? parsedContent.body ?? ''}
                                    </div>
                                )}
                            </div>
                        )
                    ) : (
                        <pre 
                            ref={contentRef}
                            contentEditable={isEditing}
                            suppressContentEditableWarning
                            className={`whitespace-pre-wrap font-sans m-0 text-gray-200 leading-relaxed text-sm p-3.5 w-full transition-all duration-200 rounded-lg ${
                                isEditing 
                                    ? 'bg-[#0f0f0f] border border-violet-500/40 focus:outline-none focus:border-violet-500/70 shadow-lg shadow-violet-500/5' 
                                    : 'bg-[#0f0f0f]/50 border border-violet-500/10'
                            }`}
                            style={{ minHeight: '60px' }}
                        >
                            {displayTextContent}
                        </pre>
                    )}
                    <div className="mt-2.5 flex justify-end">
                        <button
                            onClick={handleEditToggle}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-violet-500/10 hover:bg-violet-500/20 text-violet-300 hover:text-violet-200 transition-all duration-200 text-xs border border-violet-500/20 hover:border-violet-500/40 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md hover:shadow-violet-500/10"
                            title={isEditing ? "Save" : "Edit"}
                            disabled={isSaving}
                        >
                            {isSaving ? (
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <circle cx="12" cy="12" r="10" strokeWidth="3" strokeDasharray="31.4 31.4" />
                                </svg>
                            ) : isEditing ? (
                                <>
                                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                  </svg>
                                  <span className="font-medium">Save</span>
                                </>
                            ) : (
                                <>
                                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                  </svg>
                                  <span className="font-medium">Edit</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>
            )}
            <div className="mt-4 flex gap-2 flex-wrap">
                {options.map((option, idx) => (
                    <button 
                        key={idx} 
                        onClick={() => handleOptionClick(option)} 
                        title={option}
                        className="group relative px-4 py-2 inline-flex items-center justify-center rounded-lg cursor-pointer text-white font-medium text-[13px] transition-all duration-300 ease-out bg-gradient-to-br from-violet-600 to-violet-700 hover:from-violet-500 hover:to-violet-600 shadow-md shadow-violet-500/20 hover:shadow-lg hover:shadow-violet-500/30 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-400/60 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0a0a0a] whitespace-nowrap overflow-hidden text-ellipsis border border-violet-500/30 hover:border-violet-400/50 hover:scale-[1.02] active:scale-[0.98]"
                    >
                        <span className="relative z-10">{option}</span>
                        <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-white/0 to-white/0 group-hover:from-white/10 group-hover:to-white/5 transition-all duration-300"></div>
                    </button>
                ))}
            </div>
        </div>
    );
}