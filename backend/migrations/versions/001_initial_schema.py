"""Complete schema with CRM, Voice, Integrations, Workflows

Revision ID: 001
Revises:
Create Date: 2026-08-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Organization table
    op.create_table(
        'organization',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='America/New_York'),
        sa.Column('locale', sa.String(10), nullable=False, server_default='en_US'),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('subscription_plan', sa.String(50), server_default='BASIC'),
        sa.Column('subscription_status', sa.String(50), server_default='ACTIVE'),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_users', sa.Integer(), server_default='10'),
        sa.Column('max_contacts', sa.Integer(), server_default='10000'),
        sa.Column('max_calls_per_month', sa.Integer(), server_default='1000'),
        sa.Column('billing_email', sa.String(255), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # User table
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('role', sa.String(50), nullable=False, server_default='AGENT'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', 'organization_id', name='idx_org_user_email')
    )
    op.create_index('idx_user_is_active', 'user', ['is_active'], unique=False)

    # Create APIKey table
    op.create_table(
        'api_key',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('scopes', postgresql.JSON(), nullable=False, server_default='["read", "write"]'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_api_key', 'api_key', ['organization_id', 'is_active'], unique=False)

    # Company table
    op.create_table(
        'company',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(50), nullable=True),
        sa.Column('zip_code', sa.String(10), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('employee_count', sa.Integer(), nullable=True),
        sa.Column('annual_revenue', sa.Numeric(12, 2), nullable=True),
        sa.Column('company_status', sa.String(50), server_default='PROSPECT'),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_fields', postgresql.JSON(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.ForeignKeyConstraint(['assigned_to'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_company_name', 'company', ['organization_id', 'name'])
    op.create_index('idx_company_status', 'company', ['company_status'])

    # Contact table
    op.create_table(
        'contact',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('secondary_phone', sa.String(20), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(50), nullable=True),
        sa.Column('zip_code', sa.String(10), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('contact_type', sa.String(50), server_default='LEAD'),
        sa.Column('status', sa.String(50), server_default='NEW'),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_fields', postgresql.JSON(), server_default='{}'),
        sa.Column('last_contact_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_follow_up', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.ForeignKeyConstraint(['company_id'], ['company.id']),
        sa.ForeignKeyConstraint(['assigned_to'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_contact_phone', 'contact', ['organization_id', 'phone'])
    op.create_index('idx_org_contact_type', 'contact', ['organization_id', 'contact_type'])
    op.create_index('idx_contact_status', 'contact', ['status'])

    # Pipeline table
    op.create_table(
        'pipeline',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('stages', postgresql.JSON(), server_default='[]'),
        sa.Column('is_default', sa.Boolean(), server_default=False),
        sa.Column('is_active', sa.Boolean(), server_default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Deal table
    op.create_table(
        'deal',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('pipeline_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('stage', sa.String(100), nullable=False),
        sa.Column('deal_status', sa.String(50), server_default='OPEN'),
        sa.Column('probability', sa.Float(), server_default='50.0'),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('expected_close_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_fields', postgresql.JSON(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.ForeignKeyConstraint(['contact_id'], ['contact.id']),
        sa.ForeignKeyConstraint(['company_id'], ['company.id']),
        sa.ForeignKeyConstraint(['pipeline_id'], ['pipeline.id']),
        sa.ForeignKeyConstraint(['assigned_to'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_deal_status', 'deal', ['organization_id', 'deal_status'])
    op.create_index('idx_deal_stage', 'deal', ['stage'])

    # Activity table
    op.create_table(
        'activity',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deal_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('activity_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSON(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.ForeignKeyConstraint(['contact_id'], ['contact.id']),
        sa.ForeignKeyConstraint(['deal_id'], ['deal.id']),
        sa.ForeignKeyConstraint(['created_by'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_activity_type', 'activity', ['organization_id', 'activity_type'])
    op.create_index('idx_contact_activity', 'activity', ['contact_id', 'activity_type'])

    # Conversation table
    op.create_table(
        'conversation',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('conversation_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), server_default='ACTIVE'),
        sa.Column('phone_number', sa.String(20), nullable=True),
        sa.Column('twilio_call_sid', sa.String(255), unique=True, nullable=True),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('intent', sa.String(100), nullable=True),
        sa.Column('sentiment', sa.String(50), nullable=True),
        sa.Column('llm_provider', sa.String(50), server_default='openai'),
        sa.Column('tokens_used', sa.Integer(), server_default='0'),
        sa.Column('cost', sa.Numeric(8, 4), server_default='0'),
        sa.Column('transfer_to', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.ForeignKeyConstraint(['contact_id'], ['contact.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_conversation_status', 'conversation', ['organization_id', 'status'])
    op.create_index('idx_twilio_call_sid', 'conversation', ['twilio_call_sid'])

    # Message table
    op.create_table(
        'message',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSON(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Integration table
    op.create_table(
        'integration',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('integration_type', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('config', postgresql.JSON(), server_default='{}'),
        sa.Column('sync_status', sa.String(50), server_default='IDLE'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_sync_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_integration_type', 'integration', ['organization_id', 'integration_type'])

    # Workflow table
    op.create_table(
        'workflow',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('trigger_type', sa.String(100), nullable=False),
        sa.Column('trigger_config', postgresql.JSON(), server_default='{}'),
        sa.Column('actions', postgresql.JSON(), server_default='[]'),
        sa.Column('is_active', sa.Boolean(), server_default=True),
        sa.Column('execution_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('workflow')
    op.drop_table('integration')
    op.drop_table('message')
    op.drop_table('conversation')
    op.drop_table('activity')
    op.drop_table('deal')
    op.drop_table('pipeline')
    op.drop_table('contact')
    op.drop_table('company')
    op.drop_index('idx_org_api_key', table_name='api_key')
    op.drop_table('api_key')
    op.drop_index('idx_user_is_active', table_name='user')
    op.drop_table('user')
    op.drop_table('organization')
