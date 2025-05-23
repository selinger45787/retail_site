"""add test dates

Revision ID: add_test_dates
Revises: 
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_test_dates'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем колонки для дат теста
    op.add_column('materials', sa.Column('test_start_date', sa.DateTime(), nullable=True))
    op.add_column('materials', sa.Column('test_end_date', sa.DateTime(), nullable=True))

def downgrade():
    # Удаляем колонки при откате
    op.drop_column('materials', 'test_end_date')
    op.drop_column('materials', 'test_start_date') 