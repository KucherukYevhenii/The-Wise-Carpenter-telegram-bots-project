"""update_status_enum_to_uppercase

Revision ID: 6b7c50dd5997
Revises: a1994f4ae043
Create Date: 2026-05-19 14:55:01.296784

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b7c50dd5997'
down_revision: Union[str, Sequence[str], None] = 'a1994f4ae043'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Спочатку кастимо status до тексту, потім робимо UPPER, а потім кастимо назад до типу status
    op.execute("UPDATE questions SET status = UPPER(status::text)::status")
    op.execute("UPDATE workshop_opening_requests SET status = UPPER(status::text)::status")
    op.execute("UPDATE mobile_workshop_requests SET status = UPPER(status::text)::status")
    op.execute("UPDATE workshops SET status = UPPER(status::text)::status")

def downgrade() -> None:
    # Повертаємо все назад у нижній регістр
    op.execute("UPDATE questions SET status = LOWER(status::text)::status")
    op.execute("UPDATE workshop_opening_requests SET status = LOWER(status::text)::status")
    op.execute("UPDATE mobile_workshop_requests SET status = LOWER(status::text)::status")
    op.execute("UPDATE workshops SET status = LOWER(status::text)::status")