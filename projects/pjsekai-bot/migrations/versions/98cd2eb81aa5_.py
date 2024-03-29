"""empty message

Revision ID: 98cd2eb81aa5
Revises: 9766e4c4ea5d
Create Date: 2024-03-20 22:43:28.987364

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "98cd2eb81aa5"
down_revision: Union[str, None] = "9766e4c4ea5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("channel_intent_pkey", "channel_intent", "primary")
    op.create_primary_key(
        "channel_intent_pkey", "channel_intent", ["guild", "channel", "intent"]
    )
    op.create_table(
        "command_restrict",
        sa.Column("guild", sa.BigInteger(), nullable=False),
        sa.Column("channel", sa.BigInteger(), nullable=False),
        sa.Column("command", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("guild", "channel", "command"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("command_restrict")
    op.drop_constraint("channel_intent_pkey", "channel_intent", "primary")
    op.create_primary_key("channel_intent_pkey", "channel_intent", ["guild", "channel"])
    # ### end Alembic commands ###
