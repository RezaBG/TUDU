"""Update TaskStatus enum values

Revision ID: 99b724eeeb8d
Revises: dae606d06f39
Create Date: 2024-12-01 13:53:45.421468

"""

from alembic import op
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision = "99b724eeeb8d"
down_revision = "dae606d06f39"
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Create a new ENUM type with the new values
    new_status_enum = ENUM("pending", "in-progress", "completed", name="taskstatus_new")
    new_status_enum.create(op.get_bind(), checkfirst=True)

    # Step 2: Update the 'status' column to temporarily store strings
    op.execute(
        """
        ALTER TABLE tasks
        ALTER COLUMN status TYPE TEXT
        """
    )

    # Step 3: Update the data in the 'status' column to match the new ENUM values
    op.execute(
        """
        UPDATE tasks
        SET status = 
        CASE
            WHEN status = 'PENDING' THEN 'pending'
            WHEN status = 'IN_PROGRESS' THEN 'in-progress'
            WHEN status = 'COMPLETED' THEN 'completed'
            ELSE status
        END
        """
    )

    # Step 4: Alter the 'status' column to use the new ENUM type
    op.execute(
        """
        ALTER TABLE tasks
        ALTER COLUMN status TYPE taskstatus_new 
        USING status::taskstatus_new
        """
    )

    # Step 5: Drop the old ENUM type
    op.execute("DROP TYPE taskstatus")

    # Step 6: Rename the new ENUM type to the original name
    op.execute("ALTER TYPE taskstatus_new RENAME TO taskstatus")


def downgrade():
    # Step 1: Create the old ENUM type with the original values
    old_status_enum = ENUM("PENDING", "IN_PROGRESS", "COMPLETED", name="taskstatus_old")
    old_status_enum.create(op.get_bind(), checkfirst=True)

    # Step 2: Update the 'status' column to temporarily store strings
    op.execute(
        """
        ALTER TABLE tasks
        ALTER COLUMN status TYPE TEXT
        """
    )

    # Step 3: Update the data in the 'status' column to match the old ENUM values
    op.execute(
        """
        UPDATE tasks
        SET status = 
        CASE
            WHEN status = 'pending' THEN 'PENDING'
            WHEN status = 'in-progress' THEN 'IN_PROGRESS'
            WHEN status = 'completed' THEN 'COMPLETED'
            ELSE status
        END
        """
    )

    # Step 4: Alter the 'status' column to use the old ENUM type
    op.execute(
        """
        ALTER TABLE tasks
        ALTER COLUMN status TYPE taskstatus_old 
        USING status::taskstatus_old
        """
    )

    # Step 5: Drop the new ENUM type
    op.execute("DROP TYPE taskstatus")

    # Step 6: Rename the old ENUM type back to the original name
    op.execute("ALTER TYPE taskstatus_old RENAME TO taskstatus")
