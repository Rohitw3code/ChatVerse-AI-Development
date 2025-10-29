import React, { useState, useEffect } from 'react';
import { Plus, MessageCircle, Zap, Users, Clock, CheckCircle, XCircle, Grid, List, StopCircle, PlayCircle, Edit, Trash2, Lightbulb, Bot, Target, Reply, Image, BarChart3, ArrowLeft } from 'lucide-react';
import { AutomationApiService } from '../../../../api/automation';

interface AutomationListProps {
  automationType: string;
  platformAccount: {
    id: number;
    platform_user_id: string;
    username: string;
    profile_picture_url?: string;
  };
  onBack: () => void;
  onEdit?: (automation: Automation) => void;
}

interface Automation {
  automation_id: string;
  platform: string;
  platform_user_id: string;
  name: string;
  description: string;
  automation_type: string;
  activation_status: string;
  health_status: string;
  model_usage: string;
  cumulative_cost: number;
  execution_count: number | null;
  last_triggered_at: string | null;
  start_date: string | null;
  end_date: string | null;
  max_actions: number | null;
  time_period_seconds: number | null;
  user_cooldown_seconds: number | null;
  created_at: string;
  updated_at: string;
}

const getAutomationTypeDisplay = (type: string) => {
    switch (type) {
      case 'AI_DM_CONVERSATION':
        return { name: 'AI DM Conversation', icon: <Bot className="w-5 h-5 text-purple-400" /> };
      case 'DM_REPLY':
        return { name: 'DM Keyword Reply', icon: <Target className="w-5 h-5 text-sky-400" /> };
      case 'COMMENT_REPLY':
        return { name: 'Comment Reply', icon: <Reply className="w-5 h-5 text-amber-400" /> };
      case 'PRIVATE_MESSAGE':
        return { name: 'Private Message', icon: <Image className="w-5 h-5 text-pink-400" /> };
      default:
        return { name: type.replace(/_/g, ' '), icon: <Lightbulb className="w-5 h-5 text-neutral-400" /> };
    }
};

const StatusBadge = ({ status }: { status: string }) => {
    const isActive = status === 'ACTIVE';
    return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full ${isActive ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
            <span className={`h-1.5 w-1.5 rounded-full ${isActive ? 'bg-green-500' : 'bg-red-500'}`}></span>
            {status}
        </span>
    );
};

const HealthStatus = ({ status }: { status: string }) => {
    const isHealthy = status === 'HEALTHY';
    return (
        <span className="inline-flex items-center gap-1.5">
            {isHealthy ? <CheckCircle className="w-4 h-4 text-green-500" /> : <XCircle className="w-4 h-4 text-red-500" />}
            <span className="text-white font-medium">{status}</span>
        </span>
    );
};

const ActionButtons = ({ automation, onStop, onReactivate, onEdit, onDelete }: any) => (
    <div className="flex items-center justify-end gap-2">
        {automation.activation_status === 'ACTIVE' ? (
            <button onClick={onStop} className="p-2 text-neutral-400 hover:text-yellow-400 hover:bg-neutral-800 rounded-md transition-colors" title="Stop Automation"><StopCircle className="w-4 h-4" /></button>
        ) : (
            <button onClick={onReactivate} className="p-2 text-neutral-400 hover:text-green-400 hover:bg-neutral-800 rounded-md transition-colors" title="Reactivate Automation"><PlayCircle className="w-4 h-4" /></button>
        )}
        <button onClick={onEdit} className="p-2 text-neutral-400 hover:text-sky-400 hover:bg-neutral-800 rounded-md transition-colors" title="Edit"><Edit className="w-4 h-4" /></button>
        <button onClick={onDelete} className="p-2 text-neutral-400 hover:text-red-400 hover:bg-neutral-800 rounded-md transition-colors" title="Delete"><Trash2 className="w-4 h-4" /></button>
    </div>
);

const AutomationGridItem = ({ automation, onStop, onReactivate, onEdit, onDelete }: any) => {
    const { icon, name: typeName } = getAutomationTypeDisplay(automation.automation_type);
    return (
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl shadow-lg transition-all duration-300 hover:border-sky-500/30 hover:-translate-y-1 flex flex-col overflow-hidden">
            <div className="p-4 border-b border-neutral-800">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-neutral-800 rounded-md">{icon}</div>
                        <h3 className="font-semibold text-white truncate">{automation.name}</h3>
                    </div>
                    <StatusBadge status={automation.activation_status} />
                </div>
                <p className="text-sm text-neutral-400 mt-3 h-10 line-clamp-2">{automation.description !== "No Desc" ? automation.description : "No description provided."}</p>
            </div>
            <div className="p-4 flex-grow grid grid-cols-2 gap-4 text-sm text-neutral-400">
                <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4"/>Health: <span className="text-white font-medium">{automation.health_status}</span></div>
                <div className="flex items-center gap-2"><Zap className="w-4 h-4"/>Executions: <span className="text-white font-medium">{automation.execution_count ?? 0}</span></div>
                <div className="flex items-center gap-2"><Clock className="w-4 h-4"/>Created: <span className="text-white font-medium">{new Date(automation.created_at).toLocaleDateString()}</span></div>
                <div className="flex items-center gap-2"><span className="text-green-400 font-bold text-base leading-none">$</span>Cost: <span className="text-white font-medium">{automation.cumulative_cost.toFixed(2)}</span></div>
            </div>
            <div className="p-2 border-t border-neutral-800 bg-neutral-950/50 flex items-center justify-end">
                <ActionButtons automation={automation} onStop={onStop} onReactivate={onReactivate} onEdit={onEdit} onDelete={onDelete} />
            </div>
        </div>
    );
};

const AutomationListItem = ({ automation, onStop, onReactivate, onEdit, onDelete }: any) => {
    const { icon } = getAutomationTypeDisplay(automation.automation_type);
    return (
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg hover:bg-neutral-800/50 transition-colors text-sm">
            {/* --- Mobile View --- */}
            <div className="p-4 md:hidden">
                <div className="flex justify-between items-start">
                    <div className="flex items-center gap-3">
                        {icon}
                        <span className="font-semibold text-white truncate">{automation.name}</span>
                    </div>
                    <StatusBadge status={automation.activation_status} />
                </div>
                <div className="grid grid-cols-2 gap-x-4 gap-y-3 mt-4 text-xs">
                    <div className="text-neutral-400 flex items-center gap-1">Health: <HealthStatus status={automation.health_status} /></div>
                    <div className="text-neutral-400">Executions: <span className="font-medium text-white">{automation.execution_count ?? 0}</span></div>
                    <div className="text-neutral-400">Created: <span className="font-medium text-white">{new Date(automation.created_at).toLocaleDateString()}</span></div>
                </div>
                <div className="mt-3 border-t border-neutral-800 pt-2">
                    <ActionButtons automation={automation} onStop={onStop} onReactivate={onReactivate} onEdit={onEdit} onDelete={onDelete} />
                </div>
            </div>

            {/* --- Desktop View --- */}
            <div className="hidden md:grid md:grid-cols-12 items-center p-3">
                 <div className="col-span-4 flex items-center gap-3">
                    {icon}
                    <span className="font-semibold text-white truncate">{automation.name}</span>
                </div>
                <div className="col-span-2 flex justify-center"><StatusBadge status={automation.activation_status} /></div>
                <div className="col-span-2 flex justify-center"><HealthStatus status={automation.health_status} /></div>
                <div className="col-span-1 text-center text-white">{automation.execution_count ?? 0}</div>
                <div className="col-span-1 text-center text-neutral-400">{new Date(automation.created_at).toLocaleDateString()}</div>
                <div className="col-span-2"><ActionButtons automation={automation} onStop={onStop} onReactivate={onReactivate} onEdit={onEdit} onDelete={onDelete} /></div>
            </div>
        </div>
    );
};


const AutomationList: React.FC<AutomationListProps> = ({ automationType, platformAccount, onBack, onEdit }) => {
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [layoutView, setLayoutView] = useState<'grid' | 'list'>('list');

  useEffect(() => {
    const fetchAutomations = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await AutomationApiService.getAllAutomations(platformAccount.platform_user_id);
        if (response.success) {
          const filteredAutomations = response.data.filter((auto: Automation) => auto.automation_type === automationType);
          setAutomations(filteredAutomations);
        } else {
          setError(response.message || 'Failed to fetch automations.');
        }
      } catch (err) {
        setError('An error occurred while fetching automations.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchAutomations();
  }, [platformAccount.platform_user_id, automationType]);

    const handleDeleteAutomation = async (automationId: string) => {
        setAutomations(prev => prev.filter(auto => auto.automation_id !== automationId));
        await AutomationApiService.deleteAutomation(platformAccount.platform_user_id, automationId);
    };

    const handleStopAutomation = async (automationId: string) => {
        setAutomations(prev => prev.map(auto => auto.automation_id === automationId ? { ...auto, activation_status: 'PAUSED' } : auto));
        await AutomationApiService.setActivate(platformAccount.platform_user_id, automationId, 'PAUSED');
    };

    const handleReactivateAutomation = async (automationId: string) => {
        setAutomations(prev => prev.map(auto => auto.automation_id === automationId ? { ...auto, activation_status: 'ACTIVE' } : auto));
        await AutomationApiService.setActivate(platformAccount.platform_user_id, automationId, 'ACTIVE');
    };

    const getAutomationTypeTitle = () => {
        switch (automationType) {
            case 'DM_REPLY': return 'Trigger Messages on Keywords (DM)';
            case 'COMMENT_REPLY': return 'Reply on Comments';
            case 'PRIVATE_MESSAGE': return 'Direct Message (Who Comment on your post)';
            case 'AI_DM_CONVERSATION': return 'AI Conversation Engagement';
            default: return 'Automations';
        }
    };

  return (
    <div className="space-y-6 p-4 sm:p-6 bg-neutral-950 min-h-screen text-neutral-200 font-sans">
      <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center gap-3">
          <button onClick={onBack} className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors">
            <ArrowLeft size={18} />
            <span className="text-xs sm:text-sm font-medium">Back</span>
          </button>
          <div>
            <h1 className="text-lg sm:text-2xl font-bold text-white tracking-tight">{getAutomationTypeTitle()}</h1>
            <p className="text-neutral-400 mt-1 text-xs sm:text-sm">Manage automations for @{platformAccount.username}</p>
          </div>
        </div>
        <div className="flex justify-end md:justify-start">
          <button onClick={onBack} className="flex items-center justify-center gap-2 px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors shadow-lg font-semibold">
            <Plus className="w-5 h-5" />
            <span className="text-sm">Create New</span>
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-neutral-900 border border-neutral-800 rounded-lg flex items-center gap-4"><div className="p-3 bg-green-500/10 rounded-lg"><Zap className="w-6 h-6 text-green-400" /></div><div><p className="text-2xl font-bold text-white">{automations.filter(auto => auto.activation_status === 'ACTIVE').length}</p><p className="text-sm text-neutral-400">Active</p></div></div>
        <div className="p-4 bg-neutral-900 border border-neutral-800 rounded-lg flex items-center gap-4"><div className="p-3 bg-sky-500/10 rounded-lg"><BarChart3 className="w-6 h-6 text-sky-400" /></div><div><p className="text-2xl font-bold text-white">{automations.length}</p><p className="text-sm text-neutral-400">Total Automations</p></div></div>
        <div className="p-4 bg-neutral-900 border border-neutral-800 rounded-lg flex items-center gap-4"><div className="p-3 bg-purple-500/10 rounded-lg"><CheckCircle className="w-6 h-6 text-purple-400" /></div><div><p className="text-2xl font-bold text-white">{automations.filter(auto => auto.health_status === 'HEALTHY').length}</p><p className="text-sm text-neutral-400">Healthy</p></div></div>
      </div>
      
      <main className="bg-neutral-900 border border-neutral-800 rounded-xl p-4 space-y-4">
        <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Your Automations</h2>
            <div className="flex items-center rounded-lg bg-neutral-800 p-1">
                <button onClick={() => setLayoutView('list')} className={`p-1.5 rounded-md transition-colors ${layoutView === 'list' ? 'bg-neutral-700 text-white' : 'text-neutral-400 hover:text-white'}`}><List className="w-5 h-5" /></button>
                <button onClick={() => setLayoutView('grid')} className={`p-1.5 rounded-md transition-colors ${layoutView === 'grid' ? 'bg-neutral-700 text-white' : 'text-neutral-400 hover:text-white'}`}><Grid className="w-5 h-5" /></button>
            </div>
        </div>

        {isLoading ? ( <div className="text-center py-10 text-neutral-500">Loading...</div>
        ) : error ? ( <div className="text-center py-10 text-red-500">{error}</div>
        ) : automations.length === 0 ? (
          <div className="text-center py-10 text-neutral-500">
            <Bot className="w-12 h-12 mx-auto" />
            <h3 className="mt-2 text-lg font-semibold text-white">No Automations Found</h3>
            <p className="text-sm">Click "Create New Automation" to get started.</p>
          </div>
        ) : (
          <div>
            {layoutView === 'list' && (
              <div className="hidden md:grid grid-cols-12 p-2 text-xs font-semibold text-neutral-400">
                <div className="col-span-4">Name</div>
                <div className="col-span-2 text-center">Status</div>
                <div className="col-span-2 text-center">Health</div>
                <div className="col-span-1 text-center">Executions</div>
                <div className="col-span-1 text-center">Created</div>
                <div className="col-span-2 text-right">Actions</div>
              </div>
            )}
            <div className={`${layoutView === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'flex flex-col gap-2'}`}>
              {automations.map((automation) => {
                  const itemProps = {
                      key: automation.automation_id,
                      automation,
                      onStop: () => handleStopAutomation(automation.automation_id),
                      onReactivate: () => handleReactivateAutomation(automation.automation_id),
                      onEdit: () => onEdit && onEdit(automation),
                      onDelete: () => handleDeleteAutomation(automation.automation_id)
                  };
                  return layoutView === 'grid' ? <AutomationGridItem {...itemProps} /> : <AutomationListItem {...itemProps} />;
              })}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AutomationList;