"""
Main entry point for Enhanced Main Agent System
Handles direct responses and tool execution with semantic discovery
"""

import asyncio
import sys
import os

# Add the parent directory to the path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .enhanced_main_cli import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Enhanced execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error in enhanced system: {str(e)}")
        sys.exit(1)