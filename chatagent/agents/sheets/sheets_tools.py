"""
Google Sheets Tools Module
Contains all Google Sheets-related tools and their implementations.
No hardcoded prompts - all prompts are managed through agents_config.py
"""

from typing import Annotated, Optional, List, Dict, Any
from langgraph.prebuilt import InjectedState
from chatagent.utils import State
from chatagent.node_registry import NodeRegistry
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.types import interrupt
from pydantic import BaseModel, Field
from chatagent.config.init import non_stream_llm
from chatagent.utils import usages, log_tool_event
from langchain_community.callbacks import get_openai_callback
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from supabase_client import supabase
from chatagent.model.tool_output import ToolOutput
from chatagent.model.interrupt_model import InterruptRequest
from chatagent.agents.sheets.sheets_models import (
    SheetsInput,
    CreateSpreadsheetInput,
    ReadRangeInput,
    WriteDataInput,
    AppendDataInput,
    ClearRangeInput,
    CreateSheetInput,
    DeleteSheetInput,
    FormatCellsInput,
    SearchSheetsInput,
    SortDataInput,
    ShareSpreadsheetInput,
    SpreadsheetAnalysisInput,
    FormulaInput,
    SpreadsheetDraft,
)
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from chatagent.utils import get_user_id
import os
import json

load_dotenv()

# Load Google Sheets credentials from sheet.json
sheet_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "sheet.json")
with open(sheet_json_path, 'r') as f:
    sheet_config = json.load(f)
    google_client_id = sheet_config["web"]["client_id"]
    google_client_secret = sheet_config["web"]["client_secret"]


@tool("verify_sheets_connection")
def verify_sheets_connection(config: RunnableConfig):
    """
    Verifies if the user's Google Sheets account is connected.
    Returns a success message if connected, otherwise indicates that authentication is required.
    """
    user_id = get_user_id(config)

    log_tool_event(
        tool_name="verify_sheets_connection",
        status="started",
        params={"platform_user_id": user_id},
        parent_node="sheets_agent_node",
    )

    existing = (
        supabase.table("connected_accounts")
        .select("platform_user_id")
        .eq("provider_id", user_id)
        .eq("platform", "google_sheets")
        .execute()
    )
    
    if existing.data:
        tool_output = f"✅ Google Sheets is connected and ready to use"
        log_tool_event(
            tool_name="verify_sheets_connection",
            status="success",
            params={},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output
    else:
        tool_output = "❌ Google Sheets account is not connected. Please connect your Google account to use Sheets."
        log_tool_event(
            tool_name="verify_sheets_connection",
            status="failed",
            params={},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("create_spreadsheet", args_schema=CreateSpreadsheetInput)
def create_spreadsheet(title: str, sheet_names: Optional[List[str]] = None, config: RunnableConfig = None):
    """
    Creates a new Google Sheets spreadsheet with the specified title and optional sheet names.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="create_spreadsheet",
        status="started",
        params={"title": title, "sheet_names": sheet_names},
        parent_node="sheets_agent_node",
    )

    
    sheets_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "google_sheets")
        .execute()
    )
    print("*"*40)
    print("creds : ",user_id)
    print("sheets_data : ",sheets_data)
    print("*"*40)


    if not sheets_data.data:
        tool_output = "❌ Google Sheets account is not connected. Please connect your Google account first."
        log_tool_event(
            tool_name="create_spreadsheet",
            status="failed",
            params={"title": title},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output

    data = sheets_data.data[0]
    creds = Credentials.from_authorized_user_info(
        {
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "scopes": data["scopes"],
            "universe_domain": "googleapis.com",
        }
    )

    service = build("sheets", "v4", credentials=creds)

    try:
        spreadsheet_body = {
            "properties": {
                "title": title
            }
        }
        
        if sheet_names:
            spreadsheet_body["sheets"] = [
                {"properties": {"title": name}} for name in sheet_names
            ]

        result = service.spreadsheets().create(body=spreadsheet_body).execute()
        spreadsheet_id = result.get('spreadsheetId')
        spreadsheet_url = result.get('spreadsheetUrl')

        tool_output = f"""
✅ Spreadsheet created successfully!
📋 Title: {title}
🆔 Spreadsheet ID: {spreadsheet_id}
🔗 URL: {spreadsheet_url}
📝 Sheets: {sheet_names if sheet_names else ['Sheet1']}
        """

        log_tool_event(
            tool_name="create_spreadsheet",
            status="success",
            params={"title": title, "sheet_names": sheet_names},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output, show=True, type="format"),
        )
        return tool_output

    except Exception as e:
        tool_output = f"❌ Error creating spreadsheet: {str(e)}"
        log_tool_event(
            tool_name="create_spreadsheet",
            status="failed",
            params={"title": title},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("read_sheet_data", args_schema=ReadRangeInput)
def read_sheet_data(spreadsheet_id: str, range_name: str, config: RunnableConfig = None):
    """
    Reads data from a specific range in a Google Sheets spreadsheet.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="read_sheet_data",
        status="started",
        params={"spreadsheet_id": spreadsheet_id, "range_name": range_name},
        parent_node="sheets_agent_node",
    )
    
    sheets_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "google_sheets")
        .execute()
    )

    if not sheets_data.data:
        tool_output = "❌ Google Sheets account is not connected."
        return tool_output

    data = sheets_data.data[0]
    creds = Credentials.from_authorized_user_info(
        {
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "scopes": data["scopes"],
            "universe_domain": "googleapis.com",
        }
    )

    service = build("sheets", "v4", credentials=creds)

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            tool_output = f"📊 No data found in range {range_name}"
        else:
            tool_output = f"📊 Data from {range_name}:\n\n"
            for i, row in enumerate(values):
                tool_output += f"Row {i+1}: {row}\n"

        log_tool_event(
            tool_name="read_sheet_data",
            status="success",
            params={"spreadsheet_id": spreadsheet_id, "range_name": range_name},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output, show=True, type="format"),
        )
        return tool_output

    except Exception as e:
        tool_output = f"❌ Error reading sheet data: {str(e)}"
        log_tool_event(
            tool_name="read_sheet_data",
            status="failed",
            params={"spreadsheet_id": spreadsheet_id, "range_name": range_name},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("write_sheet_data", args_schema=WriteDataInput)
def write_sheet_data(spreadsheet_id: str, range_name: str, values: List[List], value_input_option: str = "RAW", config: RunnableConfig = None):
    """
    Writes data to a specific range in a Google Sheets spreadsheet.
    """
    print(f"\n###############{values}")
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="write_sheet_data",
        status="started",
        params={"spreadsheet_id": spreadsheet_id, "range_name": range_name},
        parent_node="sheets_agent_node",
    )
    
    sheets_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "google_sheets")
        .execute()
    )

    if not sheets_data.data:
        tool_output = "❌ Google Sheets account is not connected."
        return tool_output

    data = sheets_data.data[0]
    creds = Credentials.from_authorized_user_info(
        {
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "scopes": data["scopes"],
            "universe_domain": "googleapis.com",
        }
    )

    service = build("sheets", "v4", credentials=creds)

    try:
        body = {
            'values': values
        }
        
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body
        ).execute()

        updated_cells = result.get('updatedCells', 0)
        tool_output = f"✅ Successfully updated {updated_cells} cells in range {range_name}"

        log_tool_event(
            tool_name="write_sheet_data",
            status="success",
            params={"spreadsheet_id": spreadsheet_id, "range_name": range_name},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output, show=True),
        )
        return tool_output

    except Exception as e:
        tool_output = f"❌ Error writing sheet data: {str(e)}"
        log_tool_event(
            tool_name="write_sheet_data",
            status="failed",
            params={"spreadsheet_id": spreadsheet_id, "range_name": range_name},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("append_sheet_data", args_schema=AppendDataInput)
def append_sheet_data(spreadsheet_id: str, range_name: str, values: List[List], value_input_option: str = "RAW", config: RunnableConfig = None):
    """
    Appends data to a Google Sheets spreadsheet.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="append_sheet_data",
        status="started",
        params={"spreadsheet_id": spreadsheet_id, "range_name": range_name},
        parent_node="sheets_agent_node",
    )
    
    sheets_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "google_sheets")
        .execute()
    )

    if not sheets_data.data:
        tool_output = "❌ Google Sheets account is not connected."
        return tool_output

    data = sheets_data.data[0]
    creds = Credentials.from_authorized_user_info(
        {
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "scopes": data["scopes"],
            "universe_domain": "googleapis.com",
        }
    )

    service = build("sheets", "v4", credentials=creds)

    try:
        body = {
            'values': values
        }
        
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

        updated_cells = result.get('updates', {}).get('updatedCells', 0)
        tool_output = f"✅ Successfully appended {updated_cells} cells to {range_name}"

        log_tool_event(
            tool_name="append_sheet_data",
            status="success",
            params={"spreadsheet_id": spreadsheet_id, "range_name": range_name},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output, show=True),
        )
        return tool_output

    except Exception as e:
        tool_output = f"❌ Error appending sheet data: {str(e)}"
        log_tool_event(
            tool_name="append_sheet_data",
            status="failed",
            params={"spreadsheet_id": spreadsheet_id, "range_name": range_name},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("clear_sheet_data", args_schema=ClearRangeInput)
def clear_sheet_data(spreadsheet_id: str, range_name: str, config: RunnableConfig = None):
    """
    Clears data from a specific range in a Google Sheets spreadsheet.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="clear_sheet_data",
        status="started",
        params={"spreadsheet_id": spreadsheet_id, "range_name": range_name},
        parent_node="sheets_agent_node",
    )
    
    sheets_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "google_sheets")
        .execute()
    )

    if not sheets_data.data:
        tool_output = "❌ Google Sheets account is not connected."
        return tool_output

    data = sheets_data.data[0]
    creds = Credentials.from_authorized_user_info(
        {
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "scopes": data["scopes"],
            "universe_domain": "googleapis.com",
        }
    )

    service = build("sheets", "v4", credentials=creds)

    try:
        result = service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

        tool_output = f"✅ Successfully cleared data from range {range_name}"

        log_tool_event(
            tool_name="clear_sheet_data",
            status="success",
            params={"spreadsheet_id": spreadsheet_id, "range_name": range_name},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output, show=True),
        )
        return tool_output

    except Exception as e:
        tool_output = f"❌ Error clearing sheet data: {str(e)}"
        log_tool_event(
            tool_name="clear_sheet_data",
            status="failed",
            params={"spreadsheet_id": spreadsheet_id, "range_name": range_name},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("list_spreadsheets")
def list_spreadsheets(config: RunnableConfig = None):
    """
    Lists all spreadsheets accessible to the user's Google account.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="list_spreadsheets",
        status="started",
        params={},
        parent_node="sheets_agent_node",
    )
    
    sheets_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "google_sheets")
        .execute()
    )

    if not sheets_data.data:
        tool_output = "❌ Google Sheets account is not connected."
        return tool_output

    data = sheets_data.data[0]
    creds = Credentials.from_authorized_user_info(
        {
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "scopes": data["scopes"],
            "universe_domain": "googleapis.com",
        }
    )

    try:
        drive_service = build("drive", "v3", credentials=creds)
        
        results = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.spreadsheet'",
            fields="files(id, name, createdTime, modifiedTime)"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            tool_output = "📊 No spreadsheets found in your Google Drive."
        else:
            tool_output = f"📊 Found {len(files)} spreadsheet(s):\n\n"
            for file in files:
                tool_output += f"📋 {file['name']}\n"
                tool_output += f"   ID: {file['id']}\n"
                tool_output += f"   Created: {file.get('createdTime', 'Unknown')}\n"
                tool_output += f"   Modified: {file.get('modifiedTime', 'Unknown')}\n\n"

        log_tool_event(
            tool_name="list_spreadsheets",
            status="success",
            params={},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output, show=True, type="format"),
        )
        return tool_output

    except Exception as e:
        tool_output = f"❌ Error listing spreadsheets: {str(e)}"
        log_tool_event(
            tool_name="list_spreadsheets",
            status="failed",
            params={},
            parent_node="sheets_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("draft_spreadsheet")
def draft_spreadsheet(
    params: str = Field(..., description="The request or instructions for the spreadsheet structure")
) -> dict:
    """
    Drafts a spreadsheet structure based on user requirements using AI.
    """
    log_tool_event(
        tool_name="draft_spreadsheet",
        status="started",
        params={"request": params},
        parent_node="sheets_agent_node",
    )

    sheets_prompt = f"""
    Spreadsheet Request: {params}

    Create a professional spreadsheet structure:
    1. Title for the spreadsheet
    2. Sheet names and their purposes
    3. Column headers and data structure
    4. Sample data if applicable
    5. Keep it organized and professional
    """

    with get_openai_callback() as cb:
        tool_output = non_stream_llm.with_structured_output(SpreadsheetDraft).invoke(
            [
                SystemMessage(
                    content=f"You are a professional spreadsheet designer. {sheets_prompt}"
                ),
                HumanMessage(content=params),
            ]
        )

    usage = usages(cb)

    result = {
        "title": tool_output.title,
        "sheets": tool_output.sheets,
        "data_structure": tool_output.data_structure
    }
    
    log_tool_event(
        tool_name="draft_spreadsheet",
        status="success",
        params={"request": params},
        parent_node="sheets_agent_node",
        tool_output=ToolOutput(output=result, type="draft_spreadsheet", show=True),
        usages=usage,
    )

    return result


@tool("ask_human")
def ask_human(
    params: str = Field(..., description="What clarification is needed from the user")
) -> str:
    """
    Asks the user for clarification or missing information for Google Sheets operations.
    """
    interrupt_request = InterruptRequest.create_input_field(
        name="ask_human",
        title=params
    )

    user_input = interrupt(interrupt_request.to_dict())
    return f"AI: {params}\nHuman: {user_input}"


@tool("login_to_sheets")
def login_to_sheets(params: str = Field(..., description="error reason")) -> str:
    """
    Handles Google Sheets authentication issues and prompts user to connect.
    """
    print("Google Sheets connection issue")
    
    interrupt_request = InterruptRequest.create_connect(
        name="sheets_error",
        platform="sheets",
        title=params,
        content=""
    )
    
    user_input = interrupt(interrupt_request.to_dict())
    return str(user_input)


def get_sheets_tool_registry() -> NodeRegistry:
    """
    Returns a NodeRegistry containing all Google Sheets tools.
    This function centralizes tool registration.
    """
    sheets_tool_register = NodeRegistry()
    sheets_tool_register.add("verify_sheets_connection", verify_sheets_connection, "tool")
    sheets_tool_register.add("create_spreadsheet", create_spreadsheet, "tool")
    sheets_tool_register.add("read_sheet_data", read_sheet_data, "tool")
    sheets_tool_register.add("write_sheet_data", write_sheet_data, "tool")
    sheets_tool_register.add("append_sheet_data", append_sheet_data, "tool")
    sheets_tool_register.add("clear_sheet_data", clear_sheet_data, "tool")
    sheets_tool_register.add("list_spreadsheets", list_spreadsheets, "tool")
    sheets_tool_register.add("draft_spreadsheet", draft_spreadsheet, "tool")
    sheets_tool_register.add("ask_human", ask_human, "tool")
    sheets_tool_register.add("login_to_sheets", login_to_sheets, "tool")
    return sheets_tool_register