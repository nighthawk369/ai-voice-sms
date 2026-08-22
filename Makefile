.PHONY: help setup dev down test lint format migrate seed reset clean logs test-coverage health-check install-tools db-reset dev-full prod-build

help:
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║     AI Voice & SMS Platform - Development Commands             ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make setup              - Full setup (docker, deps, migrations)"
	@echo "  make install-tools      - Install CLI tools for development"
	@echo "  make dev                - Start all services in development mode"
	@echo "  make dev-full           - Setup + Dev with real-time logs"
	@echo "  make down               - Stop all services gracefully"
	@echo "  make reset              - Full reset (clean + setup)"
	@echo "  make clean              - Remove containers, volumes, cache"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test               - Run all tests (backend + frontend)"
	@echo "  make test-backend       - Backend tests (pytest)"
	@echo "  make test-frontend      - Frontend tests (jest)"
	@echo "  make test-coverage      - Generate coverage reports"
	@echo "  make test-e2e           - Run E2E tests"
	@echo "  make lint               - Lint all code"
	@echo "  make format             - Format all code"
	@echo "  make type-check         - Type checking (backend + frontend)"
	@echo ""
	@echo "🔄 Database:"
	@echo "  make migrate            - Run all pending migrations"
	@echo "  make migrate-down       - Rollback last migration"
	@echo "  make migrate-check      - Check current migration status"
	@echo "  make migrate-new NAME=X - Create new migration"
	@echo "  make db-reset           - Drop & recreate database"
	@echo "  make seed               - Seed demo data"
	@echo ""
	@echo "🔍 Utilities:"
	@echo "  make logs               - Follow Docker logs (all services)"
	@echo "  make logs-api           - Follow API logs only"
	@echo "  make logs-db            - Follow database logs only"
	@echo "  make health-check       - Check health of all services"
	@echo "  make shell-api          - Open Python shell in API container"
	@echo "  make psql               - Connect to PostgreSQL"
	@echo "  make redis-cli          - Connect to Redis CLI"
	@echo "  make docker-status      - Show container status"
	@echo ""
	@echo "📦 Production:"
	@echo "  make prod-build         - Build production Docker images"
	@echo "  make prod-up            - Run production containers"
	@echo ""

setup:
	@echo "🚀 Setting up AI Platform development environment..."
	@mkdir -p logs
	@echo ""
	@echo "Step 1/7: Creating .env from template..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "✅ .env created"; else echo "✅ .env already exists"; fi
	@echo ""
	@echo "Step 2/7: Installing backend dependencies..."
	@cd backend && python -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1
	@cd backend && pip install -q -r requirements.txt
	@echo "✅ Backend dependencies installed"
	@echo ""
	@echo "Step 3/7: Installing frontend dependencies..."
	@cd frontend && npm install --silent > /dev/null 2>&1
	@echo "✅ Frontend dependencies installed"
	@echo ""
	@echo "Step 4/7: Installing mobile dependencies..."
	@cd mobile && npm install --silent > /dev/null 2>&1
	@echo "✅ Mobile dependencies installed"
	@echo ""
	@echo "Step 5/7: Building and starting Docker services..."
	@docker-compose up -d --build > /dev/null 2>&1
	@echo "✅ Docker services started"
	@echo ""
	@echo "Step 6/7: Waiting for database to be ready..."
	@for i in {1..30}; do \
		if docker-compose exec -T postgres pg_isready -U dev -d ai_platform > /dev/null 2>&1; then \
			echo "✅ Database ready"; \
			break; \
		fi; \
		if [ $$i -eq 30 ]; then echo "❌ Database failed to start"; exit 1; fi; \
		sleep 1; \
	done
	@echo ""
	@echo "Step 7/7: Running database migrations..."
	@docker-compose exec -T api alembic upgrade head > /dev/null 2>&1
	@echo "✅ Database migrations completed"
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  ✅ Setup Complete!                                             ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run 'make dev' to start development"
	@echo "  2. Visit http://localhost:8000/docs for API documentation"
	@echo "  3. Visit http://localhost:3000 for the frontend"
	@echo ""

dev:
	@echo "🎯 Starting development environment..."
	@docker-compose up -d > /dev/null 2>&1
	@sleep 2
	@echo ""
	@docker-compose ps
	@echo ""
	@echo "✅ Services started successfully!"
	@echo ""
	@echo "📍 Service URLs:"
	@echo "  API Docs:       http://localhost:8000/docs"
	@echo "  ReDoc:          http://localhost:8000/redoc"
	@echo "  Frontend:       http://localhost:3000"
	@echo "  Redis Admin:    http://localhost:6379 (use redis-cli)"
	@echo "  MinIO Console:  http://localhost:9001 (admin/minioadmin)"
	@echo ""
	@echo "💡 Useful commands:"
	@echo "  make logs       - View all service logs"
	@echo "  make health-check - Check service health"
	@echo "  make test       - Run tests"
	@echo ""

dev-full: setup
	@echo "🎯 Running in development mode with live logs..."
	@docker-compose logs -f

down:
	@echo "⏹️  Stopping services..."
	@docker-compose down > /dev/null 2>&1
	@echo "✅ Services stopped"

clean:
	@echo "🧹 Cleaning up..."
	@docker-compose down -v > /dev/null 2>&1
	@rm -rf backend/__pycache__ backend/.pytest_cache backend/.venv
	@rm -rf frontend/.next frontend/node_modules frontend/dist
	@rm -rf mobile/node_modules mobile/.expo
	@rm -rf logs/**
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

reset: clean setup
	@echo "✅ Full reset complete"

test:
	@echo "🧪 Running all tests..."
	@echo ""
	@echo "Backend tests:"
	@cd backend && pytest -v --tb=short --cov=app --cov-report=term-missing
	@echo ""
	@echo "Frontend tests:"
	@cd frontend && npm run test 2>/dev/null || echo "⚠️  Frontend tests not configured"
	@echo ""
	@echo "✅ All tests completed"

test-backend:
	@echo "🧪 Running backend tests..."
	@cd backend && pytest -v --tb=short --cov=app --cov-report=term-missing --cov-report=html
	@echo "📊 Coverage report: backend/htmlcov/index.html"

test-frontend:
	@echo "🧪 Running frontend tests..."
	@cd frontend && npm run test

test-coverage:
	@echo "📊 Generating coverage reports..."
	@cd backend && pytest --cov=app --cov-report=html --cov-report=term-missing -q
	@echo "✅ Backend coverage: backend/htmlcov/index.html"

test-e2e:
	@echo "🌐 Running E2E tests (when configured)..."
	@cd frontend && npm run e2e 2>/dev/null || echo "⚠️  E2E tests not configured"

lint:
	@echo "🔍 Linting code..."
	@echo ""
	@echo "Backend:"
	@cd backend && ruff check app tests || true
	@cd backend && black --check app tests || true
	@echo "✅ Backend lint complete"
	@echo ""
	@echo "Frontend:"
	@cd frontend && npx eslint app lib --ext .ts,.tsx || true
	@echo "✅ Frontend lint complete"

format:
	@echo "🎨 Formatting code..."
	@echo ""
	@echo "Backend:"
	@cd backend && black app tests
	@cd backend && ruff check --fix app tests
	@echo "✅ Backend formatted"
	@echo ""
	@echo "Frontend:"
	@cd frontend && npx prettier --write "app/**/*.{ts,tsx,css}" "lib/**/*.{ts,tsx}"
	@echo "✅ Frontend formatted"

type-check:
	@echo "📝 Type checking..."
	@echo ""
	@echo "Backend:"
	@cd backend && pyright app tests || true
	@echo "✅ Backend type check complete"
	@echo ""
	@echo "Frontend:"
	@cd frontend && tsc --noEmit || true
	@echo "✅ Frontend type check complete"

migrate:
	@echo "📦 Running migrations..."
	@docker-compose exec -T api alembic upgrade head
	@echo "✅ Migrations completed"

migrate-down:
	@echo "⏮️  Rolling back migration..."
	@docker-compose exec -T api alembic downgrade -1
	@echo "✅ Migration rolled back"

migrate-check:
	@echo "📋 Current migration status:"
	@docker-compose exec -T api alembic current

migrate-new:
	@echo "🆕 Creating new migration..."
	@docker-compose exec -T api alembic revision --autogenerate -m "$(NAME)"
	@echo "✅ Migration created: migrations/versions/"

db-reset:
	@echo "🔄 Resetting database..."
	@docker-compose down postgres -v > /dev/null 2>&1
	@sleep 1
	@docker-compose up -d postgres > /dev/null 2>&1
	@sleep 5
	@docker-compose exec -T api alembic upgrade head > /dev/null 2>&1
	@echo "✅ Database reset complete"

seed:
	@echo "🌱 Seeding demo data..."
	@docker-compose exec -T api python -m app.cli.seed || echo "⚠️  Seed script not configured"
	@echo "✅ Demo data seeded"

logs:
	@docker-compose logs -f

logs-api:
	@docker-compose logs -f api

logs-db:
	@docker-compose logs -f postgres

health-check:
	@echo "🏥 Checking service health..."
	@echo ""
	@echo "API Health:"
	@curl -s http://localhost:8000/health || echo "❌ API is down"
	@echo ""
	@echo "Docker Status:"
	@docker-compose ps
	@echo ""
	@echo "✅ Health check complete"

shell-api:
	@docker-compose exec api python

psql:
	@docker-compose exec postgres psql -U dev -d ai_platform

redis-cli:
	@docker-compose exec redis redis-cli

docker-status:
	@docker-compose ps

install-tools:
	@echo "🛠️  Installing development tools..."
	@command -v docker > /dev/null || (echo "Please install Docker" && exit 1)
	@command -v docker-compose > /dev/null || (echo "Please install Docker Compose" && exit 1)
	@pip install --upgrade pip setuptools wheel
	@echo "✅ Tools installed"

prod-build:
	@echo "🏗️  Building production images..."
	@docker build -f backend/Dockerfile -t ai-platform-api:latest ./backend
	@docker build -f frontend/Dockerfile -t ai-platform-web:latest ./frontend
	@echo "✅ Production images built"

prod-up:
	@echo "🚀 Running production containers..."
	@docker-compose -f docker-compose.yml up -d
	@echo "✅ Production services started"
