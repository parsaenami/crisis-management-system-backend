"""modified user

Revision ID: 849c06b6fa92
Revises: b9919932295d
Create Date: 2021-03-30 14:45:24.534254

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '849c06b6fa92'
down_revision = 'b9919932295d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('token', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'token')
    # ### end Alembic commands ###
