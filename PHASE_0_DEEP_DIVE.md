# PHASE 0: REPOSITORY BOOTSTRAP - DEEP DIVE

**Solo Developer Implementation Plan**  
**Status:** Ready to Execute  
**Estimated Duration:** 2-3 weeks (40-60 hours)  
**Target Outcome:** Fully functional local dev environment with all tech stacks proven to work together

---

## Executive Summary

PHASE 0 proves all technology layers work together:
- **Backend** (FastAPI) ✓
- **Frontend** (React/Next.js) ✓
- **Mobile** (React Native) ✓
- **Database** (PostgreSQL) ✓
- **Cache** (Redis) ✓
- **LLM Abstraction** (multi-provider ready) ✓
- **Admin Platform** (shell) ✓
- **CI/CD** (GitHub Actions) ✓

By end of PHASE 0:
- [ ] Local dev environment fully functional
- [ ] All three frontends (web, iOS, Android) running locally
- [ ] API responding with mock data
- [ ] Database migrations working
- [ ] Authentication (JWT) working
- [ ] Multi-tenancy enforced
- [ ] All tests passing
- [ ] All linting/type-checking passing
- [ ] Admin platform shell with basic functions
- [ ] GitHub Actions CI pipeline running
- [ ] Can deploy to dev environment

---

## Week-by-Week Breakdown

### Week 1: Foundation & Database (12-15 hours)

#### Days 1-2: Repository Setup (4 hours)
```
Monday-Tuesday Morning

✓ Create GitHub repository
✓ Clone locally
✓ Create project structure:
  backend/
  frontend/ (web - Next.js)
  mobile/ (React Native - Expo)
  infrastructure/
  docs/

✓ Create root-level files:
  - Makefile
  - docker-compose.yml (local dev)
  - .env.example
  - .gitignore
  - README.md (basic)

✓ Initialize backend:
  - pyproject.toml (Poetry or pip)
  - requirements.txt
  - Python 3.11 venv

✓ Initialize frontend:
  - npx create-next-app@latest
  - Tailwind setup
  - package.json dependencies

✓ Initialize mobile:
  - npx create-expo-app
  - Expo Go configured
  - package.json shared deps

✓ Initialize infrastructure:
  - terraform/main.tf (empty)
  - Makefile targets for terraform

Deliverable: Repository is cloneable and all three tech stacks install locally
Commit: "Phase 0: Initial repository structure and tech stack setup"
```

#### Days 2-3: Docker Compose & Local Development (4 hours)
```
Tuesday Afternoon - Wednesday

✓ Create Docker Compose file:
  - PostgreSQL 15 service
  - Redis 7 service
  - MinIO (S3 mock) service
  - API service (FastAPI, volume mount)
  - Web service (Next.js, volume mount)
  - Ollama service (optional, local LLM)

✓ Create Docker Compose networking:
  - All services on same network
  - Health checks for each service
  - Volume management for persistence

✓ Test Docker Compose:
  docker-compose up -d
  All services healthy

✓ Create convenience Makefile targets:
  make setup       # First-time setup
  make dev         # docker-compose up
  make down        # docker-compose down
  make clean       # Remove volumes
  make logs        # Follow logs

Deliverable: "make dev" brings up all services
Test: docker-compose ps shows all healthy
Commit: "Phase 0: Docker Compose for local development"
```

#### Days 3-4: Database Schema & Migrations (4-5 hours)
```
Wednesday Afternoon - Thursday

✓ Install Alembic in backend
  alembic init migrations

✓ Create SQLAlchemy models for PHASE 0:
  - Organization
  - User
  - APIKey (minimal)

✓ Create Alembic migrations:
  alembic revision --autogenerate -m "001_initial_schema"
  alembic upgrade head

✓ Create migration helper Makefile targets:
  make migrate       # Run migrations
  make migrate-down  # Rollback
  make migrate-check # Check migration status
  make seed          # Seed demo data

✓ Test migrations:
  make migrate
  psql to verify tables created

Deliverable: Database schema created, migrations working
Test: psql shows organization, user, apikey tables
Commit: "Phase 0: Database schema and Alembic migrations"
```

---

### Week 1.5: Authentication & API Foundation (12-15 hours)

#### Days 4-5: Authentication System (5 hours)
```
Thursday Afternoon - Friday

✓ Implement JWT authentication:
  - Secret key generation
  - Token creation (access + refresh)
  - Token validation
  - Password hashing (bcrypt)

✓ Create auth models:
  - User schema (email, password_hash, role)
  - LoginRequest/LoginResponse
  - SignupRequest/SignupResponse
  - RefreshTokenRequest

✓ Implement auth routes:
  POST /api/v1/auth/signup
    Input: email, password, org_name
    Output: access_token, refresh_token, user
  
  POST /api/v1/auth/login
    Input: email, password
    Output: access_token, refresh_token, user
  
  POST /api/v1/auth/refresh
    Input: refresh_token
    Output: access_token
  
  POST /api/v1/auth/logout
    Clear tokens

✓ Create auth middleware:
  - Extract JWT from Authorization header
  - Validate token
  - Attach user_id to request
  - Reject unauthorized requests

✓ Test authentication:
  pytest tests/test_auth.py
  All auth tests passing

Deliverable: Full JWT auth system working
Test: Can signup, login, get new tokens
Commit: "Phase 0: JWT authentication system"
```

#### Days 5-6: Multi-Tenancy & API Shell (6-7 hours)
```
Friday Afternoon - Saturday Morning

✓ Implement tenant middleware:
  - Extract organization_id from JWT
  - Attach to every request context
  - Enforce tenant isolation in all queries

✓ Create base ORM patterns:
  class TenantAware(Base):
      organization_id: UUID = Column(UUID, ForeignKey('organization.id'))
  
  class TenantService:
      async def get_for_org(self, model, org_id):
          return await session.execute(
              select(model).where(
                  model.organization_id == org_id
              )
          )

✓ Create API route skeleton:
  /api/v1/
    ├── /auth (login, signup, refresh)
    ├── /organizations (CRUD - PHASE 1)
    ├── /users (CRUD - PHASE 1)
    ├── /health (liveness probe)
    └── /api-docs (auto OpenAPI)

✓ Create base response schema:
  {
    "success": true,
    "data": {...},
    "error": null,
    "timestamp": "2024-08-22T..."
  }

✓ Create error handling:
  - 400: Bad Request
  - 401: Unauthorized
  - 403: Forbidden (tenant isolation)
  - 404: Not Found
  - 500: Server Error
  - All with consistent JSON format

✓ Test tenant isolation:
  User A cannot access User B's organization
  Pytest tests/test_tenant_isolation.py

Deliverable: Multi-tenancy enforced at request layer
Test: GET /api/v1/organizations returns only current user's org
Commit: "Phase 0: Multi-tenancy middleware and API foundation"
```

#### Days 6-7: Frontend Shell (4-5 hours)
```
Saturday Afternoon - Sunday

✓ Create Next.js structure:
  app/
  ├── page.tsx (home/login)
  ├── layout.tsx (root)
  ├── auth/
  │   ├── login/page.tsx
  │   ├── signup/page.tsx
  │   └── layout.tsx
  ├── dashboard/
  │   ├── layout.tsx (authenticated)
  │   ├── page.tsx (home)
  │   ├── settings/page.tsx
  │   └── admin/
  │       └── page.tsx (admin shell)
  ├── components/
  │   ├── Header.tsx
  │   ├── Sidebar.tsx
  │   ├── Loading.tsx
  │   └── ErrorBoundary.tsx
  └── api/
      └── route.ts (API client setup)

✓ Create authentication context:
  - useAuth() hook
  - Login/signup logic
  - Token management (localStorage)
  - Protected routes

✓ Create API client:
  lib/api.ts
  - Axios instance
  - Request interceptor (add JWT)
  - Error handling

✓ Create basic pages:
  - Login page (email, password, submit)
  - Signup page (email, password, org_name, submit)
  - Dashboard home (welcome message)
  - Settings page (shell)
  - Admin panel (shell)

✓ Test frontend:
  npm run dev
  Can navigate login → signup → dashboard

Deliverable: Web frontend shell working with auth
Test: Can signup, login, reach dashboard at localhost:3000
Commit: "Phase 0: Next.js frontend shell with auth"
```

---

### Week 2: Mobile & Testing (12-15 hours)

#### Days 8-9: React Native Mobile Setup (5-6 hours)
```
Monday-Tuesday

✓ Create React Native Expo project:
  npx create-expo-app ai-platform-mobile

✓ Create navigation structure:
  - React Navigation v6
  - Stack: Auth Stack → Dashboard Stack

✓ Create mobile screens:
  screens/
  ├── auth/
  │   ├── LoginScreen.tsx
  │   ├── SignupScreen.tsx
  │   └── SplashScreen.tsx
  ├── dashboard/
  │   ├── HomeScreen.tsx
  │   ├── SettingsScreen.tsx
  │   └── AdminScreen.tsx
  └── components/ (shared with web)

✓ Create mobile API client:
  - Same lib/api.ts used by web and mobile
  - Axios instance
  - AsyncStorage for JWT

✓ Create mobile auth context:
  - useAuth() hook (same as web)
  - Login/signup logic
  - Token management

✓ Test mobile app:
  npm start
  Use Expo Go on iOS/Android simulator
  Can login, navigate, see dashboard

Deliverable: React Native app running on simulators
Test: iOS and Android simulators both showing login screen
Commit: "Phase 0: React Native mobile app with shared auth"
```

#### Days 9-10: Shared Code & TypeScript (4 hours)
```
Tuesday Afternoon - Wednesday

✓ Create shared library:
  packages/shared/ (monorepo approach with workspaces)
  ├── hooks/
  │   └── useAuth.ts
  ├── types/
  │   ├── auth.ts
  │   ├── user.ts
  │   └── organization.ts
  ├── api/
  │   └── client.ts
  ├── utils/
  │   └── validation.ts
  └── constants/
      └── config.ts

✓ Update frontend & mobile to use shared code:
  import { useAuth, User, ApiClient } from '@shared/...'

✓ Set up TypeScript strictly:
  tsconfig.json: "strict": true
  Both frontend and mobile have type safety

✓ Test shared code:
  npm run build:shared
  Both frontend and mobile compile

Deliverable: Shared code between web and mobile
Test: Change one hook, both apps update
Commit: "Phase 0: Shared code library and strict TypeScript"
```

#### Days 10-12: Testing & Admin Platform (5-6 hours)
```
Wednesday Afternoon - Friday

✓ Set up pytest for backend:
  tests/
  ├── conftest.py (fixtures)
  ├── test_auth.py
  ├── test_tenant_isolation.py
  ├── test_api.py
  └── unit/

✓ Create pytest fixtures:
  - Database session (fresh per test)
  - Test user & org
  - Test client
  - Authenticated headers

✓ Write critical tests:
  - Auth: signup, login, refresh, logout
  - Tenant: can't access other org's data
  - API: all endpoints return correct status codes
  - Database: migrations work forward and backward

✓ Set up Vitest for frontend:
  npm install -D vitest @testing-library/react
  tests/
  ├── useAuth.test.ts
  ├── login.test.tsx
  └── integration/

✓ Set up pre-commit hooks:
  .pre-commit-config.yaml
  - Ruff (lint)
  - Black (format)
  - Pyright (type check)
  - ESLint (frontend)
  - Prettier (format frontend)

✓ Build admin platform shell:
  /dashboard/admin/
  ├── page.tsx (admin dashboard)
  ├── organizations/page.tsx (list all orgs)
  ├── users/page.tsx (manage users)
  ├── system-health/page.tsx (health checks)
  └── feature-flags/page.tsx (feature toggles)

✓ Admin functionality (PHASE 0):
  - View all organizations (admin only)
  - View all users (admin only)
  - View system health (is everything up?)
  - Toggle feature flags (mock)

Deliverable: Full test suite + admin platform shell
Test: pytest passes, vitest passes, npm run build succeeds
Commit: "Phase 0: Testing infrastructure and admin platform shell"
```

---

### Week 3: LLM Abstraction & CI/CD (12-15 hours)

#### Days 13-15: LLM Provider Abstraction (6-7 hours)
```
Monday - Wednesday

✓ Create LLM abstraction layer:
  backend/app/llm/
  ├── __init__.py
  ├── base.py
      class LLMProvider(ABC):
          async def generate(self, prompt: str) -> str
          async def stream(self, prompt: str) -> AsyncIterator[str]
          async def count_tokens(self, text: str) -> int
  
  ├── openai_provider.py
      class OpenAIProvider(LLMProvider):
          - Uses OpenAI API
          - Supports GPT-4o, GPT-4 Turbo
  
  ├── anthropic_provider.py
      class AnthropicProvider(LLMProvider):
          - Uses Anthropic API
          - Supports Claude 3.5 Sonnet
  
  ├── google_provider.py
      class GoogleProvider(LLMProvider):
          - Uses Google Gemini API
          - Supports Gemini 2.0 Flash
  
  └── local_provider.py
      class LocalOpenAIProvider(LLMProvider):
          - Uses OpenAI-compatible endpoint
          - Supports vLLM, Ollama, etc

✓ Create LLM factory:
  llm_router.py
  class LLMRouter:
      async def get_provider(self, provider_name: str):
          return {
              'openai': OpenAIProvider(),
              'anthropic': AnthropicProvider(),
              'google': GoogleProvider(),
              'local': LocalOpenAIProvider(),
          }[provider_name]

✓ Create mock provider for testing:
  mock_provider.py
  class MockLLMProvider(LLMProvider):
      - Returns hardcoded responses
      - No API calls
      - Fast for tests

✓ Create configuration:
  config.py
  LLM_PROVIDER = 'openai'  # Configurable via env
  LLM_MODEL = 'gpt-4o'
  LLM_TEMPERATURE = 0.7
  LOCAL_LLM_ENDPOINT = 'http://localhost:8000'  # For private LLM

✓ Test LLM abstraction:
  tests/test_llm_providers.py
  - Test each provider (with mock API keys)
  - Test provider switching
  - Test token counting

Deliverable: Multi-provider LLM abstraction fully tested
Test: Can switch between providers in config
Commit: "Phase 0: Multi-provider LLM abstraction layer"
```

#### Days 15-17: GitHub Actions CI/CD (5-6 hours)
```
Wednesday Afternoon - Friday

✓ Create GitHub Actions workflows:
  .github/workflows/

  test.yml:
    - Lint: ruff check app tests
    - Format check: black --check app tests
    - Type check: pyright app tests
    - Unit tests: pytest
    - Coverage: pytest --cov
    - Trigger: On push to any branch

  security.yml:
    - Bandit (code security)
    - Safety (dependency vulnerabilities)
    - Trigger: On push to main

  deploy.yml:
    - Build Docker images
    - Push to ECR (when ready in PHASE 25)
    - Deploy to dev (when ready)
    - Trigger: On push to main (with approval)

✓ Set up branch protection:
  - main branch requires:
    - All CI checks pass
    - At least 1 approval (for solo: auto-approve or skip)
    - No direct pushes (always PR)

✓ Create GitHub PR template:
  .github/pull_request_template.md
  - Description of changes
  - Checklist: tests pass, docs updated, etc
  - PHASE number (which phase does this complete)

✓ Test CI pipeline:
  Push a branch with test changes
  Verify CI runs and reports results

Deliverable: Full CI/CD pipeline working
Test: Push a failing test, CI fails. Push a passing test, CI passes.
Commit: "Phase 0: GitHub Actions CI/CD pipeline"
```

#### Days 17-18: Documentation (3-4 hours)
```
Friday Afternoon

✓ Create README.md:
  - Project overview
  - Quick start (make setup, make dev)
  - Architecture overview (links to detailed docs)
  - Contributing guidelines
  - Tech stack summary

✓ Create ARCHITECTURE.md:
  - System architecture diagram
  - Component responsibilities
  - Data flow diagrams
  - Technology stack with rationales

✓ Create DEVELOPMENT.md:
  - Local setup instructions
  - Makefile targets
  - How to run tests
  - How to run linters
  - How to run migrations
  - Common issues & troubleshooting

✓ Create API_DOCS.md:
  - Link to auto-generated OpenAPI
  - How to access: http://localhost:8000/docs
  - Example requests/responses
  - Auth header format

✓ Create DEPLOYMENT.md:
  - How to deploy to dev/staging/prod
  - Terraform commands
  - Database backup/restore
  - Monitoring & logging

Deliverable: Complete PHASE 0 documentation
Test: Can new developer clone repo and follow README
Commit: "Phase 0: Complete documentation"
```

---

## PHASE 0 Acceptance Criteria

### ✅ Repository & Structure
- [ ] GitHub repository created and accessible
- [ ] Correct project structure (backend/, frontend/, mobile/, infrastructure/)
- [ ] All files in .gitignore (no secrets, node_modules, __pycache__, .venv)
- [ ] README.md with clear setup instructions
- [ ] DEVELOPMENT.md with detailed dev guide

### ✅ Docker & Local Development
- [ ] `make setup` completes successfully
- [ ] `make dev` brings up all services (postgres, redis, api, web, mobile)
- [ ] All services healthy: `docker-compose ps`
- [ ] Can connect to PostgreSQL: `psql -h localhost -U dev -d ai_platform`
- [ ] Can connect to Redis: `redis-cli -h localhost`
- [ ] API responds: `curl http://localhost:8000/health`
- [ ] Web loads: `http://localhost:3000`
- [ ] Mobile runs: Expo Go shows login screen

### ✅ Database
- [ ] PostgreSQL running and accessible
- [ ] Alembic migrations applied: `make migrate`
- [ ] Tables created: organization, user, apikey
- [ ] No migration errors
- [ ] Migration rollback works: `alembic downgrade -1`

### ✅ Backend API
- [ ] FastAPI app starts without errors
- [ ] Health check works: `GET /health/live` → 200 OK
- [ ] Authentication works:
  - [ ] `POST /auth/signup` creates org + user
  - [ ] `POST /auth/login` returns JWT tokens
  - [ ] `POST /auth/refresh` refreshes access token
- [ ] JWT validation: unauthorized requests rejected
- [ ] Tenant isolation: User A can't access User B's org
- [ ] Swagger/OpenAPI available: `http://localhost:8000/docs`

### ✅ Frontend (Web)
- [ ] Next.js app starts: `npm run dev`
- [ ] Pages load without console errors
- [ ] Login page renders (email, password inputs)
- [ ] Signup page renders (email, password, org_name inputs)
- [ ] Can submit signup form (creates account via API)
- [ ] Can submit login form (receives JWT)
- [ ] Dashboard loads when authenticated
- [ ] Admin panel accessible (shell)
- [ ] Tailwind CSS working (styling applied)
- [ ] TypeScript compiles without errors

### ✅ Mobile (React Native)
- [ ] Expo project initialized
- [ ] `npm start` works, Expo Go connects
- [ ] iOS simulator shows login screen (if on Mac)
- [ ] Android emulator shows login screen (if on Linux/Windows)
- [ ] Can navigate between screens
- [ ] Can submit login form (calls API)
- [ ] Styling applied (not just default white)
- [ ] No console errors or warnings

### ✅ Shared Code
- [ ] Shared library compiles: `npm run build:shared`
- [ ] Both web and mobile use useAuth from shared code
- [ ] Changes to shared code reflected in both apps
- [ ] TypeScript strict mode enabled
- [ ] No `any` types in shared code

### ✅ Authentication
- [ ] User signup creates organization
- [ ] Organization created with correct name
- [ ] User created with correct role
- [ ] Password hashed (not stored in plaintext)
- [ ] JWT tokens generated correctly
- [ ] Refresh token extends session
- [ ] Invalid credentials rejected
- [ ] Token expiry handled gracefully

### ✅ Multi-Tenancy
- [ ] User A's organization_id attached to JWT
- [ ] All queries filtered by organization_id
- [ ] User A cannot query User B's organization data
- [ ] Error 403 (Forbidden) returned for tenant violations
- [ ] Audit log captures isolation breach attempts

### ✅ LLM Abstraction
- [ ] LLM provider abstraction created
- [ ] Mock provider works (for testing without API keys)
- [ ] OpenAI provider class created (can be activated with API key)
- [ ] Anthropic provider class created (can be activated with API key)
- [ ] Google provider class created (can be activated with API key)
- [ ] Local/self-hosted provider class created (OpenAI-compatible)
- [ ] Provider can be switched via environment variable
- [ ] Token counting works for each provider
- [ ] Config loads from environment variables

### ✅ Admin Platform
- [ ] Admin dashboard accessible at `/dashboard/admin`
- [ ] Admin can view all organizations (list)
- [ ] Admin can view all users (list)
- [ ] System health endpoint shows service status
- [ ] Feature flags page displays available flags
- [ ] Admin-only access enforced (non-admins redirected)

### ✅ Testing
- [ ] Backend tests pass: `pytest` (100% pass)
- [ ] Frontend tests pass: `npm run test` (or vitest)
- [ ] Coverage > 80%: `pytest --cov`
- [ ] All tests are isolated (don't depend on execution order)
- [ ] Test fixtures provide fresh database per test
- [ ] No flaky tests (run 5 times, all pass)

### ✅ Code Quality
- [ ] Linting passes: `ruff check app tests`
- [ ] Formatting correct: `black --check app tests`
- [ ] Type checking passes: `pyright app tests`
- [ ] Frontend linting passes: `eslint app lib`
- [ ] Frontend formatting: `prettier --check app lib`
- [ ] No console warnings or errors in apps
- [ ] No hardcoded credentials or secrets

### ✅ CI/CD
- [ ] GitHub Actions workflows created (.github/workflows/)
- [ ] test.yml runs on all pushes
- [ ] CI checks run: lint, type check, tests
- [ ] CI prevents merge if checks fail
- [ ] PR template exists and guides contributors
- [ ] Branch protection rules set up (if desired)

### ✅ Documentation
- [ ] README.md: Clear overview and quick start
- [ ] DEVELOPMENT.md: Detailed dev setup guide
- [ ] ARCHITECTURE.md: System design explanation
- [ ] API_DOCS.md: How to access OpenAPI docs
- [ ] DEPLOYMENT.md: How to deploy (future phases)
- [ ] Code comments: Non-obvious logic explained
- [ ] Type hints: All functions annotated

### ✅ Git History
- [ ] Clean commits with descriptive messages
- [ ] Each major feature has its own commit
- [ ] No "WIP" or "fix" commits in main
- [ ] All commits reference PHASE (e.g., "Phase 0: X")

---

## Daily Checklist Template

Use this each day to track progress:

```
Monday, Aug 22:
  - [x] Setup repository structure
  - [x] Create Docker Compose
  - [x] Initialize backend/frontend/mobile
  - [x] Test docker-compose up
  Commit: "Phase 0: Repository bootstrap"
  
Tuesday, Aug 23:
  - [x] Database schema (Organization, User)
  - [x] Alembic migrations
  - [x] Auth models & routes
  - [ ] Auth tests
  TODO: Complete auth tests

Wednesday, Aug 24:
  - [x] Tenant isolation middleware
  - [x] API base structure
  - [x] Frontend shell with auth
  - [x] Test tenant isolation
  Commit: "Phase 0: Multi-tenancy and API foundation"

Thursday, Aug 25:
  - [x] React Native setup
  - [x] Shared code library
  - [x] Mobile auth screens
  - [x] Test mobile app
  Commit: "Phase 0: React Native mobile setup"

Friday, Aug 26:
  - [x] Admin platform shell
  - [x] Testing infrastructure (pytest, vitest)
  - [x] LLM abstraction layer
  - [x] GitHub Actions CI/CD
  Commit: "Phase 0: Admin platform and CI/CD"

Saturday, Aug 27:
  - [x] Documentation (README, ARCHITECTURE, DEVELOPMENT)
  - [x] Final testing of all acceptance criteria
  - [x] Cleanup and code review
  Commit: "Phase 0: Complete - ready for Phase 1"
```

---

## Potential Blockers & Solutions

| Blocker | Impact | Solution |
|---------|--------|----------|
| Docker networking issues | Can't connect services | Use service names, debug with `docker network ls` |
| PostgreSQL migration errors | Can't start app | Roll back migration, debug SQL, test in psql first |
| React Native Metro issues | Mobile won't start | Clear cache: `expo start --clear`, restart Expo Go |
| JWT token issues | Can't authenticate | Check secret key, verify exp claims, test with jwt.io |
| CORS errors | Frontend can't call API | Add CORS middleware in FastAPI |
| Expo Go not connecting | Mobile can't develop | Ensure both on same network, check firewall |

---

## Tools & Resources Needed

**Before starting PHASE 0:**
```
✓ Git installed
✓ Docker & Docker Compose installed
✓ Python 3.11+ installed
✓ Node.js 18+ installed
✓ PostgreSQL client tools (psql)
✓ Redis CLI (redis-cli)
✓ GitHub account & repository created
✓ Code editor (VS Code recommended)
✓ iOS simulator (Xcode) OR Android emulator
✓ Expo Go app on phone/emulator
```

**Helpful VS Code extensions:**
```
- Python
- Pylance
- Black Formatter
- Ruff
- TypeScript Vue Plugin (Volar)
- ESLint
- Prettier
- SQLTools
- Thunder Client (or Postman)
- Docker
- Git Graph
```

---

## Success Metrics

By end of PHASE 0, you should be able to:

1. **Clone the repo** on a fresh machine
2. **Run `make setup`** and have everything installed
3. **Run `make dev`** and have all services up and healthy
4. **Sign up** a new organization via web or mobile
5. **Log in** and reach the dashboard
6. **Access admin panel** and see system health
7. **Run tests** and see 100% pass
8. **Run linters** and see 0 errors
9. **Push to GitHub** and see CI pass
10. **Feel confident** that architecture is solid for PHASE 1+

---

## Time Tracking Template

Track actual hours to calibrate estimates:

```
Repository & Docker:     Estimated 4h  →  Actual: __ h
Database & Migrations:   Estimated 4h  →  Actual: __ h
Auth System:            Estimated 5h  →  Actual: __ h
Tenant Isolation:       Estimated 6h  →  Actual: __ h
Frontend Shell:         Estimated 4h  →  Actual: __ h
React Native:           Estimated 5h  →  Actual: __ h
Testing & Admin:        Estimated 5h  →  Actual: __ h
LLM Abstraction:        Estimated 6h  →  Actual: __ h
CI/CD:                  Estimated 5h  →  Actual: __ h
Documentation:          Estimated 3h  →  Actual: __ h
─────────────────────────────────────────────────
Total Estimated:       47h
Total Actual:          __ h
```

---

**Ready to start? Begin with Day 1 and track progress daily. Adjust timeline based on actual time spent.**

