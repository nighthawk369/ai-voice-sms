"""Add KnowledgeBaseItem model for knowledge base/documentation

Revision ID: 007
Revises: 006
Create Date: 2026-08-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # KnowledgeBaseItem table
    op.create_table(
        'knowledge_base_item',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('tags', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.ForeignKeyConstraint(['created_by'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_kb_published', 'knowledge_base_item', ['organization_id', 'is_published'], unique=False)
    op.create_index('idx_kb_category', 'knowledge_base_item', ['category'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_kb_category', table_name='knowledge_base_item')
    op.drop_index('idx_org_kb_published', table_name='knowledge_base_item')
    op.drop_table('knowledge_base_item')
