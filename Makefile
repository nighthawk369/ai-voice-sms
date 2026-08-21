.PHONY: help setup dev down test lint format migrate seed reset clean logs

help:
	@echo "=== AI Platform Development Commands ==="
	@echo ""
	@echo "Setup & Environment:"
	@echo "  make setup        - Install dependencies and initialize local dev environment"
	@echo "  make dev          - Start all services locally (docker-compose up)"
	@echo "  make down         - Stop all services (docker-compose down)"
	@echo "  make clean        - Remove volumes and containers (fresh start)"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests (backend + frontend)"
	@echo "  make test-backend - Run backend tests only"
	@echo "  make test-frontend - Run frontend tests only"
	@echo "  make test-watch   - Run tests in watch mode"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         - Lint backend and frontend code"
	@echo "  make format       - Format backend and frontend code"
	@echo "  make type-check   - Run type checking"
	@echo ""
	@echo "Database:"
	@echo "  make migrate      - Run database migrations"
	@echo "  make migrate-down - Rollback last migration"
	@echo "  make seed         - Seed demo data"
	@echo ""
	@echo "Utilities:"
	@echo "  make logs         - Follow Docker logs"
	@echo "  make shell-api    - Open Python shell in API container"
	@echo "  make psql         - Connect to PostgreSQL"

setup:
	@echo "Setting up AI Platform development environment..."
	@echo ""
	@echo "Step 1: Creating .env file from .env.example..."
	cp .env.example .env 2>/dev/null || echo ".env.example not found, skipping"
	@echo ""
	@echo "Step 2: Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo ""
	@echo "Step 3: Installing frontend dependencies..."
	cd frontend && npm install
	@echo ""
	@echo "Step 4: Installing mobile dependencies..."
	cd mobile && npm install
	@echo ""
	@echo "Step 5: Starting Docker services..."
	docker-compose up -d
	@echo ""
	@echo "Step 6: Running database migrations..."
	sleep 5
	cd backend && alembic upgrade head
	@echo ""
	@echo "✅ Setup complete! Run 'make dev' to start development"

dev:
	docker-compose up -d
	@echo "✅ Services started. Check with 'docker-compose ps'"
	@echo ""
	@echo "Services:"
	@echo "  - API:        http://localhost:8000 (Swagger: http://localhost:8000/docs)"
	@echo "  - Frontend:   http://localhost:3000"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis:      localhost:6379"

down:
	docker-compose down
	@echo "✅ Services stopped"

test:
	@echo "Running tests..."
	cd backend && pytest -v --tb=short
	cd ../frontend && npm run test

test-backend:
	cd backend && pytest -v --tb=short

test-frontend:
	cd frontend && npm run test

test-watch:
	cd backend && pytest --tb=short -v -s --looponfail

lint:
	@echo "Linting backend..."
	cd backend && ruff check app tests
	@echo "✅ Backend lint passed"
	@echo ""
	@echo "Linting frontend..."
	cd frontend && npx eslint app lib --ext .ts,.tsx
	@echo "✅ Frontend lint passed"

format:
	@echo "Formatting backend..."
	cd backend && black app tests && ruff check --fix app tests
	@echo "✅ Backend formatted"
	@echo ""
	@echo "Formatting frontend..."
	cd frontend && npx prettier --write "app/**/*.{ts,tsx}" "lib/**/*.{ts,tsx}"
	@echo "✅ Frontend formatted"

type-check:
	@echo "Type checking backend..."
	cd backend && pyright app tests
	@echo "✅ Backend type check passed"
	@echo ""
	@echo "Type checking frontend..."
	cd frontend && tsc --noEmit
	@echo "✅ Frontend type check passed"

migrate:
	cd backend && alembic upgrade head
	@echo "✅ Migrations completed"

migrate-down:
	cd backend && alembic downgrade -1
	@echo "✅ Migration rolled back"

migrate-check:
	cd backend && alembic current

seed:
	cd backend && python -m app.cli.seed
	@echo "✅ Demo data seeded"

reset: clean setup
	@echo "✅ Full reset complete"

clean:
	docker-compose down -v
	rm -rf backend/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf frontend/.next
	rm -rf frontend/node_modules
	rm -rf mobile/node_modules
	@echo "✅ Cleaned"

logs:
	docker-compose logs -f

shell-api:
	docker-compose exec api python

psql:
	docker-compose exec postgres psql -U dev -d ai_platform
