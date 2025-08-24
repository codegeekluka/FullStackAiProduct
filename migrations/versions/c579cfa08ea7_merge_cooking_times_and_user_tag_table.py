"""merge cooking times and user tag table

Revision ID: c579cfa08ea7
Revises: a199bd422d32, add_cooking_times
Create Date: 2025-08-19 15:12:34.544472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c579cfa08ea7'
down_revision: Union[str, Sequence[str], None] = ('a199bd422d32', 'add_cooking_times')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
