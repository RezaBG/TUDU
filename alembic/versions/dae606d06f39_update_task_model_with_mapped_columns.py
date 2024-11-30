"""Update Task model with Mapped columns

Revision ID: dae606d06f39
Revises: 09b5599b6005
Create Date: 2024-11-28 16:26:46.606842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dae606d06f39'
down_revision: Union[str, None] = '09b5599b6005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Set default value for existing NULLs
    op.execute("UPDATE tasks SET status = 'pending' WHERE status IS NULL")

    # Adjustments to 'tasks' table
    op.alter_column(
        'tasks',
        'status',
        existing_type=sa.String(),
        nullable=False,
        existing_server_default='pending'
    )
    op.alter_column('tasks', 'owner_id', existing_type=sa.Integer(), nullable=False)

    # Adjustments to 'users' table
    op.alter_column('users', 'username', existing_type=sa.String(), nullable=False)
    op.alter_column('users', 'email', existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    # Revert changes in 'tasks' table
    op.alter_column(
        'tasks',
        'status',
        existing_type=sa.String(),
        nullable=True,
        existing_server_default=None,
    )
    op.alter_column('tasks', 'owner_id', existing_type=sa.Integer(), nullable=True)

    # Revert changes in 'users' table
    op.alter_column('users', 'username', existing_type=sa.String(), nullable=True)
    op.alter_column('users', 'email', existing_type=sa.String(), nullable=True)