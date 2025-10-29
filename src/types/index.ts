// Global Type Definitions
// Centralized type definitions for better maintainability

export interface User {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
  provider?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
  timestamp?: string;
}

export interface ApiError {
  success: false;
  message: string;
  error?: string;
  statusCode?: number;
}

export interface PlatformAccount {
  id: string;
  platform: Platform;
  username: string;
  displayName?: string;
  avatar?: string;
  isConnected: boolean;
  connectedAt?: string;
  lastSync?: string;
}

export interface SocialMediaPost {
  id: string;
  platform: Platform;
  content: string;
  mediaUrls?: string[];
  scheduledAt?: string;
  publishedAt?: string;
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  engagement?: {
    likes: number;
    comments: number;
    shares: number;
    views?: number;
  };
}

export interface AutomationRule {
  id: string;
  name: string;
  platform: Platform;
  type: 'comment_reply' | 'dm_reply' | 'auto_post' | 'engagement';
  isActive: boolean;
  conditions: Record<string, any>;
  actions: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface Analytics {
  platform: Platform;
  period: 'day' | 'week' | 'month' | 'year';
  metrics: {
    followers: number;
    engagement: number;
    reach: number;
    impressions: number;
    clicks?: number;
  };
  growth: {
    followers: number;
    engagement: number;
  };
}

// Utility Types
export type Platform = 'instagram' | 'twitter' | 'facebook' | 'linkedin' | 'tiktok' | 'youtube';
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';
export type Theme = 'light' | 'dark' | 'system';

// Component Props Types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface ButtonProps extends BaseComponentProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  disabled?: boolean;
  onClick?: () => void;
}

export interface ModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

// Form Types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'textarea' | 'select' | 'checkbox';
  required?: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
}

export interface FormData {
  [key: string]: string | boolean | number;
}

// API Types
export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface SearchParams {
  query?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filters?: Record<string, any>;
}
