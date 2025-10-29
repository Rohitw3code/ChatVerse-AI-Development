// API Testing Utilities
import { UserApiService } from '../api/user_api';

// Test data for development only
const TEST_USER_DATA = {
  email: "test@example.com",
  phone_number: "9999999999",
  auth_provider: "google",
  provider_id: "google-oauth2|test123",
  full_name: "Test User",
  username: "testuser",
  profile_picture: "https://example.com/profile.jpg",
  is_verified: true,
};

// Test functions for development
export const testUserApi = {
  async testCreateUser() {
    console.log('Testing user creation with dummy data...');
    try {
      const result = await UserApiService.createUserProfile(TEST_USER_DATA);
      console.log('✅ User creation test passed:', result);
      return result;
    } catch (error) {
      console.error('❌ User creation test failed:', error);
      throw error;
    }
  },

  async testCheckUserExists() {
    console.log('Testing user existence check...');
    try {
      const result = await UserApiService.checkUserExists('test@example.com');
      console.log('✅ User existence check test passed:', result);
      return result;
    } catch (error) {
      console.error('❌ User existence check test failed:', error);
      throw error;
    }
  },

  async testFullAuthFlow() {
    console.log('Testing full authentication flow...');
    try {
      const result = await UserApiService.handleUserAuth(TEST_USER_DATA);
      console.log('✅ Full auth flow test passed:', result);
      return result;
    } catch (error) {
      console.error('❌ Full auth flow test failed:', error);
      throw error;
    }
  },
};

// Add to window for easy testing in browser console
if (typeof window !== 'undefined') {
  (window as any).testUserApi = testUserApi;
}