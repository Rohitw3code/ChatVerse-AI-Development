import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService, User, AuthState } from '../services/auth.service';
import { useUserStore } from './userStore';

interface AuthStore extends AuthState {
  initialize: () => void;
  signInWithGoogle: () => Promise<{ success: boolean; error?: string }>;
  signOut: () => Promise<{ success: boolean; error?: string }>;
  getAuthToken: () => Promise<string | null>;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      isLoading: true,
      isAuthenticated: false,

      initialize: async () => {
        try {
          set((state) => (state.isLoading ? state : { isLoading: true }));

          const user = await authService.getCurrentUser();
          set({ user, isAuthenticated: !!user });
          if (user) {
            useUserStore.getState().initializeUserData(user);
          } else {
            useUserStore.getState().clearUserData();
          }

          authService.onAuthStateChange((user: User | null) => {
            set({ user, isAuthenticated: !!user });
            if (user) {
              useUserStore.getState().initializeUserData(user);
            } else {
              useUserStore.getState().clearUserData();
            }
          });

        } catch (error) {
          console.error('Error during auth initialization:', error);
          set({ user: null, isAuthenticated: false });
        } finally {
          set({ isLoading: false });
        }
      },

      signInWithGoogle: async () => {
        set({ isLoading: true });
        const result = await authService.signInWithGoogle();
        if (!result.success) {
          set({ isLoading: false });
        }
        return result;
      },

      signOut: async () => {
        set({ isLoading: true });
        const result = await authService.signOut();
        if (result.success) {
          set({
            user: null,
            isAuthenticated: false,
          });
          useUserStore.getState().clearUserData();
        }
        set({ isLoading: false });
        return result;
      },

      getAuthToken: () => authService.getAuthToken(),

      setUser: (user: User | null) => {
        set({
          user,
          isAuthenticated: !!user,
        });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);