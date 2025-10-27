# Gmail Tools Formatting Update

## Overview
Updated Gmail tools to properly handle email formatting and support both plain text and HTML emails.

## Changes Made

### 1. **Fixed Plain Text Formatting** (draft_gmail)
**Problem**: Gmail was showing markdown formatting (**, *, emojis) as raw text because Gmail doesn't render markdown.

**Solution**: 
- Removed markdown formatting instructions from the default prompt
- Changed default behavior to generate clean plain text emails
- Removed automatic emoji usage
- Uses simple line breaks and dashes for bullet points

**Before**:
```
- Use emojis where appropriate
- Use bullet points, **bold**, *italic*, and spacing
```

**After**:
```
- DO NOT use markdown formatting like **bold**, *italic*, or __underline__
- DO NOT use emojis unless explicitly requested
- Use plain text formatting only
- Gmail displays markdown as raw text, so avoid all markdown syntax
```

### 2. **Added HTML Email Support**
**New Feature**: Full HTML email support with automatic detection

**Implementation**:
- Added `MIMEMultipart` import for multipart emails
- Added regex import for HTML detection
- Modified `send_gmail()` to automatically detect HTML content
- Modified `reply_to_email()` to support HTML replies
- Creates multipart emails with both plain text and HTML versions

**How it Works**:
```python
# Automatically detects HTML tags in email body
is_html = bool(re.search(r'<[^>]+>', body))

if is_html:
    # Creates multipart message with:
    # 1. Plain text version (HTML tags stripped)
    # 2. HTML version (full HTML content)
else:
    # Sends plain text email
```

### 3. **Updated GmailDraft Model**
Added optional `is_html` field to track email format type:

```python
class GmailDraft(BaseModel):
    subject: str
    body: str
    is_html: bool = Field(default=False)  # NEW
```

### 4. **Enhanced Draft Prompt**
The `draft_gmail` prompt now has three modes:

**DEFAULT (Plain Text)**:
- Clean, professional plain text
- No markdown, no emojis
- Simple formatting with line breaks

**HTML Mode** (when user requests):
Triggered by keywords: "HTML", "styled", "formatted", "designed", "beautiful"
- Full HTML structure with tags
- Inline CSS styling
- Rich formatting support
- Example provided in prompt

**Custom Style**:
- Follows exact user requirements

## Usage Examples

### Plain Text Email (Default)
```python
# User: "Draft an email to john@example.com about the meeting tomorrow"
# Result: Clean plain text email with no markdown
```

### HTML Email
```python
# User: "Draft a styled HTML email to john@example.com about our product launch"
# Result: HTML email with proper tags and styling
```

### Custom Style
```python
# User: "Draft a formal email with bullet points (use emojis) to sarah@example.com"
# Result: Follows exact user requirements including emojis
```

## Benefits

1. **No More Raw Markdown**: Emails appear professional in Gmail without ** or * characters
2. **HTML Support**: Can send beautifully designed emails with colors, fonts, and styling
3. **Automatic Detection**: System automatically detects and handles HTML content
4. **Fallback Support**: HTML emails include plain text version for compatibility
5. **User Control**: Users can request specific formatting styles
6. **Reply Support**: HTML formatting works in email replies too

## Technical Details

### Multipart Email Structure
When HTML is detected, creates RFC-compliant multipart/alternative message:
```
multipart/alternative
├── text/plain (stripped HTML for fallback)
└── text/html (full HTML content)
```

### HTML Detection
Uses regex pattern to detect HTML tags: `r'<[^>]+>'`

### Files Modified
1. `chatagent/agents/gmail/gmail_tools.py`
   - Updated `draft_gmail()` prompt
   - Modified `send_gmail()` for HTML support
   - Modified `reply_to_email()` for HTML support
   - Added necessary imports

2. `chatagent/agents/gmail/gmail_models.py`
   - Added `is_html` field to `GmailDraft` model

## Testing Recommendations

1. **Plain Text Test**: Draft and send a simple email
2. **HTML Test**: Request "styled HTML email" and verify rendering
3. **Reply Test**: Reply to an email with HTML content
4. **Markdown Prevention**: Verify no ** or * in plain text emails
5. **Mixed Content**: Test with emails containing special characters

## Backward Compatibility

✅ Fully backward compatible - existing plain text emails continue to work
✅ Automatic detection means no code changes needed for existing flows
✅ HTML is opt-in through user request keywords
