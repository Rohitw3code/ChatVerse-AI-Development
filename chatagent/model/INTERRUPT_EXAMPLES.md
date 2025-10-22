# Interrupt System - Code Examples

This file demonstrates practical examples of using the new interrupt system.

## Example 1: Gmail Send Tool (Before & After)

### Before (Using Raw Dictionaries)
```python
@tool("send_gmail", args_schema=SendGmailInput)
def send_gmail(recipient: str, subject: str, body: str) -> str:
    params = SendGmailInput(recipient=recipient, subject=subject, body=body)
    content = f"""{body}"""

    # ❌ Raw dictionary - error-prone
    approval = interrupt({
        "name": "send_gmail",
        "type": "input_option",
        "data": {
            "title": "Do you want to send this Gmail??",
            "content": content,
            "options": ["Yes", "No"],
        },
    })

    if approval.strip().lower() == "yes":
        return f"✅ Gmail sent to {recipient}"
    elif approval.strip().lower() == "no":
        return "Gmail cancelled"
    else:
        return f"Unexpected response: {approval}"
```

### After (Using InterruptRequest)
```python
from chatagent.model.interrupt_model import InterruptRequest

@tool("send_gmail", args_schema=SendGmailInput)
def send_gmail(recipient: str, subject: str, body: str) -> str:
    params = SendGmailInput(recipient=recipient, subject=subject, body=body)
    
    # ✅ Structured and validated
    interrupt_request = InterruptRequest.create_input_option(
        name="send_gmail",
        title="Do you want to send this Gmail??",
        content=body,
        options=["Yes", "No"]
    )
    
    approval = interrupt(interrupt_request.to_dict())

    if approval.strip().lower() == "yes":
        return f"✅ Gmail sent to {recipient}"
    elif approval.strip().lower() == "no":
        return "Gmail cancelled"
    else:
        return f"Unexpected response: {approval}"
```

### After (Using Helper Functions - Recommended)
```python
from chatagent.model.interrupt_helpers import ask_user_option, is_affirmative, is_negative

@tool("send_gmail", args_schema=SendGmailInput)
def send_gmail(recipient: str, subject: str, body: str) -> str:
    params = SendGmailInput(recipient=recipient, subject=subject, body=body)
    
    # ✅ Simplest and most readable
    approval = ask_user_option(
        name="send_gmail",
        question="Do you want to send this Gmail??",
        options=["Yes", "No"],
        context=body
    )

    if is_affirmative(approval):
        return f"✅ Gmail sent to {recipient}"
    elif is_negative(approval):
        return "Gmail cancelled"
    else:
        return f"Processing custom message: {approval}"
```

## Example 2: Ask Human for Input

### Before
```python
@tool("ask_human")
def ask_human(params: str) -> str:
    # ❌ Raw dictionary
    user_input = interrupt({
        "type": "input_field",
        "data": {"title": params}
    })
    return f"AI: {params}\nHuman: {user_input}"
```

### After (Using Helper)
```python
from chatagent.model.interrupt_helpers import ask_user_input

@tool("ask_human")
def ask_human(params: str) -> str:
    # ✅ Clear and simple
    user_input = ask_user_input(
        name="ask_human",
        question=params
    )
    return f"AI: {params}\nHuman: {user_input}"
```

## Example 3: Platform Connection

### Before
```python
@tool("login_to_gmail")
def login_to_gmail(params: str) -> str:
    # ❌ Raw dictionary with complex nesting
    user_input = interrupt({
        "name": "gmail_error",
        "type": "connect",
        "platform": "gmail",
        "data": {"title": params, "content": ""},
    })
    return str(user_input)
```

### After (Using Helper)
```python
from chatagent.model.interrupt_helpers import ask_user_connect

@tool("login_to_gmail")
def login_to_gmail(params: str) -> str:
    # ✅ Self-documenting and type-safe
    result = ask_user_connect(
        platform="gmail",
        name="gmail_error",
        message=params
    )
    return str(result)
```

## Example 4: Complex Multi-Option Dialog

```python
from chatagent.model.interrupt_helpers import ask_user_option, parse_option_response

@tool("schedule_email")
def schedule_email(recipient: str, subject: str, body: str) -> str:
    """Send email now, later, or save as draft."""
    
    response = ask_user_option(
        name="email_action",
        question="What would you like to do with this email?",
        options=["Send Now", "Send Later", "Save as Draft", "Cancel"],
        context=f"To: {recipient}\nSubject: {subject}\n\n{body}"
    )
    
    if parse_option_response(response, "Send Now"):
        return f"✅ Email sent immediately to {recipient}"
    
    elif parse_option_response(response, "Send Later"):
        # Request schedule time
        time = ask_user_input(
            name="schedule_time",
            question="When should this email be sent?",
            placeholder="e.g., tomorrow at 9am"
        )
        return f"✅ Email scheduled for {time}"
    
    elif parse_option_response(response, "Save as Draft"):
        return "✅ Email saved as draft"
    
    elif parse_option_response(response, "Cancel"):
        return "Email cancelled"
    
    else:
        # User provided custom input instead of selecting option
        return f"Processing custom request: {response}"
```

## Example 5: Error Recovery with Platform Connection

```python
from chatagent.model.interrupt_helpers import ask_user_connect
from supabase_client import supabase

@tool("fetch_instagram_posts")
def fetch_instagram_posts(count: int = 10) -> str:
    """Fetch recent Instagram posts with error recovery."""
    
    try:
        # Try to fetch posts
        result = get_instagram_posts(count)
        return result
        
    except AuthenticationError as e:
        # Request re-authentication
        connection_result = ask_user_connect(
            platform="instagram",
            name="instagram_reauth",
            message="Your Instagram session has expired. Please reconnect.",
            error_message=str(e)
        )
        
        # Retry after reconnection
        return get_instagram_posts(count)
        
    except Exception as e:
        return f"Error fetching posts: {str(e)}"
```

## Example 6: Input Validation with Retry

```python
from chatagent.model.interrupt_helpers import ask_user_input
import re

@tool("get_valid_email")
def get_valid_email() -> str:
    """Request and validate email address from user."""
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    max_attempts = 3
    
    for attempt in range(max_attempts):
        email = ask_user_input(
            name=f"email_input_attempt_{attempt + 1}",
            question="Please enter a valid email address:",
            placeholder="user@example.com"
        )
        
        if re.match(email_pattern, email):
            return f"✅ Valid email: {email}"
        
        if attempt < max_attempts - 1:
            ask_user_input(
                name=f"email_error_{attempt + 1}",
                question=f"Invalid email format. Please try again ({max_attempts - attempt - 1} attempts remaining):",
                placeholder="user@example.com"
            )
    
    return "❌ Failed to get valid email after maximum attempts"
```

## Example 7: Conditional Interrupt Based on Data

```python
from chatagent.model.interrupt_helpers import ask_user_option, is_affirmative

@tool("smart_email_send")
def smart_email_send(recipient: str, subject: str, body: str, priority: str = "normal") -> str:
    """Send email with smart confirmation based on priority."""
    
    # Only ask for confirmation on high-priority emails
    if priority.lower() == "high":
        confirmation = ask_user_option(
            name="high_priority_confirm",
            question="This is a HIGH PRIORITY email. Confirm send?",
            options=["Yes", "No"],
            context=f"To: {recipient}\nSubject: {subject}\n\n{body}"
        )
        
        if not is_affirmative(confirmation):
            return "High priority email cancelled by user"
    
    # Send email
    return f"✅ Email sent to {recipient} (Priority: {priority})"
```

## Example 8: Chained Interrupts

```python
from chatagent.model.interrupt_helpers import ask_user_option, ask_user_input, is_affirmative

@tool("compose_and_send_email")
def compose_and_send_email() -> str:
    """Interactive email composition with multiple steps."""
    
    # Step 1: Get recipient
    recipient = ask_user_input(
        name="email_recipient",
        question="Who is the recipient?",
        placeholder="user@example.com"
    )
    
    # Step 2: Get subject
    subject = ask_user_input(
        name="email_subject",
        question="What is the subject?",
        placeholder="Enter subject line"
    )
    
    # Step 3: Get body
    body = ask_user_input(
        name="email_body",
        question="Enter the email body:",
        placeholder="Type your message here..."
    )
    
    # Step 4: Preview and confirm
    preview_response = ask_user_option(
        name="email_preview",
        question="Review and confirm:",
        options=["Send", "Edit", "Cancel"],
        context=f"To: {recipient}\nSubject: {subject}\n\n{body}"
    )
    
    if preview_response.lower() == "send":
        return f"✅ Email sent to {recipient}"
    elif preview_response.lower() == "edit":
        return "Please start over to edit the email"
    else:
        return "Email cancelled"
```

## Benefits Demonstrated

1. **Type Safety**: Pydantic validates all inputs
2. **Readability**: Helper functions read like natural language
3. **Consistency**: Same pattern across all interrupts
4. **Maintainability**: Easy to update interrupt logic in one place
5. **Error Prevention**: Compile-time checking catches issues early
6. **Flexibility**: Can still use full InterruptRequest for complex cases
