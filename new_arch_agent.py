from langchain.tools import Tool
from langchain_core.tools import tool  # For decorator-based tools
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
import operator
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI  # Replace with your LLM
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.callbacks import StdOutCallbackHandler, BaseCallbackHandler

# Custom callback for detailed logging including tool outputs
class LoggingCallback(BaseCallbackHandler):
    def __init__(self, event_log: List[str]):
        self.event_log = event_log

    def on_chain_start(self, serialized, inputs, **kwargs):
        log = f"Chain started: {serialized.get('name', 'Unknown')}"
        print(log)
        self.event_log.append(log)

    def on_chain_end(self, outputs, **kwargs):
        log = f"Chain ended with output: {outputs}"
        print(log)
        self.event_log.append(log)

    def on_agent_start(self, serialized, inputs, **kwargs):
        log = f"Agent started: {serialized.get('name', 'Unknown Agent')} with input: {inputs}"
        print(log)
        self.event_log.append(log)

    def on_agent_end(self, outputs, **kwargs):
        log = "Agent ended"
        print(log)
        self.event_log.append(log)

    def on_agent_action(self, action, **kwargs):
        log = f"Agent action: {action}"
        print(log)
        self.event_log.append(log)

    def on_agent_finish(self, finish, **kwargs):
        log = f"Agent finished: {finish}"
        print(log)
        self.event_log.append(log)

    def on_tool_start(self, serialized, input_str, **kwargs):
        log = f"Tool started: {serialized['name']} with input: {input_str}"
        print(log)
        self.event_log.append(log)

    def on_tool_end(self, output, **kwargs):
        log = f"Tool ended with output: {output}"
        print(log)
        self.event_log.append(log)  # Include tool output in event log

    def on_tool_error(self, error, **kwargs):
        log = f"Tool error: {error}"
        print(log)
        self.event_log.append(log)

# Example tool functions
@tool
def web_search(query: str) -> str:
    """Search the web for information."""
    return f"Results for {query}"

@tool
def data_analysis(data: str) -> str:
    """Analyze provided data."""
    return f"Analysis: {data}"

# Define agents
agents = [
    {
        "name": "WebAgent",
        "description": "Handles web-related queries like searching or browsing.",
        "tools": [web_search]
    },
    {
        "name": "DataAgent",
        "description": "Performs data analysis, stats, and visualization.",
        "tools": [data_analysis]
    },
    # Add more agents...
]

agent_map = {agent["name"]: agent for agent in agents}
available_agents_desc = "\n".join([f"- {a['name']}: {a['description']}" for a in agents])

# Embeddings and vector store for routing
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
agent_descriptions = [agent["description"] for agent in agents]
vector_store = FAISS.from_texts(agent_descriptions, embeddings, metadatas=[{"name": agent["name"]} for agent in agents])

# State with event_log and plan
class AgentState(TypedDict):
    query: str
    plan: List[str]  # Step-by-step plan
    current_step: int  # Track plan progress
    selected_agent: str
    intermediate_steps: Annotated[List[str], operator.add]
    final_output: str
    event_log: Annotated[List[str], operator.add]  # Event log including tool outputs
    follow_up_query: str  # For user talking to data

# LLM
llm = ChatOpenAI(model="gpt-4")  # Adapt to your LLM

# Planner node: Create plan based on available agents
def planner_node(state: AgentState) -> AgentState:
    print("Planner started")
    query = state["query"]
    prompt = PromptTemplate.from_template(
        "Query: {query}\nAvailable agents:\n{agents}\nCreate a step-by-step plan to solve this, selecting agents for each step:"
    )
    chain = prompt | llm
    plan_str = chain.invoke({"query": query, "agents": available_agents_desc}).content.strip()
    plan = [step.strip() for step in plan_str.split("\n") if step.strip()]  # Parse into list
    log = f"Plan created: {plan}"
    print(log)
    return {"plan": plan, "current_step": 0, "event_log": [log]}

# Router node: Select agent for current plan step
def router_node(state: AgentState) -> AgentState:
    print("Router started")
    current_step = state["plan"][state["current_step"]]
    query_embedding = embeddings.embed_query(current_step)
    results = vector_store.similarity_search_by_vector(query_embedding, k=1)
    selected_agent = results[0].metadata["name"]
    
    # Optional LLM refinement
    prompt = PromptTemplate.from_template(
        "Current plan step: {step}\nAgent options: {agents}\nSelect the best agent name:"
    )
    chain = prompt | llm
    llm_decision = chain.invoke({"step": current_step, "agents": ", ".join(agent_map.keys())}).content.strip()
    if llm_decision in agent_map:
        selected_agent = llm_decision
    
    log = f"Router selected agent for step {state['current_step'] + 1}: {selected_agent}"
    print(log)
    return {"selected_agent": selected_agent, "event_log": state["event_log"] + [log]}

# Agent execution node
def agent_execution_node(state: AgentState) -> AgentState:
    agent_name = state["selected_agent"]
    log = f"Agent execution started for: {agent_name} on plan step {state['current_step'] + 1}"
    print(log)
    state["event_log"].append(log)
    agent_data = agent_map[agent_name]
    
    prompt = PromptTemplate.from_template(
        "You are {name}. Execute plan step: {step} for query: {query} using tools if needed.\n{agent_scratchpad}"
    )
    agent = create_tool_calling_agent(llm, agent_data["tools"], prompt.partial(name=agent_name))
    
    # Use custom callback with event_log
    callbacks = [LoggingCallback(state["event_log"])]
    executor = AgentExecutor(agent=agent, tools=agent_data["tools"], verbose=True, callbacks=callbacks)
    
    current_step = state["plan"][state["current_step"]]
    result = executor.invoke({"query": state["query"], "step": current_step, "intermediate_steps": state["intermediate_steps"]})
    
    new_steps = [f"Tool call: {result['output']}"]
    final_output = result["output"] if "done" in result["output"].lower() else None
    
    end_log = f"Agent execution ended for: {agent_name}"
    print(end_log)
    state["event_log"].append(end_log)
    return {
        "intermediate_steps": new_steps,
        "final_output": final_output if state["current_step"] == len(state["plan"]) - 1 else None,  # Final only at end of plan
        "current_step": state["current_step"] + 1
    }

# User interaction node: After task finish, allow "talking to data"
def user_interaction_node(state: AgentState) -> AgentState:
    if state["follow_up_query"]:
        log = f"User follow-up query on data: {state['follow_up_query']}. Processing as new task."
        print(log)
        # Reset for new query (chain as sub-task)
        return {"query": state["follow_up_query"], "plan": [], "current_step": 0, "follow_up_query": "", "event_log": state["event_log"] + [log]}
    else:
        log = "No follow-up; task complete or create another task if needed."
        print(log)
        return {"event_log": state["event_log"] + [log], "final_output": state["final_output"] or "Task complete."}

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("planner", planner_node)
workflow.add_node("router", router_node)
workflow.add_node("agent_exec", agent_execution_node)
workflow.add_node("user_interact", user_interaction_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "router")
workflow.add_edge("router", "agent_exec")

# Conditional after agent_exec: Next step or finish plan
def plan_continue(state: AgentState):
    if state["current_step"] < len(state["plan"]):
        return "router"  # Next plan step
    elif state["follow_up_query"]:  # If follow-up, interact
        return "user_interact"
    else:
        return END  # Or "user_interact" if always check

workflow.add_conditional_edges("agent_exec", plan_continue)

# After interaction, loop back if new task
workflow.add_conditional_edges("user_interact", lambda s: "planner" if s["follow_up_query"] else END)

app = workflow.compile()

# Example run
initial_state = {
    "query": "Analyze this data: [1,2,3]",
    "intermediate_steps": [],
    "event_log": [],
    "plan": [],
    "current_step": 0,
    "follow_up_query": ""  # Set to a string for follow-up, e.g., "What is the mean?"
}
result = app.invoke(initial_state)
print("Final result:", result["final_output"])
print("Event Log:", "\n".join(result["event_log"]))