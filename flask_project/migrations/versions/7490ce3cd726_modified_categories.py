"""modified categories

Revision ID: 7490ce3cd726
Revises: 03c25d5f305b
Create Date: 2021-04-01 00:31:27.833452

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7490ce3cd726'
down_revision = '03c25d5f305b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('disaster_category', sa.Column('en_title', sa.String(), nullable=True))
    op.add_column('need_category', sa.Column('en_title', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('need_category', 'en_title')
    op.drop_column('disaster_category', 'en_title')
    # ### end Alembic commands ###