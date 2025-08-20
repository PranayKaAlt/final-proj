#!/bin/bash

# 🚀 AI Recruitment System - Local Production Deployment
# This script deploys the system locally for immediate use

set -e  # Exit on any error

echo "🚀 Starting AI Recruitment System Local Deployment..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_DIR="$(pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR"
AI_PROJECT_DIR="$PROJECT_DIR/ai_interviewer_project"
DEPLOY_DIR="$PROJECT_DIR/production"

# Create production directories
print_status "Creating production directories..."
mkdir -p $DEPLOY_DIR/{backend,frontend,logs,data}
mkdir -p $DEPLOY_DIR/backend/uploads
mkdir -p $DEPLOY_DIR/backend/models

# Copy project files
print_status "Copying project files to production directory..."

# Copy backend
cp -r $BACKEND_DIR/* $DEPLOY_DIR/backend/
cp -r $AI_PROJECT_DIR/model/* $DEPLOY_DIR/backend/models/
cp -r $AI_PROJECT_DIR/data $DEPLOY_DIR/backend/

# Copy frontend build
print_status "Building React frontend for production..."
cd $FRONTEND_DIR
npm run build
cp -r build/* $DEPLOY_DIR/frontend/

# Set proper permissions
print_status "Setting proper permissions..."
chmod -R 755 $DEPLOY_DIR
chmod +x $DEPLOY_DIR/backend/app.py

# Create production environment file
print_status "Creating production environment configuration..."
cat > $DEPLOY_DIR/backend/.env << EOF
# Production Environment Variables
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
HOST=0.0.0.0

# Database Configuration (local)
DB_HOST=localhost
DB_NAME=ai_recruitment
DB_USER=ai_user
DB_PASSWORD=ai_recruitment_secure_password_2024
DB_PORT=5432

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Model Paths
MODEL_DIR=$DEPLOY_DIR/backend/models
DATA_DIR=$DEPLOY_DIR/backend/data

# Security
SECRET_KEY=your_super_secret_key_here_change_this_in_production
EOF

# Create production requirements file
print_status "Creating production requirements..."
cat > $DEPLOY_DIR/backend/requirements.txt << EOF
# Production Requirements for AI Recruitment System
flask==2.3.3
flask-cors==4.0.0
werkzeug==2.3.7
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
textblob==0.19.0
PyPDF2==3.0.1
psycopg2-binary==2.9.7
redis==4.6.0
schedule==1.2.2
gunicorn==21.2.0
EOF

# Setup Python virtual environment
print_status "Setting up Python virtual environment..."
cd $DEPLOY_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create startup script
print_status "Creating startup script..."
cat > $DEPLOY_DIR/start.sh << 'EOF'
#!/bin/bash

# AI Recruitment System Startup Script

echo "🚀 Starting AI Recruitment System..."

# Start backend
cd "$(dirname "$0")/backend"
source venv/bin/activate
nohup gunicorn --workers 4 --bind 0.0.0.0:5000 app:app > ../logs/backend.log 2>&1 &
echo $! > ../logs/backend.pid

# Start frontend (serve static files)
cd "$(dirname "$0")/frontend"
nohup python3 -m http.server 3000 > ../logs/frontend.log 2>&1 &
echo $! > ../logs/frontend.pid

echo "✅ AI Recruitment System started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo "📊 Health Check: http://localhost:5000/api/health"
echo ""
echo "📋 Logs:"
echo "  Backend: tail -f production/logs/backend.log"
echo "  Frontend: tail -f production/logs/frontend.log"
EOF

chmod +x $DEPLOY_DIR/start.sh

# Create stop script
print_status "Creating stop script..."
cat > $DEPLOY_DIR/stop.sh << 'EOF'
#!/bin/bash

# AI Recruitment System Stop Script

echo "🛑 Stopping AI Recruitment System..."

# Stop backend
if [ -f "$(dirname "$0")/logs/backend.pid" ]; then
    BACKEND_PID=$(cat "$(dirname "$0")/logs/backend.pid")
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo "✅ Backend stopped (PID: $BACKEND_PID)"
    else
        echo "⚠️  Backend process not found"
    fi
    rm -f "$(dirname "$0")/logs/backend.pid"
fi

# Stop frontend
if [ -f "$(dirname "$0")/logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$(dirname "$0")/logs/frontend.pid")
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "✅ Frontend stopped (PID: $FRONTEND_PID)"
    else
        echo "⚠️  Frontend process not found"
    fi
    rm -f "$(dirname "$0")/logs/frontend.pid"
fi

echo "✅ AI Recruitment System stopped successfully!"
EOF

chmod +x $DEPLOY_DIR/stop.sh

# Create status script
print_status "Creating status script..."
cat > $DEPLOY_DIR/status.sh << 'EOF'
#!/bin/bash

# AI Recruitment System Status Script

echo "📊 AI Recruitment System Status"
echo "================================"

# Check backend
if [ -f "$(dirname "$0")/logs/backend.pid" ]; then
    BACKEND_PID=$(cat "$(dirname "$0")/logs/backend.pid")
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "✅ Backend: RUNNING (PID: $BACKEND_PID)"
    else
        echo "❌ Backend: STOPPED"
    fi
else
    echo "❌ Backend: STOPPED"
fi

# Check frontend
if [ -f "$(dirname "$0")/logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$(dirname "$0")/logs/frontend.pid")
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "✅ Frontend: RUNNING (PID: $FRONTEND_PID)"
    else
        echo "❌ Frontend: STOPPED"
    fi
else
    echo "❌ Frontend: STOPPED"
fi

# Check if services are responding
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ Backend API: RESPONDING"
else
    echo "❌ Backend API: NOT RESPONDING"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend: RESPONDING"
else
    echo "❌ Frontend: NOT RESPONDING"
fi

# System resources
echo ""
echo "💻 System Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df . | tail -1 | awk '{print $5}')"
EOF

chmod +x $DEPLOY_DIR/status.sh

# Create monitoring script
print_status "Creating monitoring script..."
cat > $DEPLOY_DIR/monitor.sh << 'EOF'
#!/bin/bash

# AI Recruitment System Monitoring Script

LOG_FILE="$(dirname "$0")/logs/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Checking AI Recruitment System..." >> $LOG_FILE

# Check backend
if [ -f "$(dirname "$0")/logs/backend.pid" ]; then
    BACKEND_PID=$(cat "$(dirname "$0")/logs/backend.pid")
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "[$DATE] Backend is down! Restarting..." >> $LOG_FILE
        cd "$(dirname "$0")"
        ./start.sh
    else
        echo "[$DATE] Backend is running (PID: $BACKEND_PID)" >> $LOG_FILE
    fi
fi

# Check frontend
if [ -f "$(dirname "$0")/logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$(dirname "$0")/logs/frontend.pid")
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "[$DATE] Frontend is down! Restarting..." >> $LOG_FILE
        cd "$(dirname "$0")"
        ./start.sh
    else
        echo "[$DATE] Frontend is running (PID: $FRONTEND_PID)" >> $LOG_FILE
    fi
fi

# Check disk space
DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEMORY_USAGE -gt 80 ]; then
    echo "[$DATE] WARNING: Memory usage is ${MEMORY_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x $DEPLOY_DIR/monitor.sh

print_success "Local deployment completed successfully!"

echo ""
echo "🎯 Deployment Summary:"
echo "======================"
echo "✅ Production directory: $DEPLOY_DIR"
echo "✅ Backend: Python Flask with Gunicorn"
echo "✅ Frontend: React build with static server"
echo "✅ Virtual environment: Created and configured"
echo "✅ Management scripts: Created"
echo ""
echo "🚀 To start the system:"
echo "  cd $DEPLOY_DIR"
echo "  ./start.sh"
echo ""
echo "🛑 To stop the system:"
echo "  cd $DEPLOY_DIR"
echo "  ./stop.sh"
echo ""
echo "📊 To check status:"
echo "  cd $DEPLOY_DIR"
echo "  ./status.sh"
echo ""
echo "📋 To view logs:"
echo "  tail -f $DEPLOY_DIR/logs/backend.log"
echo "  tail -f $DEPLOY_DIR/logs/frontend.log"
echo ""
print_success "Local deployment ready!" 