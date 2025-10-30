"""
Google Docs Models Module
Defines the input schemas for Google Docs tools.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class GDocCreateInput(BaseModel):
    title: str = Field(..., description="The title/name of the new Google Doc to create")
    content: str | None = Field(None, description="Optional initial text content to insert into the document")

class GDocAppendTextInput(BaseModel):
    document_id: str = Field(..., description="The Google Doc ID (found in the URL after /document/d/)")
    text: str = Field(..., description="The text content to append at the end of the document")

class GDocInsertTextInput(BaseModel):
    document_id: str = Field(..., description="The Google Doc ID")
    text: str = Field(..., description="The text to insert")
    index: int = Field(..., description="Position index where to insert text (1 is start of document)")

class GDocReadInput(BaseModel):
    document_id: str = Field(..., description="The Google Doc ID to read")

class GDocListDocsInput(BaseModel):
    max_results: Optional[int] = Field(10, description="Maximum number of documents to return (default 10)")

class GDocDeleteTextInput(BaseModel):
    document_id: str = Field(..., description="The Google Doc ID")
    start_index: int = Field(..., description="Starting position of text to delete")
    end_index: int = Field(..., description="Ending position of text to delete")

class GDocReplaceTextInput(BaseModel):
    document_id: str = Field(..., description="The Google Doc ID")
    find_text: str = Field(..., description="Text to find and replace")
    replace_text: str = Field(..., description="Text to replace with")
    match_case: Optional[bool] = Field(False, description="Whether to match case when finding text")

