# ⚡ Quick Reference Guide - Common Commands & Tasks

## 🚀 Running the Project

### Start Everything Locally
```bash
# Backend (Terminal 1)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements-optimized.txt
uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev

# Mobile (Terminal 3)
cd mobile
npm install
npx expo start
```

### Stop Everything
```bash
# Kill all processes
pkill -f uvicorn
pkill -f "next dev"
pkill -f "expo start"
```

---

## 🗄️ Database Commands

### Local Setup
```bash
# Option A: Brew PostgreSQL
brew install postgresql
brew services start postgresql
createdb aivoicesms_dev

# Option B: Docker PostgreSQL
docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres
```

### Run Migrations
```bash
cd backend
alembic upgrade head          # Run all migrations
alembic downgrade -1          # Rollback last migration
alembic revision -m "message" # Create new migration
```

### Database Queries
```bash
# Connect to DB
psql aivoicesms_dev

# List tables
\dt

# Query example
SELECT * FROM users LIMIT 5;
```

---

## 🧪 Testing

### Run All Tests
```bash
cd backend
python -m pytest tests/ -v              # All tests
python -m pytest tests/test_auth.py -v # Specific file
python -m pytest -k "test_login" -v    # By test name
```

### Test Coverage
```bash
python -m pytest --cov=app tests/
```

---

## 🔑 Environment Setup

### Backend (.env)
```bash
# Copy template
cp .env.example .env

# Edit with your values
DATABASE_URL=postgresql://user:password@localhost/aivoicesms_dev
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
JWT_SECRET=your-secret-key
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Mobile (.env)
```bash
EXPO_PUBLIC_API_URL=http://localhost:8000
```

---

## 📡 API Testing

### Using curl
```bash
# Get all business types
curl http://localhost:8000/api/v1/business-types

# Get specific business type
curl http://localhost:8000/api/v1/business-types/hvac_contractor

# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","business_type":"hvac_contractor"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Using FastAPI Docs
```
http://localhost:8000/docs       # Interactive Swagger UI
http://localhost:8000/redoc      # ReDoc documentation
```

### Using Postman
1. Import OpenAPI schema from `http://localhost:8000/openapi.json`
2. Set `Authorization: Bearer {token}` header
3. Test endpoints

---

## 📁 Project Structure Quick Map

```
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app entry
│   │   ├── routes.py             # All API endpoints (50+)
│   │   ├── models.py             # SQLAlchemy models (11)
│   │   ├── schemas.py            # Pydantic schemas
│   │   ├── industry_config.py    # Business type configs (29)
│   │   ├── routes_business_types.py  # Business type endpoints
│   │   ├── db.py                 # Database connection
│   │   ├── auth.py               # JWT authentication
│   │   ├── voice/                # Twilio voice integration
│   │   ├── sms/                  # Twilio SMS integration
│   │   ├── llm/                  # LLM providers
│   │   └── crm/                  # CRM integrations
│   ├── tests/
│   ├── requirements-optimized.txt
│   ├── alembic/                  # Database migrations
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Home page
│   │   ├── layout.tsx            # Root layout
│   │   ├── components/
│   │   │   ├── BusinessTypeSelector.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ContactForm.tsx
│   │   │   └── ...
│   │   ├── auth/                 # Auth pages
│   │   └── crm/                  # CRM pages
│   ├── next.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── Dockerfile
│
├── mobile/
│   ├── app/
│   │   ├── components/
│   │   │   ├── BusinessTypeSelector.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   └── ...
│   │   ├── auth/                 # Auth screens
│   │   ├── crm/                  # CRM screens
│   │   └── _layout.tsx           # Navigation layout
│   ├── app.json                  # Expo config
│   ├── package.json
│   └── eas.json                  # EAS Build config
│
└── infrastructure/
    └── terraform/
        ├── aws/
        │   ├── main.tf
        │   ├── variables.tf
        │   ├── outputs.tf
        │   ├── modules/            # Terraform modules
        │   └── environments/       # Dev, staging, prod configs
        └── gcp/
            └── main.tf
```

---

## 🚢 Deployment Commands

### Deploy to AWS
```bash
cd infrastructure/terraform/aws

# Initialize
terraform init

# Plan deployment
terraform plan -var-file="environments/dev-ultra-optimized.tfvars"

# Apply
terraform apply -var-file="environments/dev-ultra-optimized.tfvars"

# Get outputs
terraform output -json > outputs.json
```

### Deploy Docker Image
```bash
# Build
docker build -t ai-voice-sms:latest .

# Tag
docker tag ai-voice-sms:latest {ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/ai-voice-sms:latest

# Push
docker push {ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/ai-voice-sms:latest
```

### Deploy to ECS
```bash
aws ecs update-service \
  --cluster ai-voice-sms-prod \
  --service ai-voice-sms-api \
  --force-new-deployment
```

---

## 🔍 Debugging

### Backend Logs
```bash
# View live logs
tail -f backend/logs/app.log

# Search for errors
grep ERROR backend/logs/app.log | tail -20
```

### Frontend Logs
```bash
# Check browser console
# Right-click → Inspect → Console tab
```

### Database Issues
```bash
# Check connection
psql aivoicesms_dev -c "SELECT 1"

# Restart PostgreSQL
brew services restart postgresql
```

### Environment Issues
```bash
# Check Python version
python --version  # Should be 3.9+

# Check pip packages
pip list | grep -E "(fastapi|sqlalchemy|pydantic)"

# Reinstall dependencies
pip install --force-reinstall -r requirements-optimized.txt
```

---

## 🔐 Authentication Debugging

### JWT Token
```bash
# Decode token (install jq first: brew install jq)
curl -s http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' | jq '.access_token'

# Verify token at jwt.io
# Copy token from response, paste in jwt.io
```

### Test Protected Endpoint
```bash
TOKEN="your-jwt-token-here"

curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 Common API Calls

### Business Types
```bash
# Get all business types
curl http://localhost:8000/api/v1/business-types

# Get specific business type config
curl http://localhost:8000/api/v1/business-types/hvac_contractor
```

### Users
```bash
# Signup
POST /api/v1/auth/signup
{
  "email": "user@example.com",
  "password": "password123",
  "business_type": "hvac_contractor"
}

# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

# Get current user
GET /api/v1/users/me
Header: Authorization: Bearer {token}
```

### Contacts
```bash
# Create contact
POST /api/v1/contacts
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890"
}

# Get contacts
GET /api/v1/contacts

# Update contact
PUT /api/v1/contacts/{contact_id}

# Delete contact
DELETE /api/v1/contacts/{contact_id}
```

### Conversations
```bash
# Start conversation
POST /api/v1/conversations
{
  "contact_id": "uuid",
  "type": "inbound_call"
}

# Get conversations
GET /api/v1/conversations

# Get conversation messages
GET /api/v1/conversations/{conversation_id}/messages

# Send message
POST /api/v1/conversations/{conversation_id}/messages
{
  "content": "Hello, how can I help?",
  "type": "assistant"
}
```

---

## 🔧 Common Fixes

### "Module not found" Error
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +

# Reinstall dependencies
pip install -r requirements-optimized.txt
```

### "Port already in use" Error
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 {PID}
```

### "CORS Error" in Frontend
```bash
# Backend CORS is configured in app/main.py
# Check that frontend URL is in CORS_ORIGINS
# If deploying, update infrastructure/terraform/aws/variables.tf
```

### Database Connection Error
```bash
# Check PostgreSQL running
brew services list | grep postgres

# Start PostgreSQL
brew services start postgresql

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### "No such table" Error
```bash
# Run migrations
cd backend
alembic upgrade head

# Check migration status
alembic current
```

---

## 📝 Git Workflow

### Starting New Work
```bash
# Create branch
git checkout -b feature/my-feature

# Check status
git status

# Stage changes
git add backend/app/my_file.py

# Commit
git commit -m "feat: add new feature"

# Push
git push origin feature/my-feature

# Create PR on GitHub
```

### Syncing with Main
```bash
# Fetch latest
git fetch origin

# Rebase on main
git rebase origin/main

# Force push (only on your branch!)
git push origin feature/my-feature --force
```

---

## 📊 Monitoring

### Backend Health Check
```bash
curl http://localhost:8000/health
```

### Database Queries
```bash
# Connect to PostgreSQL
psql aivoicesms_dev

# Most active tables
SELECT schemaname, tablename, seq_scan FROM pg_stat_user_tables ORDER BY seq_scan DESC LIMIT 10;

# Database size
SELECT pg_size_pretty(pg_database_size('aivoicesms_dev'));
```

### Redis Connection
```bash
# Connect to Redis
redis-cli

# Check stats
INFO

# View keys
KEYS *
```

---

## 🎯 Quick Onboarding Checklist

New to the project? Do this:

```bash
# 1. Clone repository
git clone https://github.com/nighthawk369/callsync.git
cd ai-voice-sms

# 2. Read documentation
# - START_HERE.md (10 min)
# - PROJECT_STRUCTURE.md (10 min)
# - This file (5 min)

# 3. Set up environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
cp mobile/.env.example mobile/.env

# 4. Install dependencies
cd backend && pip install -r requirements-optimized.txt
cd ../frontend && npm install
cd ../mobile && npm install

# 5. Start local database
brew services start postgresql
createdb aivoicesms_dev

# 6. Run migrations
cd backend && alembic upgrade head

# 7. Start services
# Terminal 1: backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: frontend
cd frontend && npm run dev

# Terminal 3: mobile
cd mobile && npx expo start

# 8. Test
# Visit http://localhost:3000
# Try API at http://localhost:8000/docs
```

---

## 🆘 Getting Help

**Still confused?** Check the docs:

| Problem | Document |
|---------|----------|
| "How do I start?" | START_HERE.md |
| "Where is X in the code?" | PROJECT_STRUCTURE.md |
| "What's the architecture?" | ARCHITECTURE_DIAGRAMS.md |
| "How do I run tests?" | LOCAL_TESTING_GUIDE.md |
| "What API endpoints exist?" | API_REFERENCE.md |
| "What's next?" | NEXT_STEPS.md |
| "I'm lost" | PROJECT_KNOWLEDGE_INDEX.md |

---

## 📞 Command Cheat Sheet

```bash
# Backend
uvicorn app.main:app --reload       # Start backend
python -m pytest tests/ -v          # Run tests
alembic upgrade head                # Run migrations

# Frontend
npm run dev                         # Start frontend
npm run build                       # Build for production
npm run lint                        # Check linting

# Mobile
npx expo start                      # Start Expo
npx expo build                      # Build APK/IPA
eas build --platform ios            # Build iOS with EAS

# Git
git status                          # Check status
git add .                           # Stage all
git commit -m "message"             # Commit
git push origin branch              # Push

# Docker
docker build -t name .              # Build image
docker run -p 8000:8000 name        # Run container
docker ps                           # List containers

# Terraform
terraform init                      # Initialize
terraform plan                      # Show changes
terraform apply                     # Apply changes
terraform destroy                   # Destroy resources
```

---

**Last Updated:** 2026-08-23
**Purpose:** Save time with copy-paste commands
**Pro Tip:** Bookmark this file for quick reference!
