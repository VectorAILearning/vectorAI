"""new type content code

Revision ID: 203099c57107
Revises: bb74bdeefd5a
Create Date: 2025-06-10 13:02:28.834154+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from alembic_postgresql_enum import TableReference

# revision identifiers, used by Alembic.
revision: str = "203099c57107"
down_revision: Union[str, None] = "bb74bdeefd5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values(
        enum_schema="public",
        enum_name="content_type_enum",
        new_values=[
            "TEXT",
            "VIDEO",
            "DIALOG",
            "PRACTICE",
            "EXAMPLES",
            "MISTAKES",
            "REFLECTION",
            "TEST",
            "CODE",
        ],
        affected_columns=[
            TableReference(
                table_schema="public", table_name="contents", column_name="type"
            )
        ],
        enum_values_to_rename=[],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values(
        enum_schema="public",
        enum_name="content_type_enum",
        new_values=[
            "TEXT",
            "VIDEO",
            "DIALOG",
            "PRACTICE",
            "EXAMPLES",
            "MISTAKES",
            "REFLECTION",
            "TEST",
        ],
        affected_columns=[
            TableReference(
                table_schema="public", table_name="contents", column_name="type"
            )
        ],
        enum_values_to_rename=[],
    )
    # ### end Alembic commands ###
