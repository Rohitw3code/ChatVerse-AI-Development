"""
Google Forms Models Module
Contains all Pydantic models specific to Google Forms agent operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union


class FormsInput(BaseModel):
    """Base schema for Google Forms operations."""
    form_id: str = Field(..., description="The ID of the Google Form")


class CreateFormInput(BaseModel):
    """Schema for creating a new form."""
    title: str = Field(..., description="The title/name of the form. Will be displayed at the top of the form.")
    description: Optional[str] = Field(None, description="Optional description of the form explaining its purpose to respondents.")


class AddQuestionInput(BaseModel):
    """Schema for adding a question to a form."""
    form_id: str = Field(..., description="The ID of the Google Form to add the question to")
    question_text: str = Field(..., description="The text of the question to add")
    question_type: str = Field(
        "MULTIPLE_CHOICE",
        description="Type of question: MULTIPLE_CHOICE, CHECKBOX, SHORT_ANSWER, PARAGRAPH, DROPDOWN, LINEAR_SCALE, DATE, TIME"
    )
    options: Optional[List[str]] = Field(None, description="List of options for multiple choice, checkbox, or dropdown questions")
    required: bool = Field(False, description="Whether the question is required")


class GetFormInput(BaseModel):
    """Schema for getting form details."""
    form_id: str = Field(..., description="The ID of the Google Form to retrieve")


class GetResponsesInput(BaseModel):
    """Schema for getting form responses."""
    form_id: str = Field(..., description="The ID of the Google Form to get responses from")
    max_results: Optional[int] = Field(None, description="Maximum number of responses to retrieve")


class UpdateFormInput(BaseModel):
    """Schema for updating form settings."""
    form_id: str = Field(..., description="The ID of the Google Form to update")
    title: Optional[str] = Field(None, description="New title for the form")
    description: Optional[str] = Field(None, description="New description for the form")


class DeleteFormInput(BaseModel):
    """Schema for deleting a form."""
    form_id: str = Field(..., description="The ID of the Google Form to delete")


class ShareFormInput(BaseModel):
    """Schema for sharing a form."""
    form_id: str = Field(..., description="The ID of the Google Form to share")
    email: str = Field(..., description="Email address to share with")
    role: str = Field("reader", description="Permission level: reader or writer")


class FormQuestionSchema(BaseModel):
    """Schema for a form question."""
    question_text: str = Field(..., description="The text of the question")
    question_type: str = Field(..., description="Type of question")
    options: Optional[List[str]] = Field(None, description="List of options if applicable")
    required: bool = Field(False, description="Whether the question is required")


class FormDraft(BaseModel):
    """Schema for form draft with structure."""
    title: str = Field(..., description="The title of the form")
    description: str = Field(..., description="Description explaining the purpose of the form")
    questions: List[FormQuestionSchema] = Field(..., description="List of questions for the form")


class SearchFormsInput(BaseModel):
    """Schema for searching forms."""
    query: Optional[str] = Field(None, description="Search query to filter forms by name")
    max_results: int = Field(10, description="Maximum number of forms to return")


class FormAnalysisInput(BaseModel):
    """Schema for analyzing form responses."""
    form_id: str = Field(..., description="The ID of the Google Form to analyze")
    analysis_type: str = Field(
        "summary",
        description="Type of analysis: summary, detailed, statistics, charts"
    )
