#!/bin/bash

echo "=========================================="
echo "Deployment System Status Check"
echo "=========================================="
echo ""

# Check if backend is running
echo "1. Checking Backend Server..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running on port 8000"
else
    echo "   ❌ Backend is NOT running"
    echo "   → Start with: cd /home/bittu/Desktop/chatverse/ChatVerse-AI-Development && source venv/bin/activate && python main.py"
fi
echo ""

# Check if frontend is running
echo "2. Checking Frontend Server..."
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "   ✅ Frontend is running on port 5173"
else
    echo "   ❌ Frontend is NOT running"
    echo "   → Start with: cd /home/bittu/Desktop/chatverse/ChatVerse-AI-Development/ChatVerse-Frontend-Development && npm run dev"
fi
echo ""

# Check Python environment
echo "3. Checking Python Environment..."
cd /home/bittu/Desktop/chatverse/ChatVerse-AI-Development
if [ -d "venv" ]; then
    echo "   ✅ Virtual environment exists"
else
    echo "   ❌ Virtual environment not found"
fi
echo ""

# Check if deployment endpoint exists in code
echo "4. Checking Deployment Endpoint in Code..."
if grep -q "@automation_trace_router.post(\"/deploy\")" chatagent/automation_trace_router.py 2>/dev/null; then
    echo "   ✅ Deployment endpoint found in router"
else
    echo "   ❌ Deployment endpoint NOT found"
fi
echo ""

# Check if router is registered
echo "5. Checking Router Registration..."
if grep -q "automation_trace_router" app.py 2>/dev/null; then
    echo "   ✅ Router is registered in app.py"
else
    echo "   ❌ Router NOT registered"
fi
echo ""

echo "=========================================="
echo "Quick Actions:"
echo "=========================================="
echo ""
echo "Start Backend:"
echo "  cd /home/bittu/Desktop/chatverse/ChatVerse-AI-Development"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Start Frontend:"
echo "  cd /home/bittu/Desktop/chatverse/ChatVerse-AI-Development/ChatVerse-Frontend-Development"
echo "  npm run dev"
echo ""
echo "Test Deployment Endpoint:"
echo "  cd /home/bittu/Desktop/chatverse/ChatVerse-AI-Development"
echo "  source venv/bin/activate"
echo "  python scripts/test_deploy_endpoint.py"
echo ""
echo "=========================================="
