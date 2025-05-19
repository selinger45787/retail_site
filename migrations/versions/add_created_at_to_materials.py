"""add created_at to materials

Revision ID: add_created_at_to_materials
Revises: 5fe2dc612e55
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_created_at_to_materials'
down_revision = '5fe2dc612e55'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('materials', sa.Column('created_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('materials', 'created_at') 