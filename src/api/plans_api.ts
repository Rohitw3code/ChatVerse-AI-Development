import { apiClient } from '../lib/api-client';
import { API_CONFIG, ApiResponse } from '../config/api';

export interface BillingPlanMetadata {
  popular?: boolean;
  features: string[];
}

export interface BillingPlan {
  id: number;
  name: string;
  monthly_price: number;
  yearly_price?: number;
  monthly_credits: number;
  yearly_credits: number;
  currency: string;
  metadata: BillingPlanMetadata;
}

export interface CreateOrderPayload {
  plan_id: string;
  user_id: string;
  billing_cycle?: 'monthly' | 'yearly';
}

export interface CreateOrderResponse {
  status?: string;
  order?: {
    id: string;
    amount: number;
    currency: string;
    [key: string]: any;
  };
  order_id?: string;
  razorpay_order_id?: string;
  amount?: number;
  currency?: string;
  key?: string;
  razorpay_key_id?: string;
  [key: string]: any;
}

export interface PaymentCallbackPayload {
  razorpay_payment_id: string;
  razorpay_order_id: string;
  razorpay_signature: string;
  plan_id: string;
  user_id: string;
}

export class PlansApiService {
  static async getBillingPlans(): Promise<ApiResponse<BillingPlan[]>> {
    const endpoint = API_CONFIG.ENDPOINTS.PLANS.BILLING_PLANS;
    return await apiClient.get<BillingPlan[]>(endpoint);
  }

  static async createOrder(payload: CreateOrderPayload): Promise<ApiResponse<CreateOrderResponse>> {
    const endpoint = API_CONFIG.ENDPOINTS.PLANS.CREATE_ORDER;
    return await apiClient.post<CreateOrderResponse>(endpoint, payload);
  }

  static async paymentCallback(payload: PaymentCallbackPayload): Promise<ApiResponse<any>> {
    const endpoint = API_CONFIG.ENDPOINTS.PLANS.PAYMENT_CALLBACK;
    return await apiClient.post<any>(endpoint, payload);
  }
}