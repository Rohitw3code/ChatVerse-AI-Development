// src/config/api.ts

import { ENV } from './environment';

export const API_CONFIG = {
  BASE_URL: ENV.api.baseUrl,
  ENDPOINTS: {
    USERS: {
      GET_PROFILE: (providerId: string) => `/users/profile/${providerId}`,
      CREATE_PROFILE: '/users/profile',
      GET_CONNECTED_ACCOUNTS: (providerId: string) => `/users/profile/${providerId}/connected-accounts`,
      GET_CREDIT: (userId: string) => `/users/get-credit/${userId}`,
    },
    INSTAGRAM: {
      LOGIN: (userId: string, returnUrl: string) => `/auth/instagram/login?user_id=${userId}&return_url=${encodeURIComponent(returnUrl)}`,
      CONVERSATIONS: (platformUserId: string) => `/instagram/conversations?platform_user_id=${platformUserId}`,
      MESSAGES: (params: { conversation_id: string; platform_user_id: string }) =>
        `/instagram/messages?conversation_id=${params.conversation_id}&platform_user_id=${params.platform_user_id}`,
      SEND_MESSAGE: '/instagram/send-message',
      POSTS:'/instagram/posts',
      INSIGHT: (platformUserId: string) => `/instagram/insight/instagram-insight?platform_user_id=${platformUserId}`,
    },
    X:{
      
    },
    YOUTUBE: {
      LOGIN: (userId: string, returnUrl: string) => `/auth/youtube/login?user_id=${userId}&return_url=${encodeURIComponent(returnUrl)}`,
    },
    GMAIL:{
      LOGIN: (userId: string, returnUrl: string) => `/auth/gmail/login?user_id=${userId}&return_url=${encodeURIComponent(returnUrl)}`,
      EMAILS: (userId: string) => `/auth/gmail/emails?user_id=${userId}`,
    },
    GOOGLE_SHEETS: {
      LOGIN: (userId: string, returnUrl: string) => `/auth/google-sheets/login?user_id=${userId}&return_url=${encodeURIComponent(returnUrl)}`,
      SPREADSHEETS: (userId: string) => `/auth/google-sheets/spreadsheets?user_id=${userId}`,
    },
    GDOC:{
      LOGIN: (userId: string, returnUrl: string) => `/auth/gdoc/login?user_id=${userId}&return_url=${encodeURIComponent(returnUrl)}`,
    },
    RAG: {
      UPLOAD_FILE: '/rag/sources/file-upload',
      UPLOAD_WEB_URL: '/rag/sources/web-url',
      UPLOAD_CUSTOM_TEXT: '/rag/sources/custom-text',
    },
    AUTOMATION: {
      AUTOMATION:'/automations/get-all-automations',
      DELETE:'/automations/delete',
      ACTIVATE:'/automations/update-active',
      CREATE_COMMENT_REPLY: '/instagram/automations/comment-reply',
      GET_COMMENT_REPLY: (platformUserId: string) => `/instagram/automations/comment-reply?platform_user_id=${platformUserId}`,
      DM_REPLY: '/instagram/automations/dm-keyword-reply',
    },
    AI_CHAT: {
      GET_CONFIG: (platform_user_id: string) => `/ai-chat/config/${platform_user_id}`,
      CREATE_OR_UPDATE_CONFIG: '/ai-chat/config',
      UPDATE_RAG_STATUS: (platform_user_id: string) => `/ai-chat/config/${platform_user_id}/rag`,
    },
    CHAT_AGENT:{
      SEND_MESSAGE:`/chatagent/chat/send-message`
    },
    PLANS: {
      BILLING_PLANS: '/plans/billing-plans',
      CREATE_ORDER: '/plans/create-order',
      PAYMENT_CALLBACK: '/plans/payment-callback',
    }

  },
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
} as const;

// The main API response structure from the backend
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
}

// The structure for handling API errors
export interface ApiError {
  detail: {
    success: false;
    message: string;
  } | string; // FastAPI can return error details in multiple formats
}