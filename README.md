# Finance Tracker

A modern, full-stack finance tracking application with AI-powered insights and real bank account integration via Plaid API. Built with industry best practices and designed for professional portfolios.

![Finance Tracker](https://img.shields.io/badge/Version-1.0.0-blue)
![React](https://img.shields.io/badge/React-18.2.0-61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2.2-3178C6)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)

## Features

### Core Features
- **Secure Authentication**: JWT-based authentication with password hashing
- **Bank Integration**: Real bank account connection via Plaid API
- **Transaction Sync**: Automatic transaction syncing and categorization
- **Responsive Design**: Mobile-first, modern UI with dark mode support
- **Real-time Updates**: Live transaction updates and notifications

### AI/ML Features (To Do)
- **Spending Forecasting**: Predict future spending patterns using Prophet and scikit-learn
- **Anomaly Detection**: Identify unusual transactions and potential fraud
- **Smart Categorization**: AI-powered transaction categorization
- **Insights Generation**: Personalized financial insights and recommendations
- **Budget Optimization**: AI-suggested budget improvements

### Dashboard & Analytics
- **Financial Overview**: Real-time balance, income, and expense tracking
- **Interactive Charts**: Spending trends and category breakdowns
- **Budget Management**: Set and track spending goals
- **Custom Reports**: Export financial reports in multiple formats
- **Calendar View**: Daily and weekly spending visualization
#### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with custom design system
- **State Management**: Zustand for client state
- **Data Fetching**: React Query for server state
- **Routing**: React Router DOM
- **Forms**: React Hook Form with validation
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React

#### Backend
- **Framework**: FastAPI with async/await
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt hashing
- **API Integration**: Plaid for bank connections
- **Task Queue**: Celery with Redis
- **ML/AI**: scikit-learn, Prophet for forecasting
- **Data Validation**: Pydantic schemas

#### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Web Server**: Nginx (production)
- **Process Management**: Gunicorn/Uvicorn

## Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Node.js 18+** (for local development)
- **Python 3.11+** (for local development)
- **PostgreSQL 15+** (for local development)
- **Plaid API Account** (for bank integration)

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finance-tracker
   ```

2. **Set up environment variables**
   ```bash
   # Copy environment files
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   
   # Edit with your Plaid credentials
   nano backend/.env
   ```

3. **Start the application**
   ```bash
   # Build and start all services
   docker-compose up --build
   
   # Or run in background
   docker-compose up -d --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Create database
   createdb finance_tracker
   
   # Run migrations
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Application
DEBUG=True
SECRET_KEY=your-super-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/finance_tracker

# Plaid API
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret_key
PLAID_ENV=sandbox

# Redis
REDIS_URL=redis://localhost:6379/0
```

#### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_PLAID_ENV=sandbox
```

### Plaid Integration Setup

1. **Create Plaid Account**
   - Visit [Plaid Dashboard](https://dashboard.plaid.com/)
   - Create a new application
   - Get your Client ID and Secret Key

2. **Configure Environment**
   - Set `PLAID_CLIENT_ID` and `PLAID_SECRET` in backend/.env
   - Set `PLAID_ENV` to `sandbox` for testing

3. **Test Integration**
   - Use Plaid test credentials in sandbox mode
   - Username: `user_good`, Password: `pass_good`

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Plaid Integration Endpoints
- `POST /api/v1/plaid/create-link-token` - Create Link token
- `POST /api/v1/plaid/exchange-public-token` - Exchange public token
- `GET /api/v1/plaid/connection-status` - Get connection status
- `POST /api/v1/plaid/sync-transactions` - Sync transactions

### Transaction Endpoints
- `GET /api/v1/transactions` - Get transactions with filters
- `POST /api/v1/transactions` - Create manual transaction
- `PUT /api/v1/transactions/{id}` - Update transaction
- `GET /api/v1/transactions/dashboard` - Get dashboard data

### ML/AI Endpoints
- `GET /api/v1/ml/forecast` - Get spending forecasts
- `GET /api/v1/ml/insights` - Get AI insights
- `POST /api/v1/ml/retrain` - Trigger model retraining

Full API documentation available at: http://localhost:8000/docs

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### E2E Tests
```bash
# Coming soon - Playwright/Cypress integration
```

## Deployment

### Production Deployment with Docker

1. **Update environment variables**
   ```bash
   # Set production values in .env files
   DEBUG=False
   SECRET_KEY=strong-production-secret
   DATABASE_URL=postgresql://user:pass@prod-db:5432/db
   ```

2. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Cloud Deployment Options

#### AWS ECS/Fargate
- Use provided Dockerfiles
- Set up RDS PostgreSQL
- Configure ALB for load balancing

#### Google Cloud Run
- Deploy containerized services
- Use Cloud SQL for PostgreSQL
- Set up Cloud Build for CI/CD

#### DigitalOcean App Platform
- Connect GitHub repository
- Configure build commands
- Set environment variables
