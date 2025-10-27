"""create models table

Revision ID: 002
Revises: 001
Create Date: 2025-10-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'  # Depends on previous migration
branch_labels = None
depends_on = None


def upgrade():
    """Create models table"""
    op.create_table(
        'models',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('image_url', sa.String(512), nullable=False),
        sa.Column('prompt_details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    
    # Create index on created_at for better query performance
    op.create_index('idx_models_created_at', 'models', ['created_at'])


def downgrade():
    """Drop models table"""
    op.drop_index('idx_models_created_at', 'models')
    op.drop_table('models')


