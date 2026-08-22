# PHASES 1-2 Implementation Guide: Database Schema & Authentication

This guide covers the implementation of PHASES 1-2 of the platform: comprehensive database schema with multi-tenancy and authentication with RBAC.

## Overview

### PHASE 1: Database Schema
Comprehensive PostgreSQL schema including:
- Multi-tenancy support with Organizations
- User management with role-based access control
- In-house CRM models (Contacts, Companies, Deals, Activities, Pipelines, Tasks)
- Custom fields for extensibility
- Conversations and messaging
- Knowledge base
- Integrations and workflows
- Pgvector support for embeddings

### PHASE 2: Authentication & Multi-tenancy
- JWT-based authentication (access + refresh tokens)
- Role-based access control (RBAC) with 5 roles
- Tenant isolation middleware and enforcement
- API key management
- Session tracking
- Comprehensive test coverage

## Quick Start

### 1. Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your database credentials
```

### 2. Database Setup

```bash
# Create database
createdb ai_platform_dev

# Export database URL
export DATABASE_URL="postgresql://user:password@localhost:5432/ai_platform_dev"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="your-secret-key-change-in-production"

# Run Alembic migrations
alembic upgrade head

# Or using poetry
poetry run alembic upgrade head
```

### 3. Seed Database (Optional)

```bash
# Populate demo data
python scripts/seed_database.py

# Demo credentials:
# Email: owner@example.com | Password: demo1234 (Owner)
# Email: admin@example.com | Password: demo1234 (Admin)
# Email: manager@example.com | Password: demo1234 (Manager)
# Email: agent@example.com | Password: demo1234 (Agent)
```

### 4. Run Application

```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# With poetry
poetry run uvicorn app.main:app --reload
```

### 5. Run Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_auth_comprehensive.py

# With coverage
pytest tests/ --cov=app --cov-report=html

# Watch mode
pytest-watch tests/
```

## Database Schema

### Core Models

#### Organization
- `id`: UUID (primary key)
- `name`: String
- `timezone`, `locale`: Configuration
- `subscription_plan`, `subscription_status`: Billing info
- `max_users`, `max_contacts`, `max_calls_per_month`: Limits
- Relationships: Users, Contacts, Companies, Deals, Activities, Conversations, etc.

#### User
- `id`: UUID (primary key)
- `organization_id`: UUID (foreign key - multi-tenant)
- `email`: String (unique per org)
- `password_hash`: String (bcrypt)
- `role`: String (OWNER, ADMIN, MANAGER, AGENT, VIEWER)
- `is_active`, `is_verified`: Boolean
- `last_login_at`: DateTime

#### Session
- Tracks user sessions for security
- `token_hash`: Hash of JWT token
- `expires_at`: Token expiration
- `ip_address`, `user_agent`: Security tracking

#### APIKey
- For external integrations
- `key_hash`: Hash of API key (never store plain key)
- `scopes`: JSON list of permissions
- `expires_at`: Optional expiration

### CRM Models

#### Contact
- Customer/Lead contact
- `phone`, `email`: Primary identifiers
- `contact_type`: LEAD, PROSPECT, CUSTOMER, INACTIVE
- `status`: NEW, QUALIFIED, UNQUALIFIED, CONVERTED
- `assigned_to`: User ID
- `custom_fields`: JSON for extensibility
- `last_contact_date`, `next_follow_up`: Follow-up tracking

#### Company
- Account/Company information
- `name`, `industry`, `website`
- `annual_revenue`, `employee_count`
- `company_status`: PROSPECT, CUSTOMER, INACTIVE
- Relationships: Multiple contacts, deals

#### Pipeline
- Sales pipeline configuration
- `stages`: JSON array of stage definitions
- `is_default`: Default pipeline for org

#### Deal
- Sales opportunity
- `amount`, `probability`: Deal metrics
- `stage`, `deal_status`: OPEN, WON, LOST
- `expected_close_date`, `closed_date`: Timeline

#### Activity
- Call, email, meeting, note logging
- `activity_type`: CALL, EMAIL, MEETING, NOTE, TASK
- `duration_seconds`, `metadata`: Recording URL, transcript, etc.
- `scheduled_for`, `completed_at`: Timeline

#### Task
- Task/To-do items
- `status`: PENDING, IN_PROGRESS, COMPLETED, CANCELLED
- `priority`: LOW, MEDIUM, HIGH, URGENT
- `due_date`, `completed_at`: Timeline
- `assigned_to`: User responsible

#### CustomField
- Dynamic field definitions
- `object_type`: CONTACT, COMPANY, DEAL
- `field_type`: TEXT, NUMBER, DROPDOWN, DATE, CHECKBOX
- `field_options`: For dropdowns

### Conversation Models

#### Conversation
- Voice/SMS/Chat conversation with AI
- `conversation_type`: VOICE, SMS, CHAT
- `status`: ACTIVE, ENDED, ESCALATED
- `transcript`, `summary`: Content
- `intent`, `sentiment`: Analysis
- `tokens_used`, `cost`: Usage tracking
- Relationships: Multiple messages

#### Message
- Individual message in conversation
- `role`: user, assistant, system
- `content`: Message text
- `metadata`: Additional data

### Knowledge Base

#### KnowledgeBaseItem
- Help articles/documentation
- `title`, `content`: Documentation
- `category`, `tags`: Organization
- `is_published`: Control visibility
- `order`: Display order

## Authentication Flow

### Signup
```bash
POST /api/v1/auth/signup
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "org_name": "My Organization"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "OWNER",
    "is_active": true
  }
}
```

### Login
```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response: Same as signup
```

### Refresh Token
```bash
POST /api/v1/auth/refresh
{
  "refresh_token": "eyJ..."
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Making Authenticated Requests
```bash
GET /api/v1/users/me
Authorization: Bearer eyJ...
```

## Role-Based Access Control

### Role Hierarchy
1. **OWNER**: Full access, can manage organization
2. **ADMIN**: Administrative access, manage users and settings
3. **MANAGER**: Can manage team and see analytics
4. **AGENT**: Can access assigned contacts/deals
5. **VIEWER**: Read-only access

### Permission Examples
- Creating API keys: OWNER, ADMIN only
- Creating users: OWNER, ADMIN only
- Updating user roles: OWNER only
- Creating contacts: OWNER, ADMIN, MANAGER, AGENT
- Viewing organization: All authenticated users

## Multi-Tenancy & Tenant Isolation

### Tenant Isolation Middleware
All requests (except auth endpoints) are validated for tenant isolation:
1. Extract organization ID from JWT token
2. Verify user belongs to organization
3. Ensure data access is scoped to organization

### Database Queries
All CRM queries include org_id filter:
```python
# Example: List contacts
select(Contact).where(
    and_(
        Contact.organization_id == org_id,
        # other filters...
    )
)
```

### Data Isolation
- Users from Org A cannot see/access Org B data
- API keys are org-specific
- Custom fields are org-specific
- Knowledge base is org-specific

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Create account
- `POST /api/v1/auth/login` - Authenticate
- `POST /api/v1/auth/refresh` - Refresh token

### Users
- `GET /api/v1/users/me` - Current user
- `GET /api/v1/users` - List organization users
- `POST /api/v1/users` - Create user (admin only)
- `PUT /api/v1/users/{user_id}/role` - Update role
- `PUT /api/v1/users/{user_id}/deactivate` - Deactivate

### CRM - Contacts
- `POST /api/v1/contacts` - Create contact
- `GET /api/v1/contacts` - List contacts
- `GET /api/v1/contacts/{id}` - Get contact
- `PUT /api/v1/contacts/{id}` - Update contact
- `DELETE /api/v1/contacts/{id}` - Delete contact

### CRM - Companies
- `POST /api/v1/companies` - Create company
- `GET /api/v1/companies` - List companies
- `GET /api/v1/companies/{id}` - Get company

### CRM - Deals
- `POST /api/v1/deals` - Create deal
- `GET /api/v1/deals` - List deals
- `GET /api/v1/deals/{id}` - Get deal

### CRM - Activities
- `POST /api/v1/activities` - Create activity
- `GET /api/v1/contacts/{contact_id}/activities` - List contact activities

### Tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/contacts/{contact_id}/tasks` - List contact tasks

### Conversations
- `POST /api/v1/conversations` - Create conversation
- `GET /api/v1/conversations/{id}` - Get conversation
- `POST /api/v1/conversations/{id}/messages` - Add message

### API Keys
- `POST /api/v1/api-keys` - Create API key (returns key once!)
- `GET /api/v1/api-keys` - List API keys
- `DELETE /api/v1/api-keys/{id}` - Delete API key

### Custom Fields
- `POST /api/v1/custom-fields` - Create custom field
- `GET /api/v1/custom-fields` - List custom fields

### Knowledge Base
- `POST /api/v1/knowledge-base` - Create KB item
- `GET /api/v1/knowledge-base` - List KB items

## Migrations

### Running Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade 007

# Downgrade one version
alembic downgrade -1

# View migration history
alembic history

# Create new migration
alembic revision --autogenerate -m "description"
```

### Migration Files
Located in `migrations/versions/`:
- `001_initial_schema.py` - Core tables (Organization, User, APIKey, Contact, Company, Deal, Activity, etc.)
- `002_crm_models.py` - Additional CRM tables
- `003_conversation_models.py` - Conversation and Message tables
- `004_integrations_and_workflows.py` - Integration and Workflow tables
- `005_subscription_fields.py` - Subscription-related fields
- `006_session_and_tasks.py` - Session tracking and Task tables
- `007_knowledge_base.py` - Knowledge base tables

## Testing

### Test Files
- `test_auth_comprehensive.py` - Authentication and authorization tests
- `test_tenant_isolation_comprehensive.py` - Multi-tenancy tests
- `test_database.py` - Database operations
- `test_models.py` - ORM model tests
- `test_api.py` - API endpoint tests

### Running Tests
```bash
# All tests
pytest

# Specific file
pytest tests/test_auth_comprehensive.py

# Specific test
pytest tests/test_auth_comprehensive.py::test_signup_creates_organization_and_user

# With coverage
pytest --cov=app --cov-report=html

# Watch mode
pytest-watch
```

### Test Coverage
- ✓ User signup and login
- ✓ Token refresh and expiration
- ✓ Role-based permissions
- ✓ Tenant isolation between organizations
- ✓ Contact/Company/Deal CRUD
- ✓ Activity logging
- ✓ API key management
- ✓ Custom fields
- ✓ Knowledge base
- ✓ Middleware and security

## Security Best Practices

### API Keys
- Keys are hashed before storage (never store plain keys)
- Return key value only once during creation
- Can set expiration dates
- Can revoke anytime
- Include scopes for fine-grained permissions

### JWT Tokens
- Access tokens expire (default: 60 minutes)
- Refresh tokens expire (default: 30 days)
- Both include organization ID for multi-tenancy
- Token type field validates access vs refresh

### Passwords
- Hashed with bcrypt
- Minimum 8 characters required
- Verified during login

### Tenant Isolation
- Middleware validates org ID on every request
- All queries include org_id filter
- Cannot access another org's data even with valid token

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
psql -U postgres -h localhost -d ai_platform_dev -c "SELECT 1"

# Check DATABASE_URL
echo $DATABASE_URL
```

### Migration Issues
```bash
# Check migration history
alembic history

# Current version
alembic current

# View SQL migration
alembic show <revision>
```

### Test Failures
```bash
# Run with verbose output
pytest -v

# Show print statements
pytest -s

# Run single test
pytest tests/test_auth_comprehensive.py::test_signup
```

### API Errors
- Check token in Authorization header: `Bearer <token>`
- Verify token hasn't expired
- Confirm user belongs to organization
- Check organization_id matches in database

## Performance Considerations

### Indexes
Key indexes created for performance:
- `idx_org_user_email`: Unique email per organization
- `idx_org_contact_phone`: Contact lookup by phone
- `idx_org_deal_status`: Deal filtering
- `idx_contact_activity`: Activity lookup
- `idx_org_conversation_status`: Conversation filtering

### Pagination
All list endpoints support pagination:
```bash
GET /api/v1/contacts?skip=0&limit=100
```

### Connection Pooling
Async SQLAlchemy with asyncpg for connection pooling

## Next Steps

### PHASE 3 (Recommended)
- Voice call integration (Twilio)
- SMS integration
- LLM provider integration (OpenAI, Claude, Gemini)
- Real-time conversation streaming

### PHASE 4
- Advanced analytics and reporting
- Workflow automation triggers
- Third-party CRM integrations (Salesforce, HubSpot, ServiceTitan)
- Email integration

## Support

For issues or questions:
1. Check this guide and troubleshooting section
2. Review test files for usage examples
3. Check API documentation at `/docs` (Swagger UI)
4. Check logs for error details

## Environment Variables

```bash
# Application
APP_NAME=AI Platform
ENVIRONMENT=development
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_platform_dev
DATABASE_ECHO=false

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# LLM Providers
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# External Services
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
STRIPE_API_KEY=...
SENDGRID_API_KEY=...
```

## Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com
- SQLAlchemy Documentation: https://docs.sqlalchemy.org
- Alembic Migration Guide: https://alembic.sqlalchemy.org
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- JWT Guide: https://tools.ietf.org/html/rfc7519
