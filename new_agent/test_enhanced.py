"""
Test script for Enhanced Agent Framework with OpenAI Integration
Tests LLM-powered planning, agent routing, and cost tracking
"""

import os
import sys
import asyncio
from pathlib import Path

# Add new_agent to path
sys.path.insert(0, str(Path(__file__).parent))

def test_openai_setup():
    """Test OpenAI API key setup"""
    print("🔑 Testing OpenAI Setup...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Please set it with: set OPENAI_API_KEY=your_key_here")
        return False
    
    if len(api_key) < 20:
        print("❌ OPENAI_API_KEY appears to be invalid (too short)")
        return False
    
    print(f"✅ OpenAI API key detected (length: {len(api_key)})")
    return True

def test_enhanced_imports():
    """Test importing enhanced modules"""
    print("\n📦 Testing Enhanced Module Imports...")
    
    try:
        from new_agent.llm.openai_llm import get_llm_instance
        print("✅ OpenAI LLM module imported successfully")
        
        from new_agent.agents.enhanced_agents import LinkedInAgent, InstagramAgent
        print("✅ Enhanced agents imported successfully")
        
        from new_agent.agents.registry import agent_registry
        print("✅ Agent registry imported successfully")
        
        from new_agent.planning.planner import PlanningEngine
        print("✅ Planning engine imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_llm_initialization():
    """Test LLM initialization"""
    print("\n🧠 Testing LLM Initialization...")
    
    try:
        from new_agent.llm.openai_llm import get_llm_instance
        
        llm = get_llm_instance()
        print(f"✅ LLM initialized: {llm.model}")
        print(f"   Pricing: ${llm.pricing['prompt_tokens']*1000:.3f}/1K prompt, ${llm.pricing['completion_tokens']*1000:.3f}/1K completion")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
        return False

def test_enhanced_agents():
    """Test enhanced agent instances"""
    print("\n🤖 Testing Enhanced Agents...")
    
    try:
        from new_agent.agents.registry import agent_registry
        
        # Test agent instances
        linkedin_agent = agent_registry.get_agent_instance("LinkedInAgent")
        if linkedin_agent:
            print("✅ LinkedInAgent instance available")
            info = linkedin_agent.get_agent_info()
            print(f"   Capabilities: {', '.join(info['capabilities'])}")
        else:
            print("❌ LinkedInAgent instance not found")
            return False
        
        # Test routing
        best_agent = agent_registry.route_to_best_agent("Find AI jobs on LinkedIn")
        print(f"✅ AI Routing works: '{best_agent}' selected for LinkedIn task")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced agents test failed: {e}")
        return False

def test_planning_engine():
    """Test LLM-powered planning"""
    print("\n📋 Testing LLM-Powered Planning...")
    
    try:
        from new_agent.planning.planner import PlanningEngine
        
        planner = PlanningEngine()
        print("✅ Planning engine initialized with LLM")
        
        # Test simple plan creation (this will use OpenAI API)
        print("🧠 Creating sample plan (this will consume tokens)...")
        
        query = "Get LinkedIn jobs and email summary"
        plan = planner.create_plan(query)
        
        print(f"✅ Plan created successfully!")
        print(f"   Steps: {plan.total_steps}")
        print(f"   Execution Mode: {plan.execution_mode}")
        print(f"   Estimated Duration: {plan.estimated_duration}s")
        
        if hasattr(plan, 'metadata') and 'llm_usage' in plan.metadata:
            usage = plan.metadata['llm_usage']['total_usage']
            print(f"   Tokens Used: {usage.get('total_tokens', 0)}")
            print(f"   Cost: ${usage.get('estimated_cost', 0):.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Planning test failed: {e}")
        print("   This might be due to invalid API key or network issues")
        return False

async def test_agent_execution():
    """Test agent execution with LLM decision making"""
    print("\n🔄 Testing Agent Execution...")
    
    try:
        from new_agent.agents.registry import agent_registry
        
        # Get LinkedIn agent
        agent = agent_registry.get_agent_instance("LinkedInAgent")
        if not agent:
            print("❌ Could not get agent instance")
            return False
        
        print("🧠 Testing agent decision making (this will consume tokens)...")
        
        # Test agent execution
        events = []
        async for event in agent.execute_step(
            task="Search for Python developer jobs in San Francisco",
            context={"test_mode": True}
        ):
            events.append(event)
            print(f"   Event: {event.type} - {event.data.get('reasoning', 'Processing...')[:60]}...")
        
        print(f"✅ Agent execution completed with {len(events)} events")
        
        # Show final stats
        stats = agent.execution_stats
        print(f"   Total Cost: ${stats.get('total_cost', 0):.4f}")
        print(f"   Total Tokens: {stats.get('total_tokens', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent execution test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Enhanced Agent Framework Test Suite")
    print("=" * 50)
    
    all_passed = True
    
    # Basic setup tests
    all_passed &= test_openai_setup()
    all_passed &= test_enhanced_imports()
    all_passed &= test_llm_initialization()
    all_passed &= test_enhanced_agents()
    
    # Advanced tests (consume OpenAI tokens)
    print("\n⚠️  The following tests will consume OpenAI tokens (small amounts)")
    confirm = input("Continue with LLM tests? (y/n): ").lower().strip()
    
    if confirm == 'y':
        all_passed &= test_planning_engine()
        
        # Async test
        try:
            asyncio.run(test_agent_execution())
        except Exception as e:
            print(f"❌ Async agent test failed: {e}")
            all_passed = False
    else:
        print("⏭️  Skipped LLM tests")
    
    # Final result
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! Enhanced framework is ready to use.")
        print("\n🚀 Try running:")
        print('   python -m new_agent "Find Python jobs and email summary"')
    else:
        print("❌ Some tests failed. Please check the setup.")
        print("\n📋 Common fixes:")
        print("   1. Set OPENAI_API_KEY environment variable")
        print("   2. Install requirements: pip install -r requirements.txt")
        print("   3. Verify Python 3.8+ is being used")

if __name__ == "__main__":
    main()