// src/api/user_api.ts
import { apiClient, ApiError as ApiClientError } from '../lib/api-client';
import { API_CONFIG, ApiResponse } from '../config/api';
import { UserProfile } from '../types/types';

export class UserApiService {
  static async getUserProfile(providerId: string): Promise<ApiResponse<UserProfile>> {
    const endpoint = API_CONFIG.ENDPOINTS.USERS.GET_PROFILE(providerId);
    return await apiClient.get<UserProfile>(endpoint);
  }

  static async createUserProfile(profileData: UserProfile): Promise<ApiResponse<UserProfile>> {
    const endpoint = API_CONFIG.ENDPOINTS.USERS.CREATE_PROFILE;
    return await apiClient.post<UserProfile>(endpoint, profileData);
  }

  static async getUserCredit(userId: string): Promise<ApiResponse<{ current_credits: number }>> {
    const endpoint = API_CONFIG.ENDPOINTS.USERS.GET_CREDIT(userId);
    return await apiClient.get<{ current_credits: number }>(endpoint);
  }

  static async handleUserAuth(userData: UserProfile): Promise<UserProfile> {
    // 1) Try to fetch existing profile
    try {
      const existingUserResponse = await this.getUserProfile(userData.provider_id);
      if (existingUserResponse.success && existingUserResponse.data) {
        return existingUserResponse.data;
      }
      // If backend returns success false (unlikely if 200), fall through to create
    } catch (err) {
      // If user is not found (404), proceed to create; otherwise rethrow
      if (err instanceof ApiClientError && err.status === 404) {
        console.debug('[handleUserAuth] User not found, creating new profile');
      } else {
        console.error('[handleUserAuth] Failed to get profile:', err);
        throw err;
      }
    }

    // 2) Create new profile
    const newUserResponse = await this.createUserProfile(userData);
    if (newUserResponse.success && newUserResponse.data) {
      return newUserResponse.data;
    }

    throw new Error('Failed to create user profile');
  }
}

export const extractUserDataFromGoogleAuth = (googleUser: any): UserProfile => {
  // alert("Extra "+JSON.stringify(googleUser))
  return {
    email: googleUser.email,
    auth_provider: 'google',
    provider_id: googleUser.id,
    full_name: googleUser.name,
    username: googleUser.email?.split('@')[0],
    profile_picture: googleUser.avatar,
    is_verified: true,
  };
};