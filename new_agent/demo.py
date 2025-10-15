"""
Example usage and demonstration of the New Agent Framework
"""

import asyncio
import time
from new_agent.cli import NewAgentCLI


async def demo_basic_execution():
    """Demonstrate basic query execution"""
    
    print("=" * 60)
    print("🎯 DEMO: Basic Query Execution")
    print("=" * 60)
    
    cli = NewAgentCLI()
    
    # Simple query
    result = await cli.execute_query(
        "Get Instagram insights for my account",
        user_id="demo_user",
        verbose=True,
        output_format="rich"
    )
    
    print(f"\n✅ Result: {result['success']}")
    if result['success']:
        print(f"📊 Session ID: {result['session_id']}")
        print(f"⏱️  Duration: {result['execution_stats']['session_duration_seconds']:.2f}s")
    
    return result


async def demo_complex_workflow():
    """Demonstrate complex multi-agent workflow"""
    
    print("\n" + "=" * 60)
    print("🎯 DEMO: Complex Multi-Agent Workflow")
    print("=" * 60)
    
    cli = NewAgentCLI()
    
    # Complex query with multiple agents
    complex_query = """
    Fetch AI/ML engineer jobs from LinkedIn in India, 
    also fetch Instagram insights, 
    summarize both datasets, 
    and email the comprehensive summary to rohit@gmail.com
    """
    
    result = await cli.execute_query(
        complex_query,
        user_id="demo_user",
        verbose=True,
        output_format="rich",
        show_metadata=True
    )
    
    print(f"\n✅ Result: {result['success']}")
    if result['success']:
        print(f"📊 Session ID: {result['session_id']}")
        print(f"🔧 Tools Called: {result['execution_stats']['total_tools_called']}")
        print(f"🤖 Tokens Generated: {result['execution_stats']['total_tokens']}")
    
    return result


async def demo_information_commands():
    """Demonstrate information and management commands"""
    
    print("\n" + "=" * 60)
    print("🎯 DEMO: Information Commands")
    print("=" * 60)
    
    cli = NewAgentCLI()
    
    # List agents
    print("\n📋 Available Agents:")
    agents = await cli.list_agents()
    
    # List tools
    print("\n🔧 Available Tools:")
    tools = await cli.list_tools()
    
    # Show statistics
    print("\n📊 Framework Statistics:")
    stats = await cli.get_stats()
    
    from rich.console import Console
    from rich.json import JSON
    
    console = Console()
    console.print(JSON.from_data(stats))
    
    return {"agents": len(agents), "tools": len(tools), "stats": stats}


async def demo_execution_history():
    """Demonstrate execution history and plan details"""
    
    print("\n" + "=" * 60)
    print("🎯 DEMO: Execution History")
    print("=" * 60)
    
    cli = NewAgentCLI()
    
    # Show execution history
    print("\n📜 Recent Execution History:")
    history = await cli.show_history("demo_user", limit=5)
    
    if history:
        # Show details for the most recent execution
        recent_execution = history[0]
        
        # Note: In a real scenario, you'd get the plan_id from the execution
        # For demo purposes, we'll simulate this
        print(f"\n🔍 Execution Details:")
        print(f"   Session: {recent_execution['session_id']}")
        print(f"   Query: {recent_execution['query']}")
        print(f"   Status: {recent_execution['status']}")
    
    return history


async def demo_error_handling():
    """Demonstrate error handling and recovery"""
    
    print("\n" + "=" * 60)
    print("🎯 DEMO: Error Handling")
    print("=" * 60)
    
    cli = NewAgentCLI()
    
    # Try an invalid query that might cause issues
    result = await cli.execute_query(
        "",  # Empty query
        user_id="demo_user",
        verbose=True
    )
    
    print(f"\n❌ Intentional failure result: {result['success']}")
    if not result['success']:
        print(f"🔍 Error: {result.get('error', 'Unknown error')}")
    
    return result


async def run_full_demo():
    """Run complete demonstration of all features"""
    
    print("🚀 NEW AGENT FRAMEWORK DEMONSTRATION")
    print("=" * 60)
    print("A self-contained, CLI-driven AI Agent Framework")
    print("Running completely locally with dummy implementations")
    print()
    
    try:
        # Demo 1: Basic execution
        result1 = await demo_basic_execution()
        await asyncio.sleep(1)  # Brief pause between demos
        
        # Demo 2: Complex workflow
        result2 = await demo_complex_workflow()
        await asyncio.sleep(1)
        
        # Demo 3: Information commands
        result3 = await demo_information_commands()
        await asyncio.sleep(1)
        
        # Demo 4: Execution history
        result4 = await demo_execution_history()
        await asyncio.sleep(1)
        
        # Demo 5: Error handling
        result5 = await demo_error_handling()
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 DEMONSTRATION COMPLETE")
        print("=" * 60)
        
        successful_demos = sum(1 for r in [result1, result2] if r.get('success', False))
        
        print(f"✅ Successful executions: {successful_demos}/2")
        print(f"🤖 Total agents available: {result3['agents']}")
        print(f"🔧 Total tools available: {result3['tools']}")
        print(f"📜 History entries: {len(result4) if result4 else 0}")
        
        print("\n🔍 Key Features Demonstrated:")
        print("   ✓ Real-time streaming output")
        print("   ✓ Multi-agent coordination")
        print("   ✓ Tool lifecycle tracking")
        print("   ✓ Local database storage")
        print("   ✓ Rich CLI interface")
        print("   ✓ Error handling and recovery")
        print("   ✓ Execution history and statistics")
        
        print("\n📋 Try these commands yourself:")
        print('   python -m new_agent "Search for Python jobs and email results"')
        print('   python -m new_agent --list-agents')
        print('   python -m new_agent --history')
        print('   python -m new_agent --stats')
        
        print("\n🚀 Framework ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_full_demo())