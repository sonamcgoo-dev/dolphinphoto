#!/bin/bash

# DolphinPhoto AI Studio - Development Launcher
# Black Tiger Computing — Lead Dev: Sona McGoo

cat << 'EOF'

    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🐬 DolphinPhoto AI Studio                                    ║
    ║   The Ultimate AI Creative Studio                             ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝

EOF

echo -e "\033[1;33m[1/4] Checking Python...\033[0m"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "\033[0;32m  $PYTHON_VERSION\033[0m"
else
    echo -e "\033[0;31mPython not found! Please install Python 3.12+\033[0m"
    exit 1
fi

echo -e "\033[1;33m[2/4] Checking Node.js...\033[0m"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "\033[0;32m  v$NODE_VERSION\033[0m"
else
    echo -e "\033[0;31mNode.js not found! Please install Node.js 22+\033[0m"
    exit 1
fi

echo -e "\033[1;33m[3/4] Installing Backend Dependencies...\033[0m"
pip3 install -r backend/requirements.txt -q 2>/dev/null || true
echo -e "\033[0;32m  Backend dependencies ready\033[0m"

echo -e "\033[1;33m[4/4] Installing Frontend Dependencies...\033[0m"
if [ ! -d "frontend/node_modules" ]; then
    cd frontend && npm install && cd ..
    echo -e "\033[0;32m  Frontend dependencies ready\033[0m"
else
    echo -e "\033[0;32m  Node modules already installed\033[0m"
fi

cat << 'EOF'

    ════════════════════════════════════════════════════════════════

    Starting services...

EOF

# Start Backend
echo -e "\033[1;36mStarting Backend API Server...\033[0m"
cd backend && python3 main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start Frontend
echo -e "\033[1;36mStarting Frontend Dev Server...\033[0m"
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

cat << 'EOF'

    ════════════════════════════════════════════════════════════════

    🚀 Services starting up!

    📍 Frontend:  http://localhost:5173
    📍 Backend:   http://127.0.0.1:7777
    📍 API Docs:  http://127.0.0.1:7777/api/docs

    Press Ctrl+C to stop all services

EOF

# Cleanup function
cleanup() {
    echo -e "\n\033[1;33mShutting down services...\033[0m"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "\033[0;32mServices stopped.\033[0m"
}

trap cleanup SIGINT SIGTERM

# Wait for any process to exit
wait
