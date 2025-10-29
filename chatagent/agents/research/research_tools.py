"""
Research Tools Module
Contains all research-related tools and their implementations.
No hardcoded prompts - all prompts are managed through agents_config.py
"""

from chatagent.node_registry import NodeRegistry
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from chatagent.config.init import non_stream_llm
from chatagent.utils import log_tool_event, usages
from langchain_tavily import TavilySearch
from langchain_community.callbacks import get_openai_callback
from chatagent.model.tool_output import ToolOutput
from chatagent.agents.research.research_models import (
    PersonProfile,
    PersonList,
    JobItem,
    JobList,
    LinkedInSearch,
    LinkedInJobSearch,
    Search
)
import http.client
from dotenv import load_dotenv
import json
from typing import List, Optional
import os

load_dotenv()

search_tool = TavilySearch(max_results=5)


@tool("tavily_search", args_schema=Search)
async def tavily_search(
    query: str,
    limit: int = 5,
    search_depth: str | None = None,
    time_range: str | None = None,
):
    """
    Search the web for real-time information including news, articles, documentation, and general knowledge.
    Capabilities: web search, news retrieval, current events, fact-checking, real-time data, trending topics, research queries.
    Use for: any general web search, up-to-date information, breaking news, or when other specialized tools don't fit.
    """
    log_tool_event(
        tool_name="tavily_search",
        status="started",
        parent_node="research_agent_node",
        params={"query": query},
    )
    payload = {"query": query, "max_results": limit}
    if search_depth:
        payload["search_depth"] = search_depth
    if time_range:
        payload["time_range"] = time_range

    with get_openai_callback() as cb:
        result = await search_tool.ainvoke(payload)
    usages_data = usages(cb)

    log_tool_event(
        tool_name="tavily_search",
        status="success",
        parent_node="research_agent_node",
        params={"query": query},
        usages=usages_data,
        tool_output=ToolOutput(output=result),
    )
    return result


@tool("linkedin_person_search", args_schema=LinkedInSearch)
async def linkedin_person_search(
    search_word: str, page_number: int = 1, page_size: int = 2
):
    """
    Find LinkedIn profiles and professional contacts by name, role, company, or industry.
    Capabilities: people search, profile discovery, contact finding, professional networking, executive search, talent sourcing.
    Use for: finding specific professionals, CEOs, employees at companies, industry experts, or networking contacts.
    """
    log_tool_event(
        tool_name="linkedin_person_search",
        status="started",
        parent_node="research_agent_node",
        params={
            "search_word": search_word,
            "page_number": page_number,
            "page_size": page_size,
        },
    )

    conn = http.client.HTTPSConnection("linkedin-data-max.p.rapidapi.com")

    payload_dict = {
        "search_word": search_word,
        "page_number": page_number,
        "page_size": page_size,
    }
    payload = json.dumps(payload_dict)

    api_key = "93c8528738msh9b57dbac338fc31p1dc9b3jsn4ff9295d4de1"
    if not api_key:
        return "Error: RAPID_API_KEY environment variable not set."

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "linkedin-data-max.p.rapidapi.com",
        "Content-Type": "application/json",
    }

    try:
        conn.request("POST", "/api/linkedin/persons/search/", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")

        with get_openai_callback() as cb:
            structured_llm = non_stream_llm.with_structured_output(PersonList)
            result = await structured_llm.ainvoke(
                "Extract the following job data into structured fields:\n"
                f"{json.dumps(data, indent=2)}"
            )
        usages_data = usages(cb)

        data = result.model_dump()

        log_tool_event(
            tool_name="linkedin_person_search",
            status="success",
            parent_node="research_agent_node",
            params={"search_word": search_word},
            usages=usages_data,
            tool_output=ToolOutput(output=data, type="person"),
        )
        return data

    except Exception as e:
        log_tool_event(
            tool_name="linkedin_person_search",
            status="error",
            parent_node="research_agent_node",
            params={"search_word": search_word},
            tool_output=ToolOutput(output=str(e), type="error"),
        )
        return f"An error occurred: {e}"

    finally:
        conn.close()


@tool("linkedin_job_search", args_schema=LinkedInJobSearch)
async def linkedin_job_search(
    title: str, location: str, limit: int = 5, offset: int = 0
):
    """
    Search for job openings on LinkedIn by title and location with active listings from last 7 days.
    Capabilities: job search, job listings, career opportunities, employment search, hiring positions, salary info.
    Use for: finding jobs, career research, job market analysis, hiring trends, or employment opportunities.
    """
    log_tool_event(
        tool_name="linkedin_job_search",
        status="started",
        parent_node="research_agent_node",
        params={"title": title, "location": location, "limit": limit, "offset": offset},
    )

    conn = http.client.HTTPSConnection("linkedin-job-search-api.p.rapidapi.com")
    headers = {
        "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
        "x-rapidapi-host": "linkedin-job-search-api.p.rapidapi.com",
    }

    title_filter = f"%22{title.replace(' ', '%20')}%22"
    location_filter = f"%22{location.replace(' ', '%20')}%22"

    endpoint = f"/active-jb-7d?limit={limit}&offset={offset}&title_filter={title_filter}&location_filter={location_filter}"
    conn.request("GET", endpoint, headers=headers)

    res = conn.getresponse()
    data = res.read().decode("utf-8")
    with get_openai_callback() as cb:
        structured_llm = non_stream_llm.with_structured_output(JobList)
        result = await structured_llm.ainvoke(
            "Extract the following job data into structured fields:\n"
            f"{json.dumps(data, indent=2)}"
        )

    usages_data = usages(cb)

    data = result.model_dump()
    log_tool_event(
        tool_name="linkedin_job_search",
        status="success",
        parent_node="research_agent_node",
        params={"title": title, "location": location},
        usages=usages_data,
        tool_output=ToolOutput(output=data, type="job"),
    )
    return data


def get_research_tool_registry() -> NodeRegistry:
    """
    Returns a NodeRegistry containing all Research tools.
    This function centralizes tool registration.
    """
    research_register = NodeRegistry()
    research_register.add("tavily_search", tavily_search, "tool")
    research_register.add("linkedin_job_search", linkedin_job_search, "tool")
    research_register.add("linkedin_person_search", linkedin_person_search, "tool")
    return research_register
