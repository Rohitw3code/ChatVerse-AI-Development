export interface ApiMessage {
  stream_type?: 'messages' | 'updates' | 'custom';
  message?: string;
  id?: string | number;
  query_id?: string;

  provider_id: string;
  thread_id: string;
  role: string;
  node: string;
  status: string;
  reason?: string;
  current_messages?: { role: string; content: string }[];
  type_?: string;
  params?: Record<string, any>;
  next_type?: string;
  usages?: Record<string, any>;
  execution_time?: string;
  tool_output?: Record<string, any>;
  next_node?: string;
  data?: {
    platform: any;
    name?: string;
    type?: string;
    data?: {
      title?: string;
      content?: string | any;
      options?: string[];
    };
  };
}
