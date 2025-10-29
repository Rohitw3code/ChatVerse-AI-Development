// src/api/bot.ts
import { apiClient } from '../lib/api-client';
import { API_CONFIG, ApiResponse } from '../config/api';
import { BotConfig, CommentReplyAutomationPayload, CreateBotConfigPayload, DmKeywordReplyAutomationPayload } from '../types/types';
import { CommentReplyPayload } from '../types/comment_reply';
import { PrivateReply } from '../types/private_reply';

export class BotApiService {
  static async createBotConfig(payload: CreateBotConfigPayload): Promise<ApiResponse<BotConfig>> {
    const endpoint = API_CONFIG.ENDPOINTS.AI_CHAT.CREATE_OR_UPDATE_CONFIG;
    return apiClient.post<BotConfig>(endpoint, payload);
  }

  static async getBotConfig(platform_user_id: string): Promise<ApiResponse<BotConfig>> {
    const endpoint = API_CONFIG.ENDPOINTS.AI_CHAT.GET_CONFIG(platform_user_id);
    return apiClient.get<BotConfig>(endpoint);
  }

  static async updateRagStatus(platform_user_id: string, isRagEnabled: boolean): Promise<ApiResponse<BotConfig>> {
    const endpoint = API_CONFIG.ENDPOINTS.AI_CHAT.UPDATE_RAG_STATUS(platform_user_id);
    // Note: This should ideally be a PATCH request, but we'll use POST if the client doesn't support PATCH.
    return apiClient.post<BotConfig>(endpoint, { is_rag_enabled: isRagEnabled });
  }

  static async createOrUpdateDmKeywordReply(payload: DmKeywordReplyAutomationPayload): Promise<ApiResponse> {
    const endpoint = API_CONFIG.ENDPOINTS.AUTOMATION.DM_REPLY;
    return apiClient.post(endpoint, payload);
  }

  static async getDmKeywordReplyAutomations(platformUserId: string): Promise<ApiResponse<any[]>> {
    const endpoint = API_CONFIG.ENDPOINTS.AUTOMATION.DM_REPLY;
    return apiClient.get(endpoint, { platform_user_id: platformUserId });
  }

  static async createOrUpdateCommentReply(payload:CommentReplyPayload): Promise<ApiResponse> {
    const endpoint = API_CONFIG.ENDPOINTS.AUTOMATION.CREATE_COMMENT_REPLY;
    return apiClient.post(endpoint, payload);
  }

  static async getCommentReply(platformUserId: string): Promise<ApiResponse<any[]>> {
    const endpoint = API_CONFIG.ENDPOINTS.AUTOMATION.CREATE_COMMENT_REPLY;
    return apiClient.get(endpoint, { platform_user_id: platformUserId });
  }

  static async getPosts(platformUserId: string): Promise<ApiResponse<any[]>> {
    const endpoint = API_CONFIG.ENDPOINTS.INSTAGRAM.POSTS;
    return apiClient.get(endpoint, { platform_user_id: platformUserId });
  }

  static async getAllAutomations(providerId: string): Promise<ApiResponse<any[]>> {
    const endpoint = API_CONFIG.ENDPOINTS.AUTOMATION.AUTOMATION;
    return apiClient.get(endpoint, { provider_id: providerId });
  }


  static async createPrivateMessageAutomation(payload:PrivateReply): Promise<ApiResponse<any[]>> {
    // alert("payloadd--> "+JSON.stringify(payload));
    console.log("payload private => "+JSON.stringify(payload))
    const endpoint = API_CONFIG.ENDPOINTS.AUTOMATION.PRIVATE_MESSAGE;
    return apiClient.post(endpoint,payload );
  }


  static async setActivate(platform_user_id: string, automation_id: string, activation_status: string): Promise<ApiResponse<any[]>> {
    const endpoint = API_CONFIG.ENDPOINTS.AUTOMATION.ACTIVATE
    return apiClient.get(endpoint, { platform_user_id: platform_user_id, automation_id: automation_id, activation_status: activation_status });
  }

  static async deleteAutomation(platform_user_id: string, automation_id: string): Promise<ApiResponse<any[]>> {
    const endpoint = API_CONFIG.ENDPOINTS.AUTOMATION.DELETE;
    return apiClient.get(endpoint, { platform_user_id: platform_user_id, automation_id: automation_id });
  }



}