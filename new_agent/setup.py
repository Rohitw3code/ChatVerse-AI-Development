"""
Enhanced Agent Framework Setup Script
Helps users set up the OpenAI-powered agent system
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing requirements...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Requirements installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_openai_key():
    """Help user set up OpenAI API key"""
    print("\n🔑 OpenAI API Key Setup")
    
    current_key = os.getenv("OPENAI_API_KEY")
    if current_key:
        print(f"✅ OpenAI API key already set (length: {len(current_key)})")
        return True
    
    print("❌ OpenAI API key not found in environment variables")
    print("\n📋 To set up your OpenAI API key:")
    print("1. Visit: https://platform.openai.com/api-keys")
    print("2. Create a new API key")
    print("3. Set it as an environment variable:")
    print()
    print("   Windows (Command Prompt):")
    print("   set OPENAI_API_KEY=your_api_key_here")
    print()
    print("   Windows (PowerShell):")
    print("   $env:OPENAI_API_KEY=\"your_api_key_here\"")
    print()
    print("   Linux/Mac:")
    print("   export OPENAI_API_KEY=your_api_key_here")
    print()
    
    # Offer to set it temporarily for this session
    key = input("Enter your OpenAI API key now (or press Enter to skip): ").strip()
    
    if key:
        os.environ["OPENAI_API_KEY"] = key
        print("✅ API key set for this session")
        print("⚠️  Remember to set it permanently in your system environment variables")
        return True
    else:
        print("⏭️  Skipped API key setup - you can set it later")
        return False

def test_setup():
    """Test the setup"""
    print("\n🧪 Testing setup...")
    
    try:
        # Test basic imports
        from new_agent.llm.openai_llm import get_llm_instance
        from new_agent.agents.registry import agent_registry
        
        print("✅ Enhanced modules import successfully")
        
        # Test LLM initialization
        if os.getenv("OPENAI_API_KEY"):
            try:
                llm = get_llm_instance()
                print(f"✅ LLM initialized: {llm.model}")
            except Exception as e:
                print(f"⚠️  LLM initialization warning: {e}")
        else:
            print("⏭️  Skipping LLM test (no API key)")
        
        # Test agent registry
        agents = list(agent_registry.enhanced_agents.keys())
        print(f"✅ {len(agents)} enhanced agents available: {', '.join(agents)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def show_usage_examples():
    """Show usage examples"""
    print("\n🚀 Usage Examples:")
    print()
    print("1. Basic query execution:")
    print('   python -m new_agent "Find AI jobs on LinkedIn and email summary"')
    print()
    print("2. List available agents:")
    print("   python -m new_agent --list-agents")
    print()
    print("3. Check system status:")
    print("   python -m new_agent --stats")
    print()
    print("4. Run tests:")
    print("   python test_enhanced.py")
    print()

def main():
    """Main setup routine"""
    print("🔧 Enhanced Agent Framework Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n⚠️  You may need to install requirements manually:")
        print("   pip install -r requirements.txt")
    
    # Setup OpenAI key
    api_key_set = setup_openai_key()
    
    # Test setup
    if test_setup():
        print("\n✅ Setup completed successfully!")
        
        if api_key_set:
            print("\n🎯 Your Enhanced Agent Framework is ready to use!")
            show_usage_examples()
        else:
            print("\n⚠️  Setup complete, but OpenAI API key is needed for full functionality")
            print("   Set OPENAI_API_KEY environment variable to enable LLM features")
    else:
        print("\n❌ Setup encountered issues. Please check the error messages above.")
        print("\n📋 Troubleshooting tips:")
        print("   1. Ensure Python 3.8+ is installed")
        print("   2. Install requirements: pip install -r requirements.txt")
        print("   3. Set OpenAI API key environment variable")
        print("   4. Check internet connection for package downloads")

if __name__ == "__main__":
    main()