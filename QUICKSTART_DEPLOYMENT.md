# Automation Deployment - Quick Start Guide

## What Changed?

### 1. Database Schema (`tabels/automation.sql`)
Added new columns to `automation_traces` table:
- `deployment_status` - Tracks if automation is draft, deployed, paused, or failed
- `schedule_type` - Daily, weekly, monthly, or custom schedule
- `schedule_time` - Time configuration (e.g., "09:00")
- `schedule_config` - JSONB for additional configuration (days, intervals, etc.)
- `deployed_at` - Timestamp when automation was deployed

### 2. Backend Database Handler (`chatagent/db/automation_trace_db.py`)
Added new methods:
- `deploy_automation()` - Deploy automation with schedule information
- `update_deployment_status()` - Update deployment status
- Updated existing methods to include new deployment fields

### 3. Backend API Router (`chatagent/automation_trace_router.py`)
Added new endpoints:
- `POST /automation/deploy` - Deploy automation with schedule
- `PATCH /automation/deployment-status/{trace_id}` - Update deployment status
- Added `DeployAutomationPayload` model

### 4. Frontend API Service (`src/api/automation-trace.ts`)
Added new methods:
- `deployAutomation()` - Deploy automation with schedule configuration
- `updateDeploymentStatus()` - Update deployment status
- Updated `AutomationTrace` interface with deployment fields

### 5. Frontend Component (`src/pages/chat/components/AutomationTracePanel.tsx`)
Enhanced functionality:
- Added `currentTraceId` state to track the trace being viewed
- Modified `ScheduleAutomationModal` to accept `traceId` prop
- Implemented real deployment via API instead of simulation
- Extract trace ID when loading from database
- Build schedule configuration from user selections

## How to Deploy

### Step 1: Run Database Migration

Execute the migration on your Supabase database:

```bash
# Option A: Using psql
psql <your_supabase_connection_string> -f scripts/migrate_automation_traces.sql

# Option B: Using Supabase SQL Editor
# 1. Go to Supabase Dashboard → SQL Editor
# 2. Copy contents of scripts/migrate_automation_traces.sql
# 3. Paste and click "Run"
```

### Step 2: Test Backend

Test the new deployment functionality:

```bash
# Activate virtual environment
cd /home/bittu/Desktop/chatverse/ChatVerse-AI-Development
source venv/bin/activate

# Run deployment test
python scripts/test_automation_deployment.py
```

Expected output:
```
================================================================================
Testing Automation Deployment Functionality
================================================================================

1. Creating automation trace...
   ✅ Trace created with ID: <uuid>

2. Loading trace to check initial status...
   ✅ Initial deployment_status: draft
   ✅ Initial deployed_at: None

3. Deploying automation with schedule...
   ✅ Automation deployed successfully

4. Verifying deployment details...
   ✅ Deployment status: deployed
   ✅ Schedule type: weekly
   ✅ Schedule time: 09:00
   ✅ Schedule config: {'days': ['Monday', 'Wednesday', 'Friday'], 'timezone': 'UTC'}
   ✅ Deployed at: 2025-10-30T...
   ✅ Updated name: Weekly Email Automation

... (more tests)

✅ All deployment tests passed!
```

### Step 3: Test Frontend

1. **Start the backend server:**
   ```bash
   cd /home/bittu/Desktop/chatverse/ChatVerse-AI-Development
   source venv/bin/activate
   python main.py
   ```

2. **Start the frontend:**
   ```bash
   cd /home/bittu/Desktop/chatverse/ChatVerse-AI-Development/ChatVerse-Frontend-Development
   npm run dev
   ```

3. **Test the workflow:**
   - Send a message that triggers an automation
   - Open the Automation Trace Panel (right side)
   - Click the "Convert" button (emerald gradient button)
   - Configure schedule:
     - Select schedule type (daily/weekly/monthly/custom)
     - Set time (e.g., "09:00")
     - For weekly: select days
     - For custom: enter interval
   - Click "Deploy Automation"
   - Wait for success animation
   - Verify in database:
     ```sql
     SELECT id, name, deployment_status, schedule_type, schedule_time, deployed_at 
     FROM automation_traces 
     ORDER BY created_at DESC 
     LIMIT 5;
     ```

## User Flow

1. **User Action:** Sends message → Automation trace generated
2. **User Action:** Clicks "Convert" button → Schedule modal opens
3. **User Action:** Configures schedule → Selects type, time, options
4. **User Action:** Clicks "Deploy Automation" → API call initiated
5. **System Action:** Updates database with deployment info
6. **System Action:** Shows success animation
7. **Result:** Automation is now "deployed" with schedule configuration

## API Testing with cURL

### Deploy Automation
```bash
curl -X POST http://localhost:8000/automation/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "your-trace-id-here",
    "schedule_type": "weekly",
    "schedule_time": "09:00",
    "schedule_config": {
      "days": ["Monday", "Wednesday", "Friday"]
    },
    "name": "Weekly Email Automation"
  }'
```

### Update Deployment Status
```bash
curl -X PATCH "http://localhost:8000/automation/deployment-status/your-trace-id-here?status=paused"
```

### Get Trace with Deployment Info
```bash
curl http://localhost:8000/automation/traces/your-trace-id-here
```

## Verification Checklist

- [ ] Database migration completed successfully
- [ ] New columns exist in `automation_traces` table
- [ ] Backend test script passes all tests
- [ ] Backend server starts without errors
- [ ] Frontend builds without errors
- [ ] Convert button opens schedule modal
- [ ] Schedule modal accepts all input types
- [ ] Deploy button calls backend API
- [ ] Success animation shows after deployment
- [ ] Database updated with deployment info
- [ ] Automation list shows deployment status

## Troubleshooting

### Migration fails
```
Error: column already exists
```
**Solution:** Columns already added. Skip migration or use IF NOT EXISTS clauses.

### Backend test fails
```
Error: column "deployment_status" does not exist
```
**Solution:** Run database migration first.

### Frontend doesn't show modal
```
Modal not opening on Convert button click
```
**Solution:** Check browser console for errors. Verify traceId is set.

### Deployment API returns 404
```
{"detail": "Trace not found"}
```
**Solution:** Verify trace exists and traceId is correct in frontend state.

## Next Steps

After successful deployment:

1. **Add deployment status badge** to automation list items
2. **Implement scheduler** to actually run deployed automations
3. **Add execution history** to track automation runs
4. **Add pause/resume buttons** to automation list
5. **Show deployment info** in trace panel header
6. **Add analytics** for automation performance

## Files Modified

Backend:
- ✅ `tabels/automation.sql` - Schema update
- ✅ `chatagent/db/automation_trace_db.py` - Database methods
- ✅ `chatagent/automation_trace_router.py` - API endpoints

Frontend:
- ✅ `src/api/automation-trace.ts` - API service
- ✅ `src/pages/chat/components/AutomationTracePanel.tsx` - UI component

Scripts:
- ✅ `scripts/migrate_automation_traces.sql` - Migration script
- ✅ `scripts/test_automation_deployment.py` - Test script

Documentation:
- ✅ `AUTOMATION_DEPLOYMENT.md` - Full documentation
- ✅ `QUICKSTART_DEPLOYMENT.md` - This file

## Questions?

Check the full documentation: `AUTOMATION_DEPLOYMENT.md`
