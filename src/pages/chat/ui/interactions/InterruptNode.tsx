import { InterruptMessage } from "./InterruptMessage";
import { StreamingMessage } from "../shared/StreamingMessage";
import { ApiMessage } from "../../types";
import { API_CONFIG } from '../../../../config/api';

interface InterruptNodeProps {
    message: ApiMessage;
    onOptionClick: (option: string, additionalData?: any) => void;
    providerId: string;
    isClosing?: boolean;
    onAnimationComplete?: () => void;
}

export function InterruptNode({ message, onOptionClick, providerId, isClosing, onAnimationComplete }: InterruptNodeProps) {
    if (message.status === 'streaming') {
        return (
            <StreamingMessage
                message={message}
                isClosing={isClosing}
                onAnimationComplete={onAnimationComplete}
            />
        );
    }

    const handleInstagramConnect = () => {
        if (!providerId) return;
        const returnUrl = window.location.href;
        const instagramLoginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.INSTAGRAM.LOGIN(providerId, returnUrl)}`;
        window.location.href = instagramLoginUrl;
    };

    const handleGmailConnect = () => {
        if (!providerId) return;
        const returnUrl = window.location.href;
        const gmailLoginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.GMAIL.LOGIN(providerId, returnUrl)}`;
        window.location.href = gmailLoginUrl;
    };

    const handleYoutubeConnect = () => {
        if (!providerId) return;
        const returnUrl = window.location.href;
        const youtubeLoginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.YOUTUBE.LOGIN(providerId, returnUrl)}`;
        window.location.href = youtubeLoginUrl;
    };

    const handleGdocConnect = () => {
        if (!providerId) return;
        const returnUrl = window.location.href;
        const gdocLoginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.GDOC.LOGIN(providerId, returnUrl)}`;
        window.location.href = gdocLoginUrl;
    };

    const handleSheetsConnect = () => {
        if (!providerId) return;
        const returnUrl = window.location.href;
        const sheetsLoginUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.GOOGLE_SHEETS.LOGIN(providerId, returnUrl)}`;
        window.location.href = sheetsLoginUrl;
    };

    return (
        <InterruptMessage
            message={message}
            onOptionClick={onOptionClick}
            handleInstagramConnect={handleInstagramConnect}
            handleGmailConnect={handleGmailConnect}
            handleYoutubeConnect={handleYoutubeConnect}
            handleGdocConnect={handleGdocConnect}
            handleSheetsConnect={handleSheetsConnect}
        />
    );
}
