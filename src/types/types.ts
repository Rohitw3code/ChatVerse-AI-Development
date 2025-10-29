// src/types/types.ts

// ============================================
// Core & User Types
// ============================================

export interface UserProfile {
  provider_id: string;
  auth_provider: string;
  email?: string;
  phone_number?: string;
  full_name?: string;
  username?: string;
  profile_picture?: string;
  is_verified?: boolean;
}

export interface PlatformAccount {
  id: number; // This is the connected_account_id
  provider_id: string;
  platform: string;
  platform_user_id: string;
  platform_username: string;
  scopes?: string[]; // Gmail permissions/scopes
  token_expires_at: string;
  connected: boolean;
  connected_at: string;
}

// ============================================
// Instagram & Live Chat Types
// ============================================

export interface InstagramParticipant {
  username: string;
  id: string;
}

export interface InstagramConversation {
  id: string;
  participants: {
    data: InstagramParticipant[];
  };
}

export interface InstagramMessage {
  id: string;
  created_time: string;
  from: InstagramParticipant;
  to?: {
    data: InstagramParticipant[];
  };
  message: string;
}

export interface ChatMessage {
  id: string;
  sender: string;
  message: string;
  time: string;
  isOwn: boolean;
  created_time: string;
}

export interface ChatUser {
  id: string;
  name: string;
  username: string;
  avatar: string;
  lastMessage: string;
  time: string;
  unread: number;
  online: boolean;
  conversationId: string;
}

// ============================================
// Bot & Automation Types
// ============================================

// For GETting the AI Chat Bot config
export interface AutomationConfig {
    automation_id: number;
    connected_account_id: number;
    provider_id: string;
    platform: string;
    platform_user_id: string;
    name: string;
    automation_type: string;
    is_active: boolean;
    system_prompt: string;
    model_name: string;
    temperature: number;
    is_rag_enabled: boolean;
}

// For CREATING the AI Chat Bot config (matches Pydantic model)
export interface CreateAutomationConfigPayload {
    connected_account_id: number;
    platform_user_id: string;
    platform: "instagram";
    provider_id: string;
    bot_name: string;
    system_prompt: string;
    model_name?: string;
    temperature?: number;
    is_rag_enabled?: boolean;
    is_active?: boolean;
}


export interface DmKeywordReplyAutomationPayload {
  automation_id?: string | null; // Changed to string to match UUID
  provider_id: string;
  platform_user_id: string;
  name: string;
  platform: "instagram";

  trigger_type: "KEYWORD" | "AI_DECISION";
  keywords: string[]; // Still sending as list from frontend
  match_type: "EXACT" | "CONTAINS" | "STARTS_WITH"; // Updated to match DB enum

  // AI context
  ai_context_rules?: string | null;
  system_prompt?: string;
  reply_template_type?: "text" | "image" | "quick_replies" | "button_template";
  reply_template_content: { [key: string]: any };

  // Additional automation parameters
  description?: string;
  model_usage?: "PLATFORM_DEFAULT" | "USER_CUSTOM"; // Changed CUSTOM to USER_CUSTOM to match DB
  user_cooldown_seconds?: number | null;
}

export interface CommentReplyAutomationPayload {
  rule_id?: string | null;
  automation_id?: string | null;

  name: string;
  platform?:string;
  description?: string;
  post_selection_type:string;
  specific_post_ids:string[] | null;
  date_range:string|null;

  platform_user_id: string;
  provider_id: string;

  trigger_type: "KEYWORD" | "AI_DECISION";
  keywords?: string[] | null;
  match_type: "EXACT" | "CONTAINS" | "STARTS_WITH";

  // AI context
  ai_context_rules?: string | null;
  system_prompt?: string |null;
  comment_reply_template_type?: "PLAIN_TEXT";

  max_replies_per_post?: number | null;
  reply_count_condition?: "LESS_THAN" | "EQUAL_TO" | "GREATER_THAN" | string; // Keeping flexible
  reply_count_value?: number | null;

  // Additional automation parameters
  model_usage?: "PLATFORM_DEFAULT" | "USER_CUSTOM";
  execution_count?: number | null;
  user_cooldown_seconds?: number | null;


  model_provider?: string;
  model_name?: string;
  temperature?: number | null;
  is_rag_enabled?: boolean;
  confidence_threshold?: number | null;

  max_actions?: number | null;
  time_period_seconds?: number | null;
}




// ============================================
// RAG (Data Source) Types
// ============================================

export interface RagSourceFile {
  message: string;
  file_url: string;
  filename: string;
  success: boolean;
}