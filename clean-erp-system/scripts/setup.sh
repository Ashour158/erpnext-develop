#!/bin/bash

# Clean ERP System - Setup Script
# Complete setup script for the clean ERP system

set -e

echo "🚀 Setting up Clean ERP System..."

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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if Node.js is installed
check_node() {
    if ! command -v node &> /dev/null; then
        print_warning "Node.js is not installed. Frontend development will not work."
        return 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_warning "npm is not installed. Frontend development will not work."
        return 1
    fi
    
    print_success "Node.js and npm are installed"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip3 first."
        exit 1
    fi
    
    print_success "Python 3 and pip3 are installed"
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
FLASK_ENV=development
DATABASE_URL=postgresql://erp_user:erp_password@localhost:5432/clean_erp_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-development-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
EOF
        print_success "Created .env file"
    fi
    
    cd ..
    print_success "Backend setup completed"
}

# Setup frontend
setup_frontend() {
    if check_node; then
        print_status "Setting up frontend..."
        
        cd frontend
        
        # Install dependencies
        print_status "Installing Node.js dependencies..."
        npm install
        
        # Create .env file if it doesn't exist
        if [ ! -f ".env" ]; then
            print_status "Creating .env file..."
            cat > .env << EOF
REACT_APP_API_URL=http://localhost:5000
REACT_APP_WS_URL=ws://localhost:5000
EOF
            print_success "Created .env file"
        fi
        
        cd ..
        print_success "Frontend setup completed"
    else
        print_warning "Skipping frontend setup (Node.js not available)"
    fi
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    # Create database directory
    mkdir -p database
    
    # Create init.sql file
    cat > database/init.sql << EOF
-- Clean ERP System Database Initialization
-- This file is executed when the PostgreSQL container starts

-- Create database if it doesn't exist
-- (This is handled by the POSTGRES_DB environment variable)

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create initial admin user (will be handled by the application)
-- This is just a placeholder for any initial data setup
EOF
    
    print_success "Database setup completed"
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Create monitoring directory
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    
    # Create Prometheus configuration
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'clean-erp-backend'
    static_configs:
      - targets: ['backend:5000']
    metrics_path: '/api/metrics'
    scrape_interval: 30s

  - job_name: 'clean-erp-postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  - job_name: 'clean-erp-redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
EOF
    
    # Create Grafana datasource
    cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
    
    print_success "Monitoring setup completed"
}

# Setup nginx
setup_nginx() {
    print_status "Setting up nginx..."
    
    # Create nginx directory
    mkdir -p nginx
    
    # Create nginx configuration
    cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:5000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # WebSocket support
        location /socket.io/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF
    
    print_success "Nginx setup completed"
}

# Main setup function
main() {
    print_status "Starting Clean ERP System setup..."
    
    # Check prerequisites
    check_docker
    check_python
    
    # Setup components
    setup_database
    setup_backend
    setup_frontend
    setup_monitoring
    setup_nginx
    
    print_success "🎉 Clean ERP System setup completed!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Start the system: docker-compose up -d"
    print_status "2. Access the application: http://localhost"
    print_status "3. Access Grafana: http://localhost:3001"
    print_status "4. Access Prometheus: http://localhost:9090"
    print_status ""
    print_status "Development mode:"
    print_status "1. Backend: cd backend && source venv/bin/activate && python app.py"
    print_status "2. Frontend: cd frontend && npm start"
    print_status ""
    print_success "Setup completed successfully! 🚀"
}

# Run main function
main "$@"
