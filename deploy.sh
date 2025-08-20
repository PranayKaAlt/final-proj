#!/bin/bash

# 🚀 AI Recruitment System - Production Deployment Script
# This script deploys the complete AI recruitment system to production

set -e  # Exit on any error

echo "🚀 Starting AI Recruitment System Production Deployment..."
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Configuration
PROJECT_DIR="$(pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR"
AI_PROJECT_DIR="$PROJECT_DIR/ai_interviewer_project"

# Create production directories
print_status "Creating production directories..."
sudo mkdir -p /opt/ai-recruitment/{backend,frontend,logs,data}
sudo mkdir -p /opt/ai-recruitment/backend/uploads
sudo mkdir -p /opt/ai-recruitment/backend/models

# Copy project files
print_status "Copying project files to production directory..."

# Copy backend
sudo cp -r $BACKEND_DIR/* /opt/ai-recruitment/backend/
sudo cp -r $AI_PROJECT_DIR/model/* /opt/ai-recruitment/backend/models/
sudo cp -r $AI_PROJECT_DIR/data /opt/ai-recruitment/backend/

# Copy frontend build
print_status "Building React frontend for production..."
cd $FRONTEND_DIR
npm run build
sudo cp -r build/* /opt/ai-recruitment/frontend/

# Set proper permissions
print_status "Setting proper permissions..."
sudo chown -R $USER:$USER /opt/ai-recruitment
sudo chmod -R 755 /opt/ai-recruitment
sudo chmod +x /opt/ai-recruitment/backend/app.py

# Create production environment file
print_status "Creating production environment configuration..."
cat > /opt/ai-recruitment/backend/.env << EOF
# Production Environment Variables
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
HOST=0.0.0.0

# Database Configuration
DB_HOST=localhost
DB_NAME=ai_recruitment
DB_USER=ai_user
DB_PASSWORD=your_secure_password_here
DB_PORT=5432

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Model Paths
MODEL_DIR=/opt/ai-recruitment/backend/models
DATA_DIR=/opt/ai-recruitment/backend/data

# Security
SECRET_KEY=your_super_secret_key_here_change_this_in_production
EOF

# Create systemd service file for backend
print_status "Creating systemd service for backend..."
sudo tee /etc/systemd/system/ai-recruitment-backend.service > /dev/null << EOF
[Unit]
Description=AI Recruitment System Backend
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/ai-recruitment/backend
Environment=PATH=/opt/ai-recruitment/backend/venv/bin
ExecStart=/opt/ai-recruitment/backend/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service file for frontend (nginx)
print_status "Creating nginx configuration..."
sudo tee /etc/nginx/sites-available/ai-recruitment << EOF
server {
    listen 80;
    server_name your-domain.com;  # Change this to your domain

    # Frontend
    location / {
        root /opt/ai-recruitment/frontend;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/ai-recruitment /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Create production requirements file
print_status "Creating production requirements..."
cat > /opt/ai-recruitment/backend/requirements.txt << EOF
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
cd /opt/ai-recruitment/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create log rotation configuration
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/ai-recruitment << EOF
/opt/ai-recruitment/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF

# Create monitoring script
print_status "Creating monitoring script..."
cat > /opt/ai-recruitment/monitor.sh << 'EOF'
#!/bin/bash

# AI Recruitment System Monitoring Script

LOG_FILE="/opt/ai-recruitment/logs/monitor.log"
BACKEND_PID=$(pgrep -f "gunicorn.*app:app")
FRONTEND_PID=$(pgrep -f "nginx")

echo "$(date): Checking AI Recruitment System..." >> $LOG_FILE

# Check backend
if [ -z "$BACKEND_PID" ]; then
    echo "$(date): Backend is down! Restarting..." >> $LOG_FILE
    sudo systemctl restart ai-recruitment-backend
else
    echo "$(date): Backend is running (PID: $BACKEND_PID)" >> $LOG_FILE
fi

# Check frontend
if [ -z "$FRONTEND_PID" ]; then
    echo "$(date): Frontend is down! Restarting..." >> $LOG_FILE
    sudo systemctl restart nginx
else
    echo "$(date): Frontend is running (PID: $FRONTEND_PID)" >> $LOG_FILE
fi

# Check disk space
DISK_USAGE=$(df /opt/ai-recruitment | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEMORY_USAGE -gt 80 ]; then
    echo "$(date): WARNING: Memory usage is ${MEMORY_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x /opt/ai-recruitment/monitor.sh

# Create backup script
print_status "Creating backup script..."
cat > /opt/ai-recruitment/backup.sh << 'EOF'
#!/bin/bash

# AI Recruitment System Backup Script

BACKUP_DIR="/opt/ai-recruitment/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ai_recruitment_backup_$DATE.tar.gz"

mkdir -p $BACKUP_DIR

echo "Creating backup: $BACKUP_FILE"

# Backup application files
tar -czf $BACKUP_FILE \
    /opt/ai-recruitment/backend \
    /opt/ai-recruitment/frontend \
    /opt/ai-recruitment/logs \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='venv'

# Backup database (if PostgreSQL is running)
if pg_isready -q; then
    pg_dump ai_recruitment > "$BACKUP_DIR/database_backup_$DATE.sql"
    echo "Database backup created: database_backup_$DATE.sql"
fi

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completed successfully!"
EOF

chmod +x /opt/ai-recruitment/backup.sh

# Create startup script
print_status "Creating startup script..."
cat > /opt/ai-recruitment/start.sh << 'EOF'
#!/bin/bash

# AI Recruitment System Startup Script

echo "🚀 Starting AI Recruitment System..."

# Start backend
sudo systemctl start ai-recruitment-backend
sudo systemctl enable ai-recruitment-backend

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Start monitoring
echo "✅ AI Recruitment System started successfully!"
echo "🌐 Frontend: http://your-domain.com"
echo "🔧 Backend API: http://your-domain.com/api"
echo "📊 Health Check: http://your-domain.com/api/health"
EOF

chmod +x /opt/ai-recruitment/start.sh

# Create shutdown script
print_status "Creating shutdown script..."
cat > /opt/ai-recruitment/stop.sh << 'EOF'
#!/bin/bash

# AI Recruitment System Shutdown Script

echo "🛑 Stopping AI Recruitment System..."

# Stop backend
sudo systemctl stop ai-recruitment-backend
sudo systemctl disable ai-recruitment-backend

# Stop nginx
sudo systemctl stop nginx
sudo systemctl disable nginx

echo "✅ AI Recruitment System stopped successfully!"
EOF

chmod +x /opt/ai-recruitment/stop.sh

# Create status script
print_status "Creating status script..."
cat > /opt/ai-recruitment/status.sh << 'EOF'
#!/bin/bash

# AI Recruitment System Status Script

echo "📊 AI Recruitment System Status"
echo "================================"

# Check backend
if systemctl is-active --quiet ai-recruitment-backend; then
    echo "✅ Backend: RUNNING"
else
    echo "❌ Backend: STOPPED"
fi

# Check nginx
if systemctl is-active --quiet nginx; then
    echo "✅ Frontend: RUNNING"
else
    echo "❌ Frontend: STOPPED"
fi

# Check database
if pg_isready -q; then
    echo "✅ Database: CONNECTED"
else
    echo "❌ Database: DISCONNECTED"
fi

# Check Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: CONNECTED"
else
    echo "❌ Redis: DISCONNECTED"
fi

# System resources
echo ""
echo "💻 System Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df /opt/ai-recruitment | tail -1 | awk '{print $5}')"
EOF

chmod +x /opt/ai-recruitment/status.sh

print_success "Deployment files created successfully!"

echo ""
echo "🎯 Next Steps:"
echo "1. Install PostgreSQL and Redis"
echo "2. Configure database"
echo "3. Update domain in nginx config"
echo "4. Start services"
echo ""
echo "Run: ./setup_database.sh"
echo "Run: ./start.sh"
echo ""
print_success "Deployment preparation completed!" 