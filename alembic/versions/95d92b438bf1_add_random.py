"""Add random

Revision ID: 95d92b438bf1
Revises: acf0995e8045
Create Date: 2024-09-19 16:06:24.088930

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "95d92b438bf1"
down_revision: Union[str, None] = "acf0995e8045"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("random", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "random")
