
"""Added user and workout relationship

Revision ID: 4719c48472d6
Revises: df5a67c1bd8f
Create Date: 2026-06-26 19:59:17.211984

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4719c48472d6"
down_revision: Union[str, Sequence[str], None] = "df5a67c1bd8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("workouts", sa.Column("user_id", sa.Integer(), nullable=False))
    op.create_foreign_key(None, "workouts", "users", ["user_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint(None, "workouts", type_="foreignkey")
    op.drop_column("workouts", "user_id")

