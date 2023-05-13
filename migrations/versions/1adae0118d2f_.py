"""empty message

Revision ID: 1adae0118d2f
Revises: 52664c1aa1b0
Create Date: 2023-05-12 17:11:09.642422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1adae0118d2f'
down_revision = '52664c1aa1b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('db_user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('hashed_password', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('email', sa.String(length=128), nullable=True))
        batch_op.drop_column('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('db_user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=128), nullable=True))
        batch_op.drop_column('email')
        batch_op.drop_column('hashed_password')
        batch_op.drop_column('username')

    # ### end Alembic commands ###
