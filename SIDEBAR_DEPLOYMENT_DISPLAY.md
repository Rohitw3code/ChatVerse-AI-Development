# Sidebar Automation Display Update

## Overview
Updated the Sidebar automation list to display deployment status and schedule information for each saved automation workflow.

## What Changed

### Visual Enhancements to Automation Cards

#### 1. **Deployment Status Badge**
Added next to the automation name, showing the current status:

```tsx
{automation.deployment_status && automation.deployment_status !== 'draft' && (
  <span className={`inline-flex items-center px-1.5 py-0.5 rounded-md text-[9px] font-bold border ${
    automation.deployment_status === 'deployed' 
      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'  // Green for deployed
      : automation.deployment_status === 'paused'
      ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'        // Amber for paused
      : automation.deployment_status === 'failed'
      ? 'bg-red-500/20 text-red-400 border-red-500/30'              // Red for failed
      : 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30'           // Gray for others
  }`}>
    {automation.deployment_status === 'deployed' && '🟢'}
    {automation.deployment_status === 'paused' && '⏸'}
    {automation.deployment_status === 'failed' && '❌'}
    {automation.deployment_status.toUpperCase()}
  </span>
)}
```

**Status Colors:**
- 🟢 **DEPLOYED** - Emerald green (active)
- ⏸ **PAUSED** - Amber yellow (temporarily stopped)
- ❌ **FAILED** - Red (error state)
- **DRAFT** - Hidden (default state, not shown)

#### 2. **Schedule Information Section**
Shows only for deployed automations with schedule configuration:

```tsx
{automation.deployment_status === 'deployed' && automation.schedule_type && (
  <div className="mb-2 p-2 bg-emerald-950/30 border border-emerald-500/20 rounded-md">
    {/* Schedule details */}
  </div>
)}
```

**Displays:**
- 🕐 **Schedule Type** - Daily, Weekly, Monthly, Custom
- **Schedule Time** - Execution time (e.g., "09:00")
- **Weekly Schedule** - Days of the week (e.g., "Mon, Wed, Fri at 09:00")
- **Daily Schedule** - "Every day at 09:00"
- **Monthly Schedule** - "Monthly at 09:00"
- **Deployed Date** - When the automation was deployed

## Visual Layout

### Before
```
┌──────────────────────────────────┐
│ #1  Workflow Name         [🗑️]  │
│ ✓ 5 steps • Oct 30               │
└──────────────────────────────────┘
```

### After (Deployed Automation)
```
┌──────────────────────────────────┐
│ #1  Workflow Name  🟢 DEPLOYED   │
│                           [🗑️]  │
│ ┌────────────────────────────┐   │
│ │ 🕐 Weekly Schedule         │   │
│ │ Mon, Wed, Fri at 09:00    │   │
│ │ Deployed Oct 30, 2:30 PM  │   │
│ └────────────────────────────┘   │
│ ✓ 5 steps • Oct 30               │
└──────────────────────────────────┘
```

### After (Paused Automation)
```
┌──────────────────────────────────┐
│ #2  Email Workflow  ⏸ PAUSED    │
│                           [🗑️]  │
│ ┌────────────────────────────┐   │
│ │ 🕐 Daily Schedule          │   │
│ │ Every day at 14:00        │   │
│ │ Deployed Oct 29, 9:15 AM  │   │
│ └────────────────────────────┘   │
│ ✓ 8 steps • Oct 29               │
└──────────────────────────────────┘
```

## Schedule Display Logic

### Daily Schedule
```
Input: { schedule_type: 'daily', schedule_time: '09:00' }
Display: "Every day at 09:00"
```

### Weekly Schedule
```
Input: { 
  schedule_type: 'weekly', 
  schedule_time: '14:30',
  schedule_config: { days: ['Monday', 'Wednesday', 'Friday'] }
}
Display: "Mon, Wed, Fri at 14:30"
```

### Monthly Schedule
```
Input: { schedule_type: 'monthly', schedule_time: '08:00' }
Display: "Monthly at 08:00"
```

### Custom Schedule
```
Input: { 
  schedule_type: 'custom', 
  schedule_time: 'Every 2 hours' 
}
Display: "Every 2 hours"
```

## Color Scheme

### Status Badge Colors
- **Deployed (Emerald)**
  - Background: `bg-emerald-500/20`
  - Text: `text-emerald-400`
  - Border: `border-emerald-500/30`

- **Paused (Amber)**
  - Background: `bg-amber-500/20`
  - Text: `text-amber-400`
  - Border: `border-amber-500/30`

- **Failed (Red)**
  - Background: `bg-red-500/20`
  - Text: `text-red-400`
  - Border: `border-red-500/30`

### Schedule Info Box
- Background: `bg-emerald-950/30`
- Border: `border-emerald-500/20`
- Icon color: `text-emerald-400`
- Title: `text-emerald-300`
- Description: `text-emerald-400/70`
- Timestamp: `text-emerald-500/50`

## Implementation Details

### Data Structure
The automation object now includes:
```typescript
interface Automation {
  id: string;
  name?: string;
  thread_id: string;
  entry_count: number;
  created_at: string;
  
  // New deployment fields
  deployment_status?: 'draft' | 'deployed' | 'paused' | 'failed';
  schedule_type?: 'daily' | 'weekly' | 'monthly' | 'custom';
  schedule_time?: string;
  schedule_config?: {
    days?: string[];
    customInterval?: string;
    [key: string]: any;
  };
  deployed_at?: string;
}
```

### Conditional Rendering
- Status badge shows only if `deployment_status` is NOT 'draft'
- Schedule info shows only if:
  1. `deployment_status === 'deployed'`
  2. `schedule_type` exists

### Date Formatting
```typescript
// Created date (bottom of card)
new Date(automation.created_at).toLocaleDateString('en-US', { 
  month: 'short', 
  day: 'numeric' 
})
// Output: "Oct 30"

// Deployed date (in schedule section)
new Date(automation.deployed_at).toLocaleDateString('en-US', { 
  month: 'short', 
  day: 'numeric', 
  hour: '2-digit', 
  minute: '2-digit' 
})
// Output: "Oct 30, 2:30 PM"
```

### Days Abbreviation (Weekly)
```typescript
automation.schedule_config?.days
  .slice(0, 3)              // Take first 3 days
  .map((d: string) => d.slice(0, 3))  // Abbreviate to 3 letters
  .join(', ')               // Join with commas
// Example: ['Monday', 'Wednesday', 'Friday'] → "Mon, Wed, Fri"
```

## User Experience

### What Users See

1. **Draft Automation (Just Created)**
   - No status badge
   - No schedule info
   - Just shows steps count and creation date

2. **Deployed Automation**
   - 🟢 Green "DEPLOYED" badge
   - Emerald-themed schedule info box
   - Shows schedule type, time, and when deployed
   - Full automation details

3. **Paused Automation**
   - ⏸ Amber "PAUSED" badge
   - Schedule info still visible
   - Indicates temporarily stopped

4. **Failed Automation**
   - ❌ Red "FAILED" badge
   - Schedule info visible
   - Indicates error occurred

### Interaction Flow

1. User opens Automations dropdown in sidebar
2. Sees list of all saved workflows
3. Quickly identifies status by color badge
4. Reads schedule details for deployed automations
5. Can click to view full trace
6. Can delete via trash icon

## Testing Checklist

- [ ] Draft automation shows no badge
- [ ] Deployed automation shows green badge
- [ ] Paused automation shows amber badge
- [ ] Failed automation shows red badge
- [ ] Daily schedule displays correctly
- [ ] Weekly schedule shows abbreviated days
- [ ] Monthly schedule displays correctly
- [ ] Custom schedule shows custom text
- [ ] Deployed timestamp formats correctly
- [ ] Schedule info only shows for deployed
- [ ] Long automation names truncate properly
- [ ] Hover effects work on all cards
- [ ] Delete button works for all statuses
- [ ] Click navigates to correct thread

## Integration with Deployment Flow

### Complete User Journey

1. **Create Automation**
   ```
   User sends message → Trace generated → Saved as 'draft'
   Sidebar shows: #1 Workflow Name
   ```

2. **Deploy Automation**
   ```
   User clicks Convert → Configures schedule → Clicks Deploy
   API updates database → Sidebar refreshes
   Sidebar shows: #1 Workflow Name 🟢 DEPLOYED
                  [Schedule box with details]
   ```

3. **Pause Automation** (Future)
   ```
   User pauses via API → Status updated
   Sidebar shows: #1 Workflow Name ⏸ PAUSED
   ```

4. **Resume/Delete**
   ```
   User can resume (back to deployed) or delete
   ```

## Future Enhancements

1. **Quick Actions**
   - Pause/Resume button on hover
   - Edit schedule inline
   - Duplicate automation

2. **Status Indicators**
   - Last execution time
   - Next scheduled run
   - Execution count badge

3. **Filtering**
   - Filter by status (deployed/paused/failed)
   - Sort by schedule, name, date

4. **Bulk Operations**
   - Pause all deployed
   - Delete multiple at once

5. **Advanced Schedule Display**
   - Timezone indicator
   - Next run countdown
   - Calendar preview

## Files Modified

- ✅ `src/pages/chat/ui/layout/Sidebar.tsx`
  - Added deployment status badge
  - Added schedule information section
  - Enhanced visual hierarchy
  - Improved color coding

## API Dependencies

Requires backend to return these fields in `getUserTraces()`:
```typescript
{
  deployment_status: string,
  schedule_type: string,
  schedule_time: string,
  schedule_config: object,
  deployed_at: string
}
```

These were added in the previous deployment feature implementation.

## Summary

The sidebar now provides complete visibility into automation deployment status and schedule configuration, making it easy for users to:
- ✅ See which automations are active
- ✅ View schedule details at a glance
- ✅ Identify paused or failed automations
- ✅ Track when automations were deployed
- ✅ Manage their workflow library efficiently

All changes maintain the emerald color theme and enhance the user experience with clear visual indicators! 🎨✨
