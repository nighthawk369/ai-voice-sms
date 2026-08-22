"""Add subscription and billing fields to organization

Revision ID: 005
Revises: 004
Create Date: 2024-01-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to organization
    op.add_column('organization', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('organization', sa.Column('website', sa.String(255), nullable=True))
    op.add_column('organization', sa.Column('industry', sa.String(100), nullable=True))
    op.add_column('organization', sa.Column('subscription_plan', sa.String(50), nullable=False, server_default='BASIC'))
    op.add_column('organization', sa.Column('subscription_status', sa.String(50), nullable=False, server_default='ACTIVE'))
    op.add_column('organization', sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('organization', sa.Column('max_users', sa.Integer(), nullable=False, server_default='10'))
    op.add_column('organization', sa.Column('max_contacts', sa.Integer(), nullable=False, server_default='10000'))
    op.add_column('organization', sa.Column('max_calls_per_month', sa.Integer(), nullable=False, server_default='1000'))
    op.add_column('organization', sa.Column('billing_email', sa.String(255), nullable=True))

    # Add new columns to user
    op.add_column('user', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('user', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('user', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))

    # Create index for subscription status
    op.create_index('idx_org_subscription_status', 'organization', ['subscription_status'])


def downgrade() -> None:
    op.drop_index('idx_org_subscription_status', table_name='organization')
    op.drop_column('user', 'last_login_at')
    op.drop_column('user', 'is_verified')
    op.drop_column('user', 'phone')
    op.drop_column('organization', 'billing_email')
    op.drop_column('organization', 'max_calls_per_month')
    op.drop_column('organization', 'max_contacts')
    op.drop_column('organization', 'max_users')
    op.drop_column('organization', 'trial_ends_at')
    op.drop_column('organization', 'subscription_status')
    op.drop_column('organization', 'subscription_plan')
    op.drop_column('organization', 'industry')
    op.drop_column('organization', 'website')
    op.drop_column('organization', 'phone')
