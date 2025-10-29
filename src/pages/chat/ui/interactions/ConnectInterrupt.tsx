import { ApiMessage } from "../../types";
import { GmailIcon, InstagramIcon, YouTubeIcon, DocsIcon, SheetsIcon } from "../shared/platforms";

interface ConnectInterruptProps {
    messageData: ApiMessage['data'];
    handleInstagramConnect: () => void;
    handleGmailConnect: () => void;
    handleYoutubeConnect: () => void;
    handleGdocConnect: () => void;
    handleSheetsConnect: () => void;
}

export function ConnectInterrupt({ messageData, handleInstagramConnect, handleGmailConnect, handleYoutubeConnect, handleGdocConnect, handleSheetsConnect }: ConnectInterruptProps) {
    const platform = messageData?.platform;
    const { title, content } = messageData?.data || {};

    const connectButton = () => {
        const buttonClasses = "inline-flex items-center gap-3 py-2.5 px-4 rounded-full font-semibold text-sm cursor-pointer no-underline transition-all duration-200 ease-in-out mt-4 bg-zinc-800 text-white border border-slate-700 hover:-translate-y-0.5 hover:border-violet-300";

        switch (platform) {
            case "instagram":
                return (
                    <button onClick={handleInstagramConnect} className={buttonClasses}>
                        <InstagramIcon />
                        <span>Connect Instagram</span>
                    </button>
                );
            case "gmail":
                return (
                    <button onClick={handleGmailConnect} className={buttonClasses}>
                        <GmailIcon />
                        <span>Connect Gmail</span>
                    </button>
                );
            case "youtube":
                return (
                    <button onClick={handleYoutubeConnect} className={buttonClasses}>
                        <YouTubeIcon />
                        <span>Connect YouTube</span>
                    </button>
                );
            case "gdoc":
            case "docs":
                return (
                    <button onClick={handleGdocConnect} className={buttonClasses}>
                        <DocsIcon />
                        <span>Connect Google Docs</span>
                    </button>
                );
            case "sheets":
            case "google_sheets":
                return (
                    <button onClick={handleSheetsConnect} className={buttonClasses}>
                        <SheetsIcon />
                        <span>Connect Google Sheets</span>
                    </button>
                );
            default:
                return null;
        }
    };

    return (
        <div className="prose prose-sm prose-invert max-w-none">
            {title && <div className="font-semibold mb-2.5 text-violet-300">{title}</div>}
            {content && <pre className="whitespace-pre-wrap font-sans m-0 text-white leading-relaxed text-sm">{content}</pre>}
            <div className="not-prose">
                {connectButton()}
            </div>
        </div>
    );
}