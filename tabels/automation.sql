-- Simple Automation Trace Storage
-- This table stores automation traces from chat executions
-- Just save the trace data and load it back - that's it!

CREATE TABLE IF NOT EXISTS automation_traces (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- User and thread information
    user_id VARCHAR(255) NOT NULL,
    provider_id VARCHAR(255) NOT NULL,
    thread_id VARCHAR(255) NOT NULL,
    
    -- Simple metadata
    name VARCHAR(255),
    
    -- Deployment information
    deployment_status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'deployed', 'paused', 'failed'
    schedule_type VARCHAR(50), -- 'daily', 'weekly', 'monthly', 'custom'
    schedule_time VARCHAR(255), -- Time or schedule configuration (e.g., "09:00", "Monday at 3pm")
    schedule_config JSONB, -- Additional schedule configuration (days, intervals, etc.)
    deployed_at TIMESTAMPTZ, -- When the automation was deployed
    
    -- The complete automation trace data stored as JSONB
    trace_data JSONB NOT NULL,
    -- Structure matches frontend AutomationTraceEntry[]:
    -- [
    --   {
    --     "timestamp": "2025-10-30T12:00:00Z",
    --     "node": "inputer_agent",
    --     "event": "routing_decision",
    --     "agent": "gmail_agent_node",
    --     "tool": "send_gmail",
    --     "params": {"to": "...", "subject": "..."},
    --     "decision": {"goto": "agent_tool_node", "reason": "..."},
    --     "agents": ["gmail_agent_node"]
    --   },
    --   ...
    -- ]
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for quick lookups
CREATE INDEX IF NOT EXISTS idx_automation_traces_user_id ON automation_traces(user_id);
CREATE INDEX IF NOT EXISTS idx_automation_traces_thread_id ON automation_traces(thread_id);
CREATE INDEX IF NOT EXISTS idx_automation_traces_created_at ON automation_traces(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_automation_traces_trace_data ON automation_traces USING GIN(trace_data);
CREATE INDEX IF NOT EXISTS idx_automation_traces_deployment_status ON automation_traces(deployment_status);
CREATE INDEX IF NOT EXISTS idx_automation_traces_deployed_at ON automation_traces(deployed_at DESC);

-- Update trigger for updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_automation_traces_updated_at 
    BEFORE UPDATE ON automation_traces 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Helper function to save trace
CREATE OR REPLACE FUNCTION save_automation_trace(
    p_user_id VARCHAR(255),
    p_provider_id VARCHAR(255),
    p_thread_id VARCHAR(255),
    p_trace_data JSONB,
    p_name VARCHAR(255) DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_trace_id UUID;
BEGIN
    INSERT INTO automation_traces (
        user_id,
        provider_id,
        thread_id,
        name,
        trace_data
    ) VALUES (
        p_user_id,
        p_provider_id,
        p_thread_id,
        p_name,
        p_trace_data
    ) RETURNING id INTO v_trace_id;
    
    RETURN v_trace_id;
END;
$$ LANGUAGE plpgsql;

-- Helper function to load trace
CREATE OR REPLACE FUNCTION load_automation_trace(
    p_trace_id UUID
) RETURNS JSONB AS $$
DECLARE
    v_trace_data JSONB;
BEGIN
    SELECT trace_data INTO v_trace_data
    FROM automation_traces
    WHERE id = p_trace_id;
    
    RETURN v_trace_data;
END;
$$ LANGUAGE plpgsql;

-- Helper function to load trace by thread_id
CREATE OR REPLACE FUNCTION load_automation_trace_by_thread(
    p_thread_id VARCHAR(255)
) RETURNS JSONB AS $$
DECLARE
    v_trace_data JSONB;
BEGIN
    SELECT trace_data INTO v_trace_data
    FROM automation_traces
    WHERE thread_id = p_thread_id
    ORDER BY created_at DESC
    LIMIT 1;
    
    RETURN v_trace_data;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE automation_traces IS 'Simple storage for automation traces - save and load complex trace data';
COMMENT ON COLUMN automation_traces.trace_data IS 'Complete automation trace array stored as JSONB - matches frontend AutomationTraceEntry[]';
