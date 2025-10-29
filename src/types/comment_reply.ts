export interface CommentReplyPayload {
  rule_id?: string | null;
  automation_id?: string | null;
  name: string;
  platform?: string | null;
  description?: string | null;

  platform_user_id: string;
  provider_id: string; // UUID as string
  custom_message:string;
  reply_type:string;

  trigger_type?: string | null;
  keywords?: string | null;
  match_type?: string | null;

  post_selection_type?: string | null;
  specific_post_ids?: string[] | null;
  dateRange?: string | null; // default: "1d"

  ai_context_rules?: string | null;
  system_prompt?: string | null; // default: ""

  comment_reply_template_type?: string | null;

  max_replies_per_post?: number | null;
  max_actions?: number | null;

  reply_count_condition?: string | null;
  reply_count_value: number;

  model_provider?: string | null;
  model_name: string;
  temperature: number;

  is_rag_enabled: boolean;
  confidence_threshold: number;

  model_usage?: string | null;

  time_period_seconds?: number | null;
  user_cooldown_seconds?: number | null;
}
