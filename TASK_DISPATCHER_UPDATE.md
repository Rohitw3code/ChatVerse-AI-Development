# Task Dispatcher Update - Authentication & Error Handling

## Changes Made

### 1. Removed Replanner Node
- **Reason**: Replanner node is not supported currently
- **Replaced with**: Graceful failure handling that ends the task with a user-friendly message

### 2. Added Authentication/Connection Error Detection
The dispatcher now detects when tasks fail due to authentication or connection issues by:
- Analyzing the last message content for auth-related keywords
- Keywords: 'not connected', 'not authenticated', 'authentication', 'connect your', 'token', 'login', 'connect', 'account is not connected'
- Identifying the platform (Gmail, Instagram, YouTube) that needs connection

### 3. Smart Retry Logic

#### For Authentication Errors:
- **First attempt**: Routes back to the same agent to retry
- **After 2 retries**: Ends gracefully with message asking user to connect their account
- Example message: *"Unable to complete the task. The gmail account is not connected. Please connect your account and try again, or I can help you with something else."*

#### For General Errors:
- **Max retries**: 3 attempts
- **After max retries**: Ends with helpful message
- Example message: *"I've tried multiple times but couldn't complete this task. There might be an issue with the request or required permissions. Please try rephrasing your request or provide more details."*

### 4. Updated System Prompt
Added new rules:
- **Rule 5**: If authentication or connection errors occur, route back to the same agent once to retry
- **Rule 6**: If repeated failures occur (agent reports no capabilities or auth issues), select 'END' to prevent infinite loops
- **Rule 7**: Keep reason brief and user-friendly

## Behavior Flow

### Scenario 1: Authentication Error
```
1. User asks: "Send an email to john@example.com"
2. Gmail agent responds: "Gmail account is not connected"
3. Dispatcher detects auth error (retry 1)
4. Routes back to Gmail agent
5. Gmail agent still reports not connected (retry 2)
6. Dispatcher ends gracefully with connection request message
```

### Scenario 2: General Task Failure
```
1. Task assigned to agent
2. Agent fails to complete (retry 1)
3. Dispatcher retries same agent (retry 2)
4. Agent fails again (retry 3)
5. Dispatcher ends with helpful error message
```

### Scenario 3: Successful Task
```
1. Task assigned to agent
2. Agent completes task successfully
3. Dispatcher marks task as completed
4. Routes to task_selection_node for next task
```

## Benefits

1. **Better User Experience**: Clear messages when authentication is needed
2. **No Infinite Loops**: Max retry limits prevent endless failures
3. **Smart Detection**: Automatically identifies platform needing connection
4. **Graceful Degradation**: Always ends with helpful message instead of crashing
5. **No Replanner Dependency**: Works without needing replanner node

## Platform Detection

The dispatcher can identify these platforms from error messages:
- **Gmail**: Keywords 'gmail' or 'email'
- **Instagram**: Keywords 'instagram' or 'insta'  
- **YouTube**: Keyword 'youtube'

## Status Codes

New status codes added:
- `auth_required`: Task failed due to missing authentication
- `max_retries_reached`: Task failed after maximum retry attempts

## Configuration

Default retry limits:
- `max_dispatch_retries`: 3 attempts
- `auth_retry_limit`: 2 attempts for auth errors

Can be configured in state:
```python
state = {
    "max_dispatch_retries": 3,  # Maximum general retries
    # ... other state
}
```

## Integration with Agents

Agents should use error tools when authentication is needed:
- Gmail: `gmail_error` tool
- Instagram: `instagram_error` tool
- YouTube: Should follow same pattern

These tools should include clear messages with keywords that the dispatcher can detect.

---

**Date**: October 21, 2025  
**Status**: ✅ Implemented
