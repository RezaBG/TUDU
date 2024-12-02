"""add status field to Task model

Revision ID: 09b5599b6005
Revises: 29f75c339adf
Create Date: 2024-11-27 23:08:23.903779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '09b5599b6005'
down_revision: Union[str, None] = '29f75c339adf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade the database schema by adding a status column to the Task table."""
    # Add the new 'status' column to the 'tasks' table
    # op.add_column('tasks', sa.Column('status', sa.String(), nullable=True))
    op.add_column('tasks', sa.Column('status', sa.Enum('pending', 'in-progress', 'completed', name='taskstatus'), nullable=True))

def downgrade() -> None:
    """Downgrade the database schema by removing the status column from the tasks table."""
    # Remove the 'status' column from the 'tasks' table
    op.drop_column('tasks', 'status')