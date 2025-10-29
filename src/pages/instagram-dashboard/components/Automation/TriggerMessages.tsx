import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, X, MessageSquare, ImageIcon, Link as LinkIcon, Bot, Trash2, Zap, Code, Copy, Check, AlertTriangle, BrainCircuit, Keyboard, List, ChevronUp, ChevronDown, ArrowLeft } from 'lucide-react';
import { AutomationApiService } from '../../../../api/automation';
import { PlatformAccount, DmKeywordReplyAutomationPayload } from '../../../../types/types';
import InstagramPreview from './InstagramPreview';
import AutomationList from './AutomationList';

interface TriggerMessagesProps {
  platformAccount: PlatformAccount;
  onBack: () => void;
}


export default function TriggerMessages({ platformAccount, onBack }: TriggerMessagesProps) {
    const navigate = useNavigate();
    const [editingTrigger, setEditingTrigger] = useState<any>(null);
    const [showAutomationList, setShowAutomationList] = useState(false);

    const handleEdit = (automation: any) => {
        // Transform automation data to match the editor format
        const transformedTrigger = {
            id: automation.automation_id,
            name: automation.name,
            triggerType: automation.trigger_type === 'AI_DECISION' ? 'ai' : 'keyword',
            messageType: automation.reply_template_type || 'text',
            messageContent: {
                text: automation.reply_template_content?.message?.text || '',
                imageUrl: automation.reply_template_content?.message?.attachment?.payload?.url || '',
                buttons: automation.reply_template_content?.message?.buttons || []
            },
            aiContext: automation.ai_context_rules || '',
            systemPrompt: automation.system_prompt || '',
            description: automation.description || '',
            modelUsage: automation.model_usage || 'PLATFORM_DEFAULT',
            userCooldownSeconds: automation.user_cooldown_seconds || null,
            keywords: automation.keywords ? automation.keywords.split(',').map((k: string) => k.trim()) : [],
            matchType: automation.match_type || 'CONTAINS',
            context: automation.ai_context_rules || ''
        };
        
        setEditingTrigger(transformedTrigger);
        setShowAutomationList(false);
    };

    const handleSave = () => {
        setEditingTrigger(null);
        setShowAutomationList(true); // Return to automation list after save
    };


    // Show automation list
    if (showAutomationList) {
        return (
            <AutomationList
                automationType="DM_REPLY"
                platformAccount={{
                    id: platformAccount.id,
                    platform_user_id: platformAccount.platform_user_id,
                    username: platformAccount.platform_username,
                    profile_picture_url: undefined
                }}
                onBack={()=>{setShowAutomationList(false);}}
                onEdit={handleEdit}
            />
        );
        // onClick={() => setShowAutomationList(true)}

    }

    return (
        <div className="bg-black h-screen font-sans text-neutral-200 overflow-hidden">
            <div className="max-w-7xl mx-auto h-full flex flex-col">
                <div className="py-4 sm:py-6 lg:py-8 h-full">
                    <TriggerEditor
                        key={editingTrigger ? editingTrigger.id : 'new'}
                        onSave={handleSave}
                        onCancel={onBack}
                        initialTrigger={editingTrigger}
                        platformAccount={platformAccount}
                        onShowList={() => setShowAutomationList(true)}
                    />
                </div>
            </div>
        </div>
    );
}
const AlertModal = ({ message, onClose }: { message: string, onClose: () => void }) => (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 animate-fade-in-fast p-4">
        <div className="bg-[#1C1C1E] rounded-xl shadow-xl w-full max-w-sm text-center border border-neutral-700 p-6">
            <AlertTriangle size={32} className="mx-auto text-yellow-400 mb-4"/>
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
const PayloadModal = ({ payload, onClose }: { payload: string, onClose: () => void }) => {
    const [copied, setCopied] = useState(false);
    const handleCopy = () => {
        navigator.clipboard.writeText(payload).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };
    return (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 animate-fade-in-fast p-4">
            <div className="bg-[#1C1C1E] rounded-xl shadow-xl w-full max-w-2xl border border-neutral-700">
                <div className="p-4 flex justify-between items-center border-b border-neutral-700">
                    <div className="flex items-center gap-2">
                        <Code size={18} className="text-teal-400"/>
                        <h3 className="text-lg font-semibold text-white">Data to Deploy</h3>
                    </div>
                    <button onClick={onClose} className="p-1 rounded-full hover:bg-neutral-700"><X size={20} /></button>
                </div>
                <div className="relative p-4">
                    <pre className="bg-black text-white p-4 rounded-lg text-sm overflow-x-auto max-h-[50vh]">
                        <code>{payload}</code>
                    </pre>
                    <button onClick={handleCopy} className="absolute top-6 right-6 p-2 bg-neutral-700 hover:bg-neutral-600 rounded-lg transition-colors">
                        {copied ? <Check size={16} className="text-green-400"/> : <Copy size={16} />}
                    </button>
                </div>
                 <div className="p-4 border-t border-neutral-700 text-center">
                    <p className="text-sm text-neutral-400">This is the JSON data that will be sent to the backend.</p>
                </div>
            </div>
        </div>
    );
};
const formatMessageTemplate = (triggerData: any) => {
    switch (triggerData.messageType) {
        case 'text':
            return { message: { text: triggerData.messageContent.text } };
        case 'image':
            return { message: { attachment: { type: 'image', payload: { url: triggerData.messageContent.imageUrl, is_reusable: true } } } };
        case 'button_template':
            return { message: { attachment: { type: 'template', payload: { template_type: 'button', text: triggerData.messageContent.text, buttons: triggerData.messageContent.buttons.map((btn: any) => ({ type: 'web_url', url: btn.link, title: btn.text })) } } } };
        case 'quick_replies':
            return { message: { text: triggerData.messageContent.text, quick_replies: triggerData.messageContent.buttons.map((qr: any) => ({ content_type: 'text', title: qr.text, payload: qr.payload })) } };
        default:
            return {};
    }
};
const TriggerEditor = ({ onSave, onCancel, initialTrigger, platformAccount, onShowList }: any) => {
    const [activeTab, setActiveTab] = useState<'editor' | 'preview'>('editor');
    const defaultContentForType = (type: string) => {
        switch (type) {
            case 'text': return { text: 'This is a sample text message.', imageUrl: '', buttons: [] };
            case 'image': return { text: '', imageUrl: 'https://placehold.co/600x600/121212/444?text=Sample+Image', buttons: [] };
            case 'button_template': return { text: 'Sample message with a button.', imageUrl: '', buttons: [{ text: 'Click Me', link: 'https://example.com' }] };
            case 'quick_replies': return { text: 'Please choose an option:', imageUrl: '', buttons: [{ text: 'Option 1', payload: 'OPTION_1' }, { text: 'Option 2', payload: 'OPTION_2' }] };
            default: return { text: '', imageUrl: '', buttons: [] };
        }
    };
    const getDefaultTrigger = (type = 'keyword') => {
        const baseTrigger: any = {
            triggerType: type,
            name: '',
            messageType: 'text',
            messageContent: defaultContentForType('text'),
            aiContext: '',
            systemPrompt: '',
            description: '',
            modelUsage: 'PLATFORM_DEFAULT',
            userCooldownSeconds: null,
        };
        if (type === 'keyword') {
            baseTrigger.keywords = [];
            baseTrigger.matchType = 'CONTAINS';
        } else {
            baseTrigger.context = '';
            baseTrigger.matchType = 'CONTAINS';
        }
        return baseTrigger;
    };
    const [trigger, setTrigger] = useState(initialTrigger || getDefaultTrigger());
    const [keywordInput, setKeywordInput] = useState('');
    const [showPayloadModal, setShowPayloadModal] = useState<string | null>(null);
    const [alert, setAlert] = useState({ show: false, message: '' });
    const [showDescription, setShowDescription] = useState(!!initialTrigger?.description && initialTrigger.description !== 'No Desc');
    const handleTriggerTypeChange = (newType: string) => {
        if (trigger.triggerType === newType) return;
        const newTrigger = getDefaultTrigger(newType);
        newTrigger.name = trigger.name;
        newTrigger.messageType = trigger.messageType;
        newTrigger.messageContent = trigger.messageContent;
        if (newType === 'ai') {
            newTrigger.context = trigger.context || (trigger.keywords.length > 0 ? trigger.keywords[0] : '');
            newTrigger.aiContext = trigger.aiContext;
            newTrigger.keywords = [];
        } else {
            newTrigger.keywords = trigger.keywords.length > 0 ? trigger.keywords : (trigger.context ? [trigger.context] : []);
            newTrigger.context = '';
            newTrigger.aiContext = '';
        }
        setTrigger(newTrigger);
    };
    const handleMessageTypeChange = (newType: string) => {
        setTrigger((prev: any) => ({ ...prev, messageType: newType, messageContent: defaultContentForType(newType) }));
    };
    const handleAddKeyword = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && keywordInput.trim()) {
            e.preventDefault();
            if (!trigger.keywords.includes(keywordInput.trim())) {
                setTrigger({ ...trigger, keywords: [...trigger.keywords, keywordInput.trim().toLowerCase()] });
            }
            setKeywordInput('');
        }
    };
    const handleRemoveKeyword = (keywordToRemove: string) => {
        setTrigger({ ...trigger, keywords: trigger.keywords.filter((k: string) => k !== keywordToRemove) });
    };
    const handleContentChange = (field: string, value: any) => {
        setTrigger({ ...trigger, messageContent: { ...trigger.messageContent, [field]: value } });
    };
    const handleButtonChange = (index: number, field: string, value: string) => {
        const newButtons = [...trigger.messageContent.buttons];
        newButtons[index][field] = value;
        handleContentChange('buttons', newButtons);
    };
    const handleAddButton = () => {
        const { messageType, messageContent } = trigger;
        const maxButtons = messageType === 'quick_replies' ? 13 : 3;
        if (messageContent.buttons.length < maxButtons) {
            const newButton = messageType === 'quick_replies' ? { text: '', payload: '' } : { text: '', link: '' };
            handleContentChange('buttons', [...messageContent.buttons, newButton]);
        }
    };
    const handleRemoveButton = (index: number) => {
        const newButtons = [...trigger.messageContent.buttons];
        newButtons.splice(index, 1);
        handleContentChange('buttons', newButtons);
    };
    const handleDeploy = async () => {
        if(trigger.triggerType === 'keyword' && (!trigger.keywords || trigger.keywords.length === 0)) {
            setAlert({ show: true, message: "Please add at least one keyword." });
            return;
        }
        if(trigger.triggerType === 'ai' && !trigger.context) {
            setAlert({ show: true, message: "Please provide a context for the AI." });
            return;
        }
        let keywordsToSend: string[] | null;
        let aiContextRulesToSend: string | null;
        if (trigger.triggerType === 'keyword') {
            keywordsToSend = trigger.keywords;
            aiContextRulesToSend = null;
        } else {
            keywordsToSend = null;
            aiContextRulesToSend = trigger.context;
        }
        const message_template = formatMessageTemplate(trigger);
        const payload: DmKeywordReplyAutomationPayload = {
            automation_id: trigger?.id ?? null,
            platform_user_id: platformAccount.platform_user_id,
            provider_id: platformAccount.provider_id,
            name: trigger.name,
            platform: "instagram",
            keywords: keywordsToSend || [],
            match_type: (trigger.matchType?.toUpperCase()) || 'CONTAINS',
            trigger_type: trigger.triggerType === 'keyword' ? 'KEYWORD' : 'AI_DECISION',
            ai_context_rules: aiContextRulesToSend,
            system_prompt: trigger.systemPrompt || '',
            reply_template_type: trigger.messageType,
            reply_template_content: message_template,
            description: trigger.description || 'No Desc',
            model_usage: trigger.modelUsage || 'PLATFORM_DEFAULT',
            user_cooldown_seconds: trigger.userCooldownSeconds ? parseInt(trigger.userCooldownSeconds) : null,
        };

        try {
            const response = await AutomationApiService.createOrUpdateDmKeywordReply(payload);
            if (!response.success) {
                throw new Error(response.message);
            }
            setShowPayloadModal(JSON.stringify(payload, null, 2));
            onSave(trigger);
        } catch (error: any) {
            setAlert({ show: true, message: `Failed to deploy trigger: ${error.message}` });
        }
    }
    return (
        <>
            {showPayloadModal && <PayloadModal payload={showPayloadModal} onClose={() => setShowPayloadModal(null)} />}
            {alert.show && <AlertModal message={alert.message} onClose={() => setAlert({ show: false, message: '' })} />}
            <div className="bg-[#121212] border border-neutral-800 rounded-2xl animate-fade-in h-full flex flex-col overflow-hidden">
                {/* Mobile Tabs */}
                <div className="lg:hidden border-b border-neutral-800">
                    <div className="flex">
                        <button
                            onClick={() => setActiveTab('editor')}
                            className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${
                                activeTab === 'editor'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-neutral-800 text-neutral-300 hover:bg-neutral-700'
                            }`}
                        >
                            Editor
                        </button>
                        <button
                            onClick={() => setActiveTab('preview')}
                            className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${
                                activeTab === 'preview'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-neutral-800 text-neutral-300 hover:bg-neutral-700'
                            }`}
                        >
                            Preview
                        </button>
                    </div>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 p-6 h-full overflow-hidden">
                    <div className={`space-y-6 h-full overflow-y-auto pr-4 -mr-4 no-scrollbar ${
                        activeTab === 'editor' ? 'block' : 'hidden lg:block'
                    }`}>
                        <div className="flex justify-between items-center sticky top-0 bg-[#121212] z-10 py-2">
                            <div className="flex items-center gap-3">
                                <button onClick={onCancel} className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors">
                                    <ArrowLeft size={18} />
                                    <span className="text-xs sm:text-sm font-medium">Back</span>
                                </button>
                                <h2 className="text-lg sm:text-xl font-bold text-white">{initialTrigger ? 'Edit Automation' : 'Create New Template Message automation'}</h2>
                            </div>
                        </div>
                        <NameInput name={trigger.name} setName={(value: string) => setTrigger({ ...trigger, name: value })} />
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
                                    <AutomationDescription
                                        description={trigger.description}
                                        setDescription={(value: string) => setTrigger({ ...trigger, description: value })}
                                    />
                                </div>
                            )}
                        </div> */}
                        <div className="flex items-center gap-2 bg-neutral-800 p-1 rounded-lg">
                            <button onClick={() => handleTriggerTypeChange('keyword')} className={`flex-1 flex items-center justify-center gap-2 px-3 py-1.5 rounded-md text-sm font-semibold transition-colors ${trigger.triggerType === 'keyword' ? 'bg-blue-500 text-white' : 'text-neutral-300 hover:bg-neutral-700'}`}>
                                <Keyboard size={16}/> Regular
                            </button>
                            <button onClick={() => handleTriggerTypeChange('ai')} className={`flex-1 flex items-center justify-center gap-2 px-3 py-1.5 rounded-md text-sm font-semibold transition-colors ${trigger.triggerType === 'ai' ? 'bg-purple-500 text-white' : 'text-neutral-300 hover:bg-neutral-700'}`}>
                                <BrainCircuit size={16}/> AI Decision <span className="text-xs bg-yellow-400/20 text-yellow-300 font-bold px-1.5 py-0.5 rounded-full">PRO</span>
                            </button>
                        </div>
                        {trigger.triggerType === 'keyword' ? (
                            <>
                                <KeywordInput keywords={trigger.keywords || []} keywordInput={keywordInput} setKeywordInput={setKeywordInput} handleAddKeyword={handleAddKeyword} handleRemoveKeyword={handleRemoveKeyword} />
                                <MatchTypeSelector matchType={trigger.matchType} setMatchType={(value: any) => setTrigger({ ...trigger, matchType: value })} />
                            </>
                        ) : (
                            <ContextInput context={trigger.context || ''} setContext={(value: string) => setTrigger({...trigger, context: value})} />
                        )}
                        <MessageTypeSelector messageType={trigger.messageType} setMessageType={handleMessageTypeChange} />
                        <MessageContentEditor trigger={trigger} handleContentChange={handleContentChange} handleButtonChange={handleButtonChange} handleAddButton={handleAddButton} handleRemoveButton={handleRemoveButton} />
                    </div>
                    <div className={`flex flex-col ${
                        activeTab === 'preview' ? 'block' : 'hidden lg:block'
                    }`}>
                         <div className="flex justify-between items-center mb-4">
                            <h3 className="text-sm sm:text-lg font-semibold text-neutral-400">Live Preview</h3>
                            <div className="flex items-center gap-2">
                                <button onClick={onShowList} className="flex items-center gap-2 text-xs sm:text-sm font-semibold text-blue-400 hover:text-white hover:bg-blue-500/20 p-2 rounded-lg transition-colors">
                                    <List size={14} className="sm:w-4 sm:h-4" /> <span className="hidden sm:inline">View List</span>
                                </button>
                                <button onClick={handleDeploy} className="flex items-center gap-1.5 bg-blue-500 hover:bg-blue-600 text-white text-xs sm:text-sm font-semibold px-2 sm:px-3 py-1.5 rounded-lg shadow-md transition-all">
                                    <Zap size={14} className="sm:w-4 sm:h-4" />
                                    Deploy
                                </button>
                            </div>
                        </div>
                        <InstagramPreview type="dm" trigger={trigger} platformAccount={{
                            id: platformAccount.id,
                            platform_user_id: platformAccount.platform_user_id,
                            username: platformAccount.platform_username,
                            profile_picture_url: undefined
                        }} />
                    </div>
                </div>
            </div>
        </>
    );
};
const NameInput = ({ name, setName }: { name: string, setName: (name: string) => void }) => (
    <div>
        <label className="block text-sm font-medium text-neutral-400 mb-2">Automation Name</label>
        <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., 'Welcome Message'" className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all" />
    </div>
);
const AutomationDescription = ({ description, setDescription }: { description: string, setDescription: (description: string) => void }) => (
    <div>
        <label className="block text-sm font-medium text-neutral-400 mb-2 sr-only">Description</label>
        <textarea rows={1} value={description} onChange={(e) => setDescription(e.target.value)} placeholder="A brief description of this automation (for your team's reference)" className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-sm resize-y" />
    </div>
);
const KeywordInput = ({ keywordInput, setKeywordInput, handleAddKeyword, keywords, handleRemoveKeyword }: any) => (
    <div>
        <label className="block text-sm font-medium text-neutral-400 mb-2">1. Detect Keywords</label>
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-2">
            <div className="flex flex-wrap gap-2 mb-2 min-h-[2.5rem]">
                {keywords.map((k: string) => (
                    <span key={k} className="flex items-center gap-1.5 bg-blue-500/20 text-blue-300 text-sm font-medium px-2.5 py-1 rounded-md animate-fade-in-fast">{k}<button onClick={() => handleRemoveKeyword(k)} className="hover:bg-blue-500/30 rounded-full"><X size={16} /></button></span>
                ))}
            </div>
            <input type="text" value={keywordInput} onChange={(e) => setKeywordInput(e.target.value)} onKeyDown={handleAddKeyword} placeholder="Type a keyword and press Enter..." className="w-full bg-transparent text-white placeholder-neutral-500 focus:outline-none px-2 py-1" />
        </div>
    </div>
);
const ContextInput = ({ context, setContext }: { context: string, setContext: (context: string) => void }) => (
    <div>
        <label className="block text-sm font-medium text-neutral-400 mb-2">1. When to Trigger (AI Context) <span className="text-red-400">*</span></label>
        <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Describe the context for the AI to trigger this message. e.g., 'When a user asks for a discount.' This is required for AI Decision triggers."
            className="w-full h-24 bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            required
        />
    </div>
);
const MatchTypeSelector = ({ matchType, setMatchType }: { matchType: string, setMatchType: (type: string) => void }) => {
    const options = [{ id: 'CONTAINS', label: 'Contains' }, { id: 'EXACT', label: 'Exact Match' }, { id: 'STARTS_WITH', label: 'Starts With' }];
    return (
        <div>
            <label className="block text-sm font-medium text-neutral-400 mb-2">2. Keyword Match Type</label>
            <div className="grid grid-cols-3 gap-2">
                {options.map(opt => (<button key={opt.id} onClick={() => setMatchType(opt.id)} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${matchType === opt.id ? 'bg-blue-500 text-white shadow-lg' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300'}`}>{opt.label}</button>))}
            </div>
        </div>
    );
};
const MessageTypeSelector = ({ messageType, setMessageType }: { messageType: string, setMessageType: (type: string) => void }) => {
    const types = [{ id: 'text', label: 'Text', icon: MessageSquare }, { id: 'image', label: 'Image', icon: ImageIcon }, { id: 'button_template', label: 'Button Template', icon: Bot }, { id: 'quick_replies', label: 'Quick Replies', icon: LinkIcon }];
    return (
        <div>
            <label className="block text-sm font-medium text-neutral-400 mb-2">2. Select Message Template</label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {types.map(type => (<button key={type.id} onClick={() => setMessageType(type.id)} className={`flex flex-col items-center justify-center gap-2 p-3 rounded-lg transition-all duration-200 aspect-square border ${messageType === type.id ? 'bg-blue-500/10 border-blue-500 text-white scale-105' : 'bg-neutral-800 border-neutral-700 hover:bg-neutral-700 text-neutral-300'}`}><type.icon size={24} /><span className="text-xs font-semibold text-center">{type.label}</span></button>))}
            </div>
        </div>
    );
};
const MessageContentEditor = ({ trigger, handleContentChange, handleButtonChange, handleAddButton, handleRemoveButton }: any) => {
    const { messageType, messageContent } = trigger;
    const isQuickReply = messageType === 'quick_replies';
    return (
        <div className="space-y-4">
            <h3 className="text-sm font-medium text-neutral-400">3. Configure Message</h3>
            {(messageType === 'text' || messageType === 'button_template' || messageType === 'quick_replies') && (<textarea value={messageContent.text} onChange={(e) => handleContentChange('text', e.target.value)} placeholder="Enter your message text here..." className="w-full h-24 bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all" />)}
            {messageType === 'image' && (<input type="text" value={messageContent.imageUrl} onChange={(e) => handleContentChange('imageUrl', e.target.value)} placeholder="Image URL" className="w-full bg-neutral-800 border border-neutral-700 text-white p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />)}
            {(messageType === 'button_template' || messageType === 'quick_replies') && (
                <div className="space-y-3">
                    <h4 className="text-xs font-medium text-neutral-500 uppercase tracking-wider">{isQuickReply ? 'Quick Replies' : 'Buttons'}</h4>
                    {messageContent.buttons.map((btn: any, i: number) => (
                        <div key={i} className="flex items-center gap-2 p-2 bg-neutral-800/50 border border-neutral-700/50 rounded-lg">
                            <input type="text" value={btn.text} onChange={(e) => handleButtonChange(i, 'text', e.target.value)} placeholder={isQuickReply ? "Reply Title" : "Button Text"} className="w-1/2 bg-neutral-700 text-white p-2 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500" />
                            <input type="text" value={isQuickReply ? btn.payload : btn.link} onChange={(e) => handleButtonChange(i, isQuickReply ? 'payload' : 'link', e.target.value)} placeholder={isQuickReply ? "Payload" : "Button Link/URL"} className="w-1/2 bg-neutral-700 text-white p-2 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500" />
                            <button onClick={() => handleRemoveButton(i)} className="p-2 text-neutral-400 hover:text-red-400 hover:bg-red-500/10 rounded-full"><Trash2 size={16} /></button>
                        </div>
                    ))}
                    {messageContent.buttons.length < (isQuickReply ? 13 : 3) && (<button onClick={handleAddButton} className="w-full flex items-center justify-center gap-2 text-sm font-semibold text-blue-400 hover:text-white hover:bg-blue-500/20 p-2 rounded-lg transition-colors border border-dashed border-neutral-600 hover:border-blue-500"><Plus size={16} /> Add {isQuickReply ? 'Quick Reply' : 'Button'}</button>)}
                </div>
            )}
        </div>
    );
};