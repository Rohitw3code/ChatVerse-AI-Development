"""
Research Models Module
Contains all Pydantic models specific to Research agent operations.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class PersonProfile(BaseModel):
    """Schema for LinkedIn person profile."""
    id: str = Field(..., description="Unique person ID (e.g., LinkedIn ID)")
    full_name: str = Field(..., description="Full name of the person")
    headline: Optional[str] = Field(
        None, description="Professional headline or current role"
    )
    organization: Optional[str] = Field(
        None, description="Current company or organization"
    )
    location: Optional[str] = Field(None, description="Geographic location")
    url: Optional[str] = Field(None, description="Profile URL (e.g., LinkedIn)")
    image_url: Optional[str] = Field(None, description="Profile picture URL")
    experience: Optional[List[str]] = Field(
        None, description="List of past experiences or roles"
    )
    education: Optional[List[str]] = Field(
        None, description="List of educational qualifications"
    )
    skills: Optional[List[str]] = Field(None, description="List of key skills")


class PersonList(BaseModel):
    """Schema for list of person profiles."""
    people: List[PersonProfile]


class JobItem(BaseModel):
    """Schema for LinkedIn job listing."""
    id: str = Field(..., description="Unique job ID")
    title: str = Field(..., description="Job title")
    organization: str = Field(..., description="Company or organization name")
    location: Optional[str] = Field(None, description="Job location if available")
    url: str = Field(..., description="Job posting URL")
    date_posted: str = Field(..., description="Date when the job was posted")


class JobList(BaseModel):
    """Schema for list of job listings."""
    jobs: List[JobItem]


class LinkedInSearch(BaseModel):
    """Input schema for the LinkedIn Person Search tool."""
    search_word: str = Field(
        ...,
        description="The search term for finding people (e.g., 'plastics ceo', 'software engineer at Google').",
    )
    page_number: int = Field(1, description="The page number for pagination.")
    page_size: int = Field(10, description="The number of results per page (max 10).")


class LinkedInJobSearch(BaseModel):
    """Input schema for LinkedIn job search."""
    title: str = Field(
        ..., description="Job title to search (e.g. Data Scientist, Backend Engineer)"
    )
    location: str = Field(
        ...,
        description="Location to search (e.g. United States, India, Remote, or queries like 'United States OR United Kingdom')",
    )
    limit: int = Field(10, description="Max number of results (<=10)")
    offset: int = Field(0, description="Pagination offset")


class Search(BaseModel):
    """Input schema for Tavily web search."""
    query: str = Field(..., description="User search query")
    limit: int = Field(5, description="Max results (<=10)")
    search_depth: str | None = Field(None, description="basic|advanced")
    time_range: str | None = Field(None, description="day|week|month|year")
