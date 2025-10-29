import React from 'react';
import { ArrowLeft, Users } from 'lucide-react';

interface CommentEngagementProps {
  onBack: () => void;
}

const CommentEngagement: React.FC<CommentEngagementProps> = ({ onBack }) => (
  <div className="space-y-6 p-6">
    <div className="flex items-center gap-4">
      <button onClick={onBack} className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
        <ArrowLeft className="w-5 h-5 text-white" />
      </button>
      <div>
        <h2 className="text-2xl font-bold text-white">Comment Section Engagement</h2>
        <p className="text-gray-400">Engage actively in your comment sections</p>
      </div>
    </div>
    <div className="p-8 bg-gray-800 border border-gray-700 rounded-xl text-center">
      <Users className="w-16 h-16 text-red-500 mx-auto mb-4" />
      <h3 className="text-xl font-semibold text-white mb-2">Coming Soon</h3>
      <p className="text-gray-400">Comment engagement tools are under development</p>
    </div>
  </div>
);

export default CommentEngagement;