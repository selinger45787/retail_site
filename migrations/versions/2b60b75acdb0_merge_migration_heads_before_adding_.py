"""Merge migration heads before adding image_path to orders

Revision ID: 2b60b75acdb0
Revises: 8ab52a5cd02d, ff3339e19f4d
Create Date: 2025-05-29 11:20:48.757911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b60b75acdb0'
down_revision = ('8ab52a5cd02d', 'ff3339e19f4d')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
