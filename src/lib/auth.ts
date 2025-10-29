import { supabase } from './supabase';

// Get authenticated user from Supabase
export const getSupabaseUser = async () => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    return user;
  } catch (error) {
    console.error('Error getting Supabase user:', error);
    return null;
  }
};

// Get user profile ID from Supabase user metadata
export const getUserProfileId = async (): Promise<string | null> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      console.log('No authenticated user found');
      return null;
    }

    // Try to get profile_id from user metadata
    const profileId = user.user_metadata?.profile_id || user.id;
    
    console.log('User profile ID:', profileId);
    return profileId;
  } catch (error) {
    console.error('Error getting user profile ID:', error);
    return null;
  }
};

// Get user data from Supabase
export const getUserData = async () => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    return user;
  } catch (error) {
    console.error('Error getting user data:', error);
    return null;
  }
};

// Get auth token (for backward compatibility)
export const getAuthToken = (): string | null => {
  return localStorage.getItem('sb-zkrmagxhszrywafnzruq-auth-token');
};

// Check if user is authenticated
export const isAuthenticated = async (): Promise<boolean> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    return !!user;
  } catch (error) {
    console.error('Error checking authentication:', error);
    return false;
  }
};