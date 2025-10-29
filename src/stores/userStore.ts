import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserApiService, extractUserDataFromGoogleAuth } from '../api/user_api';
import { UserProfile, PlatformAccount } from '../types/types';
import { apiClient } from '../lib/api-client';
import { API_CONFIG } from '../config/api';

interface UserStore {
  userProfile: UserProfile | null;
  connectedAccounts: PlatformAccount[];
  selectedPlatformAccount: PlatformAccount | null;
  credits: number | null;
  isLoading: boolean;
  error: string | null;

  initializeUserData: (googleUser: any) => Promise<void>;
  fetchConnectedAccounts: (providerId: string) => Promise<void>;
  fetchUserCredits: (providerId: string) => Promise<void>;
  updateCredits: (newCredits: number) => void;
  setSelectedPlatformAccount: (account: PlatformAccount | null) => void;
  addConnectedAccount: (account: PlatformAccount) => void;
  removeConnectedAccount: (accountId: number) => void;
  clearUserData: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useUserStore = create<UserStore>()(
  persist(
    (set, get) => ({
      userProfile: null,
      connectedAccounts: [],
      selectedPlatformAccount: null,
      credits: null,
      isLoading: false,
      error: null,

      initializeUserData: async (googleUser: any) => {
        set({ isLoading: true, error: null });
        try {
          let userProfile = get().userProfile;

          if (!userProfile || userProfile.provider_id !== googleUser.id) {
            const userData = extractUserDataFromGoogleAuth(googleUser);
            userProfile = await UserApiService.handleUserAuth(userData);
            set({ userProfile });
          }
          
          if (userProfile?.provider_id) {
            await get().fetchConnectedAccounts(userProfile.provider_id);
          } else {
             set({ connectedAccounts: [] });
          }
        } catch (error) {
          console.error('Error initializing user data:', error);
          set({
            error: error instanceof Error ? error.message : 'Failed to initialize user profile',
          });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchConnectedAccounts: async (providerId: string) => {
        if (!providerId) {
            set({ connectedAccounts: [], isLoading: false });
            return;
        };
        
        set({ isLoading: true, error: null });
        try {
          const endpoint = API_CONFIG.ENDPOINTS.USERS.GET_CONNECTED_ACCOUNTS(providerId);
          const response = await apiClient.get<PlatformAccount[]>(endpoint);
          
          const freshAccounts = response.success && response.data ? response.data : [];
          set({ connectedAccounts: freshAccounts });

          const currentSelected = get().selectedPlatformAccount;
          const isSelectedStillValid = freshAccounts.some(acc => acc.id === currentSelected?.id);

          if (currentSelected && !isSelectedStillValid) {
            set({ selectedPlatformAccount: freshAccounts.length > 0 ? freshAccounts[0] : null });
          } else if (!currentSelected && freshAccounts.length > 0) {
            set({ selectedPlatformAccount: freshAccounts[0] });
          }
          
        } catch (error) {
          console.error('Failed to fetch connected accounts:', error);
          set({ 
            error: 'Failed to fetch connected accounts',
            connectedAccounts: [],
          });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchUserCredits: async (providerId: string) => {
        if (!providerId) {
          set({ credits: null });
          return;
        }
        
        try {
          // This would be the actual API call to fetch user credits
          // For now, we'll use a placeholder - you'll need to implement the actual API endpoint
          const response = await apiClient.get<{ credits: number }>(`/users/${providerId}/credits`);
          if (response.success && response.data) {
            set({ credits: response.data.credits });
          }
        } catch (error) {
          console.error('Failed to fetch user credits:', error);
          // Don't set error state for credits fetch failure, just keep current value
        }
      },

      updateCredits: (newCredits: number) => {
        set({ credits: newCredits });
      },

      setSelectedPlatformAccount: (account: PlatformAccount | null) => {
        set({ selectedPlatformAccount: account });
      },

      addConnectedAccount: (account: PlatformAccount) => {
        set((state) => ({
          connectedAccounts: [...state.connectedAccounts, account]
        }));
      },

      removeConnectedAccount: (accountId: number) => {
        set((state) => ({
          connectedAccounts: state.connectedAccounts.filter(acc => acc.id !== accountId),
          selectedPlatformAccount: state.selectedPlatformAccount?.id === accountId 
            ? state.connectedAccounts.length > 1 ? state.connectedAccounts.filter(acc => acc.id !== accountId)[0] : null
            : state.selectedPlatformAccount
        }));
      },

      clearUserData: () => {
        set({
          userProfile: null,
          connectedAccounts: [],
          selectedPlatformAccount: null,
          isLoading: false,
          error: null,
        });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      setError: (error: string | null) => {
        set({ error });
      },
    }),
    {
      name: 'user-app-storage',
      partialize: (state) => ({
        userProfile: state.userProfile,
        connectedAccounts: state.connectedAccounts,
        selectedPlatformAccount: state.selectedPlatformAccount,
        credits: state.credits,
      }),
    }
  )
);