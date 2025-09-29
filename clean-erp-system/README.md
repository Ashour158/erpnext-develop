# Clean ERP System
## Complete Enterprise Resource Planning System - Zero Frappe Dependencies

A modern, fully independent ERP system built from scratch with:
- **Backend**: Python Flask/FastAPI with SQLAlchemy ORM
- **Frontend**: React TypeScript with modern UI/UX
- **Database**: PostgreSQL with Redis caching
- **Real-time**: WebSocket integration
- **AI/ML**: Built-in analytics and recommendations
- **Deployment**: Docker-ready with Kubernetes support

## System Architecture

```
clean-erp-system/
├── backend/                 # Python backend API
│   ├── core/               # Core system components
│   ├── modules/           # ERP modules
│   ├── api/               # REST API endpoints
│   ├── database/          # Database models and migrations
│   └── tests/             # Backend tests
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── utils/         # Utilities
│   └── public/            # Static assets
├── database/              # Database schemas and migrations
├── docker/                # Docker configurations
├── docs/                  # Documentation
└── scripts/              # Deployment and utility scripts
```

## Modules Included

### Core Modules
- **CRM**: Customer relationship management
- **Finance**: Accounting, invoicing, financial statements
- **People**: HR, attendance, leave management
- **Supply Chain**: Inventory, purchasing, suppliers
- **Maintenance**: Asset management, work orders
- **Booking**: Meeting and resource scheduling
- **Moments**: Social collaboration platform

### Advanced Features
- **AI Analytics**: Predictive insights and recommendations
- **Real-time Updates**: Live data synchronization
- **Workflow Engine**: Custom business processes
- **Approval System**: Multi-level approvals
- **Data Import/Export**: Bulk operations
- **Mobile Support**: Responsive design
- **Multi-company**: Multi-tenant architecture
- **Multi-currency**: International support

## Quick Start

```bash
# Clone and setup
git clone <repository>
cd clean-erp-system

# Backend setup
cd backend
pip install -r requirements.txt
python app.py

# Frontend setup
cd frontend
npm install
npm start

# Database setup
python scripts/init_database.py
```

## Technology Stack

- **Backend**: Python 3.9+, Flask/FastAPI, SQLAlchemy
- **Frontend**: React 18, TypeScript, Material-UI
- **Database**: PostgreSQL 14+, Redis 6+
- **Real-time**: Socket.IO
- **AI/ML**: scikit-learn, pandas, numpy
- **Deployment**: Docker, Kubernetes
- **Monitoring**: Prometheus, Grafana

## Features

✅ **Zero Frappe Dependencies** - Completely independent
✅ **Modern Architecture** - Microservices ready
✅ **Real-time Updates** - Live data synchronization
✅ **AI-Powered** - Smart recommendations and analytics
✅ **Mobile-First** - Responsive design
✅ **Multi-tenant** - Company isolation
✅ **Scalable** - Cloud-ready architecture
✅ **Secure** - Enterprise-grade security
✅ **Extensible** - Plugin architecture
✅ **Well-tested** - Comprehensive test coverage

## License

MIT License - Free for commercial and personal use.
