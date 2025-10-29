export interface PrivateReply {
  name:string,
  description:string,
  platform_user_id: string;
  provider_id: string;
  post_selection_type: "ALL" | "SPECIFIC" | "DATE_RANGE";
  specific_post_ids: string[];
  date_range: "1d" | "1w" | "1m" | null;
  trigger_type: "KEYWORD" | "AI_DECISION";
  keywords: string;
  match_type: "CONTAINS" | "EXACT" | "STARTSWITH";
  ai_context_rules: string;
  system_prompt: string;
  reply_template_type: "text" | "image" | "button_template" | "quick_replies" | "";
  reply_template_content: { [key: string]: any };
  model_provider: "GROQ" | "OPENAI";
  model_name: string;
  temperature: number;
  is_rag_enabled: boolean;
  confidence_threshold: number;
  model_usage: "PLATFORM_DEFAULT" | "CUSTOM";
  schedule_type: "CONTINUOUS" | "DAILY_ONE_TIME";
  max_actions: number | null;
  time_period_seconds: number;
  user_cooldown_seconds: number;
}