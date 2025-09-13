"""add cooking times to recipe

Revision ID: add_cooking_times
Revises: fc85bd59c4d4
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_cooking_times'
down_revision = 'fc85bd59c4d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add cooking time columns to recipe table
    op.add_column('recipe', sa.Column('prep_time', sa.String(), nullable=True))
    op.add_column('recipe', sa.Column('cook_time', sa.String(), nullable=True))
    op.add_column('recipe', sa.Column('total_time', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove cooking time columns from recipe table
    op.drop_column('recipe', 'total_time')
    op.drop_column('recipe', 'cook_time')
    op.drop_column('recipe', 'prep_time')
