"""Update unique constraint to use student_canvas_id for CSV data

Revision ID: cbc68128c1aa
Revises: b73924c2efd1
Create Date: 2025-10-03 17:34:52.804712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbc68128c1aa'
down_revision: Union[str, Sequence[str], None] = 'b73924c2efd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - switch unique constraint to student_canvas_id for CSV data."""
    # Drop old unique constraint
    op.drop_index('uq_student_feedback_submission', table_name='student_feedback')

    # Create new unique constraint using student_canvas_id
    op.create_index(
        'uq_student_feedback_student',
        'student_feedback',
        ['canvas_survey_id', 'student_canvas_id'],
        unique=True
    )


def downgrade() -> None:
    """Downgrade schema - revert to canvas_submission_id constraint."""
    # Drop new unique constraint
    op.drop_index('uq_student_feedback_student', table_name='student_feedback')

    # Restore old unique constraint
    op.create_index(
        'uq_student_feedback_submission',
        'student_feedback',
        ['canvas_survey_id', 'canvas_submission_id'],
        unique=True
    )
