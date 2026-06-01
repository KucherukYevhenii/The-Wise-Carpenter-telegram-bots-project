"""add_missing_enum_values

Revision ID: 95883054609c
Revises: 6b7c50dd5997
Create Date: 2026-05-19 15:34:14.576956

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95883054609c'
down_revision: Union[str, Sequence[str], None] = '6b7c50dd5997'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Додаємо значення у тип ENUM, якщо їх там ще немає
    # IF NOT EXISTS захистить нас від помилок, якщо значення вже додані
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'NEW'")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'IN_PROGRESS'")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'DRAFT'")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'COMPLETED'")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'REJECTED'")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'CLOSED'")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'ACTIVE'")

def downgrade() -> None:
    # Повернення назад для ENUM у Postgres не підтримується через ALTER TYPE (тільки видалення/перестворення типу)
    # Тому залишаємо порожнім або додаємо коментар
    pass