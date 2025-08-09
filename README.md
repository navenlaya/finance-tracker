# 💰 Finance Tracker

A comprehensive, full-stack personal finance management application with real bank account integration via Plaid API. Built with modern technologies and designed with professional-grade architecture.

![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![React](https://img.shields.io/badge/React-18.2.0-61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2.2-3178C6)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED)

## ✨ Features

### 🔐 Authentication & Security
- **Secure JWT Authentication** with bcrypt password hashing
- **Auto token validation** and session management
- **Password reset** functionality with secure token generation
- **Protected routes** with automatic redirect handling

### 🏦 Banking Integration
- **Real bank account connection** via Plaid API
- **Automatic transaction syncing** from multiple financial institutions
- **Account balance tracking** across checking, savings, and credit accounts
- **Bank-level security** with encrypted token storage

### 📊 Financial Management
- **Dashboard Overview** with real-time financial metrics
- **Transaction Management** with advanced filtering and search
- **Budget Creation & Tracking** with progress visualization
- **Account Management** with sync status and connection monitoring

### 🧠 Analytics & Insights
- **AI-Powered Insights** with spending pattern analysis
- **Spending Forecasts** using machine learning algorithms
- **Category-based Analytics** with visual breakdowns
- **Financial Health Scoring** and recommendations

### ⚙️ User Experience
- **Modern Responsive UI** with Tailwind CSS
- **Dark/Light Mode** support (planned)
- **Real-time Notifications** with toast messages
- **Loading States** and error handling
- **Mobile-first Design** for all screen sizes

## 🏗️ Architecture

### Frontend Stack
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Tailwind CSS with custom component system
- **State Management**: Zustand for lightweight, type-safe state
- **Data Fetching**: React Query for server state management
- **Routing**: React Router DOM with protected routes
- **Forms**: React Hook Form with comprehensive validation
- **Charts**: Recharts for beautiful data visualizations
- **Icons**: Lucide React for consistent iconography
- **Banking**: React Plaid Link for secure bank connections

### Backend Stack
- **Framework**: FastAPI with async/await for high performance
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **Authentication**: JWT tokens with secure password hashing
- **API Integration**: Plaid Python SDK for banking data
- **Task Queue**: Celery with Redis for background processing
- **ML/AI**: scikit-learn and Prophet for forecasting (planned)
- **Data Validation**: Pydantic for robust request/response schemas
- **Security**: Encrypted token storage and CORS protection

### Infrastructure
- **Containerization**: Docker & Docker Compose for consistent environments
- **Database**: PostgreSQL 15 with connection pooling
- **Cache/Queue**: Redis 7 for session storage and task queuing
- **Process Management**: Uvicorn/Gunicorn for production deployment
- **Background Tasks**: Celery Beat for scheduled operations

## 🚀 Quick Start

### One-Click Setup (Recommended)

Use our automated setup script:

```bash
git clone https://github.com/navenlaya/finance-tracker.git
cd finance-tracker
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The script will:
- ✅ Check Docker installation
- 🔧 Set up environment files
- 🔐 Configure Plaid credentials (optional)
- 🔑 Generate secure secret keys
- 🚀 Build and start all services
- 📍 Provide access URLs and next steps

### Manual Docker Setup

1. **Clone and navigate**
   ```bash
   git clone https://github.com/navenlaya/finance-tracker.git
   cd finance-tracker
   ```

2. **Environment setup**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   # Edit with your Plaid credentials (optional for testing)
   ```

3. **Start services**
   ```bash
   docker-compose up --build -d
   ```

4. **Access application**
   - 🌐 Frontend: http://localhost:3000
   - 🔌 Backend API: http://localhost:8000
   - 📚 API Docs: http://localhost:8000/docs

## 📱 Application Pages

### 🏠 Dashboard
- Real-time financial overview
- Balance tracking across all accounts
- Recent transactions display
- Quick action buttons for common tasks

### 🏦 Accounts
- Connected bank accounts management
- Account balance and status monitoring
- Bank connection and sync functionality
- Add new accounts via Plaid Link

### 💳 Transactions
- Comprehensive transaction history
- Advanced filtering (date, category, account, amount)
- Search functionality across transaction details
- Transaction categorization and editing

### 💰 Budgets
- Budget creation with flexible periods (monthly, weekly, yearly)
- Progress tracking with visual indicators
- Spending alerts and notifications
- Budget performance analytics

### 📈 Insights
- AI-powered spending analysis
- Category-wise expense breakdown
- Spending trends and forecasts
- Personalized financial recommendations

### ⚙️ Settings
- User profile management
- Security settings and password changes
- Notification preferences
- Account integrations and connections

## 🛠️ Development Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- PostgreSQL 15+ (for local development)

### Local Development

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Configure database and start PostgreSQL
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## 🔧 Configuration

### Environment Variables

#### Backend Configuration (`backend/.env`)
```env
# Application Settings
DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production
API_PREFIX=/api/v1

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/finance_tracker

# Plaid API Configuration
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret_key
PLAID_ENV=sandbox  # sandbox, development, production

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

#### Frontend Configuration (`frontend/.env`)
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Plaid Configuration
VITE_PLAID_ENV=sandbox
```

### Plaid Integration Setup

1. **Create Plaid Developer Account**
   - Visit [Plaid Dashboard](https://dashboard.plaid.com/)
   - Create a new application
   - Copy your Client ID and Secret Key

2. **Configure Credentials**
   - Add credentials to `backend/.env`
   - Set environment to `sandbox` for testing

3. **Test with Sandbox**
   - Use test credentials: `user_good` / `pass_good`
   - Test various account scenarios with Plaid's test data

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/token` - OAuth2 token endpoint
- `GET /api/v1/auth/me` - Get current user profile
- `POST /api/v1/auth/password-reset` - Request password reset
- `POST /api/v1/auth/password-reset/confirm` - Confirm password reset

### User Management
- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile

### Banking & Plaid Integration
- `POST /api/v1/plaid/create-link-token` - Create Plaid Link token
- `POST /api/v1/plaid/exchange-public-token` - Exchange public token for access token
- `GET /api/v1/plaid/connection-status` - Check connection status
- `POST /api/v1/plaid/sync-transactions` - Sync transactions from bank
- `POST /api/v1/plaid/sync-accounts` - Sync account information

### Account Management
- `GET /api/v1/accounts` - Get user accounts
- `GET /api/v1/accounts/{account_id}` - Get specific account details

### Transaction Management
- `GET /api/v1/transactions` - Get transactions with filtering
- `GET /api/v1/transactions/dashboard` - Get dashboard data
- `POST /api/v1/transactions` - Create manual transaction
- `PUT /api/v1/transactions/{transaction_id}` - Update transaction

### ML & Analytics (Planned)
- `GET /api/v1/ml/forecast` - Get spending forecasts
- `GET /api/v1/ml/insights` - Get AI-powered insights
- `POST /api/v1/ml/retrain` - Trigger model retraining

**📖 Complete API documentation**: http://localhost:8000/docs

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app  # With coverage
```

### Frontend Testing
```bash
cd frontend
npm run test
npm run test:coverage
```

### Integration Testing
```bash
# E2E tests with Playwright (planned)
npm run test:e2e
```

## 🚢 Deployment

### Production Docker Deployment

1. **Update environment variables for production**
   ```bash
   # backend/.env
   DEBUG=False
   SECRET_KEY=your-strong-production-secret-key
   DATABASE_URL=postgresql://user:password@prod-db:5432/finance_tracker
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Cloud Deployment Options

#### 🟡 Heroku
```bash
# Add Heroku Postgres addon
heroku addons:create heroku-postgresql:hobby-dev
# Configure environment variables
heroku config:set SECRET_KEY=your-secret-key
# Deploy
git push heroku main
```

#### 🟠 AWS ECS/Fargate
- Use provided Dockerfiles for containerization
- Set up RDS PostgreSQL for database
- Configure Application Load Balancer
- Use ECR for container registry

#### 🔵 Google Cloud Run
- Deploy containerized services individually
- Use Cloud SQL for PostgreSQL
- Set up Cloud Build for CI/CD pipeline

#### 🟢 DigitalOcean App Platform
- Connect GitHub repository
- Configure build commands and environment variables
- Automatic deployment on git push

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'Add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Open Pull Request**

### Development Guidelines
- Follow TypeScript/Python type hints
- Write tests for new features
- Update documentation for API changes
- Follow conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- 📧 Email: support@financetracker.dev
- 🐛 Issues: [GitHub Issues](https://github.com/navenlaya/finance-tracker/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/navenlaya/finance-tracker/discussions)

## 🙏 Acknowledgments

- [Plaid](https://plaid.com/) for banking data integration
- [FastAPI](https://fastapi.tiangolo.com/) for the amazing Python framework
- [React](https://reactjs.org/) and [Tailwind CSS](https://tailwindcss.com/) for the frontend
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM

---

**Built with ❤️ by the Finance Tracker Team**