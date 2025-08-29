#!/bin/bash
# Development startup script

echo "🚀 Starting A15-Patcher Web UI Development Environment"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js (v18+)"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Install backend dependencies
echo "🐍 Installing backend dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads processed

echo "✅ Setup complete!"
echo ""
echo "To start development:"
echo "  Frontend: npm run dev        (http://localhost:3000)"
echo "  Backend:  python backend/app.py  (http://localhost:5000)"
echo ""