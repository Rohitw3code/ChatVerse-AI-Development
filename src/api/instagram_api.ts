// src/api/instagram_api.ts
import { apiClient } from '../lib/api-client';
import { API_CONFIG, ApiResponse } from '../config/api';
import {
  RagSourceFile,
  InstagramConversation,
  InstagramMessage,
} from '../types/types';
import { CommentReply } from '../types/comment_reply'; // Corrected import for CommentReply as a type

interface UploadFileParams {
  file: File;
  provider_id: string;
  platform_user_id: string;
  platform: string;
}

interface UploadWebsiteParams {
  website_url: string;
  provider_id: string;
  platform_user_id: string;
  platform: string;
}

interface UploadCustomTextParams {
  text: string;
  provider_id: string;
  platform_user_id: string;
  platform: string;
}

// Assuming SendMessagePayload is defined in types.ts
interface SendMessagePayload {
  recipient_id: string;
  message: string;
  platform_user_id: string;
}

export class InstagramApiService {
  static async getConversations(platformUserId: string): Promise<ApiResponse<{ data: InstagramConversation[] }>> {
    const endpoint = API_CONFIG.ENDPOINTS.INSTAGRAM.CONVERSATIONS(platformUserId);
    return apiClient.get(endpoint);
  }

  static async getMessages(conversationId: string, platformUserId: string): Promise<ApiResponse<{ messages: InstagramMessage[] }>> {
    const endpoint = API_CONFIG.ENDPOINTS.INSTAGRAM.MESSAGES({ conversation_id: conversationId, platform_user_id: platformUserId });
    return apiClient.get(endpoint);
  }

  static async sendMessage(payload: SendMessagePayload): Promise<ApiResponse> {
    const endpoint = API_CONFIG.ENDPOINTS.INSTAGRAM.SEND_MESSAGE;
    return apiClient.post(endpoint, payload);
  }

  static async getInstagramPosts(platformUserId: string): Promise<ApiResponse<any[]>> {
    const endpoint = API_CONFIG.ENDPOINTS.INSTAGRAM.POSTS;
    return apiClient.get(endpoint, { platform_user_id: platformUserId });
  }

  static async uploadFile(params: UploadFileParams): Promise<ApiResponse<RagSourceFile>> {
    const { file, provider_id, platform_user_id, platform } = params;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('provider_id', provider_id);
    formData.append('platform_user_id', platform_user_id);
    formData.append('platform', platform);

    const endpoint = API_CONFIG.ENDPOINTS.RAG.UPLOAD_FILE;
    return apiClient.post<RagSourceFile>(endpoint, formData);
  }

  static async uploadWebsiteData(payload: UploadWebsiteParams): Promise<ApiResponse> {
    const endpoint = API_CONFIG.ENDPOINTS.RAG.UPLOAD_WEB_URL;
    return apiClient.post(endpoint, payload);
  }

  static async uploadCustomTextData(payload: UploadCustomTextParams): Promise<ApiResponse> {
    const endpoint = API_CONFIG.ENDPOINTS.RAG.UPLOAD_CUSTOM_TEXT;
    return apiClient.post(endpoint, payload);
  }

  static async saveCommentReplyAutomation(payload: CommentReply): Promise<ApiResponse> {
    const endpoint = API_CONFIG.ENDPOINTS.AUTOMATION.CREATE_COMMENT_REPLY;
    return apiClient.post(endpoint, payload);
  }

  // FIX: Added the missing getCommentReplyAutomations method
  static async getCommentReplyAutomations(platformUserId: string): Promise<ApiResponse<CommentReply[]>> {
    const endpoint = API_CONFIG.ENDPOINTS.AUTOMATION.GET_COMMENT_REPLY(platformUserId); // Assuming API_CONFIG has this endpoint
    return apiClient.get(endpoint);
  }  

  static async getInSight(platformUserId: string) {
    const endpoint = API_CONFIG.ENDPOINTS.INSTAGRAM.INSIGHT(platformUserId); 
    return apiClient.get(endpoint);
  }  



}