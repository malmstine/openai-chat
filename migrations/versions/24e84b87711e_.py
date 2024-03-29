"""empty message

Revision ID: 24e84b87711e
Revises: 66bc6b535292
Create Date: 2024-02-17 12:33:48.217875

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24e84b87711e'
down_revision = '66bc6b535292'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat', sa.Column('system_role', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chat', 'system_role')
    # ### end Alembic commands ###
