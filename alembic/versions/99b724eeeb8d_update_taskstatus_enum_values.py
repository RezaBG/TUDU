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

# Define the new and old ENUM types
new_status_enum = ENUM("pending", "in-progress", "completed", name="taskstatus", create_type=False)
old_status_enum = ENUM("PENDING", "IN_PROGRESS", "COMPLETED", name="taskstatus", create_type=False)


def upgrade():
    # Create the new ENUM type
    new_status_enum.create(op.get_bind(), checkfirst=True)

    # Update all `status` values to match the new ENUM
    op.execute(
        """
        UPDATE tasks
        SET status = 
        CASE
            WHEN status = 'PENDING' THEN 'pending'
            WHEN status = 'IN_PROGRESS' THEN 'in-progress'
            WHEN status = 'COMPLETED' THEN 'completed'
        END
        """
    )

    # Alter the `status` column to use the new ENUM type
    op.execute(
        """
        ALTER TABLE tasks
        ALTER COLUMN status TYPE taskstatus 
        USING status::text::taskstatus
        """
    )

    # Drop the old ENUM type
    old_status_enum.drop(op.get_bind(), checkfirst=True)



def downgrade():
    # Step 1: Create a temporary ENUM for the old values to handle the transition
    temp_status_enum = ENUM("PENDING", "IN_PROGRESS", "COMPLETED", name="temp_taskstatus")
    temp_status_enum.create(op.get_bind(), checkfirst=True)

    # Step 2: Temporarily change the column type to the temporary ENUM
    op.execute(
        """
        ALTER TABLE tasks
        ALTER COLUMN status TYPE temp_taskstatus 
        USING status::text::temp_taskstatus
        """
    )

    # Step 3: Update the status values to match the old ENUM values
    op.execute(
        """
        UPDATE tasks
        SET status = 
        CASE 
            WHEN status = 'pending' THEN 'PENDING'
            WHEN status = 'in-progress' THEN 'IN_PROGRESS'
            WHEN status = 'completed' THEN 'COMPLETED'
        END
        """
    )

    # Step 4: Change the column type to the old ENUM
    op.execute(
        """
        ALTER TABLE tasks
        ALTER COLUMN status TYPE taskstatus 
        USING status::text::taskstatus
        """
    )

    # Step 5: Drop the temporary ENUM
    temp_status_enum.drop(op.get_bind(), checkfirst=True)

    # Step 6: Drop the new ENUM
    new_status_enum.drop(op.get_bind(), checkfirst=True)
