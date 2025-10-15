"""
Simple test script for the New Agent Framework
Tests basic functionality without external dependencies
"""

import sys
import os
import json
from pathlib import Path

# Add the new_agent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from new_agent.core.state import create_initial_state, AgentState
        from new_agent.core.config import config
        from new_agent.agents.registry import agent_registry
        from new_agent.tools.dummy_tools import tool_registry
        from new_agent.planning.planner import planning_engine
        from new_agent.llm.dummy_llm import DummyLLM
        print("✅ All core modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_agent_registry():
    """Test agent registry functionality"""
    print("\n🧪 Testing agent registry...")
    
    try:
        from new_agent.agents.registry import agent_registry
        
        agents = agent_registry.list_agents()
        print(f"✅ Found {len(agents)} agents")
        
        for agent in agents[:3]:  # Show first 3
            print(f"   - {agent.name}: {agent.description[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Agent registry test failed: {e}")
        return False

def test_tool_registry():
    """Test tool registry functionality"""
    print("\n🧪 Testing tool registry...")
    
    try:
        from new_agent.tools.dummy_tools import tool_registry
        
        tools = tool_registry.list_tools()
        print(f"✅ Found {len(tools)} tools")
        
        # Test a tool execution
        result = tool_registry.execute_tool("linkedin_job_search", role="AI Engineer", location="India")
        print(f"✅ Tool execution successful: {result.success}")
        
        return True
    except Exception as e:
        print(f"❌ Tool registry test failed: {e}")
        return False

def test_planning_engine():
    """Test planning engine functionality"""
    print("\n🧪 Testing planning engine...")
    
    try:
        from new_agent.planning.planner import planning_engine
        
        plan = planning_engine.create_plan("Get Instagram insights and email summary")
        print(f"✅ Plan created with {len(plan.steps)} steps")
        
        for i, step in enumerate(plan.steps, 1):
            print(f"   {i}. {step.description}")
        
        return True
    except Exception as e:
        print(f"❌ Planning engine test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🧪 Testing database...")
    
    try:
        from new_agent.database.simple_db import database
        from new_agent.core.state import create_initial_state
        
        database.initialize()
        print("✅ Database initialized")
        
        # Test saving a dummy execution
        state = create_initial_state("Test query", "test_user")
        state["status"] = "completed"
        
        success = database.save_execution(state)
        print(f"✅ Execution save successful: {success}")
        
        # Test getting history
        history = database.get_execution_history("test_user", 5)
        print(f"✅ Retrieved {len(history)} history entries")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_dummy_llm():
    """Test dummy LLM functionality"""
    print("\n🧪 Testing dummy LLM...")
    
    try:
        from new_agent.llm.dummy_llm import DummyLLM, AgentResponseGenerator
        
        llm = DummyLLM()
        
        # Test planning response
        response = llm.generate_planning_response("Get LinkedIn jobs", [])
        print(f"✅ Planning response generated with {len(response['steps'])} steps")
        
        # Test agent response
        linkedin_response = AgentResponseGenerator.generate_linkedin_response("AI jobs")
        print(f"✅ LinkedIn response generated with {linkedin_response['jobs_found']} jobs")
        
        return True
    except Exception as e:
        print(f"❌ Dummy LLM test failed: {e}")
        return False

def test_configuration():
    """Test configuration system"""
    print("\n🧪 Testing configuration...")
    
    try:
        from new_agent.core.config import config
        
        print(f"✅ Config loaded: {config.framework_name} v{config.version}")
        print(f"   Database type: {config.database.type}")
        print(f"   Max agents: {config.max_agents}")
        print(f"   Output format: {config.cli.output_format}")
        
        # Test validation
        issues = config.validate()
        if issues:
            print(f"⚠️  Config issues: {issues}")
        else:
            print("✅ Configuration valid")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_end_to_end():
    """Test basic end-to-end functionality"""
    print("\n🧪 Testing end-to-end flow...")
    
    try:
        from new_agent.core.state import create_initial_state, update_state_with_plan
        from new_agent.planning.planner import planning_engine
        from new_agent.database.simple_db import database
        
        # Create state
        state = create_initial_state("Search for AI jobs and email results", "test_user")
        print("✅ Initial state created")
        
        # Create plan
        plan = planning_engine.create_plan(state["query"], state["user_id"])
        state = update_state_with_plan(state, plan)
        print(f"✅ Plan created with {len(plan.steps)} steps")
        
        # Save to database
        database.initialize()
        database.save_plan(plan, state["session_id"])
        database.save_execution(state)
        print("✅ Data saved to database")
        
        return True
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 NEW AGENT FRAMEWORK - BASIC TESTS")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_agent_registry,
        test_tool_registry,
        test_dummy_llm,
        test_database,
        test_planning_engine,
        test_end_to_end
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Framework is ready to use.")
        print("\n📋 Try running:")
        print('   python -m new_agent "Get Instagram insights"')
        print('   python -m new_agent --list-agents')
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)