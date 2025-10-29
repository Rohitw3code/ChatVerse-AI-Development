// Global Application Store
// Manages global app state, UI state, and cross-cutting concerns

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppStore {
  // UI State
  sidebarCollapsed: boolean;
  isMobile: boolean;
  showMobileNav: boolean;
  currentTheme: 'light' | 'dark' | 'system';
  
  // Navigation State
  activeTab: string;
  previousRoute: string | null;
  
  // Global Loading States
  globalLoading: boolean;
  
  // Notifications/Messages
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    timestamp: number;
    autoHide?: boolean;
  }>;
  
  // Actions
  setSidebarCollapsed: (collapsed: boolean) => void;
  setIsMobile: (isMobile: boolean) => void;
  setShowMobileNav: (show: boolean) => void;
  setActiveTab: (tab: string) => void;
  setPreviousRoute: (route: string | null) => void;
  setGlobalLoading: (loading: boolean) => void;
  addNotification: (notification: Omit<AppStore['notifications'][0], 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

export const useAppStore = create<AppStore>()(
    (set, get) => ({
      // Initial state
      sidebarCollapsed: false,
      isMobile: false,
      showMobileNav: false,
      currentTheme: 'dark',
      activeTab: 'dashboard',
      previousRoute: null,
      globalLoading: false,
      notifications: [],

      // Actions
      setSidebarCollapsed: (collapsed: boolean) => {
        set({ sidebarCollapsed: collapsed });
      },

      setIsMobile: (isMobile: boolean) => {
        set({ isMobile });
        if (isMobile) {
          set({ sidebarCollapsed: true, showMobileNav: false });
        } else {
          set({ sidebarCollapsed: false, showMobileNav: false });
        }
      },

      setShowMobileNav: (show: boolean) => {
        set({ showMobileNav: show });
      },

      setActiveTab: (tab: string) => {
        set({ activeTab: tab });
      },

      setPreviousRoute: (route: string | null) => {
        set({ previousRoute: route });
      },

      setGlobalLoading: (loading: boolean) => {
        set({ globalLoading: loading });
      },

      addNotification: (notification) => {
        const id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
        const newNotification = {
          ...notification,
          id,
          timestamp: Date.now(),
        };
        
        set((state) => ({
          notifications: [...state.notifications, newNotification]
        }));

        // Auto-remove notification after 5 seconds if autoHide is true
        if (notification.autoHide !== false) {
          setTimeout(() => {
            get().removeNotification(id);
          }, 5000);
        }
      },

      removeNotification: (id: string) => {
        set((state) => ({
          notifications: state.notifications.filter(n => n.id !== id)
        }));
      },

      clearNotifications: () => {
        set({ notifications: [] });
      },

      setTheme: (theme: 'light' | 'dark' | 'system') => {
        set({ currentTheme: theme });
      },
    }),
);
