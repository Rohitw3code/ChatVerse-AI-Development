"""
Main CLI interface for the New Agent Framework
Provides command-line access to the complete agent system
"""

import asyncio
import argparse
import sys
import json
from typing import Dict, Any, Optional
from pathlib import Path

from .core.state import create_initial_state, update_state_with_plan
from .core.config import config
from .planning.planner import planning_engine
from .execution.engine import execution_engine
from .streaming.interface import cli_streamer
from .database.simple_db import database
from .agents.registry import agent_registry
from .tools.dummy_tools import dummy_tool_registry
from .llm.openai_llm import get_llm_instance


class NewAgentCLI:
    """
    Command-line interface for the New Agent Framework
    """
    
    def __init__(self):
        self.config = config
        self.is_initialized = False
    
    def initialize(self):
        """Initialize the CLI and all components"""
        if self.is_initialized:
            return
        
        print("🚀 Initializing New Agent Framework...")
        
        # Initialize database
        database.initialize()
        print("✅ Database initialized")
        
        # Validate configuration
        issues = self.config.validate()
        if issues:
            print("⚠️  Configuration issues found:")
            for issue in issues:
                print(f"   - {issue}")
        
        print(f"✅ Framework initialized with {len(agent_registry.list_agents())} agents")
        print(f"✅ {len(dummy_tool_registry.list_tools())} tools available")
        
        self.is_initialized = True
    
    async def execute_query(self, query: str, user_id: str = "default", **options) -> Dict[str, Any]:
        """Execute a user query through the complete agent workflow"""
        
        self.initialize()
        
        try:
            print(f"\n🎯 Query: {query}")
            print("=" * 60)
            
            # Create initial state
            state = create_initial_state(query, user_id)
            
            # Update state with options
            if options.get("verbose"):
                state["verbose"] = True
            if options.get("output_format"):
                state["output_format"] = options["output_format"]
            if options.get("show_metadata"):
                state["show_metadata"] = True
            
            # Generate execution plan
            print("🧠 Creating execution plan...")
            plan = planning_engine.create_plan(query, user_id)
            
            # Validate plan
            plan_issues = planning_engine.validate_plan(plan)
            if plan_issues:
                print("⚠️  Plan validation issues:")
                for issue in plan_issues:
                    print(f"   - {issue}")
                return {"success": False, "error": "Plan validation failed", "issues": plan_issues}
            
            # Update state with plan
            state = update_state_with_plan(state, plan)
            
            # Save plan to database
            database.save_plan(plan, state["session_id"])
            
            # Display plan summary
            self._display_plan_summary(plan)
            
            # Execute plan with streaming
            print("\n🔄 Executing plan...")
            events = execution_engine.execute_plan(state)
            
            # Stream execution with CLI interface
            result = cli_streamer.stream_execution(events, state["session_id"])
            
            # Save final execution state
            database.save_execution(state)
            
            # Get LLM usage statistics
            try:
                llm = get_llm_instance()
                llm_stats = llm.get_usage_stats(state["session_id"])
            except Exception as e:
                print(f"Warning: Could not get LLM stats: {e}")
                llm_stats = {"error": "Could not retrieve LLM statistics"}
            
            # Prepare final result
            final_result = {
                "success": result["success"],
                "session_id": state["session_id"],
                "plan_id": plan.plan_id,
                "query": query,
                "execution_stats": result["stats"],
                "llm_usage": llm_stats,
                "final_output": state.get("final_output", {}),
                "tool_outputs": state.get("tool_outputs", {}),
                "execution_history": state.get("execution_history", [])
            }
            
            if not result["success"]:
                final_result["error"] = result.get("error")
            
            # Display final summary
            self._display_final_summary(final_result)
            
            return final_result
            
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            database.log_error(error_msg, {"query": query, "user_id": user_id})
            
            return {
                "success": False,
                "error": error_msg,
                "query": query
            }
    
    def _display_plan_summary(self, plan):
        """Display a summary of the execution plan"""
        
        print(f"\n📋 Execution Plan (ID: {plan.plan_id})")
        print(f"   Steps: {len(plan.steps)}")
        print(f"   Mode: {plan.execution_mode}")
        print(f"   Estimated Duration: {plan.estimated_duration}s")
        print("\n   Steps:")
        
        for i, step in enumerate(plan.steps, 1):
            print(f"   {i}. {step.description}")
            print(f"      Agent: {step.agent_name}")
            print(f"      Tools: {', '.join(tc.tool_name for tc in step.tool_calls)}")
            if step.dependencies:
                print(f"      Dependencies: {len(step.dependencies)} steps")
            print()
    
    def _display_final_summary(self, result: Dict[str, Any]):
        """Display final execution summary"""
        
        print("\n" + "=" * 60)
        
        if result["success"]:
            print("✅ Execution completed successfully!")
        else:
            print("❌ Execution failed!")
            if "error" in result:
                print(f"   Error: {result['error']}")
        
        stats = result.get("execution_stats", {})
        if stats:
            print(f"\n📊 Execution Statistics:")
            print(f"   Duration: {stats.get('session_duration_seconds', 0):.2f}s")
            print(f"   Tools Called: {stats.get('total_tools_called', 0)}")
            print(f"   Errors: {stats.get('errors', 0)}")
        
        # Display LLM usage and cost
        llm_usage = result.get("llm_usage", {})
        if llm_usage and "total_usage" in llm_usage:
            usage = llm_usage["total_usage"]
            print(f"\n💰 LLM Usage & Cost:")
            print(f"   Model: {llm_usage.get('model', 'Unknown')}")
            print(f"   Prompt Tokens: {usage.get('prompt_tokens', 0):,}")
            print(f"   Completion Tokens: {usage.get('completion_tokens', 0):,}")
            print(f"   Total Tokens: {usage.get('total_tokens', 0):,}")
            print(f"   Estimated Cost: ${usage.get('estimated_cost', 0):.4f}")
            
            # Cost warning if above threshold
            cost = usage.get('estimated_cost', 0)
            if cost > config.llm.cost_alert_threshold:
                print(f"   ⚠️  Cost Alert: Above ${config.llm.cost_alert_threshold} threshold")
        elif "error" in llm_usage:
            print(f"\n💰 LLM Usage: {llm_usage['error']}")
        
        # Display key outputs
        tool_outputs = result.get("tool_outputs", {})
        if tool_outputs:
            print(f"\n🔧 Tool Results:")
            for tool_call_id, output in tool_outputs.items():
                if isinstance(output, dict):
                    # Show summary for dict outputs
                    keys = list(output.keys())[:3]
                    print(f"   {tool_call_id}: {', '.join(keys)}{'...' if len(output) > 3 else ''}")
                else:
                    # Show truncated string output
                    output_str = str(output)[:100]
                    print(f"   {tool_call_id}: {output_str}{'...' if len(str(output)) > 100 else ''}")
    
    async def list_agents(self, agent_type: str = None, active_only: bool = True):
        """List available agents"""
        
        self.initialize()
        
        from rich.table import Table
        from rich.console import Console
        
        console = Console()
        agents = agent_registry.list_agents(agent_type, active_only)
        
        table = Table(title="Available Agents", show_header=True, header_style="bold cyan")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Description", style="white")
        table.add_column("Tools", style="yellow")
        table.add_column("Status", style="magenta")
        
        for agent in agents:
            status = "Active" if agent.is_active else "Inactive"
            tools_str = ", ".join(agent.tools[:2]) + ("..." if len(agent.tools) > 2 else "")
            
            table.add_row(
                agent.name,
                agent.agent_type,
                agent.description[:50] + ("..." if len(agent.description) > 50 else ""),
                tools_str,
                status
            )
        
        console.print(table)
        return agents
    
    async def list_tools(self):
        """List available tools"""
        
        self.initialize()
        
        from rich.table import Table
        from rich.console import Console
        
        console = Console()
        tools = dummy_tool_registry.get_tool_descriptions()
        
        table = Table(title="Available Tools", show_header=True, header_style="bold cyan")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")
        
        for tool_name, description in tools.items():
            table.add_row(tool_name, description)
        
        console.print(table)
        return tools
    
    async def show_history(self, user_id: str = "default", limit: int = 10):
        """Show execution history"""
        
        self.initialize()
        
        history = database.get_execution_history(user_id, limit)
        
        if not history:
            print("No execution history found.")
            return []
        
        from rich.table import Table
        from rich.console import Console
        
        console = Console()
        table = Table(title=f"Execution History (User: {user_id})", show_header=True, header_style="bold cyan")
        table.add_column("Session ID", style="cyan")
        table.add_column("Query", style="white")
        table.add_column("Status", style="green")
        table.add_column("Created", style="yellow")
        table.add_column("Duration", style="magenta")
        
        for exec_data in history:
            # Calculate duration if available
            duration = ""
            if exec_data.get("started_at") and exec_data.get("completed_at"):
                from datetime import datetime
                start = datetime.fromisoformat(exec_data["started_at"])
                end = datetime.fromisoformat(exec_data["completed_at"])
                duration = f"{(end - start).total_seconds():.1f}s"
            
            # Truncate query for display
            query = exec_data["query"][:40] + ("..." if len(exec_data["query"]) > 40 else "")
            
            # Format created time
            created = exec_data["created_at"][:19].replace("T", " ")
            
            table.add_row(
                exec_data["session_id"][:8] + "...",
                query,
                exec_data["status"],
                created,
                duration
            )
        
        console.print(table)
        return history
    
    async def show_plan_details(self, plan_id: str):
        """Show detailed plan information"""
        
        self.initialize()
        
        plan_data = database.get_plan_details(plan_id)
        
        if not plan_data:
            print(f"Plan {plan_id} not found.")
            return None
        
        from rich.tree import Tree
        from rich.console import Console
        
        console = Console()
        
        # Create tree structure
        tree = Tree(f"[bold cyan]Plan: {plan_id}[/bold cyan]")
        tree.add(f"Query: {plan_data['query']}")
        tree.add(f"Status: {plan_data['status']}")
        tree.add(f"Mode: {plan_data['execution_mode']}")
        tree.add(f"Steps: {plan_data['total_steps']}")
        
        steps_node = tree.add("[bold]Steps:[/bold]")
        
        for step in plan_data.get("steps", []):
            step_node = steps_node.add(f"[cyan]{step['description']}[/cyan]")
            step_node.add(f"Agent: {step['agent_name']}")
            step_node.add(f"Status: {step['status']}")
            
            if step.get("tool_calls"):
                tools_node = step_node.add("Tools:")
                for tool_call in step["tool_calls"]:
                    tool_node = tools_node.add(f"{tool_call['tool_name']}")
                    tool_node.add(f"Status: {tool_call['status']}")
        
        console.print(tree)
        return plan_data
    
    async def get_stats(self):
        """Get framework statistics"""
        
        self.initialize()
        
        # Get agent stats
        agent_stats = agent_registry.get_all_stats()
        
        # Get tool stats  
        tool_stats = dummy_tool_registry.get_all_stats()
        
        # Get execution engine stats
        engine_stats = execution_engine.get_execution_status()
        
        stats = {
            "agents": {
                "total": len(agent_registry.agents),
                "active": len(agent_registry.list_agents(active_only=True)),
                "usage_stats": agent_stats
            },
            "tools": {
                "total": len(dummy_tool_registry.tools),
                "usage_stats": tool_stats
            },
            "execution_engine": engine_stats,
            "framework": {
                "version": config.version,
                "max_agents": config.max_agents,
                "database_type": config.database.type
            }
        }
        
        return stats


def create_cli_parser():
    """Create command-line argument parser"""
    
    parser = argparse.ArgumentParser(
        description="New Agent Framework - Self-contained CLI-driven AI Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute a query
  python -m new_agent "Fetch AI/ML jobs from LinkedIn in India and email summary to rohit@gmail.com"
  
  # Execute with options
  python -m new_agent "Get Instagram insights" --verbose --output-format rich
  
  # List agents
  python -m new_agent --list-agents
  
  # Show execution history
  python -m new_agent --history --user-id default --limit 20
  
  # Get framework statistics
  python -m new_agent --stats
        """
    )
    
    # Main execution
    parser.add_argument(
        "query",
        nargs="?",
        help="Query to execute through the agent framework"
    )
    
    # Options
    parser.add_argument(
        "--user-id",
        default="default",
        help="User ID for execution context (default: default)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--output-format",
        choices=["rich", "json", "plain"],
        default=config.cli.output_format,
        help="Output format (default: rich)"
    )
    
    parser.add_argument(
        "--show-metadata",
        action="store_true",
        help="Show detailed metadata in output"
    )
    
    # Information commands
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="List all available agents"
    )
    
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all available tools"
    )
    
    parser.add_argument(
        "--history",
        action="store_true",
        help="Show execution history"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limit for history results (default: 10)"
    )
    
    parser.add_argument(
        "--plan-details",
        help="Show detailed information for a specific plan ID"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show framework statistics"
    )
    
    # Configuration
    parser.add_argument(
        "--config-path",
        help="Path to configuration file"
    )
    
    return parser


async def main():
    """Main CLI entry point"""
    
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Initialize CLI
    cli = NewAgentCLI()
    
    # Override config if specified
    if args.config_path:
        cli.config.config_path = args.config_path
        cli.config._load_config()
    
    try:
        # Handle information commands
        if args.list_agents:
            await cli.list_agents()
            return
        
        if args.list_tools:
            await cli.list_tools()
            return
        
        if args.history:
            await cli.show_history(args.user_id, args.limit)
            return
        
        if args.plan_details:
            await cli.show_plan_details(args.plan_details)
            return
        
        if args.stats:
            stats = await cli.get_stats()
            
            if args.output_format == "json":
                print(json.dumps(stats, indent=2, default=str))
            else:
                from rich.console import Console
                from rich.json import JSON
                
                console = Console()
                console.print(JSON.from_data(stats))
            return
        
        # Handle main query execution
        if not args.query:
            parser.print_help()
            sys.exit(1)
        
        # Execute query
        result = await cli.execute_query(
            args.query,
            user_id=args.user_id,
            verbose=args.verbose,
            output_format=args.output_format,
            show_metadata=args.show_metadata
        )
        
        # Output result based on format
        if args.output_format == "json":
            print(json.dumps(result, indent=2, default=str))
        
        # Exit with appropriate code
        sys.exit(0 if result["success"] else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Execution interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
    
    finally:
        # Cleanup
        try:
            database.cleanup()
            execution_engine.cleanup()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())