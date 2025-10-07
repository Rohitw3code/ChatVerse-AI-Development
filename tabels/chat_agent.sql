CREATE TABLE chat_agent (
    id BIGSERIAL PRIMARY KEY,                       -- unique chat agent id
    stream_type TEXT,                               -- type of streaming (#updates, custom, etc.)
    provider_id TEXT,                               -- LLM / provider ID
    thread_id TEXT,                                 -- conversation/thread identifier
    query_id TEXT,
    role TEXT ,  -- message role

    node TEXT,                                      -- input_node , planner_node,starter_node,supervisor_node,agent_node,tool_node
    next_node TEXT,

    type TEXT,
    next_type TEXT,

    message TEXT,                                   -- message content
    reason TEXT,                                    -- reasoning text / explanation
    current_messages JSONB,                         -- stores messages array {'messages':[{'role':'user','content':''},...]}
    params JSONB,                                   -- parameters/config for node
    embedding VECTOR(1536),                               -- for semantic search (if pgvector extension enabled)
    tool_output JSONB,
    usage JSONB,                                    -- token usage metadata
    status TEXT CHECK (status IN ('success','failed','started')), -- execution status
    total_token BIGINT,                             -- total tokens used
    total_cost FLOAT,                               -- total cost in $
    data JSONB,                                     -- extra runtime data
    execution_time TIMESTAMPTZ DEFAULT NOW()        -- when executed
);


CREATE TABLE chat_thread (
    id SERIAL PRIMARY KEY,
    provider_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    name TEXT NOT NULL,
    config JSONB
);

create table if not exists public.billing_usage (
  id serial primary key,
  provider_id text not null unique
    references public.user_profiles(provider_id) on delete cascade,
  chat_token bigint default 0,
  chat_cost numeric(12,4) default 0.0,
  platform_automation_count integer default 0,
  platform_automation_token bigint default 0,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);
