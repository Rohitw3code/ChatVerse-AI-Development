"""
Gmail Models Module
Contains all Pydantic models specific to Gmail agent operations.
"""

from pydantic import BaseModel, Field


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
