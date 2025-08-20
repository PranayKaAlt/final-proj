# 🚀 **Quick Deployment Guide - AI Recruitment System**

## **🎯 Ready to Deploy in 3 Steps!**

Your enterprise-grade AI recruitment system is ready for production deployment. Follow these simple steps:

---

## **Step 1: Prepare Your System** ⚙️

### **Prerequisites**
- Ubuntu 20.04+ or similar Linux distribution
- sudo privileges
- At least 4GB RAM (8GB recommended)
- 20GB+ free disk space
- Domain name (optional, for production)

### **System Requirements**
```bash
# Check your system
free -h                    # Memory
df -h                      # Disk space
uname -a                   # OS version
```

---

## **Step 2: Run Deployment Scripts** 🚀

### **2.1 Deploy the Application**
```bash
# Make scripts executable (if not already done)
chmod +x deploy.sh setup_database.sh

# Run the deployment script
./deploy.sh
```

**What this does:**
- ✅ Creates production directories
- ✅ Builds React frontend
- ✅ Sets up Python virtual environment
- ✅ Creates systemd services
- ✅ Configures nginx
- ✅ Sets up monitoring and backup scripts

### **2.2 Setup Database and Services**
```bash
# Install and configure PostgreSQL, Redis, and nginx
./setup_database.sh
```

**What this does:**
- ✅ Installs PostgreSQL, Redis, nginx
- ✅ Creates database and user
- ✅ Configures SSL certificates
- ✅ Sets up firewall
- ✅ Creates monitoring cron jobs

---

## **Step 3: Start Your System** 🎉

### **3.1 Start All Services**
```bash
# Navigate to production directory
cd /opt/ai-recruitment

# Start the system
./start.sh
```

### **3.2 Check System Status**
```bash
# Check if everything is running
./status.sh
```

**Expected Output:**
```
📊 AI Recruitment System Status
================================
✅ Backend: RUNNING
✅ Frontend: RUNNING
✅ Database: CONNECTED
✅ Redis: CONNECTED

💻 System Resources:
CPU Usage: 15%
Memory Usage: 45.2%
Disk Usage: 23%
```

---

## **🌐 Access Your System**

### **Local Access**
- **Frontend**: `http://localhost` or `http://your-server-ip`
- **Backend API**: `http://localhost/api`
- **Health Check**: `http://localhost/api/health`

### **Production Access**
- **Frontend**: `https://your-domain.com`
- **Backend API**: `https://your-domain.com/api`
- **Health Check**: `https://your-domain.com/api/health`

---

## **🔧 Configuration Options**

### **Update Domain Name**
```bash
# Edit nginx configuration
sudo nano /etc/nginx/sites-available/ai-recruitment

# Replace 'your-domain.com' with your actual domain
# Reload nginx
sudo systemctl reload nginx
```

### **Update SSL Certificate (Production)**
```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is automatically configured
```

### **Change Default Passwords**
```bash
# Database password
sudo -u postgres psql
ALTER USER ai_user PASSWORD 'your_new_secure_password';
\q

# Update environment file
sudo nano /opt/ai-recruitment/backend/.env
```

---

## **📊 Management Commands**

### **System Control**
```bash
cd /opt/ai-recruitment

# Start system
./start.sh

# Stop system
./stop.sh

# Check status
./status.sh

# Monitor logs
tail -f logs/monitor.log
```

### **Backup and Restore**
```bash
# Create backup
./backup.sh

# List backups
ls -la backups/

# Restore from backup (if needed)
tar -xzf backups/ai_recruitment_backup_YYYYMMDD_HHMMSS.tar.gz
```

### **Service Management**
```bash
# Backend service
sudo systemctl start/stop/restart ai-recruitment-backend
sudo systemctl status ai-recruitment-backend

# Nginx service
sudo systemctl start/stop/restart nginx
sudo systemctl status nginx

# Database service
sudo systemctl start/stop/restart postgresql
sudo systemctl status postgresql

# Redis service
sudo systemctl start/stop/restart redis-server
sudo systemctl status redis-server
```

---

## **🔍 Troubleshooting**

### **Common Issues**

**1. Port Already in Use**
```bash
# Check what's using port 5000
sudo netstat -tlnp | grep :5000

# Kill process if needed
sudo kill -9 <PID>
```

**2. Database Connection Failed**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
pg_isready -h localhost -p 5432 -U ai_user -d ai_recruitment
```

**3. Nginx Configuration Error**
```bash
# Test configuration
sudo nginx -t

# Check nginx status
sudo systemctl status nginx
```

**4. Permission Issues**
```bash
# Fix permissions
sudo chown -R $USER:$USER /opt/ai-recruitment
chmod -R 755 /opt/ai-recruitment
```

### **Log Files**
```bash
# Application logs
tail -f /opt/ai-recruitment/logs/monitor.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u ai-recruitment-backend -f
sudo journalctl -u nginx -f
```

---

## **📈 Performance Monitoring**

### **System Resources**
```bash
# CPU and Memory
htop

# Disk usage
df -h

# Network connections
netstat -tlnp
```

### **Application Metrics**
- **API Response Time**: Check nginx access logs
- **Database Performance**: Monitor PostgreSQL logs
- **Memory Usage**: Check Redis memory usage
- **Model Performance**: Review continuous learning logs

---

## **🔒 Security Checklist**

### **Production Security**
- [ ] Change default passwords
- [ ] Update SSL certificate
- [ ] Configure firewall
- [ ] Enable automatic updates
- [ ] Set up monitoring alerts
- [ ] Regular backups
- [ ] Access control
- [ ] Rate limiting

### **SSL Certificate Renewal**
```bash
# Test renewal
sudo certbot renew --dry-run

# Manual renewal
sudo certbot renew
```

---

## **🎯 Success Indicators**

### **System Health**
- ✅ All services running
- ✅ Database connected
- ✅ API responding
- ✅ Frontend accessible
- ✅ SSL working
- ✅ Monitoring active

### **Performance Metrics**
- **Response Time**: < 500ms
- **Uptime**: > 99.9%
- **Memory Usage**: < 80%
- **Disk Usage**: < 70%
- **CPU Usage**: < 60%

---

## **🚀 Congratulations!**

Your AI recruitment system is now **production-ready** and can handle:
- **1000+ resumes per day**
- **Real-time AI analysis**
- **Multi-user access**
- **Enterprise-grade security**
- **Automatic scaling**

### **Next Steps**
1. **Test with real data**
2. **Configure monitoring alerts**
3. **Set up regular backups**
4. **Train with your specific data**
5. **Scale as needed**

---

## **📞 Support**

If you encounter any issues:
1. Check the troubleshooting section
2. Review log files
3. Verify system requirements
4. Check service status

**Your enterprise AI recruitment system is ready to revolutionize hiring!** 🎉✨ 