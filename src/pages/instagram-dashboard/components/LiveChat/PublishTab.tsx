import React, { useState, useEffect } from 'react';
import { AlertCircle, Check, Edit3 } from 'lucide-react';
import { AutomationConfig, PlatformAccount, CreateAutomationConfigPayload } from '../../../../types/types';
import { AutomationApiService } from '../../../../api/automation';

interface PublishTabProps {
  platformAccount: PlatformAccount;
}

const PublishTab: React.FC<PublishTabProps> = ({ platformAccount }) => {
  const [AutomationConfig, setAutomationConfig] = useState<AutomationConfig | null>(null);
  const [botName, setBotName] = useState(`${platformAccount.platform_username}'s Bot`);
  const [systemPrompt, setSystemPrompt] = useState(`You are a friendly, human-like AI chatbot. Always respond with short, positive, and natural replies, just like a real person texting. Keep it casual, warm, and supportive. Never include code, markdown, or formatting just plain text. Use normal human language. Be encouraging, polite, and clear.`);
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishStatus, setPublishStatus] = useState<{ success: boolean; message: string } | null>(null);
  const [editingAutomationConfig, setEditingAutomationConfig] = useState(false);
  const [isRagUpdating, setIsRagUpdating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAutomationConfig = async () => {
        if (!platformAccount?.id) return;
        setIsLoading(true);
        try {
          const response = await AutomationApiService.getAutomationConfig(platformAccount.platform_user_id);
          if (response.success && response.data) {
            setAutomationConfig(response.data);
            setBotName(response.data.name);
            setSystemPrompt(response.data.system_prompt);
            setEditingAutomationConfig(false);
          } else {
            setEditingAutomationConfig(true);
          }
        } catch (error) {
          console.log("No existing bot config found, enabling creation form.");
          setEditingAutomationConfig(true);
        } finally {
            setIsLoading(false);
        }
    };
    fetchAutomationConfig();
  }, [platformAccount]);

  const handlePublish = async () => {
    setIsPublishing(true);
    setPublishStatus(null);
    try {
      const payload: CreateAutomationConfigPayload = {
        connected_account_id: platformAccount.id,
        platform_user_id: platformAccount.platform_user_id,
        platform: 'instagram',
        provider_id: platformAccount.provider_id,
        bot_name: botName,
        system_prompt: systemPrompt,
        is_rag_enabled: AutomationConfig?.is_rag_enabled || false,
        is_active: true
      };
      const response = await AutomationApiService.createAutomationConfig(payload);

      if (response.success && response.data) {
        setAutomationConfig(response.data);
        setPublishStatus({ success: true, message: "Your chatbot has been successfully published!" });
        setEditingAutomationConfig(false);
      } else {
        throw new Error(response.message || "Failed to publish the chatbot.");
      }
    } catch (err: any) {
      setPublishStatus({ success: false, message: err.message || "An unexpected error occurred." });
    } finally {
      setIsPublishing(false);
    }
  }

  const handleToggleRag = async () => {
    if (!AutomationConfig) return;

    setIsRagUpdating(true);
    setPublishStatus(null);
    try {
      const response = await AutomationApiService.updateRagStatus(platformAccount.platform_user_id, !AutomationConfig.is_rag_enabled);
      if (response.success && response.data) {
        setAutomationConfig(response.data);
        setPublishStatus({ success: true, message: `Knowledge Base (RAG) has been ${response.data.is_rag_enabled ? 'enabled' : 'disabled'}.` });
      } else {
        throw new Error(response.message || "Failed to update RAG status.");
      }
    } catch (err: any) {
      setPublishStatus({ success: false, message: err.message || "An error occurred while updating RAG status." });
    } finally {
      setIsRagUpdating(false);
    }
  }

  if (isLoading) {
    return <div className="p-6 text-center text-gray-400">Loading Configuration...</div>;
  }

  return (
    <div className="animate-fade-in">
      <div className="p-6 bg-[#1a1a1a] border border-[#262626] rounded-xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Publish Your Chatbot</h3>
            <p className="text-[#8e8e8e] mt-1 text-sm">Make your chatbot live and manage its settings.</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${AutomationConfig?.is_active ? 'bg-green-400' : 'bg-gray-400'} opacity-75`}></span>
                <span className={`relative inline-flex rounded-full h-3 w-3 ${AutomationConfig?.is_active ? 'bg-green-500' : 'bg-gray-500'}`}></span>
              </span>
              <span className={`text-sm font-medium ${AutomationConfig?.is_active ? 'text-green-400' : 'text-gray-400'}`}>
                {AutomationConfig?.is_active ? 'Live' : 'Offline'}
              </span>
            </div>
            {!editingAutomationConfig && AutomationConfig && (
              <button
                onClick={() => setEditingAutomationConfig(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#262626] hover:bg-[#333] text-white rounded-lg transition-colors text-sm"
              >
                <Edit3 className="w-4 h-4" />
                Edit
              </button>
            )}
          </div>
        </div>

        {AutomationConfig && !editingAutomationConfig && (
          <div className="mt-6 p-4 border border-[#262626] rounded-lg bg-[#202020]">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-white">Knowledge Base (RAG)</h4>
                <p className="text-sm text-[#8e8e8e]">Allow the bot to use uploaded documents to answer questions.</p>
              </div>
              <div className="flex items-center gap-4">
                <span className={`text-sm font-medium ${AutomationConfig.is_rag_enabled ? 'text-green-400' : 'text-gray-400'}`}>
                  {AutomationConfig.is_rag_enabled ? 'Enabled' : 'Disabled'}
                </span>
                <button
                  role="switch"
                  aria-checked={AutomationConfig.is_rag_enabled}
                  onClick={handleToggleRag}
                  disabled={isRagUpdating}
                  className={`${AutomationConfig.is_rag_enabled ? 'bg-[#fd1d1d]' : 'bg-[#333]'} relative inline-flex h-6 w-11 items-center rounded-full transition-colors disabled:opacity-50`}
                >
                  <span className={`${AutomationConfig.is_rag_enabled ? 'translate-x-6' : 'translate-x-1'} inline-block h-4 w-4 transform rounded-full bg-white transition-transform`} />
                </button>
              </div>
            </div>
          </div>
        )}

        {(editingAutomationConfig || !AutomationConfig) && (
          <div className="mt-6 space-y-4">
            <div>
              <label htmlFor="botName" className="block text-sm font-medium text-gray-300 mb-2">Bot Name</label>
              <input
                type="text"
                id="botName"
                value={botName}
                onChange={(e) => setBotName(e.target.value)}
                className="w-full bg-[#262626] border border-[#333] rounded-lg p-2 text-white focus:ring-2 focus:ring-[#fd1d1d]"
              />
            </div>
            <div>
              <label htmlFor="systemPrompt" className="block text-sm font-medium text-gray-300 mb-2">System Prompt</label>
              <textarea
                id="systemPrompt"
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                rows={4}
                className="w-full bg-[#262626] border border-[#333] rounded-lg p-2 text-white focus:ring-2 focus:ring-[#fd1d1d]"
              />
            </div>
            <div className="flex justify-end gap-4">
              {AutomationConfig && <button
                onClick={() => { setEditingAutomationConfig(false); setPublishStatus(null); }}
                className="px-5 py-2 bg-transparent border border-[#333] hover:bg-[#262626] text-white rounded-lg text-sm font-medium transition-colors"
              >
                Cancel
              </button>}
              <button
                onClick={handlePublish}
                disabled={isPublishing}
                className="px-5 py-2 bg-[#fd1d1d] hover:bg-[#e51a1a] text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                {isPublishing ? 'Saving...' : 'Save & Publish'}
              </button>
            </div>
          </div>
        )}

        {publishStatus && (
          <div className={`p-3 mt-4 rounded-lg flex items-center gap-3 text-sm ${publishStatus.success ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
            {publishStatus.success ? <Check className="w-4 h-4 text-green-400" /> : <AlertCircle className="w-4 h-4 text-red-400" />}
            <span className={publishStatus.success ? 'text-green-300' : 'text-red-300'}>{publishStatus.message}</span>
          </div>
        )}
      </div>
    </div>
  )
};

export default PublishTab;