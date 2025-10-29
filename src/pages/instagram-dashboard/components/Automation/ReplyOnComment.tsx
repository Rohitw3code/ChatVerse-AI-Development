import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, List, BrainCircuit, Keyboard, ChevronUp, ChevronDown, AlertTriangle, Info, Zap, ArrowLeft, Link as LinkIcon, Sparkles } from 'lucide-react';
import { AutomationApiService } from '../../../../api/automation';
import { InstagramApiService } from '../../../../api/instagram_api';
import { CommentReplyPayload } from '../../../../types/comment_reply';
import InstagramPreview from './InstagramPreview';
import AutomationList from './AutomationList';

interface Props {
  platformAccount: any;
  onBack: () => void;
}


export default function ReplyOnComment({ platformAccount, onBack }: Props): JSX.Element {
    const navigate = useNavigate();
    const [isCreating, setIsCreating] = useState(true);
    const [editingTrigger, setEditingTrigger] = useState<any>(null);

    const handleSave = () => {
        setIsCreating(false);
        setEditingTrigger(null);
    };

    const handleEdit = (automation: any) => {
        const [transformedTrigger] = transformApiDataToUiState([automation]);
        setEditingTrigger(transformedTrigger);
        setIsCreating(true);
    };

    const handleCancel = () => {
        setIsCreating(false);
        setEditingTrigger(null);
    }

    const handleCreate = () => {
        setEditingTrigger(null);
        setIsCreating(true);
    }

    const handleShowList = () => {        
        setIsCreating(false);
    }

    return (
        <div className="bg-black h-screen font-sans text-neutral-200 overflow-hidden">
            <div className="max-w-7xl mx-auto h-full flex flex-col">
                {isCreating ? (
                    <div className="py-4 sm:py-6 lg:py-8 h-full">
                        <TriggerEditor
                            key={editingTrigger ? editingTrigger.id : 'new'}
                            onSave={handleSave}
                            onCancel={handleCancel}
                            onBack={onBack}
                            initialTrigger={editingTrigger}
                            platformAccount={platformAccount}
                            onShowList={handleShowList}
                        />
                    </div>
                ) : (
                    <AutomationList
                        automationType="COMMENT_REPLY"
                        platformAccount={{
                            id: platformAccount.id,
                            platform_user_id: platformAccount.platform_user_id,
                            username: platformAccount.platform_username
                        }}
                        onBack={()=>{setIsCreating(true)}}
                        onEdit={handleEdit}
                    />
                )}
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

const TriggerEditor = ({ onSave,onBack, initialTrigger, platformAccount, onShowList }: any) => {
    const [activeTab, setActiveTab] = useState<'editor' | 'preview'>('editor');
    const [previewType, setPreviewType] = useState<'comment' | 'dm'>('comment');
    const getDefaultTrigger = (type = 'keyword') => {
        const baseTrigger: any = {
            triggerType: type,
            replyType: 'ai_decision',
            customMessage: '',
            name: '',
            postSelectionType: 'ALL',
            specificPostIds: [],
            aiContext: '',
            systemPrompt: "Write a one-line comment in a positive and friendly way.",
            modelProvider: 'GROQ',
            modelName: 'llama-3.3-70b-versatile',
            temperature: 0.7,
            isRagEnabled: false,
            confidenceThreshold: 0.75,
            description: '',
            modelUsage: 'PLATFORM_DEFAULT',
            maxActions: null,
            timePeriodSeconds: null,
            userCooldownSeconds: null,
            maxRepliesPerPost: null,
            replyCountCondition: 'LESS_THAN',
            replyCountValue: 1,
            dateRange: '1d',
        };
        if (type === 'keyword') {
            baseTrigger.keywords = [];
            baseTrigger.matchType = 'contains';
        } else {
            baseTrigger.keywords = [];
            baseTrigger.context = '';
            baseTrigger.matchType = 'contains';
        }
        return baseTrigger;
    };
    const [trigger, setTrigger] = useState(initialTrigger || getDefaultTrigger());
    const [keywordInput, setKeywordInput] = useState('');
    const [showPayloadModal, setShowPayloadModal] = useState<string | false>(false);
    const [alert, setAlert] = useState({ show: false, message: '' });
    const [showAiSettings, setShowAiSettings] = useState(false);
    const [showDescription, setShowDescription] = useState(!!initialTrigger?.description && initialTrigger.description !== 'No Desc');
    const [availablePosts, setAvailablePosts] = useState<any[]>([]);
    useEffect(() => {
        const fetchPosts = async () => {
            try {
                const response = await InstagramApiService.getInstagramPosts(platformAccount.platform_user_id);
                console.log("response : "+JSON.stringify(response))
                if (response?.success && response.data?.data && Array.isArray(response.data.data)) {
                    const mapped = response.data.data.map((p: any) => ({
                        id: p.id,
                        imageUrl: p.media_type === 'VIDEO' ? p.thumbnail_url : p.media_url,
                        caption: p.caption,
                        postUrl: p.permalink,
                        mediaType: p.media_type
                    }));
                    setAvailablePosts(mapped);
                }
            } catch (error) {
                console.error("Failed to fetch posts:", error);
            }
        };
        if (platformAccount?.platform_user_id) {
            fetchPosts();
        }
    }, [platformAccount?.platform_user_id]);
    const handleTriggerTypeChange = (newType: string) => {
        if (trigger.triggerType === newType) return;
        const newTrigger = getDefaultTrigger(newType);
        newTrigger.name = trigger.name;
        newTrigger.description = trigger.description;
        newTrigger.postSelectionType = trigger.postSelectionType;
        newTrigger.specificPostIds = trigger.specificPostIds;
        newTrigger.dateRange = trigger.dateRange;
        newTrigger.maxActions = trigger.maxActions;
        newTrigger.timePeriodSeconds = trigger.timePeriodSeconds;
        newTrigger.userCooldownSeconds = trigger.userCooldownSeconds;
        newTrigger.maxRepliesPerPost = trigger.maxRepliesPerPost;
        newTrigger.replyCountCondition = trigger.replyCountCondition;
        newTrigger.replyCountValue = trigger.replyCountValue;
        newTrigger.modelProvider = trigger.modelProvider;
        newTrigger.modelName = trigger.modelName;
        newTrigger.temperature = trigger.temperature;
        newTrigger.isRagEnabled = trigger.isRagEnabled;
        newTrigger.confidenceThreshold = trigger.confidenceThreshold;
        newTrigger.modelUsage = trigger.modelUsage;
        newTrigger.replyType = trigger.replyType;
        newTrigger.customMessage = trigger.customMessage;
        if (newType === 'ai') {
            newTrigger.context = trigger.keywords.length > 0 ? `Reply when a comment contains keywords like ${trigger.keywords.join(', ')}` : trigger.aiContext || '';
            newTrigger.keywords = [];
        } else {
            newTrigger.keywords = trigger.aiContext ? [trigger.aiContext.split(' ')[0]] : (trigger.keywords.length > 0 ? trigger.keywords : []);
            newTrigger.context = '';
        }
        newTrigger.aiContext = trigger.aiContext;
        newTrigger.systemPrompt = trigger.systemPrompt;
        setTrigger(newTrigger);
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
    const handleToggleSpecificPost = (postId: string) => {
        setTrigger((prev: any) => {
            const currentIds = prev.specificPostIds || [];
            if (currentIds.includes(postId)) {
                return { ...prev, specificPostIds: currentIds.filter((id: string) => id !== postId) };
            } else {
                return { ...prev, specificPostIds: [...currentIds, postId] };
            }
        });
    };
    const handleDeploy = async () => {
        if(trigger.name.trim() === '') {
            setAlert({ show: true, message: "Automation Name cannot be empty." });
            return;
        }
        if(trigger.triggerType === 'keyword' && (!trigger.keywords || trigger.keywords.length === 0)) {
            setAlert({ show: true, message: "Please add at least one keyword for a Regular trigger." });
            return;
        }
        if(trigger.triggerType === 'ai' && !trigger.context) {
            setAlert({ show: true, message: "Please provide a context for the AI." });
            return;
        }
        if (trigger.postSelectionType === 'SPECIFIC' && (!trigger.specificPostIds || trigger.specificPostIds.length === 0)) {
            setAlert({ show: true, message: "Please select at least one specific post or choose 'All Posts'." });
            return;
        }
        if (trigger.postSelectionType === 'DATE_RANGE' && !trigger.dateRange) {
            setAlert({ show: true, message: "Please select a date range for filtering." });
            return;
        }
        if (trigger.maxRepliesPerPost !== null && trigger.maxRepliesPerPost < 0) {
            setAlert({ show: true, message: "Max Replies per Post cannot be negative." });
            return;
        }
        if (trigger.replyCountValue < 0) {
            setAlert({ show: true, message: "Reply Count Value cannot be negative." });
            return;
        }
        if (trigger.replyType === 'custom' && trigger.customMessage.trim() === '') {
            setAlert({ show: true, message: "Please provide a custom message for a static reply." });
            return;
        }
        let keywordsToSend: string[] | null;
        let aiContextRulesToSend: string | null;
        if (trigger.triggerType === 'keyword') {
            keywordsToSend = trigger.keywords.length > 0 ? trigger.keywords : null;
            aiContextRulesToSend = null;
        } else {
            keywordsToSend = null;
            aiContextRulesToSend = trigger.context;
        }
        const payload:CommentReplyPayload = {
            automation_id: initialTrigger?.id ?? null,
            name: trigger.name,
            platform: "instagram",
            description: trigger.description || 'No Desc',
            platform_user_id: platformAccount.platform_user_id,
            provider_id: platformAccount.provider_id,
            trigger_type: trigger.triggerType === 'keyword' ? 'KEYWORD' : 'AI_DECISION',
            reply_type: trigger.replyType.toUpperCase(),
            custom_message: trigger.replyType === 'custom' ? trigger.customMessage : null,
            keywords: keywordsToSend ? keywordsToSend.join(',') : null,
            match_type: (trigger.matchType?.toUpperCase()) || 'CONTAINS',
            post_selection_type: trigger.postSelectionType || 'ALL',
            specific_post_ids: trigger.specificPostIds || [],
            dateRange: trigger.dateRange,
            ai_context_rules: aiContextRulesToSend,
            system_prompt: trigger.systemPrompt || '',
            comment_reply_template_type: 'PLAIN_TEXT',
            max_replies_per_post: trigger.maxRepliesPerPost !== null ? parseInt(trigger.maxRepliesPerPost) : null,
            reply_count_condition: trigger.replyCountCondition || 'LESS_THAN',
            reply_count_value: parseInt(trigger.replyCountValue),
            model_provider: trigger.modelProvider || 'GROQ',
            model_name: trigger.modelName || 'llama-3.3-70b-versatile',
            temperature: parseFloat(trigger.temperature) || 0.7,
            is_rag_enabled: trigger.isRagEnabled || false,
            confidence_threshold: parseFloat(trigger.confidenceThreshold) || 0.75,
            model_usage: trigger.modelUsage || 'PLATFORM_DEFAULT',
            max_actions: trigger.maxActions !== null ? parseInt(trigger.maxActions) : null,
            time_period_seconds: trigger.timePeriodSeconds !== null ? parseInt(trigger.timePeriodSeconds) : null,
            user_cooldown_seconds: trigger.userCooldownSeconds !== null ? parseInt(trigger.userCooldownSeconds) : null,
        };
        try {
            const response = await AutomationApiService.createOrUpdateCommentReply(payload);
            if (!response.success) {
                throw new Error(response.message);
            }
            setShowPayloadModal(JSON.stringify(payload, null, 2));
            onSave(trigger);
        } catch (error: any) {
            setAlert({ show: true, message: `Failed to deploy trigger: ${error.message}` });
        }
    }
    const selectedPost = trigger.postSelectionType === 'SPECIFIC' && trigger.specificPostIds.length > 0
        ? availablePosts.find((p: any) => p.id === trigger.specificPostIds[0])
        : null;
    return (
        <>
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
                                <button onClick={() => onBack()} className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors">
                                    <ArrowLeft size={18} />
                                    <span className="text-xs sm:text-sm font-medium">Back</span>
                                </button>
                                <h2 className="text-lg sm:text-xl font-bold text-white">{trigger.id ? 'Edit Automation' : 'Create New Comment Reply Automation'}</h2>
                            </div>
                        </div>
                        <NameInput name={trigger.name} setName={(value: string) => setTrigger({ ...trigger, name: value })} />
                        <div className="bg-neutral-900 border border-neutral-800 rounded-lg overflow-hidden">
                            <button
                                className="w-full flex justify-between items-center p-3 text-left font-semibold text-white hover:bg-neutral-800 transition-colors text-sm"
                                onClick={() => setShowDescription(!showDescription)}
                            >
                                Description (Optional)
                                {showDescription ? <ChevronUp size={16} className="text-neutral-400" /> : <ChevronDown size={16} className="text-neutral-400" />}
                            </button>
                            {showDescription && (
                                <div className="p-3 border-t border-neutral-800">
                                    <AutomationDescription
                                        description={trigger.description}
                                        setDescription={(value: string) => setTrigger({ ...trigger, description: value })}
                                    />
                                </div>
                            )}
                        </div>
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
                        <div>
                            <label className="block text-sm font-medium text-neutral-400 mb-2">Reply Method</label>
                            <div className="flex items-center gap-2 bg-neutral-800 p-0.5 rounded-lg">
                                <button
                                    onClick={() => setTrigger({ ...trigger, replyType: 'ai_decision' })}
                                    className={`flex-1 flex items-center justify-center gap-2 px-3 py-1.5 rounded-md text-sm font-semibold transition-colors ${trigger.replyType === 'ai_decision' ? 'bg-blue-500 text-white' : 'text-neutral-300 hover:bg-neutral-700'}`}
                                >
                                    <BrainCircuit size={16}/> AI Generated
                                </button>
                                <button
                                    onClick={() => setTrigger({ ...trigger, replyType: 'custom' })}
                                    className={`flex-1 flex items-center justify-center gap-2 px-3 py-1.5 rounded-md text-sm font-semibold transition-colors ${trigger.replyType === 'custom' ? 'bg-green-500 text-white' : 'text-neutral-300 hover:bg-neutral-700'}`}
                                >
                                    <Sparkles size={16}/> Static Custom Message
                                </button>
                            </div>
                        </div>
                        {trigger.replyType === 'custom' ? (
                            <div>
                                <label className="block text-sm font-medium text-neutral-400 mb-2">Custom Message <span className="text-red-400">*</span></label>
                                <textarea
                                    value={trigger.customMessage}
                                    onChange={(e) => setTrigger({ ...trigger, customMessage: e.target.value })}
                                    placeholder="Type your static reply here..."
                                    className="w-full h-24 bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 transition-all"
                                />
                            </div>
                        ) : (
                            <div>
                                <label className="block text-sm font-medium text-neutral-400 mb-2">System Prompt <Info size={14} className="inline-block text-neutral-500 ml-1" title="Provide a system prompt to guide the AI's response generation."/></label>
                                <textarea
                                    value={trigger.systemPrompt}
                                    onChange={(e) => setTrigger({ ...trigger, systemPrompt: e.target.value })}
                                    placeholder="e.g., 'You are a friendly social media assistant that provides helpful information.'"
                                    className="w-full h-24 bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                />
                            </div>
                        )}
                        {/* <AutomationPerformanceParameters
                            maxActions={trigger.maxActions}
                            setMaxActions={(value: number | null) => setTrigger({ ...trigger, maxActions: value })}
                            timePeriodSeconds={trigger.timePeriodSeconds}
                            setTimePeriodSeconds={(value: number | null) => setTrigger({ ...trigger, timePeriodSeconds: value })}
                            isRagEnabled={trigger.isRagEnabled}
                            setIsRagEnabled={(value: boolean) => setTrigger({ ...trigger, isRagEnabled: value })}
                        /> */}
                        <PostSelectionInput
                            postSelectionType={trigger.postSelectionType}
                            setPostSelectionType={(value: string) => setTrigger({ ...trigger, postSelectionType: value })}
                            specificPostIds={trigger.specificPostIds}
                            handleToggleSpecificPost={handleToggleSpecificPost}
                            dateRange={trigger.dateRange}
                            setDateRange={(value: string) => setTrigger({ ...trigger, dateRange: value })}
                            availablePosts={availablePosts}
                        />
                        <div className="space-y-4 bg-neutral-900 border border-neutral-800 rounded-lg p-3">
                            <h3 className="text-sm font-semibold text-white">Comment Reply Settings</h3>
                            <CommentReplySettings
                                maxRepliesPerPost={trigger.maxRepliesPerPost}
                                setMaxRepliesPerPost={(value: number | null) => setTrigger({ ...trigger, maxRepliesPerPost: value })}
                                replyCountCondition={trigger.replyCountCondition}
                                setReplyCountCondition={(value: string) => setTrigger({ ...trigger, replyCountCondition: value })}
                                replyCountValue={trigger.replyCountValue}
                                setReplyCountValue={(value: number) => setTrigger({ ...trigger, replyCountValue: value })}
                            />
                        </div>
                        <div className="bg-neutral-900 border border-neutral-800 rounded-lg overflow-hidden">
                            <button
                                className="w-full flex justify-between items-center p-3 text-left font-semibold text-white hover:bg-neutral-800 transition-colors text-sm"
                                onClick={() => setShowAiSettings(!showAiSettings)}
                            >
                                AI Settings (Developer Friendly)
                                {showAiSettings ? <ChevronUp size={16} className="text-neutral-400" /> : <ChevronDown size={16} className="text-neutral-400" />}
                            </button>
                            {showAiSettings && (
                                <div className="p-3 border-t border-neutral-800 space-y-4">
                                    <AISettings
                                        modelProvider={trigger.modelProvider}
                                        setModelProvider={(value: string) => setTrigger({ ...trigger, modelProvider: value })}
                                        modelName={trigger.modelName}
                                        setModelName={(value: string) => setTrigger({ ...trigger, modelName: value })}
                                        temperature={trigger.temperature}
                                        setTemperature={(value: number) => setTrigger({ ...trigger, temperature: value })}
                                        confidenceThreshold={trigger.confidenceThreshold}
                                        setConfidenceThreshold={(value: number) => setTrigger({ ...trigger, confidenceThreshold: value })}
                                        userCooldownSeconds={trigger.userCooldownSeconds}
                                        setUserCooldownSeconds={(value: number | null) => setTrigger({ ...trigger, userCooldownSeconds: value })}
                                        modelUsage={trigger.modelUsage}
                                        setModelUsage={(value: string) => setTrigger({ ...trigger, modelUsage: value })}
                                    />
                                </div>
                            )}
                        </div>
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
                        <InstagramPreview type={previewType} trigger={trigger} platformAccount={platformAccount} selectedPost={selectedPost} />
                    </div>
                </div>
            </div>
        </>
    );
};
const NameInput = ({ name, setName }: { name: string, setName: (name: string) => void }) => (
    <div>
        <label className="block text-sm font-medium text-neutral-400 mb-2">Comment Reply Automation Name</label>
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
const PostSelectionInput = ({
    postSelectionType,
    setPostSelectionType,
    specificPostIds,
    handleToggleSpecificPost,
    dateRange,
    setDateRange,
    availablePosts,
}: any) => (
    <div className="space-y-4">
        <label className="block text-sm font-medium text-neutral-400 mb-2">Post Selection</label>
        <div className="grid grid-cols-2 gap-1 bg-neutral-800 p-0.5 rounded-lg text-neutral-300 text-xs">
            <button onClick={() => setPostSelectionType('ALL')} className={`flex items-center justify-center gap-1 px-2 py-1.5 rounded-md font-semibold transition-colors ${postSelectionType === 'ALL' ? 'bg-blue-500 text-white' : 'hover:bg-neutral-700'}`}>
                All Posts
            </button>
            <button onClick={() => setPostSelectionType('SPECIFIC')} className={`flex items-center justify-center gap-1 px-2 py-1.5 rounded-md font-semibold transition-colors ${postSelectionType === 'SPECIFIC' ? 'bg-blue-500 text-white' : 'hover:bg-neutral-700'}`}>
                Specific Posts
            </button>
            {/* <button onClick={() => setPostSelectionType('DATE_RANGE')} className={`flex items-center justify-center gap-1 px-2 py-1.5 rounded-md font-semibold transition-colors ${postSelectionType === 'DATE_RANGE' ? 'bg-blue-500 text-white' : 'hover:bg-neutral-700'}`}>
                Date Range
            </button> */}
        </div>
        {postSelectionType === 'SPECIFIC' && (
            <div className="space-y-3 bg-neutral-900 border border-neutral-800 rounded-lg p-3 max-h-60 overflow-y-auto custom-scrollbar">
                <label className="block text-sm font-medium text-neutral-400 mb-2">Choose Posts</label>
                {availablePosts.length > 0 ? (
                    availablePosts.map((post: any) => (
                        <div
                            key={post.id}
                            className={`flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-colors ${
                                specificPostIds.includes(post.id) ? 'bg-teal-500/20 border border-teal-500' : 'bg-neutral-800 hover:bg-neutral-700 border border-neutral-700'
                            }`}
                            onClick={() => handleToggleSpecificPost(post.id)}
                        >
                            <input
                                type="checkbox"
                                checked={specificPostIds.includes(post.id)}
                                readOnly
                                className="form-checkbox h-4 w-4 text-teal-600 rounded"
                            />
                            <img src={post.imageUrl} alt="Post Thumbnail" className="w-12 h-12 rounded-md object-cover flex-shrink-0" />
                            <div className="flex-grow flex flex-col">
                                <p className="text-sm font-semibold text-white line-clamp-1">{post.caption || 'No Caption'}</p>
                                <a href={post.postUrl} target="_blank" rel="noopener noreferrer" className="text-blue-400 text-xs hover:underline flex items-center mt-1">
                                    View Post <LinkIcon size={12} className="ml-1" />
                                </a>
                            </div>
                        </div>
                    ))
                ) : (
                    <p className="text-neutral-500 text-sm text-center py-4">No posts available.</p>
                )}
            </div>
        )}
        {postSelectionType === 'DATE_RANGE' && (
            <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
                <label className="block text-sm font-medium text-neutral-400 mb-2">Date Range</label>
                <select
                    value={dateRange}
                    onChange={(e) => setDateRange(e.target.value)}
                    className="w-full bg-neutral-800 border border-neutral-700 text-white p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                >
                    <option value="1d">Last 1 Day</option>
                    <option value="2d">Last 2 Days</option>
                    <option value="1w">Last 1 Week</option>
                    <option value="2w">Last 2 Weeks</option>
                    <option value="1m">Last 1 Month</option>
                    <option value="1y">Last 1 Year</option>
                </select>
            </div>
        )}
    </div>
);
const MatchTypeSelector = ({ matchType, setMatchType }: { matchType: string, setMatchType: (type: string) => void }) => {
    const options = [{ id: 'contains', label: 'Contains' }, { id: 'exact', label: 'Exact Match' }, { id: 'startsWith', label: 'Starts With' }];
    return (
        <div>
            <label className="block text-sm font-medium text-neutral-400 mb-2">2. Keyword Match Type</label>
            <div className="grid grid-cols-3 gap-2">
                {options.map(opt => (<button key={opt.id} onClick={() => setMatchType(opt.id)} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${matchType === opt.id ? 'bg-blue-500 text-white shadow-lg' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-300'}`}>{opt.label}</button>))}
            </div>
        </div>
    );
};
const CommentReplySettings = ({
    maxRepliesPerPost,
    setMaxRepliesPerPost,
    replyCountCondition,
    setReplyCountCondition,
    replyCountValue,
    setReplyCountValue,
}: any) => (
    <div className="space-y-4">
        <div>
            <label className="block text-sm font-medium text-neutral-400 mb-2">Max Replies per Post <Info size={14} className="inline-block text-neutral-500 ml-1" title="Maximum number of times this automation should reply to comments on a single post. Leave blank for unlimited."/></label>
            <input
                type="number"
                value={maxRepliesPerPost === null ? '' : maxRepliesPerPost}
                onChange={(e) => setMaxRepliesPerPost(e.target.value === '' ? null : parseInt(e.target.value))}
                placeholder="Unlimited"
                className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
        </div>
        {/* <div>
            <label className="block text-sm font-medium text-neutral-400 mb-2">Reply Count Condition <Info size={14} className="inline-block text-neutral-500 ml-1" title="Condition for triggering reply based on existing reply count."/></label>
            <select
                value={replyCountCondition}
                onChange={(e) => setReplyCountCondition(e.target.value)}
                className="w-full bg-neutral-800 border border-neutral-700 text-white p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
                <option value="EQUALS">Equals</option>
                <option value="LESS_THAN">Less Than</option>
                <option value="GREATER_THAN">Greater Than</option>
            </select>
        </div>
        <div>
            <label className="block text-sm font-medium text-neutral-400 mb-2">Reply Count Value <Info size={14} className="inline-block text-neutral-500 ml-1" title="The value to compare against for the reply count condition."/></label>
            <input
                type="number"
                value={replyCountValue}
                onChange={(e) => setReplyCountValue(parseInt(e.target.value))}
                placeholder="1"
                min="0"
                className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
        </div> */}
    </div>
);
const AISettings = ({
    modelProvider,
    setModelProvider,
    modelName,
    setModelName,
    temperature,
    setTemperature,
    confidenceThreshold,
    setConfidenceThreshold,
    userCooldownSeconds,
    setUserCooldownSeconds,
    modelUsage,
    setModelUsage,
}: any) => (
    <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
            <div>
                <label className="block text-sm font-medium text-neutral-400 mb-2">Model Provider</label>
                <select
                    value={modelProvider}
                    onChange={(e) => setModelProvider(e.target.value)}
                    className="w-full bg-neutral-800 border border-neutral-700 text-white p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    <option value="GROQ">GROQ</option>
                </select>
            </div>
            <div>
                <label className="block text-sm font-medium text-neutral-400 mb-2">Model Name</label>
                <select
                    value={modelName}
                    onChange={(e) => setModelName(e.target.value)}
                    className="w-full bg-neutral-800 border border-neutral-700 text-white p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    <option value="llama-3.3-70b-versatile">llama-3.3-70b-versatile</option>
                    <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
                </select>
            </div>
        </div>
        <div>
            <label className="block text-sm font-medium text-neutral-400 mb-2">Temperature: {temperature} <Info size={14} className="inline-block text-neutral-500 ml-1" title="Controls the randomness of the AI's output. Higher values mean more creative, lower values mean more deterministic."/></label>
            <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer range-lg"
            />
        </div>
        <div>
            <label className="block text-sm font-medium text-neutral-400 mb-2">Confidence Threshold: {confidenceThreshold} <Info size={14} className="inline-block text-neutral-500 ml-1" title="Minimum confidence level for AI to trigger this automation."/></label>
            <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
                className="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer range-lg"
            />
        </div>
        {/* <div>
            <label className="block text-sm font-medium text-neutral-400 mb-2">User Cooldown (seconds) <Info size={14} className="inline-block text-neutral-500 ml-1" title="Minimum time in seconds before this automation can trigger again for the same user."/></label>
            <input
                type="number"
                value={userCooldownSeconds === null ? '' : userCooldownSeconds}
                onChange={(e) => setUserCooldownSeconds(e.target.value === '' ? null : parseInt(e.target.value))}
                placeholder="e.g., 300"
                className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
        </div> */}
        {/* <div>
            <label className="block text-sm font-medium text-neutral-400 mb-2">Model Usage</label>
            <select
                value={modelUsage}
                onChange={(e) => setModelUsage(e.target.value)}
                className="w-full bg-neutral-800 border border-neutral-700 text-white p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
                <option value="PLATFORM_DEFAULT">Platform Default</option>
                <option value="CUSTOM">Custom</option>
            </select>
        </div> */}
    </div>
);
const AutomationPerformanceParameters = ({
    maxActions,
    setMaxActions,
    timePeriodSeconds,
    setTimePeriodSeconds,
    isRagEnabled,
    setIsRagEnabled,
}: any) => (
    <div className="space-y-4">
        <h3 className="text-sm font-medium text-neutral-400">Automation Performance Settings</h3>
        <div className="grid grid-cols-2 gap-4">
            <div>
                <label className="block text-sm font-medium text-neutral-400 mb-2">Max Actions <Info size={14} className="inline-block text-neutral-500 ml-1" title="Maximum times this automation should execute. Leave blank for unlimited."/></label>
                <input
                    type="number"
                    value={maxActions === null ? '' : maxActions}
                    onChange={(e) => setMaxActions(e.target.value === '' ? null : parseInt(e.target.value))}
                    placeholder="Unlimited"
                    className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-neutral-400 mb-2">Reply Interval (sec) <Info size={14} className="inline-block text-neutral-500 ml-1" title="Minimum time in seconds between replies to any user. Leave blank for random."/></label>
                <input
                    type="number"
                    value={timePeriodSeconds === null ? '' : timePeriodSeconds}
                    onChange={(e) => setTimePeriodSeconds(e.target.value === '' ? null : parseInt(e.target.value))}
                    placeholder="Random"
                    className="w-full bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
            </div>
        </div>
        <div className="flex items-center justify-between bg-neutral-800 p-3 rounded-lg">
            <label htmlFor="ai-contextual-reply-toggle" className="text-sm font-medium text-neutral-300 cursor-pointer flex items-center">
                <BrainCircuit size={16} className="inline-block text-purple-400 mr-2"/> Enable AI Contextual Reply
                <Info size={14} className="inline-block text-neutral-500 ml-1" title="This setting lets the AI answer based on the post. If a user comments related to your brand, the AI can analyze your post and reply contextually."/>
            </label>
            <input
                type="checkbox"
                id="ai-contextual-reply-toggle"
                checked={isRagEnabled}
                onChange={(e) => setIsRagEnabled(e.target.checked)}
                className="w-10 h-5 rounded-full text-teal-500 focus:ring-teal-500 transition-colors duration-200 ease-in-out"
            />
        </div>
    </div>
);