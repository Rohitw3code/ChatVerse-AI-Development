"""
Google Docs Models Module
Defines the input schemas for Google Docs tools.
"""

from pydantic import BaseModel, Field

class GDocCreateInput(BaseModel):
    title: str = Field(..., description="The title of the new Google Doc to create")
    content: str | None = Field(None, description="Optional initial content to insert into the document")

class GDocAppendTextInput(BaseModel):
    document_id: str = Field(..., description="The target Google Doc ID")
    text: str = Field(..., description="The text to append to the document")
