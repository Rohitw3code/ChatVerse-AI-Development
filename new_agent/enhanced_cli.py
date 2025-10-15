"""
Enhanced CLI with Supervisor Pattern and Comprehensive Tool Streaming
Shows detailed agent execution, tool calling, and supervisor decisions
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
from rich.tree import Tree

from new_agent.core.langgraph_state import create_initial_state
from new_agent.execution.enhanced_langgraph_engine import enhanced_langgraph_engine
from new_agent.core.config import config


class EnhancedStreamingCLI:
    """Enhanced CLI with supervisor pattern and comprehensive tool streaming"""
    
    def __init__(self):
        self.console = Console()
        self.execution_stats = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "tools_called": 0,
            "agents_used": [],
            "start_time": None,
            "end_time": None,
            "supervisor_decisions": 0,
            "successful_tool_calls": 0,
            "failed_tool_calls": 0
        }
        self.current_content = ""
        self.active_tools = {}
        self.token_buffer = ""
        self.agent_progress = {}
        self.tool_history = []
    
    async def execute_query_with_streaming(
        self, 
        query: str, 
        user_id: str = "default",
        show_tokens: bool = True,
        show_tools: bool = True
    ) -> Dict[str, Any]:
        """Execute query with enhanced streaming display"""
        
        self.console.print(f"\n🎯 [bold blue]Enhanced Query Execution:[/bold blue] {query}")
        self.console.print("=" * 80)
        
        self.execution_stats["start_time"] = datetime.now()
        
        # Create enhanced layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="main", ratio=2),
            Layout(name="sidebar", size=25)
        )
        
        layout["main"].split_row(
            Layout(name="content", ratio=2),
            Layout(name="tools", ratio=1)
        )
        
        # Initialize display components
        header_panel = Panel("🚀 Initializing Enhanced LangGraph execution with Supervisor...", title="System Status")
        content_panel = Panel("", title="Agent Output", title_align="left")
        tools_panel = Panel(self._create_tools_display(), title="🔧 Tool Activity")
        stats_panel = Panel(self._create_enhanced_stats_table(), title="📊 Execution Statistics")
        
        layout["header"].update(header_panel)
        layout["content"].update(content_panel)
        layout["tools"].update(tools_panel)
        layout["sidebar"].update(stats_panel)
        
        success = True
        error_message = None
        
        try:
            with Live(layout, refresh_per_second=15, console=self.console) as live:
                
                # Stream execution with enhanced event handling
                async for event in enhanced_langgraph_engine.execute_query_with_streaming(query, user_id):
                    
                    # Update based on event type
                    if event.event_type == "execution_start":
                        header_panel = Panel(
                            f"🚀 [green]Enhanced Execution Started:[/green] {event.content}",
                            title="System Status",
                            border_style="green"
                        )
                        layout["header"].update(header_panel)
                    
                    elif event.event_type == "step_start":
                        step_name = event.metadata.get("step", "Unknown")
                        header_panel = Panel(
                            f"🔵 [blue]Workflow Step:[/blue] {step_name}",
                            title="Current Step",
                            border_style="blue"
                        )
                        layout["header"].update(header_panel)
                    
                    elif event.event_type == "agent_start":
                        header_panel = Panel(
                            f"🧠 [yellow]{event.agent_name}[/yellow] is analyzing the task...",
                            title="Agent Status",
                            border_style="yellow"
                        )
                        layout["header"].update(header_panel)
                        
                        if event.agent_name not in self.execution_stats["agents_used"]:
                            self.execution_stats["agents_used"].append(event.agent_name)
                    
                    elif event.event_type == "token" and show_tokens:
                        # Token-by-token streaming with step information
                        if event.token:
                            self.token_buffer += event.token
                            self.current_content = self.token_buffer
                            
                            # Get step information
                            step_info = ""
                            if hasattr(event, 'step_number') and event.step_number:
                                step_info = f" (Step {event.step_number})"
                            
                            # Update content with streaming text
                            content_panel = Panel(
                                Text(self.current_content, style="white"),
                                title=f"🧠 {event.agent_name or 'Agent'}{step_info} - Token Stream",
                                title_align="left",
                                border_style="cyan"
                            )
                            layout["content"].update(content_panel)
                            
                            # Print token to console for frontend debugging (optional, can be commented out)
                            # print(f"TOKEN[{event.agent_name}]: {event.token}", end="", flush=True)
                    
                    elif event.event_type == "model_start":
                        header_panel = Panel(
                            f"🤔 [cyan]{event.agent_name}[/cyan] model is thinking...",
                            title="Model Status",
                            border_style="cyan"
                        )
                        layout["header"].update(header_panel)
                        self.token_buffer = ""  # Reset for new model output
                    
                    elif event.event_type == "model_end":
                        tokens = event.metadata.get("tokens", 0)
                        self.execution_stats["total_tokens"] += tokens
                        
                        header_panel = Panel(
                            f"✅ [green]{event.agent_name}[/green] completed reasoning ({tokens} tokens)",
                            title="Model Status",
                            border_style="green"
                        )
                        layout["header"].update(header_panel)
                    
                    elif event.event_type == "tool_start" and show_tools:
                        # Enhanced tool execution tracking
                        tool_name = event.tool_name
                        agent_name = event.agent_name
                        
                        self.active_tools[tool_name] = {
                            "started_at": datetime.now(),
                            "agent": agent_name,
                            "input": event.tool_input
                        }
                        
                        self.tool_history.append({
                            "tool": tool_name,
                            "agent": agent_name,
                            "status": "started",
                            "timestamp": datetime.now()
                        })
                        
                        # Get step information
                        step_info = ""
                        if hasattr(event, 'step_number') and event.step_number:
                            step_info = f" (Step {event.step_number})"
                        
                        header_panel = Panel(
                            f"🔧 [cyan]{agent_name}[/cyan]{step_info} executing tool: [bold]{tool_name}[/bold]",
                            title="Tool Execution",
                            border_style="cyan"
                        )
                        layout["header"].update(header_panel)
                        
                        # Print tool start for frontend
                        self.console.print(f"      🔧 [bold cyan]TOOL EXECUTION STARTED:[/bold cyan] {tool_name}")
                        self.console.print(f"         Agent: {agent_name}")
                        if event.tool_input:
                            input_str = str(event.tool_input)[:100]
                            self.console.print(f"         Input: {input_str}...")
                        
                        # Show tool details
                        tool_info = f"🔧 [bold cyan]Tool Starting:[/bold cyan] {tool_name}\n"
                        tool_info += f"🤖 [dim]Agent:[/dim] {agent_name}{step_info}\n"
                        tool_info += f"⏰ [dim]Started:[/dim] {datetime.now().strftime('%H:%M:%S')}\n"
                        if event.tool_input:
                            input_str = str(event.tool_input)[:150]
                            tool_info += f"📥 [dim]Input:[/dim] {input_str}..."
                        
                        content_panel = Panel(
                            tool_info,
                            title="Tool Execution Details",
                            title_align="left",
                            border_style="cyan"
                        )
                        layout["content"].update(content_panel)
                        
                        # Update tools panel
                        tools_panel = Panel(
                            self._create_tools_display(),
                            title="🔧 Tool Activity",
                            border_style="cyan"
                        )
                        layout["tools"].update(tools_panel)
                    
                    elif event.event_type == "tool_end" and show_tools:
                        # Tool completion tracking
                        tool_name = event.tool_name
                        agent_name = event.agent_name
                        
                        duration = 0
                        if tool_name in self.active_tools:
                            duration = (datetime.now() - self.active_tools[tool_name]["started_at"]).total_seconds()
                            del self.active_tools[tool_name]
                        
                        self.execution_stats["tools_called"] += 1
                        
                        # Check if tool was successful
                        tool_success = True
                        if hasattr(event, 'tool_output') and event.tool_output:
                            if isinstance(event.tool_output, dict) and "error" in event.tool_output:
                                self.execution_stats["failed_tool_calls"] += 1
                                tool_success = False
                            else:
                                self.execution_stats["successful_tool_calls"] += 1
                        else:
                            self.execution_stats["successful_tool_calls"] += 1
                        
                        self.tool_history.append({
                            "tool": tool_name,
                            "agent": agent_name,
                            "status": "completed",
                            "duration": duration,
                            "success": tool_success,
                            "timestamp": datetime.now()
                        })
                        
                        # Get step information
                        step_info = ""
                        if hasattr(event, 'step_number') and event.step_number:
                            step_info = f" (Step {event.step_number})"
                        
                        status_icon = "✅" if tool_success else "❌"
                        status_color = "green" if tool_success else "red"
                        
                        header_panel = Panel(
                            f"{status_icon} [{status_color}]{agent_name}[/{status_color}]{step_info} completed tool: [bold]{tool_name}[/bold] ({duration:.2f}s)",
                            title="Tool Status",
                            border_style=status_color
                        )
                        layout["header"].update(header_panel)
                        
                        # Print tool completion for frontend
                        self.console.print(f"      {status_icon} [bold {status_color}]TOOL EXECUTION COMPLETED:[/bold {status_color}] {tool_name}")
                        self.console.print(f"         Agent: {agent_name}")
                        self.console.print(f"         Duration: {duration:.2f} seconds")
                        self.console.print(f"         Status: {'Success' if tool_success else 'Failed'}")
                        
                        # Show tool results
                        tool_info = f"{status_icon} [bold {status_color}]Tool Completed:[/bold {status_color}] {tool_name}\n"
                        tool_info += f"🤖 [dim]Agent:[/dim] {agent_name}{step_info}\n"
                        tool_info += f"⏱️  [dim]Duration:[/dim] {duration:.2f}s\n"
                        tool_info += f"📊 [dim]Status:[/dim] {'Success' if tool_success else 'Failed'}\n"
                        if hasattr(event, 'tool_output') and event.tool_output:
                            output_str = str(event.tool_output)[:200]
                            tool_info += f"📤 [dim]Output:[/dim] {output_str}..."
                        
                        content_panel = Panel(
                            tool_info,
                            title="Tool Results",
                            title_align="left",
                            border_style=status_color
                        )
                        layout["content"].update(content_panel)
                        
                        # Update tools panel
                        tools_panel = Panel(
                            self._create_tools_display(),
                            title="🔧 Tool Activity"
                        )
                        layout["tools"].update(tools_panel)
                    
                    elif event.event_type == "execution_plan_ready":
                        plan_info = event.metadata
                        header_panel = Panel(
                            f"📋 [blue]Execution Plan Ready:[/blue] {plan_info['total_agents']} agents selected",
                            title="Planning Complete",
                            border_style="blue"
                        )
                        layout["header"].update(header_panel)
                        
                        # Display execution plan
                        plan_text = f"📋 [bold blue]Execution Plan:[/bold blue]\n"
                        for i, agent in enumerate(plan_info['agent_list']):
                            plan_text += f"  {i+1}. {agent}\n"
                        
                        content_panel = Panel(
                            plan_text,
                            title="Execution Plan",
                            title_align="left",
                            border_style="blue"
                        )
                        layout["content"].update(content_panel)
                        
                        # Print to console for frontend
                        self.console.print(f"\n🎯 [bold]STEP-BY-STEP EXECUTION PLAN:[/bold]")
                        for i, agent in enumerate(plan_info['agent_list']):
                            self.console.print(f"   Step {i+1}: {agent}")
                        self.console.print("")
                    
                    elif event.event_type == "step_start_detailed":
                        step_info = event.metadata
                        header_panel = Panel(
                            f"🎯 [yellow]Step {event.step_number}/{step_info['total_steps']}:[/yellow] {event.agent_name}",
                            title="Current Step",
                            border_style="yellow"
                        )
                        layout["header"].update(header_panel)
                        
                        # Print step start for frontend
                        self.console.print(f"\n🎯 [bold yellow]STEP {event.step_number}/{step_info['total_steps']} STARTING:[/bold yellow] {event.agent_name}")
                        self.console.print(f"   📝 Description: {step_info.get('agent_description', 'N/A')}")
                    
                    elif event.event_type == "agent_initializing":
                        tools_info = event.metadata
                        header_panel = Panel(
                            f"🔧 [cyan]Initializing:[/cyan] {event.agent_name} ({tools_info['tool_count']} tools)",
                            title="Agent Setup",
                            border_style="cyan"
                        )
                        layout["header"].update(header_panel)
                        
                        # Print initialization for frontend
                        self.console.print(f"   🔧 [cyan]Initializing {event.agent_name}:[/cyan]")
                        self.console.print(f"      Tools: {', '.join(tools_info.get('tools_available', []))}")
                        self.console.print(f"      Capabilities: {', '.join(tools_info.get('capabilities', []))}")
                    
                    elif event.event_type == "agent_execution_start":
                        header_panel = Panel(
                            f"🚀 [green]Executing:[/green] {event.agent_name} (Step {event.step_number})",
                            title="Agent Execution",
                            border_style="green"
                        )
                        layout["header"].update(header_panel)
                        
                        # Print execution start for frontend
                        self.console.print(f"   🚀 [bold green]AGENT EXECUTION STARTED:[/bold green] {event.agent_name}")
                        self.token_buffer = ""  # Reset token buffer for new agent
                    
                    elif event.event_type == "agent_execution_complete":
                        duration = event.metadata.get('duration_seconds', 0)
                        header_panel = Panel(
                            f"✅ [green]Completed:[/green] {event.agent_name} ({duration:.2f}s)",
                            title="Agent Complete",
                            border_style="green"
                        )
                        layout["header"].update(header_panel)
                        
                        # Print completion for frontend
                        self.console.print(f"   ✅ [bold green]AGENT EXECUTION COMPLETED:[/bold green] {event.agent_name}")
                        self.console.print(f"      Duration: {duration:.2f} seconds")
                    
                    elif event.event_type == "step_complete_detailed":
                        header_panel = Panel(
                            f"🎉 [green]Step {event.step_number} Complete:[/green] {event.agent_name}",
                            title="Step Complete",
                            border_style="green"
                        )
                        layout["header"].update(header_panel)
                        
                        # Print step completion for frontend
                        self.console.print(f"🎉 [bold green]STEP {event.step_number} COMPLETED:[/bold green] {event.agent_name}\n")
                    
                    elif event.event_type == "all_agents_complete":
                        header_panel = Panel(
                            f"🎊 [bold green]All Agents Complete![/bold green] ({event.metadata['total_agents_executed']} agents)",
                            title="Execution Complete",
                            border_style="green"
                        )
                        layout["header"].update(header_panel)
                        
                        # Print final completion for frontend
                        self.console.print(f"🎊 [bold green]ALL AGENTS COMPLETED SUCCESSFULLY![/bold green]")
                        self.console.print(f"   Total agents executed: {event.metadata['total_agents_executed']}")
                        self.console.print(f"   Agents: {', '.join(event.metadata['agents_list'])}")
                    
                    elif event.event_type == "agent_execution_error":
                        header_panel = Panel(
                            f"❌ [red]Agent Error:[/red] {event.agent_name} (Step {event.step_number})",
                            title="Agent Error",
                            border_style="red"
                        )
                        layout["header"].update(header_panel)
                        
                        # Print error for frontend
                        self.console.print(f"   ❌ [bold red]AGENT EXECUTION ERROR:[/bold red] {event.agent_name}")
                        self.console.print(f"      Error: {event.metadata.get('error', 'Unknown error')}")
                    
                    elif event.event_type == "execution_complete":
                        header_panel = Panel(
                            "🎉 [bold green]Enhanced execution completed successfully![/bold green]",
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
                    
                    # Update statistics
                    stats_panel = Panel(
                        self._create_enhanced_stats_table(),
                        title="📊 Live Statistics",
                        border_style="blue"
                    )
                    layout["sidebar"].update(stats_panel)
                    
                    # Small delay for visual effect
                    await asyncio.sleep(0.02)
        
        except Exception as e:
            success = False
            error_message = str(e)
            import traceback
            self.console.print(f"❌ [red]Execution failed:[/red] {str(e)}")
            self.console.print("[dim]Full traceback:[/dim]")
            self.console.print(traceback.format_exc())
        
        finally:
            self.execution_stats["end_time"] = datetime.now()
        
        # Show enhanced final summary
        self._display_enhanced_final_summary(success, error_message)
        
        return {
            "success": success,
            "error": error_message,
            "stats": self.execution_stats,
            "query": query,
            "tool_history": self.tool_history
        }
    
    def _create_tools_display(self) -> Text:
        """Create tools activity display"""
        
        if not self.tool_history:
            return Text("No tools executed yet", style="dim")
        
        tools_text = Text()
        
        # Show last 5 tool activities
        recent_tools = self.tool_history[-5:]
        
        for tool_info in recent_tools:
            status_icon = "🟢" if tool_info["status"] == "completed" else "🟡"
            duration_text = f" ({tool_info.get('duration', 0):.1f}s)" if tool_info["status"] == "completed" else ""
            
            tools_text.append(f"{status_icon} {tool_info['tool']}")
            tools_text.append(f" by {tool_info['agent']}{duration_text}\n", style="dim")
        
        # Show active tools
        if self.active_tools:
            tools_text.append("\n🔄 Active Tools:\n", style="bold yellow")
            for tool_name, tool_info in self.active_tools.items():
                elapsed = (datetime.now() - tool_info["started_at"]).total_seconds()
                tools_text.append(f"  • {tool_name} ({elapsed:.1f}s)\n", style="yellow")
        
        return tools_text
    
    def _create_enhanced_stats_table(self) -> Table:
        """Create enhanced statistics table"""
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Metric", style="cyan", width=18)
        table.add_column("Value", style="white", width=12)
        table.add_column("Details", style="dim", width=20)
        
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
        cost = self.execution_stats['total_tokens'] * 0.000375 / 1000
        self.execution_stats['total_cost'] = cost
        table.add_row(
            "Estimated Cost",
            f"${cost:.4f}",
            "OpenAI API cost"
        )
        
        # Tools
        table.add_row(
            "Tools Called",
            str(self.execution_stats['tools_called']),
            f"✅{self.execution_stats['successful_tool_calls']} ❌{self.execution_stats['failed_tool_calls']}"
        )
        
        # Agents
        table.add_row(
            "Agents Used",
            str(len(self.execution_stats['agents_used'])),
            ", ".join(self.execution_stats['agents_used'][:2]) + ("..." if len(self.execution_stats['agents_used']) > 2 else "")
        )
        
        # Active tools
        if self.active_tools:
            table.add_row(
                "Active Tools",
                str(len(self.active_tools)),
                "Currently executing"
            )
        
        return table
    
    def _display_enhanced_final_summary(self, success: bool, error_message: Optional[str]):
        """Display enhanced final execution summary"""
        self.console.print("\n" + "=" * 80)
        
        if success:
            self.console.print("🎉 [bold green]Enhanced execution completed successfully![/bold green]")
        else:
            self.console.print("❌ [bold red]Enhanced execution failed![/bold red]")
            if error_message:
                self.console.print(f"   [red]Error:[/red] {error_message}")
        
        # Enhanced stats
        stats = self.execution_stats
        duration = 0
        if stats["start_time"] and stats["end_time"]:
            duration = (stats["end_time"] - stats["start_time"]).total_seconds()
        
        # Create summary sections
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Section", style="bold cyan", width=20)
        summary_table.add_column("Value", style="white")
        
        # Performance metrics
        summary_table.add_row("💰 Total Cost:", f"${stats['total_cost']:.4f}")
        summary_table.add_row("🔢 Total Tokens:", f"{stats['total_tokens']:,}")
        summary_table.add_row("⏱️  Duration:", f"{duration:.2f}s")
        summary_table.add_row("", "")
        
        # Agent metrics
        summary_table.add_row("🤖 Agents Used:", ", ".join(stats['agents_used']))
        summary_table.add_row("🔧 Tools Called:", f"{stats['tools_called']} total")
        summary_table.add_row("✅ Successful Tools:", str(stats['successful_tool_calls']))
        summary_table.add_row("❌ Failed Tools:", str(stats['failed_tool_calls']))
        
        if stats['total_cost'] > config.llm.cost_alert_threshold:
            summary_table.add_row("⚠️  Cost Alert:", f"Above ${config.llm.cost_alert_threshold} threshold")
        
        self.console.print(Panel(
            summary_table, 
            title="📋 Enhanced Execution Summary",
            border_style="green" if success else "red"
        ))
        
        # Show tool execution summary if tools were used
        if self.tool_history:
            self.console.print("\n🔧 [bold]Tool Execution Summary:[/bold]")
            tools_summary = Table()
            tools_summary.add_column("Tool", style="cyan")
            tools_summary.add_column("Agent", style="yellow") 
            tools_summary.add_column("Status", style="white")
            tools_summary.add_column("Duration", style="dim")
            
            for tool_info in self.tool_history[-10:]:  # Last 10 tools
                status = "✅ Success" if tool_info["status"] == "completed" else "🟡 Running"
                duration = f"{tool_info.get('duration', 0):.2f}s" if tool_info.get('duration') else "N/A"
                
                tools_summary.add_row(
                    tool_info['tool'],
                    tool_info['agent'],
                    status,
                    duration
                )
            
            self.console.print(tools_summary)


async def main():
    """Enhanced main CLI function"""
    parser = argparse.ArgumentParser(
        description="Enhanced New Agent Framework with Supervisor Pattern and Tool Streaming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute with full streaming and tool tracking
  python -m new_agent "Find Python developer jobs and email me a summary"
  
  # Execute with token streaming but no tool details
  python -m new_agent "Research AI trends" --no-tools
  
  # Execute without token display
  python -m new_agent "Get Instagram insights" --no-tokens
  
  # List available enhanced agents
  python -m new_agent --list-agents
"""
    )
    
    parser.add_argument("query", nargs="?", help="Query to execute")
    parser.add_argument("--user-id", default="default", help="User ID")
    parser.add_argument("--show-tokens", action="store_true", default=True, help="Show token-by-token streaming")
    parser.add_argument("--no-tokens", action="store_true", help="Disable token streaming")
    parser.add_argument("--show-tools", action="store_true", default=True, help="Show tool execution details")
    parser.add_argument("--no-tools", action="store_true", help="Hide tool execution details")
    parser.add_argument("--list-agents", action="store_true", help="List available enhanced agents")
    
    args = parser.parse_args()
    
    cli = EnhancedStreamingCLI()
    
    if args.list_agents:
        cli.console.print("\n🤖 [bold blue]Available Enhanced Agents with Supervisor:[/bold blue]")
        agents_info = enhanced_langgraph_engine.get_available_agents()
        
        for name, info in agents_info.items():
            cli.console.print(f"\n[bold cyan]🤖 {name}[/bold cyan]")
            cli.console.print(f"   📝 Description: {info['description']}")
            cli.console.print(f"   🎯 Capabilities: {', '.join(info['capabilities'])}")
            cli.console.print(f"   🔧 Tools: {', '.join(info['tools'])} ({info['tool_count']} total)")
        
        cli.console.print(f"\n[bold yellow]🎛️ Supervisor:[/bold yellow]")
        cli.console.print("   📝 Description: Coordinates agent execution and task routing")
        cli.console.print("   🎯 Capabilities: Planning, agent selection, workflow coordination")
        
        return
    
    if not args.query:
        parser.print_help()
        return
    
    show_tokens = args.show_tokens and not args.no_tokens
    show_tools = args.show_tools and not args.no_tools
    
    try:
        result = await cli.execute_query_with_streaming(
            args.query,
            args.user_id,
            show_tokens=show_tokens,
            show_tools=show_tools
        )
        
        sys.exit(0 if result["success"] else 1)
        
    except KeyboardInterrupt:
        cli.console.print("\n❌ [red]Enhanced execution interrupted by user[/red]")
        sys.exit(1)
    except Exception as e:
        cli.console.print(f"\n❌ [red]Unexpected error in enhanced system:[/red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())