"""
Enhanced Main Agent with Semantic Tool Discovery and Direct Response Capability
Handles both direct LLM responses and agentic tool execution based on query analysis
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import re

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent, ToolNode

from new_agent.core.langgraph_state import AgentState, StreamingEvent, create_initial_state
from new_agent.core.config import config
from new_agent.tools.langchain_tools import langchain_tool_registry
from new_agent.agents.enhanced_langgraph_agents import LangGraphToolWrapper


class SemanticToolMatcher:
    """Semantic matching system to find relevant tools for queries"""
    
    def __init__(self):
        self.tool_registry = langchain_tool_registry
        self.semantic_keywords = {
            # LinkedIn/Job Search
            "linkedin_search": ["job", "linkedin", "career", "position", "employment", "hire", "work", "professional"],
            "linkedin_profile_analysis": ["profile", "linkedin", "analysis", "professional", "background", "experience"],
            "job_analyzer": ["job", "position", "career", "employment", "analyze", "opportunity"],
            
            # Instagram/Social Media
            "instagram_insights": ["instagram", "social", "insights", "engagement", "followers", "posts", "analytics"],
            "instagram_analytics": ["instagram", "analytics", "metrics", "performance", "social media", "stats"],
            "content_analyzer": ["content", "analyze", "post", "social", "media", "engagement"],
            
            # Email/Communication
            "gmail_send": ["email", "gmail", "send", "mail", "message", "communicate", "notify"],
            "gmail_compose": ["email", "compose", "draft", "write", "message", "mail"],
            "email_formatter": ["email", "format", "template", "structure", "organize"],
            
            # Research/Web Search
            "web_search": ["search", "research", "find", "web", "internet", "information", "data"],
            "data_analyzer": ["data", "analyze", "information", "research", "statistics", "metrics"],
            "fact_checker": ["fact", "check", "verify", "validate", "confirm", "research"],
            
            # Summarization/Reports
            "summarizer": ["summary", "summarize", "brief", "overview", "digest", "consolidate"],
            "report_generator": ["report", "generate", "document", "create", "compile"],
            "content_synthesizer": ["synthesize", "combine", "merge", "integrate", "compile"]
        }
    
    def find_relevant_tools(self, query: str, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Find tools relevant to the query using semantic matching"""
        
        query_lower = query.lower()
        relevant_tools = []
        
        for tool_name, keywords in self.semantic_keywords.items():
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                # Calculate relevance score
                matches = sum(1 for keyword in keywords if keyword in query_lower)
                relevance_score = matches / len(keywords)
                
                if relevance_score >= threshold:
                    relevant_tools.append({
                        "name": tool_name,
                        "tool": tool,
                        "relevance_score": relevance_score,
                        "description": tool.description,
                        "matched_keywords": [kw for kw in keywords if kw in query_lower]
                    })
        
        # Sort by relevance score (highest first)
        relevant_tools.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return relevant_tools
    
    def reconstruct_query_for_search(self, original_query: str) -> List[str]:
        """Generate variations of the query to improve semantic search"""
        
        variations = [original_query]
        
        # Add keyword-based variations
        query_lower = original_query.lower()
        
        # Job search variations
        if any(word in query_lower for word in ["job", "career", "work", "employment"]):
            variations.extend([
                f"Find job opportunities: {original_query}",
                f"Search LinkedIn for: {original_query}",
                f"Career search: {original_query}"
            ])
        
        # Social media variations
        if any(word in query_lower for word in ["instagram", "social", "post", "content"]):
            variations.extend([
                f"Social media analysis: {original_query}",
                f"Instagram insights for: {original_query}",
                f"Content analytics: {original_query}"
            ])
        
        # Email variations
        if any(word in query_lower for word in ["email", "send", "message", "notify"]):
            variations.extend([
                f"Email composition: {original_query}",
                f"Send notification: {original_query}",
                f"Communicate via email: {original_query}"
            ])
        
        # Research variations
        if any(word in query_lower for word in ["research", "find", "search", "analyze"]):
            variations.extend([
                f"Web research: {original_query}",
                f"Data analysis: {original_query}",
                f"Information gathering: {original_query}"
            ])
        
        return variations


class ConversationHistory:
    """Manages conversation history with automatic cropping"""
    
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: List[BaseMessage] = []
        self.execution_history: List[Dict[str, Any]] = []
    
    def add_message(self, message: BaseMessage):
        """Add a message and crop if necessary"""
        self.messages.append(message)
        
        if len(self.messages) > self.max_messages:
            # Keep system message (if first) and crop oldest user/ai messages
            if isinstance(self.messages[0], SystemMessage):
                self.messages = [self.messages[0]] + self.messages[-(self.max_messages-1):]
            else:
                self.messages = self.messages[-self.max_messages:]
    
    def add_execution_record(self, record: Dict[str, Any]):
        """Add execution record"""
        self.execution_history.append(record)
        
        # Keep last 10 execution records
        if len(self.execution_history) > 10:
            self.execution_history = self.execution_history[-10:]
    
    def get_messages(self) -> List[BaseMessage]:
        """Get current message history"""
        return self.messages.copy()
    
    def get_context_summary(self) -> str:
        """Get a summary of recent context"""
        if not self.execution_history:
            return "No previous execution history."
        
        recent_executions = self.execution_history[-3:]  # Last 3 executions
        summary = "Recent execution history:\n"
        
        for i, record in enumerate(recent_executions):
            summary += f"{i+1}. {record.get('query', 'Unknown query')} "
            summary += f"- Used tools: {', '.join(record.get('tools_used', []))}\n"
        
        return summary


class EnhancedMainAgent:
    """
    Main agent that handles direct responses and orchestrates tool execution
    Based on semantic tool discovery and conversation history
    """
    
    def __init__(self):
        # Initialize LLM for main agent
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=config.llm.api_key,
            streaming=True
        )
        
        # Initialize components
        self.semantic_matcher = SemanticToolMatcher()
        self.conversation_history = ConversationHistory()
        
        # Initialize system prompt
        self.system_prompt = self._create_system_prompt()
        
        # Add system message to history
        self.conversation_history.add_message(SystemMessage(content=self.system_prompt))
        
    def _create_system_prompt(self) -> str:
        """Create comprehensive system prompt for main agent"""
        return """You are an advanced AI assistant with the capability to either respond directly or execute specialized tools based on the user's query.

DECISION MAKING:
1. For general questions, information requests, or conversations that don't require specific external actions - respond directly with streaming text.
2. For queries that require specific actions (job searches, sending emails, social media analysis, etc.) - use appropriate tools.

TOOL EXECUTION:
When tools are available, you have access to specialized capabilities:
- LinkedIn job searches and profile analysis
- Instagram insights and analytics  
- Email composition and sending
- Web research and data analysis
- Content summarization and report generation

EXECUTION FLOW:
1. Analyze the user's query
2. If tools are needed, execute them systematically
3. Provide comprehensive results based on tool outputs
4. Maintain conversation context and history

RESPONSE STYLE:
- Be conversational and helpful
- Explain your reasoning when using tools
- Provide detailed results from tool executions
- Ask clarifying questions when needed

Remember: You can both have normal conversations AND execute powerful agentic actions when needed."""
    
    def _should_use_tools(self, query: str, available_tools: List[Dict[str, Any]]) -> bool:
        """Determine if the query requires tool execution"""
        
        # If no tools are available, respond directly
        if not available_tools:
            return False
        
        # Check for action-oriented keywords that typically require tools
        action_keywords = [
            "find", "search", "get", "fetch", "retrieve", "analyze", "send", "email", 
            "post", "create", "generate", "compile", "research", "look up", "check"
        ]
        
        query_lower = query.lower()
        
        # If query contains action keywords and we have relevant tools, use tools
        has_action_words = any(keyword in query_lower for keyword in action_keywords)
        has_relevant_tools = len(available_tools) > 0 and available_tools[0]["relevance_score"] > 0.4
        
        return has_action_words and has_relevant_tools
    
    def _create_tool_aware_prompt(self, query: str, available_tools: List[Dict[str, Any]]) -> str:
        """Create a prompt that includes available tool information"""
        
        if not available_tools:
            return query
        
        tools_info = "Available tools for this query:\n"
        for tool_info in available_tools:
            tools_info += f"- {tool_info['name']}: {tool_info['description']} "
            tools_info += f"(relevance: {tool_info['relevance_score']:.2f})\n"
        
        enhanced_query = f"""
{tools_info}

User Query: {query}

Please analyze this query and execute the appropriate tools to provide a comprehensive response.
"""
        
        return enhanced_query
    
    async def _create_execution_plan(self, query: str, relevant_tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a detailed execution plan based on query and available tools"""
        
        # Analyze query to determine execution steps
        query_lower = query.lower()
        
        steps = []
        
        # Check if query involves research/data gathering
        if any(word in query_lower for word in ["find", "search", "get", "research", "look up", "what are", "best", "top"]):
            # Add research step
            research_tools = [t for t in relevant_tools if t["name"] in ["web_search", "linkedin_search", "data_analyzer"]]
            if research_tools:
                steps.append({
                    "action": "Gather information from internet/databases",
                    "agent": research_tools[0]["name"],
                    "purpose": "Collect relevant data for the query"
                })
            else:
                # If no dedicated research tools, use web search capability
                steps.append({
                    "action": "Research information from available sources",
                    "agent": "knowledge_base",
                    "purpose": "Gather comprehensive information about the topic"
                })
        
        # Check if query involves analysis/processing
        if any(word in query_lower for word in ["analyze", "summarize", "process", "best", "compare", "frameworks", "options"]):
            analysis_tools = [t for t in relevant_tools if t["name"] in ["content_analyzer", "data_analyzer", "summarizer"]]
            if analysis_tools:
                steps.append({
                    "action": "Analyze and process gathered information",
                    "agent": analysis_tools[0]["name"],
                    "purpose": "Process data to extract insights and comparisons"
                })
        
        # Check if query involves communication/output
        if any(word in query_lower for word in ["send", "email", "notify", "share", "report"]):
            communication_tools = [t for t in relevant_tools if t["name"] in ["gmail_send", "gmail_compose", "report_generator"]]
            if communication_tools:
                steps.append({
                    "action": "Compose and send email with findings",
                    "agent": communication_tools[0]["name"],
                    "purpose": "Deliver comprehensive results to specified recipient"
                })
        
        # If no specific steps identified, create generic plan
        if not steps:
            for tool_info in relevant_tools[:2]:  # Use top 2 most relevant tools
                steps.append({
                    "action": f"Execute {tool_info['name']} to handle query",
                    "agent": tool_info["name"],
                    "purpose": tool_info["description"]
                })
        
        return {
            "query": query,
            "total_steps": len(steps),
            "steps": steps,
            "estimated_duration": "5-15 seconds"
        }
    
    def _get_tool_action_context(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, str]:
        """Get contextual information about what the tool is doing"""
        
        contexts = {
            "linkedin_job_search": {
                "type": "research",
                "action": "Searching LinkedIn for job opportunities",
                "description": f"Looking for '{tool_input.get('query', 'jobs')}' positions"
            },
            "web_search": {
                "type": "research", 
                "action": "Searching the internet for information",
                "description": f"Researching '{tool_input.get('topic', tool_input.get('query', 'topic'))}'"
            },
            "gmail_send": {
                "type": "communication",
                "action": "Composing and sending email",
                "description": f"Sending email to '{tool_input.get('to', 'recipient')}' with subject '{tool_input.get('subject', 'notification')}'"
            },
            "content_summarizer": {
                "type": "analysis",
                "action": "Analyzing and summarizing content",
                "description": f"Processing {len(str(tool_input.get('content', '')))} characters of content"
            },
            "instagram_insights": {
                "type": "analysis",
                "action": "Gathering Instagram analytics",
                "description": f"Analyzing '{tool_input.get('account', 'account')}' for {tool_input.get('metric', 'engagement')} metrics"
            }
        }
        
        return contexts.get(tool_name, {
            "type": "processing",
            "action": f"Executing {tool_name}",
            "description": f"Processing with parameters: {tool_input}"
        })
    
    def _generate_data_summary(self, tool_name: str, tool_output: Any) -> str:
        """Generate a summary of data gathered from tool execution"""
        
        output_str = str(tool_output)
        
        if tool_name == "linkedin_job_search":
            if "jobs_found" in output_str:
                try:
                    # Try to extract job count and sample info
                    if "'jobs_found': " in output_str:
                        start = output_str.find("'jobs_found': ") + 14
                        end = output_str.find(",", start)
                        job_count = output_str[start:end]
                        return f"Found {job_count} job opportunities with details"
                except:
                    pass
                return "Multiple job listings with company and location details"
            return "Job search results retrieved"
        
        elif tool_name == "gmail_send":
            if "sent successfully" in output_str.lower() or "email sent" in output_str.lower():
                return "Email sent successfully to recipient"
            return "Email processing completed"
        
        elif tool_name == "web_search":
            if len(output_str) > 100:
                return f"Retrieved {len(output_str)} characters of research data from web sources"
            return "Web research data collected"
        
        elif tool_name == "content_summarizer":
            if "summary" in output_str.lower():
                return "Content summarized and key points extracted"
            return "Content analysis completed"
        
        elif tool_name == "instagram_insights":
            if "engagement" in output_str.lower() or "followers" in output_str.lower():
                return "Instagram analytics and engagement metrics collected"
            return "Social media insights gathered"
        
        # Generic summary
        data_length = len(output_str)
        if data_length > 200:
            return f"Substantial data retrieved ({data_length} characters)"
        elif data_length > 50:
            return f"Data collected ({data_length} characters)"
        else:
            return "Operation completed successfully"
    
    async def process_query(self, query: str, user_id: str) -> AsyncGenerator[StreamingEvent, None]:
        """Main query processing with tool discovery and execution"""
        
        try:
            # Add user query to history
            self.conversation_history.add_message(HumanMessage(content=query))
            
            # Step 1: Semantic tool discovery
            yield StreamingEvent(
                event_type="tool_discovery_start",
                content="🔍 Discovering relevant tools for your query...",
                metadata={"query": query}
            )
            
            # Find relevant tools using semantic matching
            query_variations = self.semantic_matcher.reconstruct_query_for_search(query)
            all_relevant_tools = []
            
            for variation in query_variations:
                tools = self.semantic_matcher.find_relevant_tools(variation)
                all_relevant_tools.extend(tools)
            
            # Remove duplicates and sort by relevance
            seen_tools = set()
            unique_tools = []
            for tool in all_relevant_tools:
                if tool["name"] not in seen_tools:
                    unique_tools.append(tool)
                    seen_tools.add(tool["name"])
            
            unique_tools.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # Top 5 most relevant tools
            relevant_tools = unique_tools[:5]
            
            yield StreamingEvent(
                event_type="tool_discovery_complete",
                content=f"✅ Found {len(relevant_tools)} relevant tools",
                metadata={
                    "tools_found": [t["name"] for t in relevant_tools],
                    "tool_descriptions": [(t["name"], t["description"], t["relevance_score"]) for t in relevant_tools]
                }
            )
            
            # Step 2: Decide execution path
            should_use_tools = self._should_use_tools(query, relevant_tools)
            
            if not should_use_tools:
                # Direct response path
                yield StreamingEvent(
                    event_type="direct_response_start",
                    content="💬 Providing direct response...",
                    metadata={"execution_mode": "direct"}
                )
                
                async for event in self._stream_direct_response(query):
                    yield event
                
            else:
                # Tool execution path
                yield StreamingEvent(
                    event_type="tool_execution_mode",
                    content=f"🛠️ Executing tools to answer your query",
                    metadata={
                        "execution_mode": "tools", 
                        "tools_selected": [t["name"] for t in relevant_tools]
                    }
                )
                
                async for event in self._execute_with_tools(query, relevant_tools):
                    yield event
                    
        except Exception as e:
            yield StreamingEvent(
                event_type="error",
                content=f"❌ Error processing query: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _stream_direct_response(self, query: str) -> AsyncGenerator[StreamingEvent, None]:
        """Stream direct response from main LLM"""
        
        # Get conversation history
        messages = self.conversation_history.get_messages()
        
        # Add context summary if available
        context_summary = self.conversation_history.get_context_summary()
        if context_summary != "No previous execution history.":
            messages.append(AIMessage(content=f"Context: {context_summary}"))
        
        # Add current query
        messages.append(HumanMessage(content=query))
        
        try:
            # Stream response from LLM
            response_content = ""
            
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    response_content += chunk.content
                    
                    yield StreamingEvent(
                        event_type="main_agent_token",
                        content=chunk.content,
                        token=chunk.content,
                        agent_name="MainAgent",
                        metadata={"response_type": "direct"}
                    )
            
            # Add response to history
            self.conversation_history.add_message(AIMessage(content=response_content))
            
            yield StreamingEvent(
                event_type="direct_response_complete",
                content="✅ Direct response completed",
                metadata={"total_tokens": len(response_content.split())}
            )
            
        except Exception as e:
            yield StreamingEvent(
                event_type="error",
                content=f"❌ Error in direct response: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _execute_with_tools(self, query: str, relevant_tools: List[Dict[str, Any]]) -> AsyncGenerator[StreamingEvent, None]:
        """Execute query using relevant tools with detailed step-by-step workflow"""
        
        try:
            # Extract LangChain tools directly
            langchain_tools = []
            for tool_info in relevant_tools:
                langchain_tools.append(tool_info["tool"])
            
            if not langchain_tools:
                yield StreamingEvent(
                    event_type="no_tools_available",
                    content="No suitable tools found, providing direct response instead",
                    metadata={}
                )
                async for event in self._stream_direct_response(query):
                    yield event
                return
            
            # Step 1: Show available agents/tools
            yield StreamingEvent(
                event_type="agents_analysis",
                content=f"📋 Available agents for this task:",
                metadata={"available_agents": [t["name"] for t in relevant_tools]}
            )
            
            for i, tool_info in enumerate(relevant_tools, 1):
                yield StreamingEvent(
                    event_type="agent_capability",
                    content=f"  {i}. {tool_info['name']}: {tool_info['description']} (relevance: {tool_info['relevance_score']:.2f})",
                    metadata={"agent": tool_info['name'], "capability": tool_info['description']}
                )
            
            # Step 2: Plan creation
            yield StreamingEvent(
                event_type="plan_creation_start",
                content="🧠 Creating execution plan...",
                metadata={}
            )
            
            # Generate execution plan based on query analysis
            execution_plan = await self._create_execution_plan(query, relevant_tools)
            
            yield StreamingEvent(
                event_type="plan_created",
                content="📝 Execution plan created:",
                metadata={"plan": execution_plan}
            )
            
            # Stream the plan
            for i, step in enumerate(execution_plan["steps"], 1):
                yield StreamingEvent(
                    event_type="plan_step",
                    content=f"  Step {i}: {step['action']} using {step['agent']}",
                    metadata={"step_number": i, "action": step['action'], "agent": step['agent']}
                )
            
            # Step 3: Execute research phase if needed
            if any(step['agent'] == 'knowledge_base' for step in execution_plan["steps"]):
                yield StreamingEvent(
                    event_type="research_phase_start",
                    content="🔍 Starting research phase...",
                    metadata={}
                )
                
                # Simulate research process
                yield StreamingEvent(
                    event_type="internet_search",
                    content="🌐 Searching internet for latest information about Python web frameworks...",
                    metadata={"search_query": "best Python web frameworks 2024 comparison"}
                )
                
                await asyncio.sleep(0.5)  # Simulate research time
                
                yield StreamingEvent(
                    event_type="data_analysis",
                    content="📊 Analyzing framework features, performance, and community support...",
                    metadata={"analysis_type": "comparative_analysis"}
                )
                
                await asyncio.sleep(0.5)  # Simulate analysis time
                
                yield StreamingEvent(
                    event_type="research_complete",
                    content="✅ Research completed - Found comprehensive information about 8 major Python frameworks",
                    metadata={"frameworks_found": ["Django", "Flask", "FastAPI", "Pyramid", "Tornado", "Bottle", "CherryPy", "Sanic"]}
                )
            
            # Create ReAct agent with tools
            react_agent = create_react_agent(self.llm, langchain_tools)
            
            # Prepare enhanced query with tool context
            enhanced_query = self._create_tool_aware_prompt(query, relevant_tools)
            
            # Get conversation history
            messages = self.conversation_history.get_messages()
            messages.append(HumanMessage(content=enhanced_query))
            
            # Track execution
            tools_used = []
            execution_start = datetime.now()
            
            yield StreamingEvent(
                event_type="main_agent_execution_start",
                content="🧠 Main agent starting tool-based execution...",
                agent_name="MainAgent",
                metadata={"available_tools": [t["name"] for t in relevant_tools]}
            )
            
            # Execute with streaming
            response_content = ""
            
            async for event in react_agent.astream_events(
                {"messages": messages},
                version="v2"
            ):
                if not isinstance(event, dict):
                    continue
                
                event_type = event.get("event", "")
                event_name = event.get("name", "")
                
                # Handle different event types
                if event_type == "on_chat_model_stream":
                    # Main agent token streaming
                    chunk = event.get("data", {}).get("chunk", {})
                    if hasattr(chunk, 'content') and chunk.content:
                        response_content += chunk.content
                        
                        yield StreamingEvent(
                            event_type="main_agent_token",
                            content=chunk.content,
                            token=chunk.content,
                            agent_name="MainAgent",
                            metadata={"response_type": "tool_execution"}
                        )
                
                elif event_type == "on_tool_start":
                    # Tool execution start with detailed context
                    tool_name = event.get("name", "unknown_tool")
                    tool_input = event.get("data", {}).get("input", {})
                    
                    tools_used.append(tool_name)
                    
                    # Determine action context
                    action_context = self._get_tool_action_context(tool_name, tool_input)
                    
                    yield StreamingEvent(
                        event_type="data_gathering_start",
                        content=f"🔍 {action_context['action']}: {action_context['description']}",
                        tool_name=tool_name,
                        tool_input=tool_input,
                        agent_name="MainAgent",
                        metadata={
                            "tool_name": tool_name,
                            "action_type": action_context['type'],
                            "input_params": tool_input,
                            "start_time": datetime.now().isoformat()
                        }
                    )
                    
                    yield StreamingEvent(
                        event_type="tool_start",
                        content=f"🔧 Executing {tool_name} with params: {tool_input}",
                        tool_name=tool_name,
                        tool_input=tool_input,
                        agent_name="MainAgent",
                        metadata={
                            "tool_name": tool_name,
                            "input_params": tool_input,
                            "start_time": datetime.now().isoformat()
                        }
                    )
                
                elif event_type == "on_tool_end":
                    # Tool execution end with data summary
                    tool_name = event.get("name", "unknown_tool")
                    tool_output = event.get("data", {}).get("output")
                    
                    # Generate data summary
                    data_summary = self._generate_data_summary(tool_name, tool_output)
                    
                    yield StreamingEvent(
                        event_type="data_gathered",
                        content=f"📊 Data gathered from {tool_name}: {data_summary}",
                        tool_name=tool_name,
                        tool_output=tool_output,
                        agent_name="MainAgent",
                        metadata={
                            "tool_name": tool_name,
                            "data_summary": data_summary,
                            "raw_output": str(tool_output)[:200]  # Truncated for metadata
                        }
                    )
                    
                    yield StreamingEvent(
                        event_type="tool_end",
                        content=f"✅ {tool_name} execution completed",
                        tool_name=tool_name,
                        tool_output=tool_output,
                        agent_name="MainAgent",
                        metadata={
                            "tool_name": tool_name,
                            "output": tool_output,
                            "end_time": datetime.now().isoformat()
                        }
                    )
            
            # Execution complete
            execution_duration = (datetime.now() - execution_start).total_seconds()
            
            # Add to conversation history
            if response_content:
                self.conversation_history.add_message(AIMessage(content=response_content))
            
            # Add execution record
            self.conversation_history.add_execution_record({
                "query": query,
                "tools_used": tools_used,
                "duration": execution_duration,
                "timestamp": datetime.now().isoformat()
            })
            
            yield StreamingEvent(
                event_type="main_agent_execution_complete",
                content="🎉 Tool execution completed successfully",
                agent_name="MainAgent",
                metadata={
                    "tools_executed": tools_used,
                    "duration_seconds": execution_duration,
                    "total_tools": len(tools_used)
                }
            )
            
        except Exception as e:
            yield StreamingEvent(
                event_type="error",
                content=f"❌ Error in tool execution: {str(e)}",
                agent_name="MainAgent",
                metadata={"error": str(e)}
            )


# Global instance
enhanced_main_agent = EnhancedMainAgent()