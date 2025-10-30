# Automation Deployment Feature

## Overview

The automation deployment feature allows users to convert their automation traces into scheduled workflows that run automatically at specified times. When a user clicks the "Convert" button in the Automation Trace Panel, they can configure a schedule and deploy the automation.

## Architecture

### Database Schema

The `automation_traces` table includes the following deployment-related columns:

```sql
deployment_status VARCHAR(50) DEFAULT 'draft'  -- Status: draft, deployed, paused, failed
schedule_type VARCHAR(50)                       -- Type: daily, weekly, monthly, custom
schedule_time VARCHAR(255)                      -- Time configuration (e.g., "09:00")
schedule_config JSONB                           -- Additional config (days, intervals, etc.)
deployed_at TIMESTAMPTZ                         -- Timestamp of deployment
```

### Backend API Endpoints

#### 1. Deploy Automation
**POST** `/automation/deploy`

Deploy an automation with schedule configuration.

**Request Body:**
```json
{
  "trace_id": "uuid-string",
  "schedule_type": "weekly",
  "schedule_time": "09:00",
  "schedule_config": {
    "days": ["Monday", "Wednesday", "Friday"],
    "timezone": "UTC"
  },
  "name": "Weekly Email Automation"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Automation deployed successfully",
  "deployment_status": "deployed"
}
```

#### 2. Update Deployment Status
**PATCH** `/automation/deployment-status/{trace_id}?status=paused`

Update the deployment status of an automation.

**Query Parameters:**
- `status`: New status (draft, deployed, paused, failed)

**Response:**
```json
{
  "success": true,
  "message": "Deployment status updated to 'paused'"
}
```

### Frontend Components

#### ScheduleAutomationModal

A modal dialog that appears when the user clicks the "Convert" button. It allows users to:

1. **Select Schedule Type:**
   - Daily: Runs every day at specified time
   - Weekly: Runs on selected days of the week
   - Monthly: Runs on specific days of the month
   - Custom: Custom interval configuration

2. **Configure Time:**
   - Time picker for selecting execution time

3. **Additional Configuration:**
   - For weekly: Select specific days (Mon-Sun)
   - For custom: Enter custom interval string

4. **Deploy:**
   - Calls the deploy API with selected configuration
   - Shows success animation on completion

#### AutomationTracePanel

The main panel that displays the automation trace. Features:

- **Convert Button:** Opens the schedule modal
- **Trace ID Tracking:** Stores the current trace ID for deployment
- **Real-time Updates:** Automatically loads trace data including deployment status

## Workflow

### User Journey

1. **User sends message** → Automation trace is generated and saved with `deployment_status: 'draft'`

2. **User clicks "Convert" button** → Schedule modal opens with the current trace ID

3. **User configures schedule:**
   - Selects schedule type (daily/weekly/monthly/custom)
   - Sets time (e.g., "09:00")
   - Configures additional options (days for weekly, etc.)

4. **User clicks "Deploy Automation":**
   - Frontend calls `AutomationTraceApiService.deployAutomation()`
   - Backend updates trace with:
     - `deployment_status`: 'deployed'
     - `schedule_type`: Selected type
     - `schedule_time`: Selected time
     - `schedule_config`: Additional configuration
     - `deployed_at`: Current timestamp
   - Success message shown to user

5. **Automation is now scheduled** and can be:
   - Viewed in the automation list
   - Paused/resumed via status updates
   - Modified or deleted

### Technical Flow

```
Frontend (AutomationTracePanel)
  │
  ├─► Load trace → Store trace_id
  │
  └─► User clicks Convert
        │
        └─► ScheduleAutomationModal
              │
              ├─► User configures schedule
              │
              └─► handleDeploy()
                    │
                    └─► AutomationTraceApiService.deployAutomation()
                          │
                          └─► Backend API (/automation/deploy)
                                │
                                └─► AutomationTraceDB.deploy_automation()
                                      │
                                      └─► UPDATE automation_traces
                                            SET deployment_status = 'deployed',
                                                schedule_type = ...,
                                                schedule_time = ...,
                                                deployed_at = NOW()
```

## Database Methods

### `deploy_automation()`

```python
async def deploy_automation(
    trace_id: str,
    schedule_type: str,
    schedule_time: str,
    schedule_config: Optional[Dict[str, Any]] = None,
    name: Optional[str] = None
) -> bool
```

Deploys an automation by updating its deployment status and schedule information.

**Parameters:**
- `trace_id`: UUID of the trace to deploy
- `schedule_type`: Type of schedule (daily, weekly, monthly, custom)
- `schedule_time`: Time or schedule configuration
- `schedule_config`: Additional schedule configuration (days, intervals, etc.)
- `name`: Optional name for the automation

**Returns:** `True` if deployed successfully, `False` if not found

### `update_deployment_status()`

```python
async def update_deployment_status(
    trace_id: str,
    status: str
) -> bool
```

Updates the deployment status of an automation.

**Parameters:**
- `trace_id`: UUID of the trace
- `status`: New status (draft, deployed, paused, failed)

**Returns:** `True` if updated, `False` if not found

## API Service Methods

### `deployAutomation()`

```typescript
deployAutomation: async (params: {
  trace_id: string;
  schedule_type: 'daily' | 'weekly' | 'monthly' | 'custom';
  schedule_time: string;
  schedule_config?: Record<string, any>;
  name?: string;
})
```

Deploys an automation with schedule configuration.

### `updateDeploymentStatus()`

```typescript
updateDeploymentStatus: async (
  trace_id: string,
  status: 'draft' | 'deployed' | 'paused' | 'failed'
)
```

Updates the deployment status of an automation.

## Migration

To add the deployment feature to an existing database, run:

```bash
# Run the migration script on your Supabase database
psql <connection_string> -f scripts/migrate_automation_traces.sql
```

Or execute the migration SQL directly in Supabase SQL Editor:
- Navigate to SQL Editor in Supabase dashboard
- Copy contents of `scripts/migrate_automation_traces.sql`
- Execute the SQL

## Testing

Run the deployment test script:

```bash
# Activate virtual environment
source venv/bin/activate

# Run deployment tests
python scripts/test_automation_deployment.py
```

The test script will:
1. Create a test automation trace
2. Deploy it with a schedule
3. Verify deployment details
4. Update deployment status
5. Verify status change
6. List user traces with deployment info
7. Clean up test data

## Schedule Configuration Examples

### Daily Schedule
```json
{
  "schedule_type": "daily",
  "schedule_time": "09:00",
  "schedule_config": {
    "timezone": "UTC"
  }
}
```

### Weekly Schedule
```json
{
  "schedule_type": "weekly",
  "schedule_time": "14:30",
  "schedule_config": {
    "days": ["Monday", "Wednesday", "Friday"],
    "timezone": "America/New_York"
  }
}
```

### Monthly Schedule
```json
{
  "schedule_type": "monthly",
  "schedule_time": "08:00",
  "schedule_config": {
    "day_of_month": 1,
    "timezone": "UTC"
  }
}
```

### Custom Schedule
```json
{
  "schedule_type": "custom",
  "schedule_time": "Every 2 hours",
  "schedule_config": {
    "customInterval": "Every 2 hours",
    "timezone": "UTC"
  }
}
```

## Future Enhancements

1. **Execution History:** Track when automations run and their results
2. **Error Handling:** Retry logic and failure notifications
3. **Advanced Scheduling:** Cron expressions, date ranges, exclusions
4. **Execution Logs:** Detailed logs of automation runs
5. **Analytics:** Success rates, execution times, trends
6. **Notifications:** Email/SMS alerts on failures or completions
7. **Version Control:** Track changes to automation configurations
8. **Conditional Execution:** Run based on conditions or triggers

## Deployment Status Values

| Status | Description |
|--------|-------------|
| `draft` | Automation created but not yet deployed |
| `deployed` | Automation is active and scheduled to run |
| `paused` | Automation temporarily stopped, can be resumed |
| `failed` | Automation encountered errors during execution |

## Security Considerations

1. **Authorization:** Ensure users can only deploy their own automations
2. **Validation:** Validate schedule configuration before deployment
3. **Rate Limiting:** Prevent abuse of deployment API
4. **Audit Log:** Track who deployed, paused, or modified automations
5. **Encryption:** Sensitive schedule configuration data should be encrypted

## Troubleshooting

### Deployment fails with "Trace not found"
- Ensure the trace has been saved to the database
- Check that `currentTraceId` is set correctly in the frontend
- Verify the trace exists with `GET /automation/traces/{trace_id}`

### Schedule not executing
- Verify `deployment_status` is 'deployed'
- Check `schedule_time` format is correct
- Ensure background scheduler is running (future implementation)

### Cannot update deployment status
- Verify trace exists and user has permission
- Check status value is valid (draft, deployed, paused, failed)
- Review backend logs for SQL errors

## Support

For issues or questions:
1. Check backend logs: `tail -f logs/automation.log`
2. Test with: `python scripts/test_automation_deployment.py`
3. Review database: `SELECT * FROM automation_traces WHERE id = 'trace-id'`
4. Open an issue with error details and reproduction steps
