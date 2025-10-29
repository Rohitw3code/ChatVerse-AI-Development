import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Zap, Clock, XCircle, Grid, List, StopCircle, PlayCircle, Edit, Trash2, Lightbulb, Bot, Target, Reply, Image, ChevronDown, ChevronRight } from 'lucide-react';
import { AutomationApiService } from '../../../../api/automation';

interface AllAutomationsDashboardProps {
  onBack: () => void;
  onSelectAutomationType: (typeId: string) => void;
  platformAccount: {
    id: number;
    platform_user_id: string;
    username: string;
    profile_picture_url?: string;
  };
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
}

const getAutomationTypeDisplay = (type: string) => {
  switch (type) {
    case 'AI_DM_CONVERSATION':
      return { name: 'AI DM Conversation', icon: <Bot className="w-4 h-4 sm:w-5 sm:h-5 text-purple-400" />, color: 'from-blue-500 to-purple-600' };
    case 'DM_REPLY':
      return { name: 'DM Keyword Reply', icon: <Target className="w-4 h-4 sm:w-5 sm:h-5 text-sky-400" />, color: 'from-green-500 to-teal-600' };
    case 'COMMENT_REPLY':
      return { name: 'Comment Reply', icon: <Reply className="w-4 h-4 sm:w-5 sm:h-5 text-amber-400" />, color: 'from-orange-500 to-red-600' };
    case 'PRIVATE_MESSAGE':
      return { name: 'Private Message', icon: <Image className="w-4 h-4 sm:w-5 sm:h-5 text-pink-400" />, color: 'from-pink-500 to-rose-600' };
    default:
      return { name: type.replace(/_/g, ' '), icon: <Lightbulb className="w-4 h-4 sm:w-5 sm:h-5 text-neutral-400" />, color: 'from-gray-500 to-gray-600' };
  }
};

const StatusBadge = ({ status }: { status: string }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'PAUSED':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'INACTIVE':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-neutral-500/20 text-neutral-400 border-neutral-500/30';
    }
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(status)}`}>
      {status}
    </span>
  );
};

const HealthStatus = ({ status }: { status: string }) => {
  const getHealthColor = (status: string) => {
    switch (status) {
      case 'HEALTHY':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'WARNING':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-neutral-500/20 text-neutral-400 border-neutral-500/30';
    }
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getHealthColor(status)}`}>
      {status}
    </span>
  );
};

const ActionButtons = ({ automation, onStop, onReactivate, onEdit, onDelete }: any) => (
  <div className="flex items-center justify-end gap-1 sm:gap-2">
    {automation.activation_status === 'ACTIVE' ? (
      <button 
        onClick={onStop} 
        className="p-1.5 sm:p-2 text-neutral-400 hover:text-yellow-400 hover:bg-neutral-800 rounded-md transition-colors" 
        title="Pause Automation"
      >
        <StopCircle className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
      </button>
    ) : (
      <button 
        onClick={onReactivate} 
        className="p-1.5 sm:p-2 text-neutral-400 hover:text-green-400 hover:bg-neutral-800 rounded-md transition-colors" 
        title="Activate Automation"
      >
        <PlayCircle className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
      </button>
    )}
    <button 
      onClick={onEdit} 
      className="p-1.5 sm:p-2 text-neutral-400 hover:text-sky-400 hover:bg-neutral-800 rounded-md transition-colors" 
      title="Edit"
    >
      <Edit className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
    </button>
    <button 
      onClick={onDelete} 
      className="p-1.5 sm:p-2 text-neutral-400 hover:text-red-400 hover:bg-neutral-800 rounded-md transition-colors" 
      title="Delete"
    >
      <Trash2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
    </button>
  </div>
);

const AutomationCard = ({ automation, onStop, onReactivate, onEdit, onDelete }: any) => {
  const { icon, name: typeName } = getAutomationTypeDisplay(automation.automation_type);
  
  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl shadow-lg transition-all duration-300 hover:border-sky-500/30 hover:-translate-y-1 flex flex-col overflow-hidden">
      <div className="p-3 sm:p-4 border-b border-neutral-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="p-1.5 sm:p-2 bg-neutral-800 rounded-md">{icon}</div>
            <h3 className="font-semibold text-white truncate text-sm sm:text-base">{automation.name}</h3>
          </div>
          <StatusBadge status={automation.activation_status} />
        </div>
        <p className="text-xs sm:text-sm text-neutral-400 mt-2 sm:mt-3 h-8 sm:h-10 line-clamp-2">
          {automation.description !== "No Desc" ? automation.description : "No description provided."}
        </p>
      </div>
      <div className="p-3 sm:p-4 flex-grow grid grid-cols-2 gap-2 sm:gap-4 text-xs sm:text-sm text-neutral-400">
        <div className="flex items-center gap-1.5 sm:gap-2">
          <Zap className="w-3.5 h-3.5 sm:w-4 sm:h-4"/>
          <span>Executions: <span className="text-white font-medium">{automation.execution_count ?? 0}</span></span>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-2">
          <Clock className="w-3.5 h-3.5 sm:w-4 sm:h-4"/>
          <span>Created: <span className="text-white font-medium">{new Date(automation.created_at).toLocaleDateString()}</span></span>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-2">
          <span className="text-green-400 font-bold text-sm sm:text-base leading-none">$</span>
          <span>Cost: <span className="text-white font-medium">{automation.cumulative_cost.toFixed(2)}</span></span>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-2">
          <span>Health: <HealthStatus status={automation.health_status} /></span>
        </div>
      </div>
      <div className="p-2 border-t border-neutral-800 bg-neutral-950/50 flex items-center justify-end">
        <ActionButtons 
          automation={automation} 
          onStop={onStop} 
          onReactivate={onReactivate} 
          onEdit={onEdit} 
          onDelete={onDelete} 
        />
      </div>
    </div>
  );
};

const AutomationListItem = ({ automation, onStop, onReactivate, onEdit, onDelete }: any) => {
  const { icon } = getAutomationTypeDisplay(automation.automation_type);
  
  return (
    <div className="grid grid-cols-12 items-center p-3 sm:p-4 bg-neutral-900 border border-neutral-800 rounded-lg hover:bg-neutral-800/50 transition-colors text-xs sm:text-sm">
      <div className="col-span-3 flex items-center gap-2 sm:gap-3">
        <div className="p-1.5 sm:p-2 bg-neutral-800 rounded-md">{icon}</div>
        <div>
          <h3 className="font-semibold text-white truncate text-xs sm:text-sm">{automation.name}</h3>
          <p className="text-xs text-neutral-400 truncate">
            {automation.description !== "No Desc" ? automation.description : "No description provided."}
          </p>
        </div>
      </div>
      <div className="col-span-2 flex justify-center">
        <StatusBadge status={automation.activation_status} />
      </div>
      <div className="col-span-2 flex justify-center">
        <HealthStatus status={automation.health_status} />
      </div>
      <div className="col-span-1 text-center text-white font-medium text-xs sm:text-sm">
        {automation.execution_count ?? 0}
      </div>
      <div className="col-span-1 text-center text-neutral-400 text-xs sm:text-sm">
        ${automation.cumulative_cost.toFixed(2)}
      </div>
      <div className="col-span-1 text-center text-neutral-400 text-xs sm:text-sm">
        {new Date(automation.created_at).toLocaleDateString()}
      </div>
      <div className="col-span-2 flex justify-end">
        <ActionButtons 
          automation={automation} 
          onStop={onStop} 
          onReactivate={onReactivate} 
          onEdit={onEdit} 
          onDelete={onDelete} 
        />
      </div>
    </div>
  );
};

const AutomationTypeSection = ({ 
  type, 
  automations, 
  onStop, 
  onReactivate, 
  onEdit, 
  onDelete,
  layoutView
}: {
  type: string;
  automations: Automation[];
  onStop: (id: string) => void;
  onReactivate: (id: string) => void;
  onEdit: (automation: Automation) => void;
  onDelete: (id: string) => void;
  layoutView: 'grid' | 'list';
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const { name: typeName, icon, color } = getAutomationTypeDisplay(type);
  const count = automations.length;

  if (count === 0) return null;

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden">
      <div 
        className="p-3 sm:p-4 cursor-pointer hover:bg-neutral-800/50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className={`w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-gradient-to-r ${color} p-2 sm:p-2.5 flex items-center justify-center`}>
              {icon}
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-semibold text-white">{typeName}</h3>
              <p className="text-xs sm:text-sm text-neutral-400">{count} automation{count !== 1 ? 's' : ''}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs sm:text-sm text-neutral-400">{count}</span>
            {isExpanded ? <ChevronDown className="w-4 h-4 sm:w-5 sm:h-5 text-neutral-400" /> : <ChevronRight className="w-4 h-4 sm:w-5 sm:h-5 text-neutral-400" />}
          </div>
        </div>
      </div>
      
      {isExpanded && (
        <div className="border-t border-neutral-800 p-3 sm:p-4">
          {layoutView === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
              {automations.map((automation) => (
                <AutomationCard
                  key={automation.automation_id}
                  automation={automation}
                  onStop={() => onStop(automation.automation_id)}
                  onReactivate={() => onReactivate(automation.automation_id)}
                  onEdit={() => onEdit(automation)}
                  onDelete={() => onDelete(automation.automation_id)}
                />
              ))}
            </div>
          ) : (
            <div className="space-y-2 sm:space-y-3">
              {automations.map((automation) => (
                <AutomationListItem
                  key={automation.automation_id}
                  automation={automation}
                  onStop={() => onStop(automation.automation_id)}
                  onReactivate={() => onReactivate(automation.automation_id)}
                  onEdit={() => onEdit(automation)}
                  onDelete={() => onDelete(automation.automation_id)}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const AllAutomationsDashboard: React.FC<AllAutomationsDashboardProps> = ({ platformAccount,onBack, onSelectAutomationType }) => {
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [layoutView, setLayoutView] = useState<'grid' | 'list'>('grid');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAutomations = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await AutomationApiService.getAllAutomations(platformAccount.platform_user_id);
        if (response.success) {
          setAutomations(response.data);
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
  }, [platformAccount.platform_user_id]);

  const handleDeleteAutomation = async (automationId: string) => {
    setAutomations(prev => prev.filter(auto => auto.automation_id !== automationId));
    await AutomationApiService.deleteAutomation(platformAccount.platform_user_id, automationId);
  };

  const handleStopAutomation = async (automationId: string) => {
    setAutomations(prev => prev.map(auto => 
      auto.automation_id === automationId 
        ? { ...auto, activation_status: 'PAUSED' } 
        : auto
    ));
    await AutomationApiService.setActivate(platformAccount.platform_user_id, automationId, 'PAUSED');
  };

  const handleReactivateAutomation = async (automationId: string) => {
    setAutomations(prev => prev.map(auto => 
      auto.automation_id === automationId 
        ? { ...auto, activation_status: 'ACTIVE' } 
        : auto
    ));
    await AutomationApiService.setActivate(platformAccount.platform_user_id, automationId, 'ACTIVE');
  };

  const handleEditAutomation = (automation: Automation) => {
    // This will be handled by individual components
    console.log('Edit automation:', automation);
  };

  const handleNavigateToCreate = () => {
    navigate('/instagram/create-automation');
    onSelectAutomationType('automation')
    
  };

  // Group automations by type
  const groupedAutomations = automations.reduce((acc, automation) => {
    const type = automation.automation_type;
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(automation);
    return acc;
  }, {} as Record<string, Automation[]>);

  return (
    <div className="p-3 sm:p-4 md:p-6 lg:p-8 bg-[#000000] min-h-screen text-neutral-200 font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 sm:gap-0 mb-6 sm:mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white tracking-tight">Automations Dashboard</h1>
          <p className="text-neutral-500 mt-2 text-sm sm:text-base">Manage all your automations for @{platformAccount.username}</p>
        </div>
        <button
          onClick={handleNavigateToCreate}
          className="flex items-center justify-center gap-2 px-4 sm:px-6 py-2.5 sm:py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-300 hover:scale-105 shadow-lg text-sm sm:text-base"
        >
          <Plus className="w-4 h-4 sm:w-5 sm:h-5" />
          <span className="hidden sm:inline">Create New Automation</span>
          <span className="sm:hidden">Create</span>
        </button>
      </div>

      {/* Dashboard Banner */}
      <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-xl p-4 sm:p-6 mb-6 sm:mb-8">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <div className="text-center">
            <div className="text-2xl sm:text-3xl font-bold text-white mb-1 sm:mb-2">{automations.length}</div>
            <div className="text-xs sm:text-sm text-blue-300">Total Automations</div>
          </div>
          <div className="text-center">
            <div className="text-2xl sm:text-3xl font-bold text-green-400 mb-1 sm:mb-2">
              {automations.filter(a => a.activation_status === 'ACTIVE').length}
            </div>
            <div className="text-xs sm:text-sm text-green-300">Active</div>
          </div>
          <div className="text-center">
            <div className="text-2xl sm:text-3xl font-bold text-yellow-400 mb-1 sm:mb-2">
              {automations.filter(a => a.activation_status === 'PAUSED').length}
            </div>
            <div className="text-xs sm:text-sm text-yellow-300">Paused</div>
          </div>
          <div className="text-center">
            <div className="text-2xl sm:text-3xl font-bold text-purple-400 mb-1 sm:mb-2">
              ${automations.reduce((sum, a) => sum + a.cumulative_cost, 0).toFixed(2)}
            </div>
            <div className="text-xs sm:text-sm text-purple-300">Total Cost</div>
          </div>
        </div>
        <div className="mt-3 sm:mt-4 text-center">
          <p className="text-xs sm:text-sm text-neutral-400">
            Manage your Instagram automations, monitor performance, and optimize engagement strategies
          </p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 sm:gap-0 mb-4 sm:mb-6">
        <div className="flex items-center gap-4">
          <div className="text-xs sm:text-sm text-neutral-400">
            View: <span className="text-white font-medium">{layoutView === 'grid' ? 'Grid' : 'List'}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setLayoutView('grid')}
            className={`p-1.5 sm:p-2 rounded-md transition-colors ${
              layoutView === 'grid' 
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' 
                : 'text-neutral-400 hover:text-white hover:bg-neutral-800'
            }`}
          >
            <Grid className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          </button>
          <button
            onClick={() => setLayoutView('list')}
            className={`p-1.5 sm:p-2 rounded-md transition-colors ${
              layoutView === 'list' 
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' 
                : 'text-neutral-400 hover:text-white hover:bg-neutral-800'
            }`}
          >
            <List className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-16 sm:py-20">
          <div className="animate-spin rounded-full h-10 w-10 sm:h-12 sm:w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-neutral-500 mt-3 sm:mt-4 text-sm sm:text-base">Loading automations...</p>
        </div>
      ) : error ? (
        <div className="text-center py-16 sm:py-20">
          <XCircle className="w-12 h-12 sm:w-16 sm:h-16 text-red-500 mx-auto mb-3 sm:mb-4" />
          <h3 className="text-lg sm:text-xl font-semibold text-white mb-2">Error Loading Automations</h3>
          <p className="text-red-400 text-sm sm:text-base">{error}</p>
        </div>
      ) : automations.length === 0 ? (
        <div className="text-center py-16 sm:py-20">
          <Bot className="w-12 h-12 sm:w-16 sm:h-16 text-neutral-500 mx-auto mb-3 sm:mb-4" />
          <h3 className="text-lg sm:text-xl font-semibold text-white mb-2">No Automations Found</h3>
          <p className="text-neutral-400 mb-4 sm:mb-6 text-sm sm:text-base">Get started by creating your first automation.</p>
          <button
            onClick={handleNavigateToCreate}
            className="px-4 sm:px-6 py-2.5 sm:py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-300 hover:scale-105 text-sm sm:text-base"
          >
            Create Your First Automation
          </button>
        </div>
      ) : (
        <div className="space-y-4 sm:space-y-6">
          {/* List View Header */}
          {layoutView === 'list' && (
            <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3 sm:p-4">
              <div className="grid grid-cols-12 text-xs font-semibold text-neutral-400">
                <div className="col-span-3">Automation</div>
                <div className="col-span-2 text-center">Status</div>
                <div className="col-span-2 text-center">Health</div>
                <div className="col-span-1 text-center">Executions</div>
                <div className="col-span-1 text-center">Cost</div>
                <div className="col-span-1 text-center">Created</div>
                <div className="col-span-2 text-right">Actions</div>
              </div>
            </div>
          )}
          
          {Object.entries(groupedAutomations).map(([type, typeAutomations]) => (
            <AutomationTypeSection
              key={type}
              type={type}
              automations={typeAutomations}
              onStop={handleStopAutomation}
              onReactivate={handleReactivateAutomation}
              onEdit={handleEditAutomation}
              onDelete={handleDeleteAutomation}
              layoutView={layoutView}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default AllAutomationsDashboard;
