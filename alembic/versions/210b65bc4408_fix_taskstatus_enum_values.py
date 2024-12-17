"""Fix taskstatus enum values

Revision ID: 210b65bc4408
Revises: 47e6e8192233
Create Date: 2024-12-17 23:45:52.576225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '210b65bc4408'
down_revision: Union[str, None] = '47e6e8192233'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename the existing type to backup
    op.execute("ALTER TYPE taskstatus RENAME TO taskstatus_old;")

    # Create a new ENUM type with the correct values
    taskstatus_new = sa.Enum('pending', 'in-progress', 'completed', name='taskstatus')
    taskstatus_new.create(op.get_bind(), checkfirst=True)

    # Update the table to use the new ENUM
    op.alter_column(
        'tasks',
        'status',
        type_=taskstatus_new,
        existing_type=sa.Enum(name='taskstatus_old'),
        postgresql_using="status::text::taskstatus"
    )

    # Drop the old ENUM type
    op.execute("DROP TYPE taskstatus_old;")


def downgrade() -> None:
    # Recreate the old ENUM
    taskstatus_old = sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', name='taskstatus_old')
    taskstatus_old.create(op.get_bind(), checkfirst=True)

    # Revert the table to the old ENUM type
    op.alter_column(
        'tasks',
        'status',
        type_=taskstatus_old,
        existing_type=sa.Enum(name='taskstatus'),
        postgresql_using="status::text::taskstatus_old"
    )

    # Drop the new ENUM type
    op.execute("DROP TYPE taskstatus;")

    # Rename the old ENUM back to the original name
    op.execute("ALTER TYPE taskstatus_old RENAME TO taskstatus;")
