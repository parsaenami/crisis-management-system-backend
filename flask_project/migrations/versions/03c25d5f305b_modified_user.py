"""modified user

Revision ID: 03c25d5f305b
Revises: 7bbd263faaaf
Create Date: 2021-03-31 19:39:38.001377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03c25d5f305b'
down_revision = '7bbd263faaaf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('otp_exp', sa.String(), nullable=True))
    op.add_column('users', sa.Column('token_exp', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'token_exp')
    op.drop_column('users', 'otp_exp')
    # ### end Alembic commands ###