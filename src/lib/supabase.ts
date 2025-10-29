import { createClient } from '@supabase/supabase-js'
import { ENV, validateEnvironment } from '../config/environment'

// Validate environment variables on initialization
if (!validateEnvironment()) {
  throw new Error('Missing required environment variables for Supabase configuration');
}

// Create Supabase client with environment variables
export const supabase = createClient(ENV.supabase.url, ENV.supabase.anonKey)

// Export configuration for debugging (development only)
if (ENV.app.environment === 'development') {
  console.log('✅ Supabase client initialized successfully');
}