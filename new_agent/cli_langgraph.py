"""
Enhanced CLI with LangGraph streaming, token-by-token display, and tool call tracking
"""

import asyncio
import argparse
import sys
import time
from typing import Dict, Any, Optional
from datetime import datetime

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.layout import Layout

from new_agent.core.langgraph_state import create_initial_state
from new_agent.execution.langgraph_engine import langgraph_execution_engine
from new_agent.core.config import config


class LangGraphStreamingCLI:
    """Enhanced CLI with LangGraph streaming support"""
    
    def __init__(self):
        self.console = Console()
        self.execution_stats = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "tools_called": 0,
            "agents_used": [],
            "start_time": None,
            "end_time": None
        }
        self.current_content = ""
        self.active_tools = {}
        self.token_buffer = ""
    
    async def execute_query_with_streaming(
        self, 
        query: str, 
        user_id: str = "default",
        show_tokens: bool = True
    ) -> Dict[str, Any]:
        """Execute query with rich streaming display"""
        
        self.console.print(f"\n🎯 [bold blue]Query:[/bold blue] {query}")
        self.console.print("=" * 60)
        
        self.execution_stats["start_time"] = datetime.now()
        
        # Create layout for streaming display
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=8)
        )
        
        # Initialize display components
        header_panel = Panel("🚀 Initializing LangGraph execution...", title="Status")
        main_content = Panel("", title="Agent Output", title_align="left")
        stats_table = self._create_stats_table()
        
        layout["header"].update(header_panel)
        layout["main"].update(main_content)
        layout["footer"].update(stats_table)
        
        success = True
        error_message = None
        
        try:
            with Live(layout, refresh_per_second=10, console=self.console) as live:
                
                # Stream execution
                async for event in langgraph_execution_engine.execute_query_with_streaming(query, user_id):
                    
                    # Update based on event type
                    if event.event_type == "execution_start":
                        header_panel = Panel(
                            f"🚀 [green]Started:[/green] {event.content}",
                            title="Execution Status",
                            border_style="green"
                        )
                        layout["header"].update(header_panel)
                    
                    elif event.event_type == "agent_start":
                        header_panel = Panel(
                            f"🧠 [yellow]{event.agent_name}[/yellow] is thinking...",
                            title="Current Agent",
                            border_style="yellow"
                        )
                        layout["header"].update(header_panel)
                        
                        if event.agent_name not in self.execution_stats["agents_used"]:
                            self.execution_stats["agents_used"].append(event.agent_name)
                    
                    elif event.event_type == "token" and show_tokens:
                        # Token-by-token streaming
                        if event.token:
                            self.token_buffer += event.token
                            self.current_content = self.token_buffer
                            
                            # Update main content with streaming text
                            main_content = Panel(
                                Text(self.current_content, style="white"),
                                title=f"🧠 {event.agent_name or 'Agent'} - Thinking",
                                title_align="left",
                                border_style="cyan"
                            )
                            layout["main"].update(main_content)
                    
                    elif event.event_type == "agent_end":
                        # Agent completed
                        header_panel = Panel(
                            f"✅ [green]{event.agent_name}[/green] completed reasoning",
                            title="Agent Status",
                            border_style="green"
                        )
                        layout["header"].update(header_panel)
                        
                        # Update token stats
                        if hasattr(event, 'tokens_used'):
                            self.execution_stats["total_tokens"] += event.tokens_used
                        if hasattr(event, 'cost_incurred'):
                            self.execution_stats["total_cost"] += event.cost_incurred
                        
                        # Clear token buffer for next agent
                        self.token_buffer = ""
                    
                    elif event.event_type == "tool_start":
                        # Tool execution started
                        tool_name = event.tool_name
                        self.active_tools[tool_name] = {
                            "started_at": datetime.now(),
                            "input": event.tool_input
                        }
                        
                        header_panel = Panel(
                            f"🔧 [cyan]Tool:[/cyan] {tool_name} starting...",
                            title="Tool Execution",
                            border_style="cyan"
                        )
                        layout["header"].update(header_panel)
                        
                        # Show tool input
                        tool_info = f"🔧 [bold cyan]Starting Tool:[/bold cyan] {tool_name}\n"
                        if event.tool_input:
                            tool_info += f"📥 [dim]Input:[/dim] {str(event.tool_input)[:100]}..."
                        
                        main_content = Panel(
                            tool_info,
                            title="Tool Execution",
                            title_align="left",
                            border_style="cyan"
                        )
                        layout["main"].update(main_content)
                    
                    elif event.event_type == "tool_end":
                        # Tool execution completed
                        tool_name = event.tool_name
                        self.execution_stats["tools_called"] += 1
                        
                        if tool_name in self.active_tools:
                            duration = (datetime.now() - self.active_tools[tool_name]["started_at"]).total_seconds()
                            del self.active_tools[tool_name]
                        else:
                            duration = 0
                        
                        header_panel = Panel(
                            f"✅ [green]Tool:[/green] {tool_name} completed ({duration:.2f}s)",
                            title="Tool Status",
                            border_style="green"
                        )
                        layout["header"].update(header_panel)
                        
                        # Show tool output
                        tool_info = f"✅ [bold green]Completed Tool:[/bold green] {tool_name}\n"
                        tool_info += f"⏱️  [dim]Duration:[/dim] {duration:.2f}s\n"
                        if event.tool_output:
                            output_str = str(event.tool_output)[:200]
                            tool_info += f"📤 [dim]Output:[/dim] {output_str}..."
                        
                        main_content = Panel(
                            tool_info,
                            title="Tool Result",
                            title_align="left",
                            border_style="green"
                        )
                        layout["main"].update(main_content)
                    
                    elif event.event_type == "step_start":
                        step_name = event.metadata.get("step", "Unknown")
                        header_panel = Panel(
                            f"🔵 [blue]Step:[/blue] {step_name}",
                            title="Workflow Step",
                            border_style="blue"
                        )
                        layout["header"].update(header_panel)
                    
                    elif event.event_type == "step_end":
                        step_name = event.metadata.get("step", "Unknown")
                        header_panel = Panel(
                            f"✅ [green]Completed:[/green] {step_name}",
                            title="Workflow Step",
                            border_style="green"
                        )
                        layout["header"].update(header_panel)
                    
                    elif event.event_type == "execution_complete":
                        header_panel = Panel(
                            "🎉 [bold green]Execution completed successfully![/bold green]",
                            title="Final Status",
                            border_style="green"
                        )
                        layout["header"].update(header_panel)
                    
                    elif event.event_type == "error":
                        success = False
                        error_message = event.content
                        header_panel = Panel(
                            f"❌ [red]Error:[/red] {event.content}",
                            title="Error",
                            border_style="red"
                        )
                        layout["header"].update(header_panel)
                        
                        # Show traceback if available
                        if hasattr(event, 'metadata') and event.metadata.get('traceback'):
                            self.console.print(f"[dim]Full traceback:[/dim]")
                            self.console.print(event.metadata['traceback'])
                    
                    # Update stats table
                    stats_table = self._create_stats_table()
                    layout["footer"].update(stats_table)
                    
                    # Small delay for visual effect
                    await asyncio.sleep(0.01)
        
        except Exception as e:
            success = False
            error_message = str(e)
            import traceback
            self.console.print(f"❌ [red]Execution failed:[/red] {str(e)}")
            self.console.print("[dim]Full traceback:[/dim]")
            self.console.print(traceback.format_exc())
        
        finally:
            self.execution_stats["end_time"] = datetime.now()
        
        # Show final summary
        self._display_final_summary(success, error_message)
        
        return {
            "success": success,
            "error": error_message,
            "stats": self.execution_stats,
            "query": query
        }
    
    def _create_stats_table(self) -> Panel:
        """Create statistics table"""
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="white", width=15)
        table.add_column("Details", style="dim", width=25)
        
        # Execution time
        if self.execution_stats["start_time"]:
            if self.execution_stats["end_time"]:
                duration = (self.execution_stats["end_time"] - self.execution_stats["start_time"]).total_seconds()
            else:
                duration = (datetime.now() - self.execution_stats["start_time"]).total_seconds()
            table.add_row("Duration", f"{duration:.2f}s", "Real-time execution")
        
        # Token usage
        table.add_row(
            "Tokens Used", 
            f"{self.execution_stats['total_tokens']:,}",
            "GPT-4o Mini tokens"
        )
        
        # Cost
        table.add_row(
            "Estimated Cost",
            f"${self.execution_stats['total_cost']:.4f}",
            "OpenAI API cost"
        )
        
        # Tools and agents
        table.add_row(
            "Tools Called",
            str(self.execution_stats['tools_called']),
            "External tool executions"
        )
        
        table.add_row(
            "Agents Used",
            str(len(self.execution_stats['agents_used'])),
            ", ".join(self.execution_stats['agents_used'][:2])
        )
        
        return Panel(table, title="📊 Live Statistics", border_style="blue")
    
    def _display_final_summary(self, success: bool, error_message: Optional[str]):
        """Display final execution summary"""
        self.console.print("\n" + "=" * 60)
        
        if success:
            self.console.print("✅ [bold green]Execution completed successfully![/bold green]")
        else:
            self.console.print("❌ [bold red]Execution failed![/bold red]")
            if error_message:
                self.console.print(f"   [red]Error:[/red] {error_message}")
        
        # Final stats
        stats = self.execution_stats
        duration = 0
        if stats["start_time"] and stats["end_time"]:
            duration = (stats["end_time"] - stats["start_time"]).total_seconds()
        
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("💰 Total Cost:", f"${stats['total_cost']:.4f}")
        summary_table.add_row("🔢 Total Tokens:", f"{stats['total_tokens']:,}")
        summary_table.add_row("🔧 Tools Called:", str(stats['tools_called']))
        summary_table.add_row("🤖 Agents Used:", ", ".join(stats['agents_used']))
        summary_table.add_row("⏱️  Duration:", f"{duration:.2f}s")
        
        if stats['total_cost'] > config.llm.cost_alert_threshold:
            summary_table.add_row("⚠️  Cost Alert:", f"Above ${config.llm.cost_alert_threshold} threshold")
        
        self.console.print(Panel(summary_table, title="📋 Final Summary", border_style="green" if success else "red"))


async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Enhanced New Agent Framework with LangGraph streaming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute with token streaming
  python -m new_agent "Find Python developer jobs on LinkedIn"
  
  # Execute with full streaming display
  python -m new_agent "Get Instagram insights and email summary" --show-tokens
  
  # Execute without token display
  python -m new_agent "Research AI trends" --no-tokens
"""
    )
    
    parser.add_argument("query", nargs="?", help="Query to execute")
    parser.add_argument("--user-id", default="default", help="User ID")
    parser.add_argument("--show-tokens", action="store_true", default=True, help="Show token-by-token streaming")
    parser.add_argument("--no-tokens", action="store_true", help="Disable token streaming")
    parser.add_argument("--list-agents", action="store_true", help="List available agents")
    
    args = parser.parse_args()
    
    cli = LangGraphStreamingCLI()
    
    if args.list_agents:
        cli.console.print("\n🤖 [bold blue]Available LangGraph Agents:[/bold blue]")
        agents = langgraph_execution_engine.agents
        for name, agent in agents.items():
            info = agent.get_agent_info()
            cli.console.print(f"  • [cyan]{name}[/cyan]: {info['description']}")
        return
    
    if not args.query:
        parser.print_help()
        return
    
    show_tokens = args.show_tokens and not args.no_tokens
    
    try:
        result = await cli.execute_query_with_streaming(
            args.query,
            args.user_id,
            show_tokens=show_tokens
        )
        
        sys.exit(0 if result["success"] else 1)
        
    except KeyboardInterrupt:
        cli.console.print("\n❌ [red]Execution interrupted by user[/red]")
        sys.exit(1)
    except Exception as e:
        cli.console.print(f"\n❌ [red]Unexpected error:[/red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())