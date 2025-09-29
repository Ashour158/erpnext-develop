# Complete ERP System Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Production Deployment](#production-deployment)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

## Overview

This guide covers deploying the complete ERP system across multiple platforms and environments. The system includes:

- **Backend**: Python Flask API with SQLAlchemy ORM
- **Frontend**: React TypeScript application
- **Database**: PostgreSQL with Redis for caching
- **Modules**: CRM, Finance, People, Supply Chain, Maintenance, Booking, Moments, AI, Workflow

## Prerequisites

### System Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB+ recommended for production)
- **Storage**: 20GB+ free space
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows 10+

### Software Requirements
- **Python**: 3.8+
- **Node.js**: 16+
- **PostgreSQL**: 12+
- **Redis**: 6+
- **Docker**: 20+ (optional)
- **Git**: 2.0+

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd clean-erp-system
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Install PostgreSQL and Redis
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib redis-server

# Create database
sudo -u postgres psql
CREATE DATABASE erp_system;
CREATE USER erp_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE erp_system TO erp_user;
\q
```

### 4. Environment Configuration
```bash
# Create environment file
cp .env.example .env

# Edit .env file
DATABASE_URL=postgresql://erp_user:your_password@localhost:5432/erp_system
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

### 5. Initialize Database
```bash
python app.py --init-db
```

### 6. Frontend Setup
```bash
cd ../frontend
npm install
npm start
```

### 7. Run Development Server
```bash
# Backend (Terminal 1)
cd backend
python app.py

# Frontend (Terminal 2)
cd frontend
npm start
```

## Docker Deployment

### 1. Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: erp_system
      POSTGRES_USER: erp_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://erp_user:your_password@postgres:5432/erp_system
      REDIS_URL: redis://redis:6379/0
    ports:
      - "5000:5000"
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 2. Build and Run
```bash
# Build images
docker-compose build

# Run services
docker-compose up -d

# Initialize database
docker-compose exec backend python app.py --init-db
```

## Cloud Deployment

### DigitalOcean Droplet

#### 1. Create Droplet
```bash
# Create Ubuntu 20.04 droplet
# Minimum: 2GB RAM, 1 CPU, 50GB SSD
```

#### 2. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql redis-server nginx git

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 3. Application Deployment
```bash
# Clone repository
git clone <repository-url>
cd clean-erp-system

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup database
sudo -u postgres psql
CREATE DATABASE erp_system;
CREATE USER erp_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE erp_system TO erp_user;
\q

# Initialize database
python app.py --init-db

# Setup frontend
cd ../frontend
npm install
npm run build
```

#### 4. Nginx Configuration
```nginx
# /etc/nginx/sites-available/erp-system
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 5. Systemd Services
```bash
# Backend service
sudo nano /etc/systemd/system/erp-backend.service
```

```ini
[Unit]
Description=ERP Backend Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/clean-erp-system/backend
Environment=PATH=/home/ubuntu/clean-erp-system/backend/venv/bin
ExecStart=/home/ubuntu/clean-erp-system/backend/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start services
sudo systemctl enable erp-backend
sudo systemctl start erp-backend
sudo systemctl enable nginx
sudo systemctl start nginx
```

### AWS EC2 Deployment

#### 1. Launch EC2 Instance
- **Instance Type**: t3.medium or larger
- **AMI**: Ubuntu Server 20.04 LTS
- **Security Groups**: Allow HTTP (80), HTTPS (443), SSH (22)

#### 2. Application Setup
```bash
# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Follow similar setup as DigitalOcean
# Install dependencies and deploy application
```

#### 3. RDS Database Setup
```bash
# Create RDS PostgreSQL instance
# Update DATABASE_URL in environment
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/erp_system
```

### Google Cloud Platform

#### 1. Compute Engine
```bash
# Create VM instance
gcloud compute instances create erp-system \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-medium \
    --zone=us-central1-a
```

#### 2. Cloud SQL Setup
```bash
# Create Cloud SQL instance
gcloud sql instances create erp-db \
    --database-version=POSTGRES_13 \
    --tier=db-f1-micro \
    --region=us-central1
```

### Azure Deployment

#### 1. Virtual Machine
```bash
# Create VM
az vm create \
    --resource-group myResourceGroup \
    --name erp-system \
    --image UbuntuLTS \
    --size Standard_B2s \
    --admin-username azureuser
```

#### 2. Database Setup
```bash
# Create Azure Database for PostgreSQL
az postgres server create \
    --resource-group myResourceGroup \
    --name erp-db-server \
    --location eastus \
    --admin-user erpadmin \
    --admin-password YourPassword123! \
    --sku-name GP_Gen5_2
```

## Production Deployment

### 1. Environment Configuration
```bash
# Production environment variables
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/0
SECRET_KEY=your-production-secret-key
DEBUG=False
```

### 2. Security Configuration
```bash
# Install SSL certificate
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# Configure firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 3. Performance Optimization
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Configure PostgreSQL
sudo nano /etc/postgresql/13/main/postgresql.conf
# Adjust memory settings based on server size
```

### 4. Backup Strategy
```bash
# Database backup script
#!/bin/bash
pg_dump -h localhost -U erp_user erp_system > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup with cron
0 2 * * * /path/to/backup_script.sh
```

## Monitoring & Maintenance

### 1. Application Monitoring
```bash
# Install monitoring tools
pip install psutil
pip install prometheus-client

# Setup log rotation
sudo nano /etc/logrotate.d/erp-system
```

### 2. Database Monitoring
```bash
# PostgreSQL monitoring
sudo -u postgres psql
SELECT * FROM pg_stat_activity;
SELECT * FROM pg_stat_database;
```

### 3. Health Checks
```bash
# Create health check script
curl -f http://localhost:5000/health || exit 1
curl -f http://localhost:3000 || exit 1
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U erp_user -d erp_system
```

#### 2. Port Conflicts
```bash
# Check port usage
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :3000

# Kill processes if needed
sudo kill -9 <PID>
```

#### 3. Memory Issues
```bash
# Check memory usage
free -h
htop

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. Application Logs
```bash
# Check application logs
journalctl -u erp-backend -f
tail -f /var/log/nginx/error.log
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_employees_department ON employees(department_id);
```

#### 2. Caching Strategy
```python
# Redis caching
import redis
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.memoize(timeout=300)
def get_customer_data(customer_id):
    # Expensive database query
    pass
```

#### 3. Load Balancing
```nginx
# Nginx load balancing
upstream backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

## Security Best Practices

### 1. Environment Security
```bash
# Secure environment variables
chmod 600 .env
chown root:root .env
```

### 2. Database Security
```sql
-- Create read-only user
CREATE USER erp_readonly WITH PASSWORD 'readonly_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO erp_readonly;
```

### 3. Application Security
```python
# Enable CORS properly
from flask_cors import CORS
CORS(app, origins=['https://yourdomain.com'])

# Rate limiting
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)
```

## Scaling Considerations

### 1. Horizontal Scaling
- Use load balancers (HAProxy, Nginx)
- Implement database read replicas
- Use Redis clustering for caching

### 2. Vertical Scaling
- Increase server resources
- Optimize database queries
- Implement connection pooling

### 3. Microservices Architecture
- Split modules into separate services
- Use API gateways
- Implement service discovery

## Conclusion

This deployment guide provides comprehensive instructions for deploying the complete ERP system across various platforms. Choose the deployment method that best fits your requirements and infrastructure.

For additional support, refer to the troubleshooting section or contact the development team.
