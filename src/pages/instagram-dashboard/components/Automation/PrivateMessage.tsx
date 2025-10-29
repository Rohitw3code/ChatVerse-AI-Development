import React, { useEffect, useMemo, useState } from "react";
import { MessageSquare, Smartphone, X, List, Plus, ImageIcon, Link as LinkIcon, Bot, Trash2, Zap, Keyboard, BrainCircuit, ChevronUp, ChevronDown, AlertTriangle, ArrowLeft } from 'lucide-react';
import InstagramPreview from "./InstagramPreview";
import { PrivateReply } from "../../../../types/private_reply";
import { AutomationApiService } from "../../../../api/automation";
import { InstagramApiService } from "../../../../api/instagram_api";
import AutomationList from "./AutomationList";

type MessageTemplateType = "text" | "image" | "button_template" | "quick_replies";

type TriggerUI = {
    id?: string;
    name: string;
    description: string;
    triggerType: "keyword" | "ai";
    keywords: string[];
    matchType: "contains" | "exact" | "startsWith";
    replyType: "ai" | "template";
    systemPrompt?: string;
    postSelectionType: "ALL" | "SPECIFIC" | "DATE_RANGE";
    specificPostIds: string[];
    dateRange?: "1d" | "1w" | "1m" | null;
    aiContext?: string;
    messageType: MessageTemplateType | "text";
    messageContent: {
        text?: string;
        imageUrl?: string;
        buttons?: Array<any>;
    };
    temperature: number;
    confidenceThreshold: number;
    modelProvider: "GROQ" | "OPENAI";
    modelName: string;
    is_rag_enabled: boolean;
    model_usage: "PLATFORM_DEFAULT" | "CUSTOM";
    schedule_type: "CONTINUOUS" | "DAILY_ONE_TIME";
    max_actions: number | null;
    time_period_seconds: number;
    user_cooldown_seconds: number;
};

const defaultContentForType = (type: MessageTemplateType) => {
    switch (type) {
        case "text":
            return { text: "Hi! Thanks for asking — we'll DM you the details shortly.", imageUrl: "", buttons: [] };
        case "image":
            return { text: "", imageUrl: "https://placehold.co/600x600/121212/444?text=Sample+Image", buttons: [] };
        case "button_template":
            return { text: "Here are the details — tap to learn more.", imageUrl: "", buttons: [{ text: "View", link: "https://example.com" }] };
        case "quick_replies":
            return { text: "Which option do you want?", imageUrl: "", buttons: [{ text: "Option A", payload: "OPT_A" }, { text: "Option B", payload: "OPT_B" }] };
        default:
            return { text: "", imageUrl: "", buttons: [] };
    }
};

const getDefaultTrigger = (): TriggerUI => ({
    id: undefined,
    name: "Welcome & Info Reply",
    description: "",
    triggerType: "keyword",
    keywords: ["discount", "price", "coupon"],
    matchType: "contains",
    replyType: "ai",
    systemPrompt: "Write a short friendly DM with discount details.",
    postSelectionType: "ALL",
    specificPostIds: [],
    dateRange: null,
    aiContext: "requests for discount or pricing",
    messageType: "text",
    messageContent: defaultContentForType("text"),
    temperature: 0.7,
    confidenceThreshold: 0.75,
    modelProvider: "GROQ",
    modelName: "llama-3.3-70b-versatile",
    is_rag_enabled: false,
    model_usage: "PLATFORM_DEFAULT",
    schedule_type: "CONTINUOUS",
    max_actions: null,
    time_period_seconds: 60,
    user_cooldown_seconds: 300,
});

const AlertModal = ({ message, onClose }: { message: string, onClose: () => void }) => (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 animate-fade-in-fast p-4">
        <div className="bg-[#1C1C1E] rounded-xl shadow-xl w-full max-w-sm text-center border border-neutral-700 p-6">
            <AlertTriangle size={32} className="mx-auto text-yellow-400 mb-4" />
            <p className="text-white text-lg mb-6">{message}</p>
            <button
                onClick={onClose}
                className="bg-blue-500 hover:bg-blue-600 w-full text-white font-semibold px-6 py-2 rounded-lg transition-colors"
            >
                OK
            </button>
        </div>
    </div>
);

interface Props {
    onBack: () => void;
    platformAccount?: any;
}

export default function PrivateMessage({ onBack, platformAccount }: Props): JSX.Element {
    const [trigger, setTrigger] = useState<TriggerUI>(getDefaultTrigger());
    const [activeView, setActiveView] = useState<"comment" | "dm">("comment");
    const [activeTab, setActiveTab] = useState<'editor' | 'preview'>('editor');
    const [keywordInput, setKeywordInput] = useState("");
    const [availablePosts, setAvailablePosts] = useState<any[]>([]);
    const [isFetchingPosts, setIsFetchingPosts] = useState(false);
    const [showAutomationList, setShowAutomationList] = useState(false);
    const [showDescription, setShowDescription] = useState(false);
    const [alert, setAlert] = useState({ show: false, message: '' });


    useEffect(() => {
        const fetchPosts = async () => {
            if (!platformAccount?.platform_user_id) {
                setAvailablePosts([]);
                return;
            }
            setIsFetchingPosts(true);
            try {
                const response = await InstagramApiService.getInstagramPosts(platformAccount.platform_user_id);
                if (response?.success && response.data?.data && Array.isArray(response.data.data)) {
                    const mapped = response.data.data.map((p: any) => ({
                        id: p.id,
                        imageUrl: p.media_type === "VIDEO" ? p.thumbnail_url || p.media_url : p.media_url,
                        caption: p.caption,
                        permalink: p.permalink,
                        mediaType: p.media_type,
                    }));
                    setAvailablePosts(mapped);
                } else {
                    setAvailablePosts([]);
                }
            } catch (err) {
                console.error("Error fetching posts:", err);
                setAvailablePosts([]);
            } finally {
                setIsFetchingPosts(false);
            }
        };
        fetchPosts();
    }, [platformAccount?.platform_user_id]);

    const handleEdit = (automation: any) => {
        const transformedTrigger: TriggerUI = {
            id: automation.automation_id,
            name: automation.name || '',
            description: automation.description || '',
            triggerType: automation.trigger_type === 'AI_DECISION' ? 'ai' : 'keyword',
            keywords: automation.keywords ? automation.keywords.split(',').map((k: string) => k.trim()) : [],
            matchType: automation.match_type?.toLowerCase() || 'contains',
            replyType: automation.reply_type === 'CUSTOM' ? 'template' : 'ai',
            systemPrompt: automation.system_prompt || '',
            postSelectionType: automation.post_selection_type || 'ALL',
            specificPostIds: automation.specific_post_ids || [],
            dateRange: automation.date_range || null,
            aiContext: automation.ai_context_rules || '',
            messageType: automation.reply_template_type || 'text',
            messageContent: {
                text: automation.reply_template_content?.message?.text || '',
                imageUrl: automation.reply_template_content?.message?.attachment?.payload?.url || '',
                buttons: automation.reply_template_content?.message?.buttons || []
            },
            temperature: automation.temperature || 0.7,
            confidenceThreshold: automation.confidence_threshold || 0.75,
            modelProvider: automation.model_provider || 'GROQ',
            modelName: automation.model_name || 'llama-3.3-70b-versatile',
            is_rag_enabled: automation.is_rag_enabled || false,
            model_usage: automation.model_usage || 'PLATFORM_DEFAULT',
            schedule_type: automation.schedule_type || 'CONTINUOUS',
            max_actions: automation.max_actions || null,
            time_period_seconds: automation.time_period_seconds || 60,
            user_cooldown_seconds: automation.user_cooldown_seconds || 300,
        };

        setTrigger(transformedTrigger);
        setShowDescription(!!automation.description && automation.description !== 'No Desc');
        setShowAutomationList(false);
    };

    const handleAddKeyword = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && keywordInput.trim()) {
            e.preventDefault();
            const newKeyword = keywordInput.trim().toLowerCase();
            if (!trigger.keywords.includes(newKeyword)) {
                setTrigger({ ...trigger, keywords: [...trigger.keywords, newKeyword] });
            }
            setKeywordInput('');
        }
    };

    const handleRemoveKeyword = (kw: string) => {
        setTrigger({ ...trigger, keywords: trigger.keywords.filter((x) => x !== kw) });
    };

    const toggleSelectPost = (postId: string) => {
        setTrigger(prev => {
            const exists = prev.specificPostIds.includes(postId);
            return { ...prev, specificPostIds: exists ? prev.specificPostIds.filter(id => id !== postId) : [...prev.specificPostIds, postId] };
        });
    };

    const setMessageType = (type: MessageTemplateType) => {
        setTrigger(prev => ({ ...prev, messageType: type, messageContent: defaultContentForType(type) }));
    };

    const handleMessageContentChange = (field: string, value: any) => {
        setTrigger(prev => ({ ...prev, messageContent: { ...prev.messageContent, [field]: value } }));
    };

    const handleButtonChange = (index: number, field: string, value: any) => {
        const buttons = [...(trigger.messageContent.buttons || [])];
        buttons[index][field] = value;
        handleMessageContentChange("buttons", buttons);
    };

    const handleAddButton = () => {
        const max = trigger.messageType === "quick_replies" ? 13 : 3;
        const buttons = [...(trigger.messageContent.buttons || [])];
        if (buttons.length >= max) return;
        buttons.push(trigger.messageType === "quick_replies" ? { text: "", payload: "" } : { text: "", link: "" });
        handleMessageContentChange("buttons", buttons);
    };

    const handleRemoveButton = (index: number) => {
        const buttons = [...(trigger.messageContent.buttons || [])];
        buttons.splice(index, 1);
        handleMessageContentChange("buttons", buttons);
    };

    const deployPayload = async () => {
        const privateReplyPayload: PrivateReply = {
            name: trigger.name,
            description: trigger.description || 'No Desc',
            platform_user_id: platformAccount?.platform_user_id || "",
            provider_id: platformAccount?.provider_id || "",
            post_selection_type: trigger.postSelectionType,
            specific_post_ids: trigger.postSelectionType === "SPECIFIC" ? trigger.specificPostIds : [],
            date_range: trigger.postSelectionType === "DATE_RANGE" ? (trigger.dateRange || null) : null,
            trigger_type: trigger.triggerType === "keyword" ? "KEYWORD" : "AI_DECISION",
            keywords: trigger.triggerType === "keyword" ? trigger.keywords.join(",") : "",
            match_type: trigger.matchType.toUpperCase() as "CONTAINS" | "EXACT" | "STARTSWITH",
            ai_context_rules: trigger.triggerType === "ai" ? (trigger.aiContext || "") : "",
            system_prompt: trigger.replyType === "ai" ? (trigger.systemPrompt || "") : "",
            reply_template_type: trigger.replyType === "template" ? trigger.messageType : "",
            reply_template_content: trigger.replyType === "template" ? trigger.messageContent : {},
            model_provider: trigger.modelProvider,
            model_name: trigger.modelName,
            temperature: trigger.temperature,
            is_rag_enabled: trigger.is_rag_enabled,
            confidence_threshold: trigger.confidenceThreshold,
            model_usage: trigger.model_usage,
            schedule_type: trigger.schedule_type,
            max_actions: trigger.max_actions,
            time_period_seconds: trigger.time_period_seconds,
            user_cooldown_seconds: trigger.user_cooldown_seconds,
        };

        const payload = {
            ...privateReplyPayload,
            automation_id: trigger.id ?? null,
        };

        try {
            const response = await AutomationApiService.createPrivateMessageAutomation(payload as any);
            if (!response.success) {
                throw new Error(response.message || "An unknown error occurred.");
            }
            setShowAutomationList(true);
        } catch (error: any) {
            setAlert({ show: true, message: `Failed to deploy: ${error.message}` });
        }
    };

    const selectedPost = useMemo(() => {
        if (trigger.postSelectionType === "SPECIFIC" && trigger.specificPostIds.length > 0) {
            return availablePosts.find(p => p.id === trigger.specificPostIds[0]);
        }
        return null;
    }, [trigger.postSelectionType, trigger.specificPostIds, availablePosts]);

    const simulatedTrigger = useMemo(() => {
        if (trigger.triggerType === "keyword" && trigger.keywords.length > 0) {
            return `Comment with keyword: "${trigger.keywords[0]}"`;
        } else if (trigger.triggerType === "ai" && trigger.aiContext) {
            return `AI detected: ${trigger.aiContext}`;
        }
        return "Sample comment that triggered this DM";
    }, [trigger.triggerType, trigger.keywords, trigger.aiContext]);

    if (showAutomationList) {
        return (
            <AutomationList
                automationType="PRIVATE_MESSAGE"
                platformAccount={{
                    id: platformAccount?.id || 0,
                    platform_user_id: platformAccount?.platform_user_id || '',
                    username: platformAccount?.platform_username || '',
                    profile_picture_url: undefined
                }}
                onBack={() => setShowAutomationList(false)}
                onEdit={handleEdit}
            />
        );
    }

    const messageTypeOptions = [
        { id: 'text', label: 'Text', icon: MessageSquare },
        { id: 'image', label: 'Image', icon: ImageIcon },
        { id: 'button_template', label: 'Button Template', icon: Bot },
        { id: 'quick_replies', label: 'Quick Replies', icon: LinkIcon }
    ];

    const isQuickReply = trigger.messageType === 'quick_replies';

    return (
        <div className="bg-black h-screen font-sans text-neutral-200 overflow-hidden">
            {alert.show && <AlertModal message={alert.message} onClose={() => setAlert({ show: false, message: '' })} />}
            <div className="max-w-7xl mx-auto h-full flex flex-col">
                <div className="py-4 sm:py-6 lg:py-8 h-full">
                    <div className="bg-[#121212] border border-neutral-800 rounded-2xl animate-fade-in h-full flex flex-col overflow-hidden">
                        {/* Mobile Tabs */}
                        <div className="lg:hidden border-b border-neutral-800">
                            <div className="flex">
                                <button
                                    onClick={() => setActiveTab('editor')}
                                    className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${activeTab === 'editor'
                                            ? 'bg-blue-500 text-white'
                                            : 'bg-neutral-800 text-neutral-300 hover:bg-neutral-700'
                                        }`}
                                >
                                    Editor
                                </button>
                                <button
                                    onClick={() => setActiveTab('preview')}
                                    className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${activeTab === 'preview'
                                            ? 'bg-blue-500 text-white'
                                            : 'bg-neutral-800 text-neutral-300 hover:bg-neutral-700'
                                        }`}
                                >
                                    Preview
                                </button>
                            </div>
                        </div>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 p-6 h-full overflow-hidden">
                            <div className={`space-y-6 h-full overflow-y-auto pr-4 -mr-4 no-scrollbar ${activeTab === 'editor' ? 'block' : 'hidden lg:block'
                                }`}>
                                <div className="flex justify-between items-center sticky top-0 bg-[#121212] z-10 py-2">
                                    <div className="flex items-center gap-3">
                                        <button onClick={onBack} className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors">
                                            <ArrowLeft size={18} />
                                            <span className="text-xs sm:text-sm font-medium">Back</span>
                                        </button>
                                        <h2 className="text-lg sm:text-xl font-bold text-white">{trigger.id ? 'Edit Automation' : 'Create New Comment-to-DM Automation'}</h2>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-neutral-400 mb-2">Automation Name</label>
                                    <input type="text" value={trigger.name} onChange={(e) => setTrigger({ ...trigger, name: e.target.value })} placeholder="e.g., 'Discount Responder'" className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all" />
                                </div>

                                {/* <div className="bg-neutral-900 border border-neutral-800 rounded-lg overflow-hidden">
                                    <button
                                        className="w-full flex justify-between items-center p-3 text-left font-semibold text-white hover:bg-neutral-800 transition-colors"
                                        onClick={() => setShowDescription(!showDescription)}
                                    >
                                        Description (Optional)
                                        {showDescription ? <ChevronUp size={20} className="text-neutral-400" /> : <ChevronDown size={20} className="text-neutral-400" />}
                                    </button>
                                    {showDescription && (
                                        <div className="p-3 border-t border-neutral-800">
                                            <textarea rows={1} value={trigger.description} onChange={(e) => setTrigger({ ...trigger, description: e.target.value })} placeholder="A brief description of this automation (for your team's reference)" className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-sm resize-y" />
                                        </div>
                                    )}
                                </div> */}

                                {/* Trigger Type */}
                                <div className="flex items-center gap-2 bg-neutral-800 p-1 rounded-lg">
                                    <button onClick={() => setTrigger({ ...trigger, triggerType: "keyword" })} className={`flex-1 flex items-center justify-center gap-2 px-3 py-1.5 rounded-md text-sm font-semibold transition-colors ${trigger.triggerType === 'keyword' ? 'bg-blue-500 text-white' : 'text-neutral-300 hover:bg-neutral-700'}`}>
                                        <Keyboard size={16} /> Keyword-based
                                    </button>
                                    <button onClick={() => setTrigger({ ...trigger, triggerType: "ai" })} className={`flex-1 flex items-center justify-center gap-2 px-3 py-1.5 rounded-md text-sm font-semibold transition-colors ${trigger.triggerType === 'ai' ? 'bg-purple-500 text-white' : 'text-neutral-300 hover:bg-neutral-700'}`}>
                                        <BrainCircuit size={16} /> AI Decision <span className="text-xs bg-yellow-400/20 text-yellow-300 font-bold px-1.5 py-0.5 rounded-full">PRO</span>
                                    </button>
                                </div>

                                {/* Keyword or Context Input */}
                                {trigger.triggerType === 'keyword' ? (
                                    <>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-400 mb-2">1. Detect Keywords in Comments</label>
                                            <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-2">
                                                <div className="flex flex-wrap gap-2 mb-2 min-h-[2.5rem]">
                                                    {trigger.keywords.map((k) => (
                                                        <span key={k} className="flex items-center gap-1.5 bg-blue-500/20 text-blue-300 text-sm font-medium px-2.5 py-1 rounded-md animate-fade-in-fast">{k}<button onClick={() => handleRemoveKeyword(k)} className="hover:bg-blue-500/30 rounded-full"><X size={16} /></button></span>
                                                    ))}
                                                </div>
                                                <input type="text" value={keywordInput} onChange={(e) => setKeywordInput(e.target.value)} onKeyDown={handleAddKeyword} placeholder="Type a keyword and press Enter..." className="w-full bg-transparent text-white placeholder-neutral-500 focus:outline-none px-2 py-1" />
                                            </div>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-400 mb-2">2. Keyword Match Type</label>
                                            <div className="grid grid-cols-3 gap-2">
                                                <button onClick={() => setTrigger({ ...trigger, matchType: "contains" })} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${trigger.matchType === 'contains' ? 'bg-blue-500 text-white shadow-lg' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300'}`}>Contains</button>
                                                <button onClick={() => setTrigger({ ...trigger, matchType: "exact" })} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${trigger.matchType === 'exact' ? 'bg-blue-500 text-white shadow-lg' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300'}`}>Exact Match</button>
                                                <button onClick={() => setTrigger({ ...trigger, matchType: "startsWith" })} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${trigger.matchType === 'startsWith' ? 'bg-blue-500 text-white shadow-lg' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300'}`}>Starts With</button>
                                            </div>
                                        </div>
                                    </>
                                ) : (
                                    <div>
                                        <label className="block text-sm font-medium text-neutral-400 mb-2">1. When to Trigger (AI Context) <span className="text-red-400">*</span></label>
                                        <textarea value={trigger.aiContext} onChange={(e) => setTrigger({ ...trigger, aiContext: e.target.value })} placeholder="Describe what comments should trigger a DM (example: 'requests for discount or price details')" className="w-full h-24 bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all" required />
                                    </div>
                                )}

                                {/* Reply Type */}
                                <div>
                                    <label className="block text-sm font-medium text-neutral-400 mb-2">3. Reply with</label>
                                    <div className="flex items-center gap-2 bg-neutral-800 p-1 rounded-lg">
                                        <button onClick={() => setTrigger({ ...trigger, replyType: "ai" })} className={`flex-1 flex items-center justify-center gap-2 px-3 py-1.5 rounded-md text-sm font-semibold transition-colors ${trigger.replyType === 'ai' ? 'bg-blue-500 text-white' : 'text-neutral-300 hover:bg-neutral-700'}`}>AI Generated DM</button>
                                        <button onClick={() => setTrigger({ ...trigger, replyType: "template" })} className={`flex-1 flex items-center justify-center gap-2 px-3 py-1.5 rounded-md text-sm font-semibold transition-colors ${trigger.replyType === 'template' ? 'bg-green-500 text-white' : 'text-neutral-300 hover:bg-neutral-700'}`}>Template DM</button>
                                    </div>
                                </div>

                                {trigger.replyType === 'ai' && (
                                    <div className="space-y-4">
                                        <textarea value={trigger.systemPrompt} onChange={(e) => setTrigger({ ...trigger, systemPrompt: e.target.value })} placeholder="System prompt for the AI to generate the DM..." className="w-full h-24 bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all" />
                                        <div className="flex items-center gap-2">
                                            <input type="checkbox" id="rag-checkbox" checked={!!trigger.is_rag_enabled} onChange={(e) => setTrigger({ ...trigger, is_rag_enabled: e.target.checked })} className="w-4 h-4 rounded-md bg-neutral-900 border-neutral-700 text-blue-500 focus:ring-blue-500" />
                                            <label htmlFor="rag-checkbox" className="text-sm text-neutral-300">Enable RAG (Retrieval-Augmented Generation)</label>
                                        </div>
                                    </div>
                                )}

                                {trigger.replyType === 'template' && (
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-400 mb-2">4. Select Message Template</label>
                                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                                                {messageTypeOptions.map(type => (<button key={type.id} onClick={() => setMessageType(type.id as MessageTemplateType)} className={`flex flex-col items-center justify-center gap-2 p-3 rounded-lg transition-all duration-200 aspect-square border ${trigger.messageType === type.id ? 'bg-blue-500/10 border-blue-500 text-white scale-105' : 'bg-neutral-800 border-neutral-700 hover:bg-neutral-700 text-neutral-300'}`}><type.icon size={24} /><span className="text-xs font-semibold text-center">{type.label}</span></button>))}
                                            </div>
                                        </div>

                                        <div className="space-y-4">
                                            <h3 className="text-sm font-medium text-neutral-400">5. Configure Message</h3>
                                            {(trigger.messageType === 'text' || trigger.messageType === 'button_template' || trigger.messageType === 'quick_replies') && (<textarea value={trigger.messageContent.text} onChange={(e) => handleMessageContentChange('text', e.target.value)} placeholder="Enter your message text here..." className="w-full h-24 bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all" />)}
                                            {trigger.messageType === 'image' && (<input type="text" value={trigger.messageContent.imageUrl} onChange={(e) => handleMessageContentChange('imageUrl', e.target.value)} placeholder="Image URL" className="w-full bg-neutral-800 border border-neutral-700 text-white p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />)}
                                            {(trigger.messageType === 'button_template' || trigger.messageType === 'quick_replies') && (
                                                <div className="space-y-3">
                                                    <h4 className="text-xs font-medium text-neutral-500 uppercase tracking-wider">{isQuickReply ? 'Quick Replies' : 'Buttons'}</h4>
                                                    {(trigger.messageContent.buttons || []).map((btn: any, i: number) => (
                                                        <div key={i} className="flex items-center gap-2 p-2 bg-neutral-800/50 border border-neutral-700/50 rounded-lg">
                                                            <input type="text" value={btn.text} onChange={(e) => handleButtonChange(i, 'text', e.target.value)} placeholder={isQuickReply ? "Reply Title" : "Button Text"} className="w-1/2 bg-neutral-700 text-white p-2 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500" />
                                                            <input type="text" value={isQuickReply ? btn.payload : btn.link} onChange={(e) => handleButtonChange(i, isQuickReply ? 'payload' : 'link', e.target.value)} placeholder={isQuickReply ? "Payload" : "Button Link/URL"} className="w-1/2 bg-neutral-700 text-white p-2 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500" />
                                                            <button onClick={() => handleRemoveButton(i)} className="p-2 text-neutral-400 hover:text-red-400 hover:bg-red-500/10 rounded-full"><Trash2 size={16} /></button>
                                                        </div>
                                                    ))}
                                                    {trigger.messageContent.buttons && trigger.messageContent.buttons.length < (isQuickReply ? 13 : 3) && (<button onClick={handleAddButton} className="w-full flex items-center justify-center gap-2 text-sm font-semibold text-blue-400 hover:text-white hover:bg-blue-500/20 p-2 rounded-lg transition-colors border border-dashed border-neutral-600 hover:border-blue-500"><Plus size={16} /> Add {isQuickReply ? 'Quick Reply' : 'Button'}</button>)}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}

                                <div>
                                    <label className="block text-sm font-medium text-neutral-400 mb-2">Post Selection</label>
                                    <div className="grid grid-cols-3 gap-2">
                                        <button onClick={() => setTrigger({ ...trigger, postSelectionType: "ALL" })} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${trigger.postSelectionType === 'ALL' ? 'bg-blue-500 text-white shadow-lg' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300'}`}>All Posts</button>
                                        <button onClick={() => setTrigger({ ...trigger, postSelectionType: "SPECIFIC" })} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${trigger.postSelectionType === 'SPECIFIC' ? 'bg-blue-500 text-white shadow-lg' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300'}`}>Select Posts</button>
                                        <button onClick={() => setTrigger({ ...trigger, postSelectionType: "DATE_RANGE" })} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${trigger.postSelectionType === 'DATE_RANGE' ? 'bg-blue-500 text-white shadow-lg' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300'}`}>Date Range</button>
                                    </div>
                                    {trigger.postSelectionType === "SPECIFIC" && (
                                        <div className="mt-3 max-h-44 overflow-y-auto space-y-2 p-1">
                                            {isFetchingPosts ? <div className="text-sm text-neutral-400">Loading posts...</div>
                                                : availablePosts.length > 0 ? availablePosts.map(p => (
                                                    <div key={p.id} className={`flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-colors ${trigger.specificPostIds.includes(p.id) ? "bg-blue-500/10 border border-blue-500" : "bg-neutral-800/50 border border-neutral-700/50 hover:bg-neutral-700/50"}`} onClick={() => toggleSelectPost(p.id)}>
                                                        <input type="checkbox" checked={trigger.specificPostIds.includes(p.id)} readOnly className="w-4 h-4 rounded bg-neutral-700 border-neutral-600 text-blue-500 focus:ring-blue-500" />
                                                        <img src={p.imageUrl} alt="post thumbnail" className="w-10 h-10 rounded-md object-cover" />
                                                        <p className="flex-1 text-sm line-clamp-2">{p.caption || "No caption"}</p>
                                                    </div>
                                                )) : <div className="text-sm text-neutral-500">No posts available.</div>
                                            }
                                        </div>
                                    )}
                                    {trigger.postSelectionType === "DATE_RANGE" && (
                                        <div className="mt-3 grid grid-cols-3 gap-2">
                                            <button onClick={() => setTrigger({ ...trigger, dateRange: "1d" })} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${trigger.dateRange === '1d' ? 'bg-blue-500 text-white shadow-lg' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300'}`}>Last Day</button>
                                            <button onClick={() => setTrigger({ ...trigger, dateRange: "1w" })} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${trigger.dateRange === '1w' ? 'bg-blue-500 text-white shadow-lg' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300'}`}>Last Week</button>
                                            <button onClick={() => setTrigger({ ...trigger, dateRange: "1m" })} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${trigger.dateRange === '1m' ? 'bg-blue-500 text-white shadow-lg' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300'}`}>Last Month</button>
                                        </div>
                                    )}
                                </div>

                                <div className="space-y-4">
                                    <h3 className="text-sm font-medium text-neutral-400">AI Settings</h3>
                                    {/* <div className="flex items-center gap-4">
                                        <label className="text-sm text-neutral-400 w-1/3">Model Usage</label>
                                        <select value={trigger.model_usage} onChange={(e) => setTrigger({ ...trigger, model_usage: e.target.value as "PLATFORM_DEFAULT" | "CUSTOM" })} className="flex-1 p-2 rounded-lg bg-neutral-800 border border-neutral-700 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none">
                                            <option value="PLATFORM_DEFAULT">Platform Default</option>
                                            <option value="CUSTOM">Custom</option>
                                        </select>
                                    </div> */}
                                    {trigger.model_usage === "CUSTOM" && (
                                        <div className="space-y-3 pl-4 border-l-2 border-neutral-800">
                                            <div className="flex items-center gap-4">
                                                <label className="text-sm text-neutral-400 w-1/3">Provider</label>
                                                <select value={trigger.modelProvider} onChange={(e) => setTrigger({ ...trigger, modelProvider: e.target.value as "GROQ" | "OPENAI" })} className="flex-1 p-2 rounded-lg bg-neutral-800 border border-neutral-700 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none">
                                                    <option value="GROQ">GROQ</option>
                                                    <option value="OPENAI">OPENAI</option>
                                                </select>
                                            </div>
                                            <div className="flex items-center gap-4">
                                                <label className="text-sm text-neutral-400 w-1/3">Model</label>
                                                <select value={trigger.modelName} onChange={(e) => setTrigger({ ...trigger, modelName: e.target.value })} className="flex-1 p-2 rounded-lg bg-neutral-800 border border-neutral-700 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none">
                                                    {trigger.modelProvider === "GROQ" ? (<>
                                                        <option value="llama-3.3-70b-versatile">llama-3.3-70b-versatile</option>
                                                        <option value="llama-3.3-8b-versatile">llama-3.3-8b-versatile</option>
                                                    </>) : (<>
                                                        <option value="meta-llama/llama-4-maverick-17b-128e-instruct">meta-llama/llama-4-maverick-17b-128e-instruct</option>
                                                        <option value="gpt4omini">gpt4omini</option>
                                                        <option value="gpt-4o">gpt-4o</option>
                                                    </>)}
                                                </select>
                                            </div>
                                            <div className="flex items-center gap-4">
                                                <label className="text-sm text-neutral-400 w-1/3">Temperature</label>
                                                <input type="number" value={trigger.temperature} onChange={(e) => setTrigger({ ...trigger, temperature: parseFloat(e.target.value) })} step="0.1" min="0" max="1" className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                                            </div>
                                            <div className="flex items-center gap-4">
                                                <label className="text-sm text-neutral-400 w-1/3">Confidence</label>
                                                <input type="number" value={trigger.confidenceThreshold} onChange={(e) => setTrigger({ ...trigger, confidenceThreshold: parseFloat(e.target.value) })} step="0.05" min="0" max="1" className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                                            </div>
                                        </div>
                                    )}
                                </div>

                                <div className="space-y-4">
                                    {/* <h3 className="text-sm font-medium text-neutral-400">Schedule & Rate Limits</h3> */}
                                    {/* <div className="flex items-center gap-4">
                                        <label className="text-sm text-neutral-400 w-1/3">Schedule Type</label>
                                        <select value={trigger.schedule_type} onChange={(e) => setTrigger({ ...trigger, schedule_type: e.target.value as "CONTINUOUS" | "DAILY_ONE_TIME" })} className="flex-1 p-2 rounded-lg bg-neutral-800 border border-neutral-700 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none">
                                            <option value="CONTINUOUS">Continuous</option>
                                            <option value="DAILY_ONE_TIME">Daily One Time</option>
                                        </select>
                                    </div> */}
                                    <div className="flex items-center gap-4">
                                        <label className="text-sm text-neutral-400 w-1/3">Max Actions</label>
                                        <input type="number" value={trigger.max_actions === null ? "" : trigger.max_actions} onChange={(e) => setTrigger({ ...trigger, max_actions: e.target.value === "" ? null : parseInt(e.target.value, 10) })} placeholder="Unlimited" min="0" className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                                    </div>
                                    {/* <div className="flex items-center gap-4">
                                        <label className="text-sm text-neutral-400 w-1/3">Time Period (s)</label>
                                        <input type="number" value={trigger.time_period_seconds} onChange={(e) => setTrigger({ ...trigger, time_period_seconds: parseInt(e.target.value, 10) })} min="1" className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                                    </div> */}
                                    {/* <div className="flex items-center gap-4">
                                        <label className="text-sm text-neutral-400 w-1/3">User Cooldown (s)</label>
                                        <input type="number" value={trigger.user_cooldown_seconds} onChange={(e) => setTrigger({ ...trigger, user_cooldown_seconds: parseInt(e.target.value, 10) })} min="0" className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                                    </div> */}
                                </div>
                            </div>

                            <div className={`flex flex-col ${activeTab === 'preview' ? 'block' : 'hidden lg:block'
                                }`}>
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="text-sm sm:text-lg font-semibold text-neutral-400">Live Preview</h3>
                                    <div className="flex items-center gap-2">
                                        <button onClick={() => setShowAutomationList(true)} className="flex items-center gap-2 text-xs sm:text-sm font-semibold text-blue-400 hover:text-white hover:bg-blue-500/20 p-2 rounded-lg transition-colors">
                                            <List size={14} className="sm:w-4 sm:h-4" /> <span className="hidden sm:inline">View List</span>
                                        </button>
                                        <button onClick={deployPayload} className="flex items-center gap-1.5 bg-blue-500 hover:bg-blue-600 text-white text-xs sm:text-sm font-semibold px-2 sm:px-3 py-1.5 rounded-lg shadow-md transition-all">
                                            <Zap size={14} className="sm:w-4 sm:h-4" />
                                            Deploy
                                        </button>
                                    </div>
                                </div>
                                <div className="flex justify-center my-4">
                                    <div className="inline-flex items-center gap-3 rounded-full bg-[#1C1C1E] border border-neutral-800 px-3 py-2 shadow-sm">
                                        <button
                                            onClick={() => setActiveView("comment")}
                                            className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium transition-colors ${activeView === "comment"
                                                    ? "bg-neutral-700 text-white"
                                                    : "text-neutral-300 hover:bg-neutral-800"
                                                }`}
                                        >
                                            <Smartphone className="w-4 h-4" />
                                            <span>Comment</span>
                                        </button>
                                        <div className="w-px h-6 bg-neutral-700" />
                                        <button
                                            onClick={() => setActiveView("dm")}
                                            className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium transition-colors ${activeView === "dm"
                                                    ? "bg-neutral-700 text-white"
                                                    : "text-neutral-300 hover:bg-neutral-800"
                                                }`}
                                        >
                                            <MessageSquare className="w-4 h-4" />
                                            <span>DM</span>
                                        </button>
                                    </div>
                                </div>

                                <div className="w-full">
                                    <div className="max-w-[350px] mx-auto">
                                        {activeView === "comment" ? (
                                            <InstagramPreview
                                                type="comment"
                                                trigger={{
                                                    replyType: trigger.replyType === "template" ? "template" : "ai",
                                                    systemPrompt: trigger.systemPrompt,
                                                    triggerType: trigger.triggerType,
                                                    keywords: trigger.keywords,
                                                    matchType: trigger.matchType,
                                                    postSelectionType: trigger.postSelectionType,
                                                    specificPostIds: trigger.specificPostIds,
                                                    dateRange: trigger.dateRange,
                                                    messageType: trigger.messageType,
                                                    messageContent: trigger.messageContent,
                                                }}
                                                platformAccount={
                                                    platformAccount ?? { username: "preview_account", profile_picture_url: "https://placehold.co/64x64/222222/777777?text=A" }
                                                }
                                                selectedPost={selectedPost ?? undefined}
                                            />
                                        ) : (
                                            <InstagramPreview
                                                type="dm"
                                                trigger={{
                                                    messageType: trigger.messageType,
                                                    messageContent: trigger.messageContent,
                                                    _triggeredByComment: simulatedTrigger,
                                                    systemPrompt: trigger.replyType === "ai" ? trigger.systemPrompt : undefined,
                                                }}
                                                platformAccount={
                                                    platformAccount ?? { username: "preview_account", profile_picture_url: "https://placehold.co/64x64/222222/777777?text=A" }
                                                }
                                                selectedPost={selectedPost ?? undefined}
                                            />
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}