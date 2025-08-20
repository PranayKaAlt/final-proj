#!/bin/bash

# 🗄️ AI Recruitment System - Database Setup Script
# This script sets up PostgreSQL and Redis for production

set -e  # Exit on any error

echo "🗄️ Setting up AI Recruitment System Database..."
echo "=============================================="

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

# Update system packages
print_status "Updating system packages..."
sudo apt-get update

# Install PostgreSQL
print_status "Installing PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib

# Install Redis
print_status "Installing Redis..."
sudo apt-get install -y redis-server

# Install nginx
print_status "Installing nginx..."
sudo apt-get install -y nginx

# Start and enable services
print_status "Starting and enabling services..."
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl start redis-server
sudo systemctl enable redis-server
sudo systemctl start nginx
sudo systemctl enable nginx

# Configure PostgreSQL
print_status "Configuring PostgreSQL..."

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE ai_recruitment;
CREATE USER ai_user WITH PASSWORD 'ai_recruitment_secure_password_2024';
GRANT ALL PRIVILEGES ON DATABASE ai_recruitment TO ai_user;
ALTER USER ai_user CREATEDB;
\q
EOF

# Configure PostgreSQL for remote connections (optional)
print_status "Configuring PostgreSQL for connections..."
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf
sudo sed -i "s/#port = 5432/port = 5432/" /etc/postgresql/*/main/postgresql.conf

# Configure Redis
print_status "Configuring Redis..."
sudo sed -i "s/# maxmemory <bytes>/maxmemory 256mb/" /etc/redis/redis.conf
sudo sed -i "s/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/" /etc/redis/redis.conf

# Restart services
print_status "Restarting services..."
sudo systemctl restart postgresql
sudo systemctl restart redis-server

# Test database connection
print_status "Testing database connection..."
if pg_isready -h localhost -p 5432 -U ai_user -d ai_recruitment; then
    print_success "PostgreSQL connection successful!"
else
    print_error "PostgreSQL connection failed!"
    exit 1
fi

# Test Redis connection
print_status "Testing Redis connection..."
if redis-cli ping | grep -q "PONG"; then
    print_success "Redis connection successful!"
else
    print_error "Redis connection failed!"
    exit 1
fi

# Create database tables
print_status "Creating database tables..."
cd /opt/ai-recruitment/backend
source venv/bin/activate
python3 database_config.py

# Set up firewall (optional)
print_status "Setting up firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

# Create SSL certificate (self-signed for development)
print_status "Creating SSL certificate..."
sudo mkdir -p /etc/ssl/private
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/ai-recruitment.key \
    -out /etc/ssl/certs/ai-recruitment.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"

# Update nginx configuration with SSL
print_status "Updating nginx configuration with SSL..."
sudo tee /etc/nginx/sites-available/ai-recruitment << EOF
# HTTP redirect to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/ai-recruitment.crt;
    ssl_certificate_key /etc/ssl/private/ai-recruitment.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

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
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
EOF

# Test nginx configuration
print_status "Testing nginx configuration..."
if sudo nginx -t; then
    print_success "Nginx configuration is valid!"
    sudo systemctl reload nginx
else
    print_error "Nginx configuration is invalid!"
    exit 1
fi

# Create cron job for monitoring
print_status "Setting up monitoring cron job..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/ai-recruitment/monitor.sh") | crontab -

# Create cron job for backups
print_status "Setting up backup cron job..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/ai-recruitment/backup.sh") | crontab -

# Set up log rotation
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
    postrotate
        sudo systemctl reload nginx
    endscript
}
EOF

print_success "Database setup completed successfully!"

echo ""
echo "🎯 Database Configuration Summary:"
echo "=================================="
echo "PostgreSQL:"
echo "  - Database: ai_recruitment"
echo "  - User: ai_user"
echo "  - Password: ai_recruitment_secure_password_2024"
echo "  - Port: 5432"
echo ""
echo "Redis:"
echo "  - Host: localhost"
echo "  - Port: 6379"
echo "  - Max Memory: 256MB"
echo ""
echo "Nginx:"
echo "  - HTTP Port: 80 (redirects to HTTPS)"
echo "  - HTTPS Port: 443"
echo "  - SSL Certificate: Self-signed"
echo ""
echo "🔧 Next Steps:"
echo "1. Update domain name in nginx config"
echo "2. Update SSL certificate for production"
echo "3. Change default passwords"
echo "4. Start the application"
echo ""
echo "Run: ./start.sh"
echo ""
print_success "Database setup completed!" 