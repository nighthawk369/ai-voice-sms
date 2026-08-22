"""Add conversation and messaging models for voice/SMS/chat

Revision ID: 003
Revises: 002
Create Date: 2024-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create Conversation table
    op.create_table(
        'conversation',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('conversation_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='ACTIVE'),
        sa.Column('phone_number', sa.String(20), nullable=True),
        sa.Column('twilio_call_sid', sa.String(255), nullable=True, unique=True),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('intent', sa.String(100), nullable=True),
        sa.Column('sentiment', sa.String(50), nullable=True),
        sa.Column('llm_provider', sa.String(50), nullable=False, server_default='openai'),
        sa.Column('tokens_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cost', sa.Numeric(precision=8, scale=4), nullable=False, server_default='0'),
        sa.Column('transfer_to', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.ForeignKeyConstraint(['contact_id'], ['contact.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_conversation_status', 'conversation', ['organization_id', 'status'])
    op.create_index('idx_twilio_call_sid', 'conversation', ['twilio_call_sid'])

    # Create Message table
    op.create_table(
        'message',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversation_messages', 'message', ['conversation_id'])


def downgrade() -> None:
    op.drop_index('idx_conversation_messages', table_name='message')
    op.drop_table('message')
    op.drop_index('idx_twilio_call_sid', table_name='conversation')
    op.drop_index('idx_org_conversation_status', table_name='conversation')
    op.drop_table('conversation')
