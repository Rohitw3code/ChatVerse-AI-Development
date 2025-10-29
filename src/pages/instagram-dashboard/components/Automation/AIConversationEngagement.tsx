import React, { useState } from 'react';
import { ArrowLeft, Bot, Upload, Link, AlignLeft, Settings, Check, AlertCircle, X } from 'lucide-react';
import { InstagramApiService } from '../../../../api/instagram_api';
import { PlatformAccount } from '../../../../types/types';
import { AutomationConfig, CreateAutomationConfigPayload } from '../../../../types/types';
import { AutomationApiService } from '../../../../api/automation';


interface AIConversationEngagementProps {
  onBack: () => void;
  platformAccount: PlatformAccount;
}


const AIConversationEngagement: React.FC<AIConversationEngagementProps> = ({ onBack, platformAccount }) => {
  const [currentTab, setCurrentTab] = useState('pdf');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [customText, setCustomText] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [showSettings, setShowSettings] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState('You are a friendly, human-like AI chatbot. Always respond with short, positive, and natural replies, just like a real person texting. Keep it casual, warm, and supportive. Never include code, markdown, or formatting just plain text. Use normal human language. Be encouraging, polite, and clear.');
  const [temperature, setTemperature] = useState(0.7);
  const [provider, setProvider] = useState('openai');
  const [modelName, setModelName] = useState('gpt-4o');
  const [isProcessing, setIsProcessing] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;
    const pdfFiles = Array.from(files).filter(file => file.type === 'application/pdf');
    setUploadedFiles(prev => [...prev, ...pdfFiles]);
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const isProcessButtonDisabled = () => {
    if (isProcessing) return true;
    switch (currentTab) {
      case 'pdf':
        return uploadedFiles.length === 0;
      case 'url':
        return !websiteUrl.trim();
      case 'text':
        return !customText.trim();
      default:
        return true;
    }
  };

  const handleProcess = async () => {
    setStatusMessage(null);
    setIsProcessing(true);
    try {
      let response;
      switch (currentTab) {
        case 'pdf':
          const uploadPromises = uploadedFiles.map(file =>
            InstagramApiService.uploadFile({
              file,
              platform: 'instagram',
              platform_user_id: platformAccount.platform_user_id,
              provider_id: platformAccount.provider_id,
            })
          );
          const responses = await Promise.all(uploadPromises);
          const failedUpload = responses.find(res => !res.success);
          if (failedUpload) throw new Error(failedUpload.message || 'One or more files failed to upload.');
          setStatusMessage({ type: 'success', message: 'PDF documents successfully added to knowledge base!' });
          setUploadedFiles([]);
          break;
        case 'url':
          response = await InstagramApiService.uploadWebsiteData({
            website_url: websiteUrl,
            provider_id: platformAccount.provider_id,
            platform_user_id: platformAccount.platform_user_id,
            platform: 'instagram',
          });
          if (!response.success) throw new Error(response.message);
          setStatusMessage({ type: 'success', message: 'Website content successfully added to knowledge base!' });
          setWebsiteUrl('');
          break;
        case 'text':
          response = await InstagramApiService.uploadCustomTextData({
            text: customText,
            provider_id: platformAccount.provider_id,
            platform_user_id: platformAccount.platform_user_id,
            platform: 'instagram',
          });
          if (!response.success) throw new Error(response.message);
          setStatusMessage({ type: 'success', message: 'Custom text successfully added to knowledge base!' });
          setCustomText('');
          break;
      }
    } catch (error: any) {
      setStatusMessage({ type: 'error', message: error.message || 'Failed to process training data.' });
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePublish = async () => {
    setStatusMessage(null);
    setIsProcessing(true);
    try {
      const payload: CreateAutomationConfigPayload = {
        connected_account_id: platformAccount.id,
        platform_user_id: platformAccount.platform_user_id,
        platform: 'instagram',
        provider_id: platformAccount.provider_id,
        bot_name: `${platformAccount.username}'s Bot`,
        system_prompt: systemPrompt,
        is_rag_enabled: true,
        is_active: true
      };
      const response = await AutomationApiService.createAutomationConfig(payload);
      if (!response.success) throw new Error(response.message || "Failed to publish the chatbot.");
      setStatusMessage({ type: 'success', message: "Your chatbot has been successfully published!" });
    } catch (err: any) {
      setStatusMessage({ type: 'error', message: err.message || "An unexpected error occurred." });
    } finally {
      setIsProcessing(false);
    }
  };

  const renderTabContent = () => {
    switch (currentTab) {
      case 'pdf':
        return (
          <div className="space-y-4">
            <p className="text-neutral-400 text-sm">
              The AI bot will use the knowledge from this PDF to answer client questions.
            </p>
            <div className="border-2 border-dashed border-red-500 rounded-lg p-6 text-center hover:border-red-500/50 transition-colors">
              <input type="file" accept=".pdf" multiple onChange={handleFileUpload} className="hidden" id="pdf-upload" />
              <label htmlFor="pdf-upload" className="cursor-pointer flex flex-col items-center gap-2">
                <Upload className="w-8 h-8 text-red-500" />
                <span className="text-sm text-neutral-400">Click to upload PDF files or drag and drop</span>
                <span className="text-xs text-neutral-500">Only .pdf files are accepted</span>
              </label>
            </div>
            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-white">Staged Files:</h4>
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-neutral-800 rounded-lg">
                    <div className="flex items-center gap-2 overflow-hidden">
                      <Upload className="w-4 h-4 text-red-500 flex-shrink-0" />
                      <span className="text-sm text-white truncate" title={file.name}>{file.name}</span>
                      <span className="text-xs text-neutral-500 flex-shrink-0">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                    </div>
                    <button onClick={() => removeFile(index)} className="p-1 text-neutral-400 hover:text-red-400 transition-colors">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      case 'url':
        return (
          <div className="space-y-4">
            <p className="text-neutral-400 text-sm">
              The website crawler will use this URL to gather data and answer client questions based on that information alone.
            </p>
            <input
              type="url"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              placeholder="https://example.com"
              className="w-full p-3 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-red-500"
            />
          </div>
        );
      case 'text':
        return (
          <div className="space-y-4">
            <p className="text-neutral-400 text-sm">
              Provide custom text data for the AI bot to use as its knowledge base.
            </p>
            <textarea
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
              placeholder="Enter your custom text here..."
              rows={6}
              className="w-full p-3 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 resize-none focus:outline-none focus:ring-2 focus:ring-red-500"
            ></textarea>
          </div>
        );
      default:
        return null;
    }
  };

  const renderProviderOptions = () => {
    switch (provider) {
      case 'openai':
        return (
          <select
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            className="w-full p-3 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            <option value="gpt-4o">GPT-4o</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
          </select>
        );
      case 'groq':
        return (
          <select
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            className="w-full p-3 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            <option value="llama3-8b-8192">Llama3 8b</option>
            <option value="llama3-70b-8192">Llama3 70b</option>
            <option value="mixtral-8x7b-32768">Mixtral</option>
          </select>
        );
      case 'gemini':
        return (
          <select
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            className="w-full p-3 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            <option value="gemini-pro">Gemini Pro</option>
            <option value="gemini-1.5-flash-latest">Gemini 1.5 Flash</option>
            <option value="gemini-1.5-pro-latest">Gemini 1.5 Pro</option>
          </select>
        );
      default:
        return null;
    }
  };

  const gradientButton = "w-full p-3 rounded-xl font-semibold text-white bg-gradient-to-r from-purple-600 to-red-500 transition-all hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-black";
  const textButton = "w-full p-3 rounded-xl font-semibold text-neutral-400 bg-neutral-800 hover:bg-neutral-700 transition-colors focus:outline-none focus:ring-2 focus:ring-neutral-600 focus:ring-offset-2 focus:ring-offset-black";

  return (
    <div className="min-h-screen bg-black text-white p-2 sm:p-4 lg:p-6 font-sans">
      <div className="max-w-3xl mx-auto space-y-4">
        <div className="flex items-center gap-4">
          <button onClick={onBack} className="p-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-neutral-600">
            <ArrowLeft className="w-5 h-5 text-white" />
          </button>
          <div>
            <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">AI Conversation Engagement</h2>
            <p className="text-neutral-500 mt-1 text-sm sm:text-base">Intelligent AI-powered conversations with your audience</p>
          </div>
        </div>

        <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-4 sm:p-6">
          {statusMessage && (
            <div className={`p-3 mb-4 rounded-lg flex items-center gap-3 text-sm ${statusMessage.type === 'success' ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
              {statusMessage.type === 'success' ? <Check className="w-4 h-4 text-green-400" /> : <AlertCircle className="w-4 h-4 text-red-400" />}
              <span className={statusMessage.type === 'success' ? 'text-green-300' : 'text-red-300'}>{statusMessage.message}</span>
            </div>
          )}

          {!showSettings ? (
            <>
              <div className="flex justify-between gap-2 sm:gap-4 mb-4">
                <button
                  onClick={() => setCurrentTab('pdf')}
                  className={`flex-1 flex flex-col items-center p-4 rounded-xl transition-colors ${
                    currentTab === 'pdf' ? 'bg-neutral-800 text-white' : 'bg-neutral-900 text-neutral-400 hover:bg-neutral-800'
                  }`}
                >
                  <Upload className="w-6 h-6 mb-1 text-red-500" />
                  <span className="text-xs sm:text-sm font-semibold">Upload PDF</span>
                </button>
                <button
                  onClick={() => setCurrentTab('url')}
                  className={`flex-1 flex flex-col items-center p-4 rounded-xl transition-colors ${
                    currentTab === 'url' ? 'bg-neutral-800 text-white' : 'bg-neutral-900 text-neutral-400 hover:bg-neutral-800'
                  }`}
                >
                  <Link className="w-6 h-6 mb-1 text-red-500" />
                  <span className="text-xs sm:text-sm font-semibold">Website URL</span>
                </button>
                <button
                  onClick={() => setCurrentTab('text')}
                  className={`flex-1 flex flex-col items-center p-4 rounded-xl transition-colors ${
                    currentTab === 'text' ? 'bg-neutral-800 text-white' : 'bg-neutral-900 text-neutral-400 hover:bg-neutral-800'
                  }`}
                >
                  <AlignLeft className="w-6 h-6 mb-1 text-red-500" />
                  <span className="text-xs sm:text-sm font-semibold">Custom Text</span>
                </button>
              </div>

              {renderTabContent()}

              <div className="flex gap-4 mt-4">
                <button
                  onClick={handleProcess}
                  disabled={isProcessButtonDisabled()}
                  className={`${gradientButton} disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {isProcessing ? (
                    <div className="flex items-center justify-center gap-3">
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Processing...</span>
                    </div>
                  ) : (
                    "Upload and Process"
                  )}
                </button>
                <button onClick={() => setShowSettings(true)} className={textButton}>
                  Skip
                </button>
              </div>
            </>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Settings className="w-6 h-6 text-red-500" />
                <h3 className="text-xl sm:text-2xl font-bold">Advanced Settings</h3>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1 text-neutral-400">System Prompt</label>
                <textarea
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  placeholder="Define the bot's persona and instructions..."
                  rows={4}
                  className="w-full p-3 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 resize-none focus:outline-none focus:ring-2 focus:ring-red-500"
                ></textarea>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-neutral-400">Provider</label>
                  <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    className="w-full p-3 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500"
                  >
                    <option value="openai">OpenAI</option>
                    <option value="groq">Groq</option>
                    <option value="gemini">Gemini</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-neutral-400">Model Name</label>
                  {renderProviderOptions()}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1 text-neutral-400">Temperature: {temperature}</label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <button onClick={handlePublish} disabled={isProcessing} className={`${gradientButton} disabled:opacity-50 disabled:cursor-not-allowed`}>
                {isProcessing ? (
                  <div className="flex items-center justify-center gap-3">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Saving...</span>
                  </div>
                ) : (
                  "Save & Publish"
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIConversationEngagement;
