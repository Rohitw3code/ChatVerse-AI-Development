"""
Enhanced CLI for Main Agent System
Handles direct responses and tool execution with detailed streaming display
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align

from new_agent.execution.enhanced_main_engine import enhanced_main_engine
from new_agent.core.langgraph_state import StreamingEvent


class EnhancedMainAgentCLI:
    """
    Advanced CLI for the Enhanced Main Agent System
    Displays streaming responses and tool execution details
    """
    
    def __init__(self):
        self.console = Console()
        self.engine = enhanced_main_engine
        
        # Display components
        self.layout = Layout()
        self.setup_layout()
        
        # State tracking
        self.current_response = ""
        self.tool_executions = []
        self.execution_stats = {
            "start_time": None,
            "tools_executed": 0,
            "tokens_streamed": 0,
            "execution_mode": "unknown"
        }
        
    def setup_layout(self):
        """Setup the Rich layout with multiple panels"""
        
        # Main layout structure
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=5)
        )
        
        # Split main section
        self.layout["main"].split_row(
            Layout(name="response", ratio=2),
            Layout(name="tools", ratio=1)
        )
        
        # Split footer
        self.layout["footer"].split_row(
            Layout(name="stats", ratio=1),
            Layout(name="status", ratio=1)
        )
    
    def update_header(self, query: str):
        """Update header with current query"""
        
        header_content = Panel(
            f"🧠 Enhanced Main Agent - Processing: {query[:60]}{'...' if len(query) > 60 else ''}",
            style="bold blue",
            border_style="blue"
        )
        self.layout["header"].update(header_content)
    
    def update_response_panel(self):
        """Update the main response panel"""
        
        if self.current_response:
            response_text = Text(self.current_response)
            response_panel = Panel(
                response_text,
                title="💬 Main Agent Response",
                border_style="green",
                padding=(1, 2)
            )
        else:
            response_panel = Panel(
                "Waiting for response...",
                title="💬 Main Agent Response",
                border_style="yellow",
                padding=(1, 2)
            )
        
        self.layout["response"].update(response_panel)
    
    def update_tools_panel(self):
        """Update the tools execution panel"""
        
        if self.tool_executions:
            tools_table = Table(title="🛠️ Tool Executions")
            tools_table.add_column("Tool", style="cyan")
            tools_table.add_column("Status", style="magenta")
            tools_table.add_column("Output", style="white", max_width=30)
            
            for tool_exec in self.tool_executions[-5:]:  # Show last 5
                status = "✅ Complete" if tool_exec.get("completed") else "🔄 Running"
                output = str(tool_exec.get("output", ""))[:50] + "..." if len(str(tool_exec.get("output", ""))) > 50 else str(tool_exec.get("output", ""))
                
                tools_table.add_row(
                    tool_exec.get("name", "Unknown"),
                    status,
                    output
                )
            
            tools_panel = Panel(tools_table, border_style="blue")
        else:
            tools_panel = Panel(
                "No tool executions yet",
                title="🛠️ Tool Executions",
                border_style="dim blue"
            )
        
        self.layout["tools"].update(tools_panel)
    
    def update_stats_panel(self):
        """Update execution statistics panel"""
        
        stats_table = Table(title="📊 Execution Stats")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        if self.execution_stats["start_time"]:
            duration = (datetime.now() - self.execution_stats["start_time"]).total_seconds()
            stats_table.add_row("Duration", f"{duration:.1f}s")
        
        stats_table.add_row("Mode", self.execution_stats["execution_mode"])
        stats_table.add_row("Tools", str(self.execution_stats["tools_executed"]))
        stats_table.add_row("Tokens", str(self.execution_stats["tokens_streamed"]))
        
        stats_panel = Panel(stats_table, border_style="green")
        self.layout["stats"].update(stats_panel)
    
    def update_status_panel(self, latest_event: Optional[StreamingEvent] = None):
        """Update status panel with latest event"""
        
        if latest_event:
            event_type = latest_event.event_type
            content = latest_event.content
            
            # Status indicators
            status_indicators = {
                "tool_discovery_start": "🔍 Discovering Tools",
                "tool_discovery_complete": "✅ Tools Found",
                "direct_response_start": "💬 Direct Response",
                "tool_execution_mode": "🛠️ Tool Execution",
                "main_agent_token": "📝 Streaming Text",
                "tool_start": "🔧 Tool Running",
                "tool_end": "✅ Tool Complete",
                "execution_complete": "🎉 Complete"
            }
            
            status_text = status_indicators.get(event_type, f"📡 {event_type}")
            
            status_content = f"{status_text}\n{content}"
        else:
            status_content = "🟢 System Ready"
        
        status_panel = Panel(
            status_content,
            title="🚦 Status",
            border_style="magenta"
        )
        self.layout["status"].update(status_panel)
    
    def update_display(self, latest_event: Optional[StreamingEvent] = None):
        """Update all display components"""
        
        self.update_response_panel()
        self.update_tools_panel()
        self.update_stats_panel()
        self.update_status_panel(latest_event)
    
    async def process_streaming_event(self, event: StreamingEvent):
        """Process a streaming event and update display"""
        
        event_type = event.event_type
        
        # Handle different event types
        if event_type == "execution_start":
            self.execution_stats["start_time"] = datetime.now()
            
        elif event_type == "tool_discovery_complete":
            tools_found = event.metadata.get("tools_found", [])
            self.console.print(f"[green]🔍 Found {len(tools_found)} relevant tools: {', '.join(tools_found)}[/green]")
            
        elif event_type == "direct_response_start":
            self.execution_stats["execution_mode"] = "Direct Response"
            
        elif event_type == "tool_execution_mode":
            self.execution_stats["execution_mode"] = "Tool Execution"
            
        elif event_type == "main_agent_token":
            # Handle streaming tokens
            if hasattr(event, 'token') and event.token:
                self.current_response += event.token
                self.execution_stats["tokens_streamed"] += 1
                
                # Print to console for frontend integration
                print(f"TOKEN: {event.token}", end="", flush=True)
            
        elif event_type == "tool_start":
            # Track tool execution start
            tool_execution = {
                "name": event.tool_name,
                "input": event.tool_input,
                "start_time": datetime.now(),
                "completed": False
            }
            self.tool_executions.append(tool_execution)
            self.execution_stats["tools_executed"] += 1
            
            # Console output for frontend
            print(f"\nTOOL_START: {event.tool_name} with params: {event.tool_input}")
            
        elif event_type == "tool_end":
            # Mark tool as completed
            for tool_exec in reversed(self.tool_executions):
                if tool_exec["name"] == event.tool_name and not tool_exec.get("completed"):
                    tool_exec["completed"] = True
                    tool_exec["output"] = event.tool_output
                    tool_exec["end_time"] = datetime.now()
                    break
            
            # Console output for frontend
            print(f"\nTOOL_END: {event.tool_name} - Output: {str(event.tool_output)[:100]}{'...' if len(str(event.tool_output)) > 100 else ''}")
            
        elif event_type in ["execution_complete", "direct_response_complete", "main_agent_execution_complete"]:
            # Final completion
            duration = (datetime.now() - self.execution_stats["start_time"]).total_seconds() if self.execution_stats["start_time"] else 0
            self.console.print(f"\n[green]✅ Execution completed in {duration:.1f}s[/green]")
            
        elif event_type == "error":
            self.console.print(f"[red]❌ Error: {event.content}[/red]")
    
    async def run_query(self, query: str, user_id: str = "default_user"):
        """Run a query with live display updates"""
        
        # Reset state
        self.current_response = ""
        self.tool_executions = []
        self.execution_stats = {
            "start_time": None,
            "tools_executed": 0,
            "tokens_streamed": 0,
            "execution_mode": "unknown"
        }
        
        # Update header
        self.update_header(query)
        
        try:
            with Live(self.layout, console=self.console, refresh_per_second=10) as live:
                
                # Process query through engine
                async for event in self.engine.execute_query(query, user_id):
                    await self.process_streaming_event(event)
                    self.update_display(event)
                    
                    # Small delay for smooth updates
                    await asyncio.sleep(0.01)
                
                # Final display update
                self.update_display()
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]⚠️ Execution interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]❌ Execution failed: {str(e)}[/red]")
    
    async def interactive_mode(self):
        """Run interactive CLI mode"""
        
        self.console.print(Panel(
            "🧠 Enhanced Main Agent CLI\n"
            "Supports both direct responses and tool execution\n"
            "Type 'quit' to exit, 'help' for commands",
            title="Welcome",
            style="bold blue"
        ))
        
        while True:
            try:
                # Get user input
                query = input("\n💬 Your query: ").strip()
                
                if not query:
                    continue
                    
                if query.lower() in ['quit', 'exit', 'q']:
                    self.console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                    
                if query.lower() == 'help':
                    self.show_help()
                    continue
                    
                if query.lower() == 'history':
                    await self.show_history()
                    continue
                    
                if query.lower() == 'clear':
                    await self.clear_history()
                    continue
                    
                if query.lower() == 'tools':
                    self.show_available_tools()
                    continue
                    
                if query.lower() == 'status':
                    self.show_system_status()
                    continue
                
                # Process the query
                await self.run_query(query)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'quit' to exit[/yellow]")
            except Exception as e:
                self.console.print(f"[red]❌ Error: {str(e)}[/red]")
    
    def show_help(self):
        """Show help information"""
        
        help_table = Table(title="Available Commands")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")
        
        help_table.add_row("help", "Show this help message")
        help_table.add_row("history", "Show conversation history")
        help_table.add_row("clear", "Clear conversation history")
        help_table.add_row("tools", "Show available tools")
        help_table.add_row("status", "Show system status")
        help_table.add_row("quit/exit/q", "Exit the CLI")
        
        self.console.print(Panel(help_table, border_style="blue"))
    
    async def show_history(self):
        """Show conversation history"""
        
        history = await self.engine.get_conversation_history()
        
        if "error" in history:
            self.console.print(f"[red]❌ {history['error']}[/red]")
            return
        
        self.console.print(f"[green]📚 Conversation History ({history['total_messages']} messages, {history['total_executions']} executions)[/green]")
        
        for i, msg in enumerate(history["conversation_messages"][-5:]):  # Last 5 messages
            msg_type = msg["type"].replace("Message", "")
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            self.console.print(f"[dim]{i+1}. {msg_type}:[/dim] {content}")
    
    async def clear_history(self):
        """Clear conversation history"""
        
        result = await self.engine.clear_conversation_history()
        
        if result["success"]:
            self.console.print(f"[green]✅ {result['message']}[/green]")
        else:
            self.console.print(f"[red]❌ {result['error']}[/red]")
    
    def show_available_tools(self):
        """Show available tools"""
        
        tools_info = self.engine.get_available_tools()
        
        if "error" in tools_info:
            self.console.print(f"[red]❌ {tools_info['error']}[/red]")
            return
        
        tools_table = Table(title=f"Available Tools ({tools_info['total_tools']} total)")
        tools_table.add_column("Tool Name", style="cyan")
        tools_table.add_column("Description", style="white", max_width=50)
        
        for tool_name, tool_info in tools_info["available_tools"].items():
            tools_table.add_row(
                tool_name,
                tool_info["description"]
            )
        
        self.console.print(Panel(tools_table, border_style="blue"))
    
    def show_system_status(self):
        """Show system status"""
        
        status = self.engine.get_system_status()
        
        status_table = Table(title="System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="white")
        
        status_table.add_row("Overall Status", "✅ Operational" if status["status"] == "operational" else "❌ Error")
        status_table.add_row("Main Agent", "✅ Ready" if status["main_agent_ready"] else "❌ Not Ready")
        status_table.add_row("Conversation History", f"{status['conversation_history_size']} messages")
        status_table.add_row("Execution History", f"{status['execution_history_size']} executions")
        
        capabilities = status.get("capabilities", {})
        for cap_name, cap_status in capabilities.items():
            status_table.add_row(
                cap_name.replace("_", " ").title(),
                "✅ Available" if cap_status else "❌ Unavailable"
            )
        
        self.console.print(Panel(status_table, border_style="green"))


async def main():
    """Main CLI entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Main Agent CLI")
    parser.add_argument("query", nargs="?", help="Query to process")
    parser.add_argument("--user-id", default="default_user", help="User ID for session")
    
    args = parser.parse_args()
    
    cli = EnhancedMainAgentCLI()
    
    if args.query:
        # Single query mode
        await cli.run_query(args.query, args.user_id)
    else:
        # Interactive mode
        await cli.interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())