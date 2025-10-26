"""
Google Sheets Models Module
Contains all Pydantic models specific to Google Sheets agent operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union


class SheetsInput(BaseModel):
    """Base schema for Google Sheets operations."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")


class CreateSpreadsheetInput(BaseModel):
    """Schema for creating a new spreadsheet."""
    title: str = Field(..., description="The title of the new spreadsheet")
    sheet_names: Optional[List[str]] = Field(None, description="Names of sheets to create (optional)")


class ReadRangeInput(BaseModel):
    """Schema for reading data from a specific range."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")
    range_name: str = Field(..., description="The range to read (e.g., 'Sheet1!A1:C10' or 'A1:C10')")


class WriteDataInput(BaseModel):
    """Schema for writing data to a spreadsheet."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")
    range_name: str = Field(..., description="The range to write to (e.g., 'Sheet1!A1:C10')")
    values: List[List[Union[str, int, float]]] = Field(..., description="2D array of values to write")
    value_input_option: str = Field("RAW", description="How values should be interpreted (RAW or USER_ENTERED)")


class AppendDataInput(BaseModel):
    """Schema for appending data to a spreadsheet."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")
    range_name: str = Field(..., description="The range to append to (e.g., 'Sheet1!A:C')")
    values: List[List[Union[str, int, float]]] = Field(..., description="2D array of values to append")
    value_input_option: str = Field("RAW", description="How values should be interpreted (RAW or USER_ENTERED)")


class ClearRangeInput(BaseModel):
    """Schema for clearing data from a range."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")
    range_name: str = Field(..., description="The range to clear (e.g., 'Sheet1!A1:C10')")


class CreateSheetInput(BaseModel):
    """Schema for creating a new sheet within a spreadsheet."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")
    sheet_name: str = Field(..., description="The name of the new sheet")
    rows: Optional[int] = Field(1000, description="Number of rows in the new sheet")
    columns: Optional[int] = Field(26, description="Number of columns in the new sheet")


class DeleteSheetInput(BaseModel):
    """Schema for deleting a sheet."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")
    sheet_id: int = Field(..., description="The ID of the sheet to delete")


class FormatCellsInput(BaseModel):
    """Schema for formatting cells."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")
    range_name: str = Field(..., description="The range to format (e.g., 'Sheet1!A1:C10')")
    format_options: Dict[str, Any] = Field(..., description="Formatting options (bold, color, etc.)")


class SearchSheetsInput(BaseModel):
    """Schema for searching within spreadsheet data."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")
    search_term: str = Field(..., description="The term to search for")
    sheet_name: Optional[str] = Field(None, description="Specific sheet to search in (optional)")


class SortDataInput(BaseModel):
    """Schema for sorting data in a range."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")
    range_name: str = Field(..., description="The range to sort")
    sort_column: int = Field(..., description="Column index to sort by (0-based)")
    ascending: bool = Field(True, description="Sort in ascending order")


class ShareSpreadsheetInput(BaseModel):
    """Schema for sharing a spreadsheet."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")
    email: str = Field(..., description="Email address to share with")
    role: str = Field("reader", description="Permission level: reader, writer, or owner")


class SpreadsheetAnalysisInput(BaseModel):
    """Schema for analyzing spreadsheet data."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")
    analysis_type: str = Field(..., description="Type of analysis: summary, statistics, charts")
    range_name: Optional[str] = Field(None, description="Specific range to analyze (optional)")


class FormulaInput(BaseModel):
    """Schema for adding formulas to cells."""
    spreadsheet_id: str = Field(..., description="The ID of the Google Sheets spreadsheet")
    cell_range: str = Field(..., description="The cell or range to add formula to")
    formula: str = Field(..., description="The formula to add (e.g., '=SUM(A1:A10)')")


class SpreadsheetDraft(BaseModel):
    """Schema for spreadsheet draft with structure."""
    title: str = Field(..., description="The title of the spreadsheet")
    sheets: List[Dict[str, Any]] = Field(..., description="List of sheet configurations")
    data_structure: str = Field(..., description="Description of the data structure")