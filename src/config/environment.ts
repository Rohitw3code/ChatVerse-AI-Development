// Environment Configuration
// This file handles all environment variables in a centralized way

interface EnvironmentConfig {
  supabase: {
    url: string;
    anonKey: string;
  };
  api: {
    baseUrl: string;
  };
  app: {
    name: string;
    version: string;
    environment: 'development' | 'staging' | 'production';
  };
}

// Helper function to get environment variable with fallback
export const getEnvVar = (key: string, fallback?: string): string => {
  const value = import.meta.env[key];
  if (!value && !fallback) {
    console.warn(`Environment variable ${key} is not set`);
    return '';
  }
  return value || fallback || '';
};

// Centralized environment configuration
export const ENV: EnvironmentConfig = {
  supabase: {
    url: import.meta.env.VITE_SUPABASE_URL,
    anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY,
  },
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL,
  },
  app: {
    name: import.meta.env.VITE_APP_NAME || 'ChatVerse',
    version: import.meta.env.VITE_APP_VERSION || '0.1.0',
    environment: 'development',
  },
};

// Validation function to check if all required environment variables are set
export const validateEnvironment = (): boolean => {
  const requiredVars = [
    { key: 'VITE_SUPABASE_URL', value: ENV.supabase.url },
    { key: 'VITE_SUPABASE_ANON_KEY', value: ENV.supabase.anonKey },
  ];

  const missingVars = requiredVars.filter(({ value }) => !value);
  
  if (missingVars.length > 0) {
    console.error('Missing required environment variables:', missingVars.map(v => v.key));
    return false;
  }
  
  return true;
};

// Development helper to log environment status
if (ENV.app.environment === 'development') {
  console.log('🔧 Environment Configuration:', {
    environment: ENV.app.environment,
    apiBaseUrl: ENV.api.baseUrl,
    hasSupabaseUrl: !!ENV.supabase.url,
    hasSupabaseKey: !!ENV.supabase.anonKey,
  });
}
