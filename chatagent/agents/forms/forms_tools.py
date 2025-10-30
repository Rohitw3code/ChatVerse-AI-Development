"""
Google Forms Tools Module
Contains all Google Forms-related tools and their implementations.
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
from chatagent.agents.forms.forms_models import (
    FormsInput,
    CreateFormInput,
    AddQuestionInput,
    GetFormInput,
    GetResponsesInput,
    UpdateFormInput,
    DeleteFormInput,
    ShareFormInput,
    FormDraft,
    SearchFormsInput,
    FormAnalysisInput,
)
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from chatagent.utils import get_user_id
import os
import json

load_dotenv()

# Load Google Forms credentials from google_form.json
form_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "google_form.json")
with open(form_json_path, 'r') as f:
    form_config = json.load(f)
    google_client_id = form_config["web"]["client_id"]
    google_client_secret = form_config["web"]["client_secret"]


@tool("verify_forms_connection")
def verify_forms_connection(config: RunnableConfig):
    """
    Verifies if user's Google Forms account is connected. Use before performing any forms operations or when user asks about connection status.
    Returns success if connected, prompts authentication if not.
    """
    user_id = get_user_id(config)

    log_tool_event(
        tool_name="verify_forms_connection",
        status="started",
        params={"platform_user_id": user_id},
        parent_node="forms_agent_node",
    )

    existing = (
        supabase.table("connected_accounts")
        .select("platform_user_id")
        .eq("provider_id", user_id)
        .eq("platform", "google_forms")
        .execute()
    )
    
    if existing.data:
        tool_output = "Google Forms is connected and ready to use"
        log_tool_event(
            tool_name="verify_forms_connection",
            status="success",
            params={},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output
    else:
        tool_output = "Google Forms account is not connected. Please connect your Google account to use Forms."
        log_tool_event(
            tool_name="verify_forms_connection",
            status="failed",
            params={},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("create_form", args_schema=CreateFormInput)
def create_form(title: str, description: Optional[str] = None, config: RunnableConfig = None):
    """
    Creates a new Google Form with specified title and optional description. Use when user wants to create/make/start a new form.
    Examples: "create a form called Customer Feedback", "make a survey about employee satisfaction". Returns form ID and URL.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="create_form",
        status="started",
        params={"title": title, "description": description},
        parent_node="forms_agent_node",
    )

    forms_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "google_forms")
        .execute()
    )

    if not forms_data.data:
        tool_output = "Google Forms account is not connected. Please connect your Google account first."
        log_tool_event(
            tool_name="create_form",
            status="failed",
            params={"title": title},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output

    data = forms_data.data[0]
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

    service = build("forms", "v1", credentials=creds)

    try:
        # First create the form with only title (API limitation)
        form_body = {
            "info": {
                "title": title,
            }
        }

        result = service.forms().create(body=form_body).execute()
        form_id = result.get('formId')
        responder_uri = result.get('responderUri')
        
        # Get the edit URL (this is what users need to add questions)
        # The form edit URL uses the actual form ID
        edit_url = f"https://docs.google.com/forms/d/{form_id}/edit"
        
        # If description provided, update it using batchUpdate
        if description:
            update_requests = [{
                "updateFormInfo": {
                    "info": {
                        "title": title,
                        "description": description
                    },
                    "updateMask": "description"
                }
            }]
            service.forms().batchUpdate(
                formId=form_id,
                body={"requests": update_requests}
            ).execute()

        # Structured output for frontend
        output_data = {
            "title": title,
            "form_id": form_id,
            "form_url": responder_uri,
            "edit_url": edit_url,
            "description": description if description else None,
            "message": "Form created successfully"
        }

        log_tool_event(
            tool_name="create_form",
            status="success",
            params={"title": title, "description": description},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=output_data, show=True, type="form_created"),
        )
        return f"Form created successfully: {title}\nForm ID: {form_id}\nForm URL: {responder_uri}\nEdit URL: {edit_url}\n\nIMPORTANT: Use form ID '{form_id}' to add questions to this form."

    except Exception as e:
        tool_output = f"Error creating form: {str(e)}"
        log_tool_event(
            tool_name="create_form",
            status="failed",
            params={"title": title},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("add_form_question", args_schema=AddQuestionInput)
def add_form_question(
    form_id: str,
    question_text: str,
    question_type: str = "MULTIPLE_CHOICE",
    options: Optional[List[str]] = None,
    required: bool = False,
    config: RunnableConfig = None
):
    """
    Adds a question to an existing Google Form. Use when user wants to add/insert questions to a form.
    Question types: MULTIPLE_CHOICE, CHECKBOX, SHORT_ANSWER, PARAGRAPH, DROPDOWN, LINEAR_SCALE, DATE, TIME.
    For choice-based questions (MULTIPLE_CHOICE, CHECKBOX, DROPDOWN), provide options list.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="add_form_question",
        status="started",
        params={"form_id": form_id, "question_text": question_text, "question_type": question_type},
        parent_node="forms_agent_node",
    )

    forms_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "google_forms")
        .execute()
    )

    if not forms_data.data:
        tool_output = "❌ Google Forms account is not connected."
        return tool_output

    data = forms_data.data[0]
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

    service = build("forms", "v1", credentials=creds)

    try:
        # Validate form ID format - form IDs should NOT start with "1FAIpQLSe"
        if form_id.startswith("1FAIpQLSe"):
            error_msg = f"Invalid form ID. The ID '{form_id}' appears to be a response ID (from the form submission URL), not a form ID. Please use the actual form ID which you can find in the form's edit URL: https://docs.google.com/forms/d/FORM_ID_HERE/edit"
            log_tool_event(
                tool_name="add_form_question",
                status="failed",
                params={"form_id": form_id},
                parent_node="forms_agent_node",
                tool_output=ToolOutput(output=error_msg),
            )
            return error_msg
        
        # Get current form to determine item location
        form = service.forms().get(formId=form_id).execute()
        item_count = len(form.get('items', []))
        
        # Build question item
        question_item = {
            "title": question_text,
            "questionItem": {
                "question": {}
            }
        }
        
        # Add question type and options
        if question_type in ["MULTIPLE_CHOICE", "RADIO"]:
            question_item["questionItem"]["question"]["choiceQuestion"] = {
                "type": "RADIO",
                "options": [{"value": opt} for opt in (options or [])]
            }
        elif question_type == "CHECKBOX":
            question_item["questionItem"]["question"]["choiceQuestion"] = {
                "type": "CHECKBOX",
                "options": [{"value": opt} for opt in (options or [])]
            }
        elif question_type == "DROPDOWN":
            question_item["questionItem"]["question"]["choiceQuestion"] = {
                "type": "DROP_DOWN",
                "options": [{"value": opt} for opt in (options or [])]
            }
        elif question_type == "SHORT_ANSWER":
            question_item["questionItem"]["question"]["textQuestion"] = {
                "paragraph": False
            }
        elif question_type == "PARAGRAPH":
            question_item["questionItem"]["question"]["textQuestion"] = {
                "paragraph": True
            }
        elif question_type == "LINEAR_SCALE":
            question_item["questionItem"]["question"]["scaleQuestion"] = {
                "low": 1,
                "high": 5
            }
        elif question_type == "DATE":
            question_item["questionItem"]["question"]["dateQuestion"] = {
                "includeTime": False,
                "includeYear": True
            }
        elif question_type == "TIME":
            question_item["questionItem"]["question"]["timeQuestion"] = {
                "duration": False
            }
        
        # Set required
        if required:
            question_item["questionItem"]["question"]["required"] = True
        
        # Create request to add question
        requests = [{
            "createItem": {
                "item": question_item,
                "location": {"index": item_count}
            }
        }]
        
        update_body = {"requests": requests}
        service.forms().batchUpdate(formId=form_id, body=update_body).execute()

        output_data = {
            "form_id": form_id,
            "question_text": question_text,
            "question_type": question_type,
            "required": required,
            "message": f"Question added successfully to form"
        }

        log_tool_event(
            tool_name="add_form_question",
            status="success",
            params={"form_id": form_id, "question_text": question_text},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=output_data, show=True, type="question_added"),
        )
        return f"Question '{question_text}' added successfully to form"

    except Exception as e:
        tool_output = f"Error adding question to form: {str(e)}"
        log_tool_event(
            tool_name="add_form_question",
            status="failed",
            params={"form_id": form_id},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("get_form", args_schema=GetFormInput)
def get_form(form_id: str, config: RunnableConfig = None):
    """
    Retrieves details of a specific Google Form including questions and structure. Use when user wants to see/view/inspect a form.
    Returns form title, description, questions, and settings.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="get_form",
        status="started",
        params={"form_id": form_id},
        parent_node="forms_agent_node",
    )

    forms_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "google_forms")
        .execute()
    )

    if not forms_data.data:
        tool_output = "Google Forms account is not connected."
        return tool_output

    data = forms_data.data[0]
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

    service = build("forms", "v1", credentials=creds)

    try:
        form = service.forms().get(formId=form_id).execute()
        
        info = form.get('info', {})
        title = info.get('title', 'Untitled Form')
        description = info.get('description', '')
        responder_uri = form.get('responderUri', '')
        
        # Build questions list
        questions = []
        items = form.get('items', [])
        for idx, item in enumerate(items, 1):
            if 'questionItem' in item:
                q_title = item.get('title', 'Untitled Question')
                questions.append({
                    "number": idx,
                    "text": q_title
                })
        
        output_data = {
            "title": title,
            "form_id": form_id,
            "form_url": responder_uri,
            "description": description if description else None,
            "questions": questions,
            "total_questions": len(questions)
        }

        log_tool_event(
            tool_name="get_form",
            status="success",
            params={"form_id": form_id},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=output_data, show=True, type="form_details"),
        )
        
        # Return user-friendly text for agent
        return f"Form: {title}\nURL: {responder_uri}\nQuestions: {len(questions)}"

    except Exception as e:
        tool_output = f"Error retrieving form: {str(e)}"
        log_tool_event(
            tool_name="get_form",
            status="failed",
            params={"form_id": form_id},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("get_form_responses", args_schema=GetResponsesInput)
def get_form_responses(form_id: str, max_results: Optional[int] = None, config: RunnableConfig = None):
    """
    Retrieves responses submitted to a Google Form. Use when user wants to see/view/analyze form submissions.
    Returns list of responses with answers to all questions. Can limit number of results with max_results parameter.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="get_form_responses",
        status="started",
        params={"form_id": form_id, "max_results": max_results},
        parent_node="forms_agent_node",
    )

    forms_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "google_forms")
        .execute()
    )

    if not forms_data.data:
        tool_output = "Google Forms account is not connected."
        return tool_output

    data = forms_data.data[0]
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

    service = build("forms", "v1", credentials=creds)

    try:
        responses = service.forms().responses().list(formId=form_id).execute()
        
        response_list = responses.get('responses', [])
        
        if max_results:
            response_list = response_list[:max_results]
        
        # Build structured response data
        formatted_responses = []
        for idx, response in enumerate(response_list, 1):
            response_data = {
                "response_number": idx,
                "response_id": response.get('responseId', ''),
                "answers": []
            }
            
            answers = response.get('answers', {})
            for question_id, answer in answers.items():
                text_answers = answer.get('textAnswers', {}).get('answers', [])
                if text_answers:
                    response_data["answers"].append({
                        "question_id": question_id,
                        "value": text_answers[0].get('value', '')
                    })
            
            formatted_responses.append(response_data)
        
        output_data = {
            "form_id": form_id,
            "total_responses": len(response_list),
            "responses": formatted_responses
        }

        log_tool_event(
            tool_name="get_form_responses",
            status="success",
            params={"form_id": form_id},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=output_data, show=True, type="form_responses"),
        )
        
        if len(response_list) == 0:
            return f"No responses found for form {form_id}"
        return f"Found {len(response_list)} response(s) for form"

    except Exception as e:
        tool_output = f"Error retrieving form responses: {str(e)}"
        log_tool_event(
            tool_name="get_form_responses",
            status="failed",
            params={"form_id": form_id},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("list_forms", args_schema=SearchFormsInput)
def list_forms(query: Optional[str] = None, max_results: int = 10, config: RunnableConfig = None):
    """
    Lists all Google Forms in user's Drive with IDs, titles, and URLs. Use when user wants to see/find their forms or needs a form ID.
    Can filter by query string to search for specific forms by name. Returns list with form details.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="list_forms",
        status="started",
        params={"query": query, "max_results": max_results},
        parent_node="forms_agent_node",
    )

    forms_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "google_forms")
        .execute()
    )

    if not forms_data.data:
        tool_output = "Google Forms account is not connected."
        return tool_output

    data = forms_data.data[0]
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
        
        # Build query for Google Drive
        drive_query = "mimeType='application/vnd.google-apps.form'"
        if query:
            drive_query += f" and name contains '{query}'"
        
        results = drive_service.files().list(
            q=drive_query,
            fields="files(id, name, createdTime, modifiedTime, webViewLink)",
            pageSize=max_results
        ).execute()
        
        files = results.get('files', [])
        
        # Build structured forms list
        forms_list = []
        for file in files:
            forms_list.append({
                "name": file['name'],
                "form_id": file['id'],
                "form_url": file.get('webViewLink', 'N/A'),
                "created": file.get('createdTime', 'Unknown'),
                "modified": file.get('modifiedTime', 'Unknown')
            })
        
        output_data = {
            "total_forms": len(files),
            "forms": forms_list
        }

        log_tool_event(
            tool_name="list_forms",
            status="success",
            params={"query": query, "max_results": max_results},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=output_data, show=True, type="forms_list"),
        )
        
        if len(files) == 0:
            return "No forms found in your Google Drive"
        return f"Found {len(files)} form(s) in your Google Drive"

    except Exception as e:
        tool_output = f"Error listing forms: {str(e)}"
        log_tool_event(
            tool_name="list_forms",
            status="failed",
            params={},
            parent_node="forms_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("draft_form")
def draft_form(
    params: str = Field(..., description="The request or instructions for the form structure")
) -> dict:
    """
    Uses AI to design professional form structure based on user requirements. Use when user needs help planning/designing a form or is unsure about questions.
    Returns suggested title, description, and questions. Examples: "design a customer feedback form", "plan employee onboarding survey".
    """
    log_tool_event(
        tool_name="draft_form",
        status="started",
        params={"request": params},
        parent_node="forms_agent_node",
    )

    forms_prompt = f"""
    Form Request: {params}

    Create a professional form structure:
    1. Title for the form
    2. Description explaining the purpose
    3. Well-structured questions with appropriate types
    4. Logical question flow
    5. Keep it organized and user-friendly
    """

    with get_openai_callback() as cb:
        tool_output = non_stream_llm.with_structured_output(FormDraft).invoke(
            [
                SystemMessage(
                    content=f"You are a professional form designer. {forms_prompt}"
                ),
                HumanMessage(content=params),
            ]
        )

    usage = usages(cb)

    result = {
        "title": tool_output.title,
        "description": tool_output.description,
        "questions": [q.dict() for q in tool_output.questions]
    }
    
    log_tool_event(
        tool_name="draft_form",
        status="success",
        params={"request": params},
        parent_node="forms_agent_node",
        tool_output=ToolOutput(output=result, type="draft_form", show=True),
        usages=usage,
    )

    return result


@tool("ask_human")
def ask_human(
    params: str = Field(..., description="What clarification is needed from the user")
) -> str:
    """
    Requests clarification from user when information is missing or unclear. Use when missing critical info (form ID, question details) or confirming destructive operations.
    Interrupts flow to wait for user response. Examples: "Which form?", "What questions should I add?", "Confirm deleting this form?".
    """
    interrupt_request = InterruptRequest.create_input_field(
        name="ask_human",
        title=params
    )

    user_input = interrupt(interrupt_request.to_dict())
    return f"AI: {params}\nHuman: {user_input}"


@tool("login_to_forms")
def login_to_forms(params: str = Field(..., description="error reason")) -> str:
    """
    Handles Google Forms authentication errors and prompts user to connect their Google account via OAuth. Use when account not connected or token expired.
    Initiates OAuth flow for necessary permissions. Returns authentication confirmation or cancellation status.
    """
    print("Google Forms connection issue")
    
    interrupt_request = InterruptRequest.create_connect(
        name="forms_error",
        platform="forms",
        title=params,
        content=""
    )
    
    user_input = interrupt(interrupt_request.to_dict())
    return str(user_input)


def get_forms_tool_registry() -> NodeRegistry:
    """
    Returns a NodeRegistry containing all Google Forms tools.
    This function centralizes tool registration.
    """
    forms_tool_register = NodeRegistry()
    forms_tool_register.add("verify_forms_connection", verify_forms_connection, "tool")
    forms_tool_register.add("create_form", create_form, "tool")
    forms_tool_register.add("add_form_question", add_form_question, "tool")
    forms_tool_register.add("get_form", get_form, "tool")
    forms_tool_register.add("get_form_responses", get_form_responses, "tool")
    forms_tool_register.add("list_forms", list_forms, "tool")
    forms_tool_register.add("draft_form", draft_form, "tool")
    forms_tool_register.add("ask_human", ask_human, "tool")
    forms_tool_register.add("login_to_forms", login_to_forms, "tool")
    return forms_tool_register
