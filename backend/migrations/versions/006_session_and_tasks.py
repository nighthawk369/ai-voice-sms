"""Add Session, Task, and CustomField models

Revision ID: 006
Revises: 005
Create Date: 2026-08-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Session table for tracking user sessions
    op.create_table(
        'session',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_session', 'session', ['organization_id', 'user_id'], unique=False)
    op.create_index('idx_session_expires', 'session', ['expires_at'], unique=False)

    # Task table for tasks/to-dos
    op.create_table(
        'task',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='PENDING'),
        sa.Column('priority', sa.String(50), nullable=False, server_default='MEDIUM'),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.ForeignKeyConstraint(['contact_id'], ['contact.id']),
        sa.ForeignKeyConstraint(['assigned_to'], ['user.id']),
        sa.ForeignKeyConstraint(['created_by'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_task_status', 'task', ['organization_id', 'status'], unique=False)
    op.create_index('idx_task_due_date', 'task', ['due_date'], unique=False)

    # CustomField table for extensible fields
    op.create_table(
        'custom_field',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('object_type', sa.String(50), nullable=False),
        sa.Column('field_name', sa.String(255), nullable=False),
        sa.Column('field_label', sa.String(255), nullable=False),
        sa.Column('field_type', sa.String(50), nullable=False),
        sa.Column('field_options', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_custom_field', 'custom_field', ['organization_id', 'object_type'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_org_custom_field', table_name='custom_field')
    op.drop_table('custom_field')
    op.drop_index('idx_task_due_date', table_name='task')
    op.drop_index('idx_org_task_status', table_name='task')
    op.drop_table('task')
    op.drop_index('idx_session_expires', table_name='session')
    op.drop_index('idx_org_session', table_name='session')
    op.drop_table('session')
