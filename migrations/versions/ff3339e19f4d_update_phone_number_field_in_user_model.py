"""Update phone_number field in User model

Revision ID: ff3339e19f4d
Revises: add_test_dates
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff3339e19f4d'
down_revision = 'add_test_dates'
branch_labels = None
depends_on = None


def upgrade():
    # Сначала обновляем существующие записи
    op.execute("UPDATE users SET phone_number = '0000000000' WHERE phone_number IS NULL")
    
    # Затем делаем поле NOT NULL
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('phone_number',
                            existing_type=sa.String(length=20),
                            nullable=False)


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('phone_number',
                            existing_type=sa.String(length=20),
                            nullable=True)
