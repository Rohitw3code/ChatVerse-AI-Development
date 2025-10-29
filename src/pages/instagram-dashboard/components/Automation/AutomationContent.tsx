import React from 'react';
import AIConversationEngagement from './AIConversationEngagement';
import TriggerMessages from './TriggerMessages';
import ReplyOnComment from './ReplyOnComment';
import PrivateMessage from './PrivateMessage';
import CreateAutomationForm from './CreateAutomationForm';
import AllAutomationsDashboard from './AllAutomationsDashboard';

import { PlatformAccount } from '../../../../types/types';

interface AutomationContextProps {
  platformAccount: PlatformAccount;
}

const AutomationContent: React.FC<AutomationContextProps> = ({ platformAccount }) => {
  const [currentView, setCurrentView] = React.useState<string>('list');

  const handleSelectAutomationType = (type: string) => {
    setCurrentView(type);
  };

  const handleEditAutomation = (automation: any) => {
    // This will be handled by individual components
    console.log('Edit automation:', automation);
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'list':
        return <AllAutomationsDashboard platformAccount={{
          id: platformAccount.id,
          platform_user_id: platformAccount.platform_user_id,
          username: platformAccount.platform_username,
          profile_picture_url: undefined
        }} />;
      case 'create':
        return <CreateAutomationForm onBack={() => setCurrentView('list')} onSelectAutomationType={handleSelectAutomationType} platformAccount={{
          id: platformAccount.id,
          platform_user_id: platformAccount.platform_user_id,
          username: platformAccount.platform_username,
          profile_picture_url: undefined
        }} />;
      case 'ai-conversation':
        return (
          <div className="p-4 sm:p-6 lg:p-8 bg-[#000000] min-h-screen text-neutral-200 font-sans">
            <AIConversationEngagement platformAccount={platformAccount} onBack={() => setCurrentView('create')} />
          </div>
        );
      case 'trigger-messages':
        return (
          <div className="p-4 sm:p-6 lg:p-8 bg-[#000000] min-h-screen text-neutral-200 font-sans">
            <TriggerMessages onBack={() => setCurrentView('create')} platformAccount={platformAccount} />
          </div>
        );
      case 'reply-comment':
        return (
          <div className="p-4 sm:p-6 lg:p-8 bg-[#000000] min-h-screen text-neutral-200 font-sans">
            <ReplyOnComment platformAccount={platformAccount} onBack={() => setCurrentView('create')} />
          </div>
        );
      case 'private-message':
        return (
          <div className="p-4 sm:p-6 lg:p-8 bg-[#000000] min-h-screen text-neutral-200 font-sans">
            <PrivateMessage onBack={() => setCurrentView('create')} platformAccount={platformAccount} />
          </div>
        );
      default:
        const components: { [key: string]: React.FC<{ onBack: () => void; platformAccount: AutomationContextProps['platformAccount'] }> } = {
          'ai-conversation': AIConversationEngagement,
        };
        const Component = components[currentView];
        return Component ? (
          <div className="p-4 sm:p-6 lg:p-8 bg-[#000000] min-h-screen text-neutral-200 font-sans">
            <Component platformAccount={platformAccount} onBack={() => setCurrentView('create')} />
          </div>
        ) : (
          <div className="text-center text-red-500 p-8">
            <p className="text-lg">This automation type is not yet implemented.</p>
            <button
              onClick={() => setCurrentView('create')}
              className="mt-4 px-5 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
            >
              Go Back
            </button>
          </div>
        );
    }
  };

  return renderCurrentView();
};

export default AutomationContent;