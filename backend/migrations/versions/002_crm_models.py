"""Add CRM models - Contacts, Companies, Deals, Pipelines, Activities

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create Contact table
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
        sa.Column('contact_type', sa.String(50), nullable=False, server_default='LEAD'),
        sa.Column('status', sa.String(50), nullable=False, server_default='NEW'),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_fields', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('last_contact_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_follow_up', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.ForeignKeyConstraint(['assigned_to'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_contact_phone', 'contact', ['organization_id', 'phone'])
    op.create_index('idx_org_contact_type', 'contact', ['organization_id', 'contact_type'])
    op.create_index('idx_contact_status', 'contact', ['status'])

    # Create Company table
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
        sa.Column('annual_revenue', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('company_status', sa.String(50), nullable=False, server_default='PROSPECT'),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_fields', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.ForeignKeyConstraint(['assigned_to'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_company_name', 'company', ['organization_id', 'name'])
    op.create_index('idx_company_status', 'company', ['company_status'])

    # Add company_id foreign key to contact
    op.create_foreign_key('fk_contact_company', 'contact', 'company', ['company_id'], ['id'])

    # Create Pipeline table
    op.create_table(
        'pipeline',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('stages', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create Deal table
    op.create_table(
        'deal',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('pipeline_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('stage', sa.String(100), nullable=False),
        sa.Column('deal_status', sa.String(50), nullable=False, server_default='OPEN'),
        sa.Column('probability', sa.Float(), nullable=False, server_default='50.0'),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('expected_close_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_fields', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.ForeignKeyConstraint(['contact_id'], ['contact.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
        sa.ForeignKeyConstraint(['pipeline_id'], ['pipeline.id'], ),
        sa.ForeignKeyConstraint(['assigned_to'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_deal_status', 'deal', ['organization_id', 'deal_status'])
    op.create_index('idx_deal_stage', 'deal', ['stage'])

    # Create Activity table
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
        sa.Column('metadata', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.ForeignKeyConstraint(['contact_id'], ['contact.id'], ),
        sa.ForeignKeyConstraint(['deal_id'], ['deal.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_org_activity_type', 'activity', ['organization_id', 'activity_type'])
    op.create_index('idx_contact_activity', 'activity', ['contact_id', 'activity_type'])


def downgrade() -> None:
    op.drop_index('idx_contact_activity', table_name='activity')
    op.drop_index('idx_org_activity_type', table_name='activity')
    op.drop_table('activity')
    op.drop_index('idx_deal_stage', table_name='deal')
    op.drop_index('idx_org_deal_status', table_name='deal')
    op.drop_table('deal')
    op.drop_table('pipeline')
    op.drop_foreign_key('fk_contact_company', 'contact', type_='foreignkey')
    op.drop_index('idx_company_status', table_name='company')
    op.drop_index('idx_org_company_name', table_name='company')
    op.drop_table('company')
    op.drop_index('idx_contact_status', table_name='contact')
    op.drop_index('idx_org_contact_type', table_name='contact')
    op.drop_index('idx_org_contact_phone', table_name='contact')
    op.drop_table('contact')
