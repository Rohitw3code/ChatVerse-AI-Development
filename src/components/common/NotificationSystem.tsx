// Global Notification System Component
// Displays notifications from the app store

import React from 'react';
import { useAppStore } from '../../stores';
import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

const NotificationSystem: React.FC = () => {
  const { notifications, removeNotification } = useAppStore();

  if (notifications.length === 0) return null;

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'info':
      default:
        return <Info className="w-5 h-5 text-blue-400" />;
    }
  };

  const getBackgroundColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-500/20 border-green-500/30';
      case 'error':
        return 'bg-red-500/20 border-red-500/30';
      case 'warning':
        return 'bg-yellow-500/20 border-yellow-500/30';
      case 'info':
      default:
        return 'bg-blue-500/20 border-blue-500/30';
    }
  };

  const getTextColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-green-300';
      case 'error':
        return 'text-red-300';
      case 'warning':
        return 'text-yellow-300';
      case 'info':
      default:
        return 'text-blue-300';
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`p-4 rounded-lg border flex items-center gap-3 shadow-lg backdrop-blur-sm animate-in slide-in-from-right-full ${getBackgroundColor(notification.type)}`}
        >
          {getIcon(notification.type)}
          <span className={`font-medium text-sm flex-1 ${getTextColor(notification.type)}`}>
            {notification.message}
          </span>
          <button
            onClick={() => removeNotification(notification.id)}
            className="p-1 rounded-full hover:bg-black/20 transition-colors"
          >
            <X className="w-4 h-4 text-gray-400 hover:text-white" />
          </button>
        </div>
      ))}
    </div>
  );
};

export default NotificationSystem;
