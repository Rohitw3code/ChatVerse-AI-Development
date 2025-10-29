// Application Constants
// Centralized constants for better maintainability

export const APP_CONSTANTS = {
  // App Information
  APP_NAME: 'Autometa',
  APP_VERSION: '1.0.0',
  
  // Local Storage Keys
  STORAGE_KEYS: {
    USER_PREFERENCES: 'autometa_user_preferences',
    THEME: 'autometa_theme',
    LAST_VISITED_PAGE: 'autometa_last_page',
  },
  
  // API Configuration
  API: {
    TIMEOUT: 30000, // 30 seconds
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000, // 1 second
  },
  
  // UI Constants
  UI: {
    DEBOUNCE_DELAY: 300,
    ANIMATION_DURATION: 200,
    TOAST_DURATION: 5000,
  },
  
  // Validation Rules
  VALIDATION: {
    MIN_PASSWORD_LENGTH: 8,
    MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  },
  
  // Social Media Platforms
  PLATFORMS: {
    INSTAGRAM: 'instagram',
    TWITTER: 'twitter',
    FACEBOOK: 'facebook',
    LINKEDIN: 'linkedin',
    TIKTOK: 'tiktok',
    YOUTUBE: 'youtube',
  },
  
  // Routes
  ROUTES: {
    HOME: '/',
    GET_STARTED: '/get-started',
    PLATFORMS: '/platforms',
    DASHBOARD: '/dashboard',
    INSTAGRAM_DASHBOARD: '/instagram',
  },
} as const;

// Type definitions for constants
export type Platform = typeof APP_CONSTANTS.PLATFORMS[keyof typeof APP_CONSTANTS.PLATFORMS];
export type Route = typeof APP_CONSTANTS.ROUTES[keyof typeof APP_CONSTANTS.ROUTES];
