from chatagent.node_registry import NodeRegistry
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from chatagent.config.init import llm
from chatagent.agents.create_agent_tool import make_agent_tool_node
from chatagent.utils import log_tool_event
from langgraph.types import interrupt
from chatagent.agents.social_media_manager.instagram import instagram_profile
from supabase_client import supabase
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from chatagent.utils import log_tool_event, usages
from langchain_community.callbacks import get_openai_callback
from pydantic import BaseModel, Field
import http.client
from dotenv import load_dotenv
from chatagent.model.tool_output import ToolOutput
import json
from typing import List, Optional
import os

load_dotenv()


search_tool = TavilySearch(max_results=5)


class LinkedInSearch(BaseModel):
    """Input schema for the LinkedIn Person Search tool."""
    search_word: str = Field(
        ...,
        description="The search term for finding people (e.g., 'plastics ceo', 'software engineer at Google').")
    page_number: int = Field(1, description="The page number for pagination.")
    page_size: int = Field(
        10, description="The number of results per page (max 10).")


class PersonProfile(BaseModel):
    id: str = Field(..., description="Unique person ID (e.g., LinkedIn ID)")
    full_name: str = Field(..., description="Full name of the person")
    headline: Optional[str] = Field(
        None, description="Professional headline or current role")
    organization: Optional[str] = Field(
        None, description="Current company or organization")
    location: Optional[str] = Field(None, description="Geographic location")
    url: Optional[str] = Field(
        None, description="Profile URL (e.g., LinkedIn)")
    image_url: Optional[str] = Field(None, description="Profile picture URL")
    experience: Optional[List[str]] = Field(
        None, description="List of past experiences or roles"
    )
    education: Optional[List[str]] = Field(
        None, description="List of educational qualifications"
    )
    skills: Optional[List[str]] = Field(
        None, description="List of key skills"
    )


class PersonList(BaseModel):
    people: List[PersonProfile]


class JobItem(BaseModel):
    id: str = Field(..., description="Unique job ID")
    title: str = Field(..., description="Job title")
    organization: str = Field(..., description="Company or organization name")
    location: Optional[str] = Field(
        None, description="Job location if available")
    url: str = Field(..., description="Job posting URL")
    date_posted: str = Field(..., description="Date when the job was posted")

# Step 2: Define schema for list of jobs


class JobList(BaseModel):
    jobs: List[JobItem]


@tool("linkedin_person_search", args_schema=LinkedInSearch)
async def linkedin_person_search(
        search_word: str,
        page_number: int = 1,
        page_size: int = 2):
    """
    Search for LinkedIn profiles using the RapidAPI LinkedIn Data Max API.

    This tool queries for LinkedIn profiles based on a search term, with
    pagination controls. It is useful for finding specific individuals or
    professionals in a certain field.

    Args:
        search_word (str): The search term to use (e.g., "plastics ceo").
        page_number (int, optional): The page number of results to return. Defaults to 1.
        page_size (int, optional): The number of results per page. Defaults to 2.

    Returns:
        str: Raw JSON response string from the RapidAPI, typically containing
        a list of LinkedIn profiles matching the search criteria.
    """
    log_tool_event(
        tool_name="linkedin_person_search",
        status="started",
        parent_node="research_agent_node",  # Assuming parent node
        params={
            "search_word": search_word,
            "page_number": page_number,
            "page_size": page_size}
    )

    conn = http.client.HTTPSConnection("linkedin-data-max.p.rapidapi.com")

    # Create a dictionary for the payload and convert it to a JSON string
    payload_dict = {
        "search_word": search_word,
        "page_number": page_number,
        "page_size": page_size
    }
    payload = json.dumps(payload_dict)

    # Retrieve the API key from environment variables
    # os.getenv("RAPID_API_KEY")
    api_key = "93c8528738msh9b57dbac338fc31p1dc9b3jsn4ff9295d4de1"
    if not api_key:
        return "Error: RAPID_API_KEY environment variable not set."

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "linkedin-data-max.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    try:
        conn.request("POST", "/api/linkedin/persons/search/", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")

        with get_openai_callback() as cb:
            structured_llm = llm.with_structured_output(PersonList)
            result = await structured_llm.ainvoke(
                "Extract the following job data into structured fields:\n"
                f"{json.dumps(data, indent=2)}"
            )

        data = result.model_dump()

        log_tool_event(
            tool_name="linkedin_person_search",
            status="success",
            parent_node="research_agent_node",
            params={"search_word": search_word},
            tool_output=ToolOutput(output=data, type="person")
        )
        return data

    except Exception as e:
        log_tool_event(
            tool_name="linkedin_person_search",
            status="error",
            parent_node="research_agent_node",
            params={"search_word": search_word},
            tool_output=ToolOutput(output=str(e), type="error")
        )
        return f"An error occurred: {e}"

    finally:
        conn.close()


class LinkedInJobSearch(BaseModel):
    title: str = Field(...,
                       description="Job title to search (e.g. Data Scientist, Backend Engineer)")
    location: str = Field(
        ...,
        description="Location to search (e.g. United States, India, Remote, or queries like 'United States OR United Kingdom')")
    limit: int = Field(10, description="Max number of results (<=10)")
    offset: int = Field(0, description="Pagination offset")


@tool("linkedin_job_search", args_schema=LinkedInJobSearch)
async def linkedin_job_search(
        title: str,
        location: str,
        limit: int = 5,
        offset: int = 0):
    """
    Search LinkedIn job listings using the RapidAPI LinkedIn Job Search API.

    This tool queries LinkedIn jobs filtered by job title and location, with
    optional pagination controls. It is part of the Research Agent and should
    be used when the user explicitly requests job search information.

    Args:
        title (str): Job title to search for (e.g., "Data Scientist", "Backend Engineer").
        location (str): Location filter (e.g., "United States", "India", "Remote",
                        or compound queries like "United States OR United Kingdom").
        limit (int, optional): Maximum number of results to return.
            - Default = 5
            - Maximum = 10 (per API limits)
        offset (int, optional): Pagination offset for retrieving additional results.
            - Default = 0
    """
    log_tool_event(
        tool_name="linkedin_job_search",
        status="started",
        parent_node="research_agent_node",
        params={
            "title": title,
            "location": location,
            "limit": limit,
            "offset": offset})

    conn = http.client.HTTPSConnection(
        "linkedin-job-search-api.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': os.getenv("RAPID_API_KEY"),
        'x-rapidapi-host': "linkedin-job-search-api.p.rapidapi.com"
    }

    # Construct filters exactly like test.py format
    title_filter = f"%22{title.replace(' ', '%20')}%22"
    location_filter = f"%22{location.replace(' ', '%20')}%22"

    endpoint = f"/active-jb-7d?limit={limit}&offset={offset}&title_filter={title_filter}&location_filter={location_filter}"
    conn.request("GET", endpoint, headers=headers)

    res = conn.getresponse()
    data = res.read().decode("utf-8")
    structured_llm = llm.with_structured_output(JobList)
    result = await structured_llm.ainvoke(
        "Extract the following job data into structured fields:\n"
        f"{json.dumps(data, indent=2)}"
    )

    data = result.model_dump()
    log_tool_event(
        tool_name="linkedin_job_search",
        status="success",
        parent_node="research_agent_node",
        params={"title": title, "location": location},
        tool_output=ToolOutput(output=data, type="job")
    )
    return data


class Search(BaseModel):
    query: str = Field(..., description="User search query")
    limit: int = Field(5, description="Max results (<=10)")
    search_depth: str | None = Field(None, description="basic|advanced")
    time_range: str | None = Field(None, description="day|week|month|year")


@tool("tavily_search", args_schema=Search)
async def tavily_search(
    query: str,
    limit: int = 5,
    search_depth: str | None = None,
    time_range: str | None = None,
):
    """
    Perform a web search using the Tavily API.

    This tool retrieves fresh information (news, job listings, documents, etc.)
    directly from the web. It is part of the Research Agent and should be used
    whenever the user asks for real-time or up-to-date knowledge.
    Args:
        query (str): The user’s search query.
        limit (int, optional): Maximum number of results to return.
            - Default = 5
            - Maximum = 10
        search_depth (str, optional): Controls the breadth of results.
            - Options: "basic", "advanced"
            - Default = None (API default applies)
        time_range (str, optional): Restrict results to a recent time period.
            - Options: "day", "week", "month", "year"
            - Default = None (no time restriction)
    """
    log_tool_event(
        tool_name="tavily_search",
        status="started",
        parent_node="research_agent_node",
        params={
            "query": query})
    payload = {"query": query, "max_results": limit}
    if search_depth:
        payload["search_depth"] = search_depth
    if time_range:
        payload["time_range"] = time_range
    result = await search_tool.ainvoke(payload)
    log_tool_event(
        tool_name="tavily_search",
        status="success",
        parent_node="research_agent_node",
        params={
            "query": query},
        tool_output=ToolOutput(
            output=result))
    return result


research_register = NodeRegistry()
research_register.add("tavily_search", search_tool, "tool")
research_register.add("linkedin_job_search", linkedin_job_search, "tool")
research_register.add("linkedin_person_search", linkedin_person_search, "tool")

research_agent_node = make_agent_tool_node(
    llm=llm,
    members=research_register,
    prompt=(
        "You are a Research/Search Agent with access to these tools:\n"
        "- tavily_search: Search the web for fresh information (news/jobs/docs).\n"
        "- linkedin_job_search: Search LinkedIn job listings by title and location.\n"
        "- linkedin_person_search: Search any person takes search keyword"
        "Pick the appropriate tool based on the user query."),
    node_name="research_agent_node",
    parent_node="task_dispatcher_node",
)
