import React, { useState } from 'react';
import { Brain, FileText, Globe, Upload, X, Check, AlertCircle } from 'lucide-react';
import { InstagramApiService } from '../../../../api/instagram_api';
import { PlatformAccount } from '../../../../types/types';

interface TrainTabContentProps {
    platformAccount: PlatformAccount;
}

const TrainTabContent: React.FC<TrainTabContentProps> = ({ platformAccount }) => {
    const [activeView, setActiveView] = useState<'text' | 'website' | 'file'>('text');
    const [trainText, setTrainText] = useState('');
    const [websiteUrl, setWebsiteUrl] = useState('');
    const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
    const [isTraining, setIsTraining] = useState(false);
    const [trainSuccess, setTrainSuccess] = useState<string | null>(null);
    const [trainError, setTrainError] = useState<string | null>(null);

    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (!files) return;
        const pdfFiles = Array.from(files).filter(file => file.type === 'application/pdf');
        setUploadedFiles(prev => [...prev, ...pdfFiles]);
    };

    const removeFile = (index: number) => {
        setUploadedFiles(prev => prev.filter((_, i) => i !== index));
    };

    const isTrainButtonDisabled = () => {
        if (isTraining) return true;
        switch (activeView) {
            case 'text':
                return !trainText.trim();
            case 'website':
                return !websiteUrl.trim();
            case 'file':
                return uploadedFiles.length === 0;
            default:
                return true;
        }
    };

    const handleTrain = async () => {
        setTrainError(null);
        setTrainSuccess(null);
        if (isTrainButtonDisabled()) return;

        setIsTraining(true);
        try {
            let response;
            switch (activeView) {
                case 'text':
                    response = await InstagramApiService.uploadCustomTextData({
                        text: trainText,
                        provider_id: platformAccount.provider_id,
                        platform_user_id: platformAccount.platform_user_id,
                        platform: 'instagram',
                    });
                    if (!response.success) throw new Error(response.message);
                    setTrainSuccess('Custom text successfully added to knowledge base!');
                    setTrainText('');
                    break;
                
                case 'website':
                    response = await InstagramApiService.uploadWebsiteData({
                        website_url: websiteUrl,
                        provider_id: platformAccount.provider_id,
                        platform_user_id: platformAccount.platform_user_id,
                        platform: 'instagram',
                    });
                    if (!response.success) throw new Error(response.message);
                    setTrainSuccess('Website content successfully added to knowledge base!');
                    setWebsiteUrl('');
                    break;

                case 'file':
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

                    setTrainSuccess('PDF documents successfully added to knowledge base!');
                    setUploadedFiles([]);
                    break;
            }
        } catch (error: any) {
            setTrainError(error.message || 'Failed to process training data.');
        } finally {
            setIsTraining(false);
        }
    };

    const renderActiveViewContent = () => {
        switch (activeView) {
            case 'text':
                return (
                    <div className="p-6 bg-[#1a1a1a] border border-[#262626] rounded-xl animate-fade-in">
                        <div className="flex items-center gap-3 mb-4"><FileText className="w-5 h-5 text-[#fd1d1d]" /><h3 className="text-lg font-semibold text-white">Custom Training Text</h3></div>
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <label className="block text-sm font-medium text-[#8e8e8e]">Enter custom text content, FAQs, or product details.</label>
                                <span className={`text-xs ${trainText.length > 10000 ? 'text-red-400' : 'text-[#8e8e8e]'}`}>{trainText.length}/10,000</span>
                            </div>
                            <textarea 
                                value={trainText} 
                                onChange={(e) => { if (e.target.value.length <= 10000) setTrainText(e.target.value); }} 
                                placeholder="Enter any custom information you want the chatbot to know about..." 
                                rows={12} 
                                className="w-full px-4 py-3 bg-[#0a0a0a] border border-[#262626] rounded-lg text-white placeholder-[#8e8e8e] focus:outline-none focus:border-[#fd1d1d] transition-colors resize-none" 
                            />
                        </div>
                    </div>
                );
            case 'website':
                return (
                    <div className="p-6 bg-[#1a1a1a] border border-[#262626] rounded-xl animate-fade-in">
                        <div className="flex items-center gap-3 mb-4"><Globe className="w-5 h-5 text-[#fd1d1d]" /><h3 className="text-lg font-semibold text-white">Website URL</h3></div>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-[#8e8e8e] mb-2">Enter a website URL to scrape for knowledge base content.</label>
                                <input 
                                    type="url" 
                                    value={websiteUrl} 
                                    onChange={(e) => setWebsiteUrl(e.target.value)} 
                                    placeholder="https://example.com/about" 
                                    className="w-full px-4 py-3 bg-[#0a0a0a] border border-[#262626] rounded-lg text-white placeholder-[#8e8e8e] focus:outline-none focus:border-[#fd1d1d] transition-colors" 
                                />
                            </div>
                        </div>
                    </div>
                );
            case 'file':
                return (
                    <div className="p-6 bg-[#1a1a1a] border border-[#262626] rounded-xl animate-fade-in">
                        <div className="flex items-center gap-3 mb-4"><Upload className="w-5 h-5 text-[#fd1d1d]" /><h3 className="text-lg font-semibold text-white">Upload PDF Documents</h3></div>
                        <div className="space-y-4">
                            <div className="border-2 border-dashed border-[#262626] rounded-lg p-6 text-center hover:border-[#fd1d1d]/50 transition-colors">
                                <input type="file" accept=".pdf" multiple onChange={handleFileUpload} className="hidden" id="pdf-upload" />
                                <label htmlFor="pdf-upload" className="cursor-pointer flex flex-col items-center gap-2">
                                    <Upload className="w-8 h-8 text-[#8e8e8e]" />
                                    <span className="text-sm text-[#8e8e8e]">Click to upload PDF files or drag and drop</span>
                                    <span className="text-xs text-[#666]">Only .pdf files are accepted</span>
                                </label>
                            </div>
                            {uploadedFiles.length > 0 && (
                                <div className="space-y-2">
                                    <h4 className="text-sm font-medium text-white">Staged Files:</h4>
                                    {uploadedFiles.map((file, index) => (
                                        <div key={index} className="flex items-center justify-between p-3 bg-[#0a0a0a] rounded-lg">
                                            <div className="flex items-center gap-2 overflow-hidden">
                                                <FileText className="w-4 h-4 text-[#fd1d1d] flex-shrink-0" />
                                                <span className="text-sm text-white truncate" title={file.name}>{file.name}</span>
                                                <span className="text-xs text-[#8e8e8e] flex-shrink-0">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                                            </div>
                                            <button onClick={() => removeFile(index)} className="p-1 text-[#8e8e8e] hover:text-red-400 transition-colors"><X className="w-4 h-4" /></button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                );
            default:
                return null;
        }
    }

    const configOptions = [
        { id: 'text', label: 'Custom Text', icon: FileText },
        { id: 'website', label: 'Website URL', icon: Globe },
        { id: 'file', label: 'Upload File', icon: Upload },
    ];

    return (
        <div className="flex flex-col lg:flex-row gap-8 animate-fade-in">
            <aside className="lg:w-1/4 space-y-6">
                <div className="p-4 bg-[#1a1a1a] border border-[#262626] rounded-xl space-y-2">
                    <h3 className="font-semibold text-white px-2 mb-2">Data Source</h3>
                    {configOptions.map(item => (
                        <button 
                            key={item.id} 
                            onClick={() => setActiveView(item.id as 'text' | 'website' | 'file')} 
                            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200 ${activeView === item.id ? 'bg-[#fd1d1d] text-white' : 'text-[#8e8e8e] hover:bg-[#262626] hover:text-white'}`}
                        >
                            <item.icon className="w-4 h-4" /><span>{item.label}</span>
                        </button>
                    ))}
                </div>
            </aside>
            <main className="flex-1 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-4 bg-[#1a1a1a] border border-[#262626] rounded-xl">
                    <div>
                        <h3 className="font-semibold text-white">Provide Your Content</h3>
                        <p className="text-sm text-[#8e8e8e]">Select a data source and provide the content for training.</p>
                    </div>
                    <button 
                        onClick={handleTrain} 
                        disabled={isTrainButtonDisabled()} 
                        className="flex items-center justify-center gap-3 px-6 py-3 bg-gradient-to-r from-[#833ab4] to-[#fd1d1d] text-white rounded-lg font-semibold hover:opacity-90 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                    >
                        {isTraining ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                <span>Processing...</span>
                            </>
                        ) : (
                            <>
                                <Brain className="w-5 h-5" />
                                <span>Train Chatbot</span>
                            </>
                        )}
                    </button>
                </div>
                {trainSuccess && (
                    <div className="p-4 bg-green-500/20 border border-green-500/30 rounded-lg flex items-center gap-3 animate-fade-in">
                        <Check className="w-5 h-5 text-green-400" />
                        <span className="text-green-300">{trainSuccess}</span>
                    </div>
                )}
                {trainError && (
                    <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-lg flex items-center gap-3 animate-fade-in">
                        <AlertCircle className="w-5 h-5 text-red-400" />
                        <span className="text-red-300">{trainError}</span>
                    </div>
                )}
                
                {renderActiveViewContent()}
            </main>
        </div>
    );
};

export default TrainTabContent;