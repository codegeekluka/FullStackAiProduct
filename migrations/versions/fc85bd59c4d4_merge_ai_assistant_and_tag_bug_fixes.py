"""Merge AI assistant and tag bug fixes

Revision ID: fc85bd59c4d4
Revises: ai_assistant_v1, e5774313f9d7
Create Date: 2025-08-15 20:44:25.975092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc85bd59c4d4'
down_revision: Union[str, Sequence[str], None] = ('ai_assistant_v1', 'e5774313f9d7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
