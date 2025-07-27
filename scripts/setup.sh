#!/bin/bash

# Finance Tracker Setup Script
echo "🏦 Finance Tracker Setup Script"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker and Docker Compose first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create environment files if they don't exist
echo "📝 Setting up environment files..."

if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from example"
else
    echo "⚠️  backend/.env already exists, skipping..."
fi

if [ ! -f "frontend/.env" ]; then
    cp frontend/.env.example frontend/.env
    echo "✅ Created frontend/.env from example"
else
    echo "⚠️  frontend/.env already exists, skipping..."
fi

# Prompt for Plaid credentials
echo ""
echo "🔐 Plaid API Configuration"
echo "=========================="
echo "To use the bank integration features, you need Plaid API credentials."
echo "Visit https://dashboard.plaid.com/ to get your credentials."
echo ""

read -p "Do you have Plaid credentials? (y/n): " has_plaid

if [ "$has_plaid" = "y" ] || [ "$has_plaid" = "Y" ]; then
    read -p "Enter your Plaid Client ID: " plaid_client_id
    read -p "Enter your Plaid Secret Key: " plaid_secret
    read -p "Enter Plaid Environment (sandbox/development/production) [sandbox]: " plaid_env
    plaid_env=${plaid_env:-sandbox}
    
    # Update backend .env file
    sed -i "s/PLAID_CLIENT_ID=your_plaid_client_id/PLAID_CLIENT_ID=$plaid_client_id/" backend/.env
    sed -i "s/PLAID_SECRET=your_plaid_secret_key/PLAID_SECRET=$plaid_secret/" backend/.env
    sed -i "s/PLAID_ENV=sandbox/PLAID_ENV=$plaid_env/" backend/.env
    
    echo "✅ Plaid credentials configured"
else
    echo "⚠️  Skipping Plaid configuration. You can set it up later in backend/.env"
fi

# Generate a secure secret key
echo ""
echo "🔑 Generating secure secret key..."
secret_key=$(openssl rand -hex 32)
sed -i "s/SECRET_KEY=your-super-secret-key-change-in-production/SECRET_KEY=$secret_key/" backend/.env
echo "✅ Generated secure secret key"

# Build and start the application
echo ""
echo "🚀 Building and starting the application..."
echo "This may take a few minutes for the first build..."
echo ""

docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📍 Application URLs:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo ""
    echo "🔧 Management Commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop app: docker-compose down"
    echo "   Restart: docker-compose restart"
    echo ""
    echo "📖 Next Steps:"
    echo "   1. Visit http://localhost:3000 to access the application"
    echo "   2. Create an account or login"
    echo "   3. Connect your bank account using Plaid"
    echo "   4. Start tracking your finances!"
    echo ""
else
    echo "❌ Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi 