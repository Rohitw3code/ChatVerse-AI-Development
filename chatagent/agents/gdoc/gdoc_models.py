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

class GDocFormatTextInput(BaseModel):
    document_id: str = Field(..., description="The Google Doc ID")
    start_index: int = Field(..., description="Starting position of text to format")
    end_index: int = Field(..., description="Ending position of text to format")
    bold: Optional[bool] = Field(None, description="Apply bold formatting")
    italic: Optional[bool] = Field(None, description="Apply italic formatting")
    underline: Optional[bool] = Field(None, description="Apply underline formatting")
    font_size: Optional[int] = Field(None, description="Font size in points (e.g., 12, 14, 18)")
    font_family: Optional[str] = Field(None, description="Font family name (e.g., 'Arial', 'Times New Roman', 'Calibri')")
    text_color_red: Optional[float] = Field(None, description="Red color component (0.0 to 1.0)", ge=0.0, le=1.0)
    text_color_green: Optional[float] = Field(None, description="Green color component (0.0 to 1.0)", ge=0.0, le=1.0)
    text_color_blue: Optional[float] = Field(None, description="Blue color component (0.0 to 1.0)", ge=0.0, le=1.0)
    heading_level: Optional[int] = Field(None, description="Heading level: 1 (Title), 2 (Heading 1), 3 (Heading 2), 4 (Heading 3)", ge=1, le=4)
    alignment: Optional[str] = Field(None, description="Text alignment: 'START' (left), 'CENTER', 'END' (right), 'JUSTIFIED'")

class GDocColorTextInput(BaseModel):
    document_id: str = Field(..., description="The Google Doc ID")
    start_index: int = Field(..., description="Starting position of text to color")
    end_index: int = Field(..., description="Ending position of text to color")
    red: float = Field(..., description="Red color component (0.0 to 1.0)", ge=0.0, le=1.0)
    green: float = Field(..., description="Green color component (0.0 to 1.0)", ge=0.0, le=1.0)
    blue: float = Field(..., description="Blue color component (0.0 to 1.0)", ge=0.0, le=1.0)

class GDocHeadingInput(BaseModel):
    document_id: str = Field(..., description="The Google Doc ID")
    start_index: int = Field(..., description="Starting position of text to make a heading")
    end_index: int = Field(..., description="Ending position of text to make a heading")
    heading_level: int = Field(..., description="Heading level: 1 (Title), 2 (Heading 1), 3 (Heading 2), 4 (Heading 3)", ge=1, le=4)

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

class GDocBulletListInput(BaseModel):
    document_id: str = Field(..., description="The Google Doc ID")
    start_index: int = Field(..., description="Starting position to apply list")
    end_index: int = Field(..., description="Ending position to apply list")
    list_type: Optional[str] = Field("bullet", description="List type: 'bullet' or 'numbered'")

class GDocNumberedListInput(BaseModel):
    document_id: str = Field(..., description="The Google Doc ID")
    start_index: int = Field(..., description="Starting position to apply numbered list")
    end_index: int = Field(..., description="Ending position to apply numbered list")


