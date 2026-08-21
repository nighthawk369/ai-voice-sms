# AI Platform - Voice & SMS for Field Service Businesses

An enterprise-grade, open-source AI voice and SMS platform for field service businesses (HVAC, plumbing, electrical). Built with FastAPI, PostgreSQL, React, React Native, and support for multiple LLM providers.

## 🎯 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- Expo Go app (for mobile testing)

### Setup (5 minutes)

```bash
# Clone and navigate
git clone <repo-url>
cd ai-platform

# Copy environment file
cp .env.example .env

# Start all services
make setup
make dev

# Services will be available at:
# - API: http://localhost:8000
# - Web: http://localhost:3000
# - API Docs: http://localhost:8000/docs
```

### First Test Call

1. Visit http://localhost:3000
2. Sign up with test account
3. API will respond to requests

## 📁 Project Structure

```
ai-platform/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI app
│   │   ├── routes.py    # API routes
│   │   ├── models.py    # Database models
│   │   ├── schemas.py   # Pydantic schemas
│   │   └── security.py  # Auth & JWT
│   ├── migrations/       # Alembic migrations
│   ├── tests/           # Pytest tests
│   └── requirements.txt # Python dependencies
├── frontend/             # Next.js web app
│   ├── app/             # Next.js pages & components
│   ├── lib/             # Utilities & hooks
│   └── package.json     # Node dependencies
├── mobile/              # React Native app (Expo)
│   ├── app/             # Native screens
│   ├── lib/             # Shared logic
│   └── package.json
├── docker-compose.yml   # Local dev services
├── Makefile            # Development commands
└── .env.example        # Environment template
```

## 🚀 Key Commands

```bash
# Development
make dev              # Start all services
make down             # Stop services
make reset            # Fresh reset (wipe database)

# Testing
make test             # Run all tests
make test-backend     # Backend tests only
make test-frontend    # Frontend tests only

# Code Quality
make lint             # Lint code
make format           # Format code
make type-check       # Type checking

# Database
make migrate          # Run migrations
make migrate-down     # Rollback migration
make seed             # Seed demo data

# Utilities
make logs             # Follow Docker logs
make psql             # Connect to PostgreSQL
make shell-api        # Python shell in API
```

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Next.js + React + TypeScript + Tailwind CSS
- **Mobile**: React Native + Expo + TypeScript
- **Cache**: Redis
- **Database**: PostgreSQL with Pgvector (for embeddings)
- **Storage**: MinIO (S3-compatible)
- **LLM**: Multi-provider abstraction (OpenAI, Claude, Gemini, vLLM/Ollama)
- **Voice/SMS**: Twilio integration
- **CI/CD**: GitHub Actions
- **Infrastructure**: Docker + Terraform + AWS

### System Architecture

```
Customer (Phone/SMS/Web)
    ↓
Communication Gateway (Twilio)
    ↓
AI Orchestrator (State machine, Intent detection)
    ↓
LLM Gateway (OpenAI, Claude, Gemini, vLLM)
    ↓
Tool Gateway (CRM ops, Calendar, SMS, Knowledge)
    ↓
Integration Engine (ServiceTitan, Jobber, HubSpot, etc)
    ↓
Data Layer (PostgreSQL, Redis, S3)
```

## 🔐 Multi-Tenancy & Security

- ✅ Complete tenant isolation at database layer
- ✅ JWT authentication with refresh tokens
- ✅ Role-based access control (OWNER, ADMIN, MANAGER, AGENT, VIEWER)
- ✅ Audit logging for all actions
- ✅ Encrypted credential storage
- ✅ Input validation and sanitization
- ✅ CORS protection

## 🤖 LLM Providers

Supports multiple LLM providers out of the box:
- **OpenAI**: GPT-4o, GPT-4 Turbo
- **Anthropic**: Claude 3.5 Sonnet
- **Google**: Gemini 2.0 Flash
- **Local**: vLLM/Ollama (for private inference)

Switch providers via environment variable: `LLM_PROVIDER=openai|anthropic|google|local`

## 📊 Features (Phase 0 Complete)

### Authentication
- ✅ User signup with organization creation
- ✅ Email/password login
- ✅ JWT tokens (access + refresh)
- ✅ Multi-tenancy enforcement

### API
- ✅ REST API with OpenAPI documentation
- ✅ Health checks (liveness + readiness)
- ✅ Tenant isolation at request layer
- ✅ Error handling with request IDs

### Frontend
- ✅ Login/Signup pages
- ✅ Dashboard shell
- ✅ Settings page
- ✅ Admin panel shell
- ✅ Responsive design with Tailwind CSS

### Mobile
- ✅ React Native app with Expo
- ✅ Login/Signup screens
- ✅ Dashboard
- ✅ iOS and Android support

### Database
- ✅ PostgreSQL with async SQLAlchemy
- ✅ Alembic migrations
- ✅ Tenant-aware models
- ✅ Indexes for performance

### Testing
- ✅ Pytest for backend
- ✅ Fixtures for common test scenarios
- ✅ Database isolation per test
- ✅ Vitest for frontend (ready to use)

## 🔄 Development Workflow

1. **Create feature branch**: `git checkout -b feature/my-feature`
2. **Make changes**: Edit code
3. **Run tests**: `make test`
4. **Format code**: `make format`
5. **Type check**: `make type-check`
6. **Commit**: `git commit -am "feat: add my feature"`
7. **Push**: `git push origin feature/my-feature`
8. **Create PR**: On GitHub

## 📚 Documentation

- [ARCHITECTURE.md](./MASTER_SPECIFICATION.md) - Complete architecture & design decisions
- [DEVELOPMENT.md](./MASTER_SPECIFICATION.md) - Development guide & detailed setup
- [PHASE_0_DEEP_DIVE.md](./PHASE_0_DEEP_DIVE.md) - Week-by-week PHASE 0 breakdown
- [RISK_AND_TIMELINE.md](./RISK_AND_TIMELINE.md) - Timeline projections & risk analysis
- [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI

## 🚦 Status

### PHASE 0: Repository Bootstrap ✅ IN PROGRESS
- [x] Git repository initialized
- [x] Project structure created
- [x] Docker Compose for local development
- [x] Database schema and migrations
- [x] Authentication system (JWT)
- [x] Multi-tenancy middleware
- [x] API base structure
- [x] Frontend shell
- [x] Mobile shell
- [ ] Tests written and passing
- [ ] All linting/formatting passing
- [ ] Documentation complete
- [ ] Ready for PHASE 1

### Roadmap
- **PHASE 1-7**: Core infrastructure (8-10 weeks)
- **PHASE 8-12**: AI orchestrator + voice (8-10 weeks)
- **PHASE 13-21**: Integrations + analytics + billing (12-15 weeks)
- **PHASE 22-28**: Security + observability + deployment (12-15 weeks)

**Total MVP Timeline**: ~18 months (product-driven, quality-focused)

## 🤝 Contributing

This is an open-source project. We welcome contributions!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass and code is formatted
5. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 📧 Contact & Support

- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Email**: noreply@example.com

---

**Built with ❤️ for field service businesses**

Start with PHASE 0, read [MASTER_SPECIFICATION.md](./MASTER_SPECIFICATION.md) for complete details, and join us in building the future of AI-powered field service!
