import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Users,
  Heart,
  MessageCircle,
  TrendingUp,
  Eye,
  Clock,
  Bookmark,
  Link as LinkIcon,
  UserCheck
} from 'lucide-react';
import { InstagramApiService } from '../../../api/instagram_api';

interface Insight {
  name: string;
  total_value: {
    value: number;
  };
  title: string;
}

interface DashboardContentProps {
  platform_user_id: string;
}

const iconMapping: { [key: string]: React.ElementType } = {
  reach: Eye,
  website_clicks: LinkIcon,
  profile_views: Users,
  accounts_engaged: UserCheck,
  total_interactions: BarChart3,
  likes: Heart,
  comments: MessageCircle,
  saves: Bookmark,
};

const colorMapping: { [key: string]: { color: string; bgColor: string } } = {
  reach: { color: 'text-purple-400', bgColor: 'bg-purple-400/10' },
  website_clicks: { color: 'text-sky-400', bgColor: 'bg-sky-400/10' },
  profile_views: { color: 'text-yellow-400', bgColor: 'bg-yellow-400/10' },
  accounts_engaged: { color: 'text-indigo-400', bgColor: 'bg-indigo-400/10' },
  total_interactions: { color: 'text-rose-400', bgColor: 'bg-rose-400/10' },
  likes: { color: 'text-red-400', bgColor: 'bg-red-400/10' },
  comments: { color: 'text-green-400', bgColor: 'bg-green-400/10' },
  saves: { color: 'text-blue-400', bgColor: 'bg-blue-400/10' },
};

const formatValue = (value: number): string => {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`;
  }
  return value.toString();
};

const DashboardContent: React.FC<DashboardContentProps> = ({ platform_user_id }) => {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

useEffect(() => {
    const fetchInsights = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await InstagramApiService.getInSight(platform_user_id);
        
        if (response && typeof response === 'object') {
          const formattedInsights = Object.entries(response).map(([key, value]) => ({
            name: key,
            total_value: { value: value as number },
            title: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          }));
          setInsights(formattedInsights);
          setLastUpdated(new Date());
        } else {
          setInsights([]);
        }
      } catch (err) {
        setError('Failed to fetch Instagram insights.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, [platform_user_id]);

  
  return (
    <div className="space-y-6 p-4 md:p-6 lg:p-8 bg-[#000000] min-h-screen text-neutral-200 font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold text-white tracking-tight">Dashboard</h1>
          <p className="text-neutral-500 mt-1 text-sm md:text-base">Welcome back! Here's your Instagram overview.</p>
        </div>
        <div className="flex items-center gap-3 bg-[#1a1a1a] border border-[#262626] rounded-xl px-4 py-2 shadow-sm">
          <Clock size={16} className="text-neutral-500" />
          <span className="text-xs text-neutral-500">Last updated: </span>
          <span className="text-sm font-medium text-white">{lastUpdated.toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Stats Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
            {Array.from({ length: 8 }).map((_, index) => (
                <div key={index} className="p-5 bg-[#1a1a1a] border border-[#262626] rounded-xl shadow-lg h-36 animate-pulse">
                    <div className="flex items-center justify-between mb-3">
                        <div className="p-2 rounded-full bg-neutral-700 w-10 h-10"></div>
                        <div className="h-5 w-16 bg-neutral-700 rounded-full"></div>
                    </div>
                    <div>
                        <div className="h-8 w-24 bg-neutral-700 rounded-md mb-1.5"></div>
                        <div className="h-5 w-20 bg-neutral-700 rounded-md"></div>
                    </div>
                </div>
            ))}
        </div>
      ) : error ? (
        <div className="text-center py-10 text-red-400 bg-[#1a1a1a] border border-[#262626] rounded-xl">
          <p>{error}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {insights.map((stat) => {
            const Icon = iconMapping[stat.name] || BarChart3;
            const colors = colorMapping[stat.name] || { color: 'text-gray-400', bgColor: 'bg-gray-400/10' };

            return (
              <div key={stat.name} className="p-5 bg-[#1a1a1a] border border-[#262626] rounded-xl shadow-lg transition-all duration-300 hover:border-neutral-600">
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2 rounded-full ${colors.bgColor}`}>
                    <Icon className={`w-5 h-5 ${colors.color}`} />
                  </div>
                  <span className={`text-xs font-medium ${colors.color} ${colors.bgColor} px-2.5 py-1 rounded-full`}>
                    Daily
                  </span>
                </div>
                <div>
                  <p className="text-2xl font-bold text-white mb-0.5">{formatValue(stat.total_value.value)}</p>
                  <p className="text-sm text-neutral-400">{stat.title}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Engagement Chart */}
        <div className="p-6 bg-[#1a1a1a] border border-[#262626] rounded-xl shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">Engagement Overview</h3>
            <BarChart3 className="w-5 h-5 text-neutral-500" />
          </div>
          <div className="h-64 flex items-center justify-center border border-[#262626] rounded-lg bg-[#0a0a0a]">
            <p className="text-neutral-500 text-sm">Chart component will be implemented here</p>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="p-6 bg-[#1a1a1a] border border-[#262626] rounded-xl shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">Recent Activity</h3>
            <TrendingUp className="w-5 h-5 text-neutral-500" />
          </div>
          <div className="space-y-3">
            {[
              { action: 'New follower', user: '@john_doe', time: '2 min ago' },
              { action: 'Post liked', user: '@jane_smith', time: '5 min ago' },
              { action: 'Comment received', user: '@mike_wilson', time: '10 min ago' },
              { action: 'Story viewed', user: '@sarah_jones', time: '15 min ago' },
              { action: 'New follower', user: '@alex_g', time: '20 min ago' },
              { action: 'Post liked', user: '@lisa_k', time: '25 min ago' },
            ].map((activity, index) => (
              <div key={index} className="flex items-center gap-3 p-3 bg-[#0a0a0a] rounded-lg border border-[#1c1c1c] transition-colors duration-200 hover:border-blue-500/50">
                <div className="w-2 h-2 bg-green-400 rounded-full flex-shrink-0"></div>
                <div className="flex-1">
                  <p className="text-sm text-white truncate">{activity.action} <span className="text-blue-400 font-medium">{activity.user}</span></p>
                  <p className="text-xs text-neutral-500 mt-0.5">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardContent;