"""
Real-time streaming interface for the New Agent Framework
Handles token-by-token streaming, tool lifecycle events, and node transitions
"""

import time
import threading
import queue
from typing import Generator, Dict, Any, List, Optional, Callable
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.layout import Layout

from ..core.state import StreamingEvent, AgentState
from ..core.config import config


class StreamingInterface:
    """
    Real-time streaming interface that provides token-by-token output,
    tool lifecycle tracking, and visual progress indicators
    """
    
    def __init__(self, output_format: str = "rich"):
        self.output_format = output_format or config.cli.output_format
        self.console = Console()
        self.is_streaming = False
        self.current_session = None
        
        # Streaming state
        self.current_node = None
        self.current_tool = None
        self.streaming_buffer = []
        self.event_history = []
        
        # Rich components
        self.live = None
        self.progress = None
        self.layout = None
        
        # Callbacks
        self.event_callbacks: List[Callable[[StreamingEvent], None]] = []
    
    def start_streaming(self, session_id: str, total_steps: int = 0):
        """Start streaming for a new session"""
        self.is_streaming = True
        self.current_session = session_id
        self.streaming_buffer.clear()
        self.event_history.clear()
        
        if self.output_format == "rich":
            self._start_rich_streaming(total_steps)
        
        self.console.print(f"🚀 [bold green]Starting execution session: {session_id}[/bold green]")
    
    def stop_streaming(self):
        """Stop streaming and cleanup"""
        self.is_streaming = False
        
        if self.live:
            self.live.stop()
            self.live = None
        
        if self.progress:
            self.progress.stop()
            self.progress = None
        
        self.console.print("✅ [bold green]Streaming completed[/bold green]")
    
    def stream_events(self, events: Generator[StreamingEvent, None, None]) -> Generator[StreamingEvent, None, None]:
        """Stream events with real-time display"""
        
        for event in events:
            self._process_event(event)
            
            # Call registered callbacks
            for callback in self.event_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    self.console.print(f"[red]Callback error: {e}[/red]")
            
            yield event
    
    def _process_event(self, event: StreamingEvent):
        """Process a single streaming event"""
        
        self.event_history.append(event)
        
        if self.output_format == "rich":
            self._process_rich_event(event)
        elif self.output_format == "json":
            self._process_json_event(event)
        else:  # plain text
            self._process_plain_event(event)
    
    def _start_rich_streaming(self, total_steps: int):
        """Initialize Rich streaming interface"""
        
        # Create layout
        self.layout = Layout()
        
        # Create progress tracker
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
        
        # Add main task
        self.main_task_id = self.progress.add_task(
            "[cyan]Executing plan...", 
            total=total_steps if total_steps > 0 else 100
        )
        
        # Split layout
        self.layout.split_column(
            Layout(self.progress, name="progress", size=3),
            Layout(name="content", ratio=1),
            Layout(name="status", size=5)
        )
    
    def _process_rich_event(self, event: StreamingEvent):
        """Process event for Rich display"""
        
        if event.event_type == "token":
            # Token-by-token display
            self.streaming_buffer.append(event.content)
            
            # Display streaming tokens
            if len(self.streaming_buffer) > 0:
                text = Text("".join(self.streaming_buffer))
                if self.current_node:
                    text.stylize(f"bold {self._get_node_color(self.current_node)}")
                
                if self.live and hasattr(self.live, 'update'):
                    self.live.update(Panel(text, title=f"🤖 {self.current_node or 'AI Agent'}", border_style="blue"))
        
        elif event.event_type == "node_start":
            self.current_node = event.node_name
            self.streaming_buffer.clear()
            
            self.console.print(f"🔵 [bold blue]Started: {event.content}[/bold blue]")
            
            if self.progress and hasattr(self, 'main_task_id'):
                self.progress.update(self.main_task_id, description=f"[cyan]{event.content}")
        
        elif event.event_type == "node_end":
            self.console.print(f"✅ [bold green]Completed: {event.content}[/bold green]")
            
            if self.progress and hasattr(self, 'main_task_id'):
                current_progress = self.progress.tasks[self.main_task_id].completed + 1
                self.progress.update(self.main_task_id, completed=current_progress)
                
            self.current_node = None
            self.streaming_buffer.clear()
        
        elif event.event_type == "tool_start":
            self.current_tool = event.tool_name
            
            tool_params = event.metadata.get("parameters", {})
            params_str = ", ".join(f"{k}={v}" for k, v in tool_params.items())
            
            self.console.print(f"🔧 [yellow]Started calling tool {event.tool_name}[/yellow]")
            self.console.print(f"   [dim]Parameters: {params_str}[/dim]")
        
        elif event.event_type == "tool_end":
            execution_time = event.metadata.get("execution_time_ms", 0)
            success = event.metadata.get("success", True)
            
            if success:
                self.console.print(f"🔧 [green]Completed calling tool {event.tool_name} ({execution_time}ms)[/green]")
            else:
                self.console.print(f"🔧 [red]Failed calling tool {event.tool_name} ({execution_time}ms)[/red]")
            
            # Show result preview if available
            result_preview = event.metadata.get("result_preview")
            if result_preview:
                self.console.print(f"   [dim]Result: {result_preview}[/dim]")
            
            self.current_tool = None
        
        elif event.event_type == "error":
            self.console.print(f"❌ [bold red]{event.content}[/bold red]")
            
            error_details = event.metadata.get("error")
            if error_details:
                self.console.print(f"   [dim red]Details: {error_details}[/dim red]")
        
        elif event.event_type == "status":
            self.console.print(f"ℹ️  [blue]{event.content}[/blue]")
            
            if self.progress and "completed" in event.content.lower():
                if hasattr(self, 'main_task_id'):
                    total_tasks = self.progress.tasks[self.main_task_id].total
                    self.progress.update(self.main_task_id, completed=total_tasks)
    
    def _process_json_event(self, event: StreamingEvent):
        """Process event for JSON output"""
        
        event_data = {
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "content": event.content,
            "node_name": event.node_name,
            "tool_name": event.tool_name,
            "metadata": event.metadata
        }
        
        import json
        print(json.dumps(event_data, ensure_ascii=False))
    
    def _process_plain_event(self, event: StreamingEvent):
        """Process event for plain text output"""
        
        timestamp = event.timestamp.strftime("%H:%M:%S")
        
        if event.event_type == "token":
            print(event.content, end="", flush=True)
        
        elif event.event_type == "node_start":
            print(f"\n[{timestamp}] 🔵 Started: {event.content}")
        
        elif event.event_type == "node_end":
            print(f"[{timestamp}] ✅ Completed: {event.content}")
        
        elif event.event_type == "tool_start":
            print(f"[{timestamp}] 🔧 Started calling tool {event.tool_name}")
        
        elif event.event_type == "tool_end":
            print(f"[{timestamp}] 🔧 Completed calling tool {event.tool_name}")
        
        elif event.event_type == "error":
            print(f"[{timestamp}] ❌ {event.content}")
        
        elif event.event_type == "status":
            print(f"[{timestamp}] ℹ️  {event.content}")
    
    def _get_node_color(self, node_name: str) -> str:
        """Get color for node based on its type"""
        
        color_map = {
            "LinkedInAgent": "blue",
            "InstagramAgent": "magenta",
            "GmailAgent": "green",
            "ResearchAgent": "yellow",
            "SummarizerAgent": "cyan",
            "OrchestratorAgent": "red"
        }
        
        return color_map.get(node_name, "white")
    
    def add_event_callback(self, callback: Callable[[StreamingEvent], None]):
        """Add callback function for streaming events"""
        self.event_callbacks.append(callback)
    
    def remove_event_callback(self, callback: Callable[[StreamingEvent], None]):
        """Remove callback function"""
        if callback in self.event_callbacks:
            self.event_callbacks.remove(callback)
    
    def get_streaming_stats(self) -> Dict[str, Any]:
        """Get streaming statistics"""
        
        if not self.event_history:
            return {}
        
        event_counts = {}
        for event in self.event_history:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        
        total_tokens = event_counts.get("token", 0)
        total_tools = event_counts.get("tool_start", 0)
        total_nodes = event_counts.get("node_start", 0)
        errors = event_counts.get("error", 0)
        
        session_duration = 0
        if self.event_history:
            start_time = self.event_history[0].timestamp
            end_time = self.event_history[-1].timestamp
            session_duration = (end_time - start_time).total_seconds()
        
        return {
            "session_id": self.current_session,
            "total_events": len(self.event_history),
            "event_counts": event_counts,
            "total_tokens": total_tokens,
            "total_tools_called": total_tools,
            "total_nodes_executed": total_nodes,
            "errors": errors,
            "session_duration_seconds": session_duration,
            "tokens_per_second": total_tokens / session_duration if session_duration > 0 else 0
        }
    
    def export_session_log(self, filename: Optional[str] = None) -> str:
        """Export current session events to file"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"streaming_session_{self.current_session}_{timestamp}.json"
        
        log_data = {
            "session_id": self.current_session,
            "exported_at": datetime.now().isoformat(),
            "stats": self.get_streaming_stats(),
            "events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "content": event.content,
                    "node_name": event.node_name,
                    "tool_name": event.tool_name,
                    "metadata": event.metadata
                }
                for event in self.event_history
            ]
        }
        
        import json
        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        return filename


# Enhanced streaming with CLI integration
class CLIStreamer:
    """CLI-integrated streaming interface with additional features"""
    
    def __init__(self, verbose: bool = True, show_metadata: bool = False):
        self.verbose = verbose
        self.show_metadata = show_metadata
        self.streaming_interface = StreamingInterface(
            output_format=config.cli.output_format
        )
    
    def stream_execution(self, events: Generator[StreamingEvent, None, None], session_id: str) -> Dict[str, Any]:
        """Stream execution with CLI-specific enhancements"""
        
        self.streaming_interface.start_streaming(session_id)
        
        try:
            # Process all events
            all_events = list(self.streaming_interface.stream_events(events))
            
            # Get final stats
            stats = self.streaming_interface.get_streaming_stats()
            
            # Display summary if verbose
            if self.verbose:
                self._display_execution_summary(stats)
            
            return {
                "success": True,
                "stats": stats,
                "total_events": len(all_events)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stats": self.streaming_interface.get_streaming_stats()
            }
        
        finally:
            self.streaming_interface.stop_streaming()
    
    def _display_execution_summary(self, stats: Dict[str, Any]):
        """Display execution summary"""
        
        console = self.streaming_interface.console
        
        # Create summary table
        table = Table(title="Execution Summary", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Events", str(stats.get("total_events", 0)))
        table.add_row("Tokens Generated", str(stats.get("total_tokens", 0)))
        table.add_row("Tools Called", str(stats.get("total_tools_called", 0)))
        table.add_row("Nodes Executed", str(stats.get("total_nodes_executed", 0)))
        table.add_row("Errors", str(stats.get("errors", 0)))
        table.add_row("Duration", f"{stats.get('session_duration_seconds', 0):.2f}s")
        table.add_row("Tokens/Second", f"{stats.get('tokens_per_second', 0):.2f}")
        
        console.print(table)
        
        # Show metadata if requested
        if self.show_metadata:
            console.print("\n[bold]Event Breakdown:[/bold]")
            event_counts = stats.get("event_counts", {})
            for event_type, count in event_counts.items():
                console.print(f"  {event_type}: {count}")


# Global streaming interface instance
streaming_interface = StreamingInterface()
cli_streamer = CLIStreamer()