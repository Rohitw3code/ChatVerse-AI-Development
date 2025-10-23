"""
Gmail Models Module
Contains all Pydantic models specific to Gmail agent operations.
"""

from pydantic import BaseModel, Field
from typing import Optional


class SendGmailInput(BaseModel):
    """Schema for sending a Gmail via the send_gmail tool."""
    recipient: str = Field(..., description="The recipient's email address.")
    subject: str = Field(..., description="The subject line of the email.")
    body: str = Field(..., description="The full body content of the email.")


class GmailCount(BaseModel):
    """Schema for specifying number of Gmail messages to fetch."""
    message_count: int = Field(
        5, description="Number of Gmail messages to fetch. Defaults to 5."
    )


class GmailUnreadCount(BaseModel):
    """Schema for specifying number of unread Gmail messages to fetch."""
    message_count: int = Field(
        5, description="Number of unread Gmail messages to fetch. Defaults to 5."
    )


class GmailDraft(BaseModel):
    """Schema for Gmail draft with subject and body."""
    subject: str = Field(..., description="The subject line of the Gmail")
    body: str = Field(..., description="The professional Gmail body text")


class SearchGmailInput(BaseModel):
    """Schema for searching Gmail messages."""
    query: str = Field(..., description="Search query (e.g., 'from:example@gmail.com', 'subject:meeting', 'is:important')")
    max_results: int = Field(10, description="Maximum number of results to return. Defaults to 10.")


class EmailIdInput(BaseModel):
    """Schema for operations requiring an email ID."""
    email_id: str = Field(..., description="The Gmail message ID")


class ReplyEmailInput(BaseModel):
    """Schema for replying to an email."""
    email_id: str = Field(..., description="The Gmail message ID to reply to")
    body: str = Field(..., description="The reply message body")


class ForwardEmailInput(BaseModel):
    """Schema for forwarding an email."""
    email_id: str = Field(..., description="The Gmail message ID to forward")
    recipient: str = Field(..., description="The recipient's email address")
    additional_message: Optional[str] = Field(None, description="Optional message to add before forwarded content")


class LabelOperationInput(BaseModel):
    """Schema for adding/removing labels to/from emails."""
    email_id: str = Field(..., description="The Gmail message ID")
    label_ids: list[str] = Field(..., description="List of label IDs to add or remove")
