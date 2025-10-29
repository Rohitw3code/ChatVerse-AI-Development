import { Markdown } from '../components/Markdown';
import { ApiMessage } from "../../types";
import { InputOptionInterrupt } from './InputOptionInterrupt';
import { ConnectInterrupt } from './ConnectInterrupt';
import { InputFieldInterrupt } from './InputFieldInterrupt';

interface InterruptMessageProps {
    message: ApiMessage;
    onOptionClick: (option: string, additionalData?: any) => void;
    handleInstagramConnect: () => void;
    handleGmailConnect: () => void;
    handleYoutubeConnect: () => void;
    handleGdocConnect: () => void;
    handleSheetsConnect: () => void;
}

export function InterruptMessage({ message, onOptionClick, handleInstagramConnect, handleGmailConnect, handleYoutubeConnect, handleGdocConnect, handleSheetsConnect }: InterruptMessageProps) {
    const renderInterruptContent = () => {
        switch (message.data?.type) {
            case "input_option":
                return <InputOptionInterrupt messageData={message.data} onOptionClick={onOptionClick} message={message} />;
            case "connect":
                return <ConnectInterrupt messageData={message.data} handleInstagramConnect={handleInstagramConnect} handleGmailConnect={handleGmailConnect} handleYoutubeConnect={handleYoutubeConnect} handleGdocConnect={handleGdocConnect} handleSheetsConnect={handleSheetsConnect} />;
            case "input_field":
                return <InputFieldInterrupt messageData={message.data} />;
            default:
                return (
                    <div className="prose prose-sm prose-invert max-w-none">
                        {message.current_messages?.map((cm: { content: string }, idx: number) => (
                            <Markdown key={idx}>{cm.content}</Markdown>
                        )) || null}
                    </div>
                );
        }
    };

    return (
        <div className="flex justify-start mb-5">
            <div className="w-full sm:max-w-[80%] py-2 px-2 sm:py-3 sm:px-4 rounded-2xl rounded-bl-md leading-snug text-white bg-[#1a1a1a]">
                {renderInterruptContent()}
            </div>
        </div>
    );
}