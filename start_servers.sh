#!/bin/bash
# MedAgent-Heart Startup Script for Linux/Mac
# This script starts both the backend and frontend servers

echo "==============================================="
echo "   MedAgent-Heart - Server Startup"
echo "==============================================="
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda not found!"
    echo "Please install Miniconda or Anaconda"
    exit 1
fi

# Check if medagent environment exists
if ! conda env list | grep -q "medagent"; then
    echo "ERROR: 'medagent' conda environment not found!"
    echo "Please run: conda create -n medagent python=3.11 -y"
    exit 1
fi

echo "Environment found!"
echo ""

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "WARNING: backend/.env file not found!"
    echo "Please create backend/.env with your API keys"
    echo "See QUICKSTART.md for details"
    exit 1
fi

echo "Starting servers..."
echo ""

# Get the conda base path
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"

# Start backend in background
echo "[1/2] Starting Backend Server (port 8000)..."
conda activate medagent
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend in background
echo "[2/2] Starting Frontend Server (port 8501)..."
streamlit run frontend/app.py > frontend.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "==============================================="
echo "   Servers Started!"
echo "==============================================="
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8501"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Logs:"
echo "  Backend: backend.log"
echo "  Frontend: frontend.log"
echo ""
echo "To stop servers, run:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all servers..."

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; echo 'Servers stopped'; exit" INT
wait
