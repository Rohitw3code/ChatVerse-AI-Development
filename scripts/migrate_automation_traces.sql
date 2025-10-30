-- Migration script to add deployment and schedule columns to automation_traces table
-- Run this on your Supabase database

-- Add new columns for deployment tracking
ALTER TABLE automation_traces 
ADD COLUMN IF NOT EXISTS deployment_status VARCHAR(50) DEFAULT 'draft',
ADD COLUMN IF NOT EXISTS schedule_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS schedule_time VARCHAR(255),
ADD COLUMN IF NOT EXISTS schedule_config JSONB,
ADD COLUMN IF NOT EXISTS deployed_at TIMESTAMPTZ;

-- Add comments for new columns
COMMENT ON COLUMN automation_traces.deployment_status IS 'Status of deployment: draft, deployed, paused, failed';
COMMENT ON COLUMN automation_traces.schedule_type IS 'Type of schedule: daily, weekly, monthly, custom';
COMMENT ON COLUMN automation_traces.schedule_time IS 'Time or schedule configuration string';
COMMENT ON COLUMN automation_traces.schedule_config IS 'Additional schedule configuration (days, intervals, etc.)';
COMMENT ON COLUMN automation_traces.deployed_at IS 'Timestamp when the automation was deployed';

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_automation_traces_deployment_status ON automation_traces(deployment_status);
CREATE INDEX IF NOT EXISTS idx_automation_traces_deployed_at ON automation_traces(deployed_at DESC);

-- Update existing records to have 'draft' status
UPDATE automation_traces 
SET deployment_status = 'draft' 
WHERE deployment_status IS NULL;

SELECT 'Migration completed successfully!' as message;
