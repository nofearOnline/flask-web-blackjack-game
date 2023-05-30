"""empty message

Revision ID: 2b7a2f3825af
Revises: dc9120627c43
Create Date: 2023-05-30 17:17:03.881931

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b7a2f3825af'
down_revision = 'dc9120627c43'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('db_game',
    sa.Column('id', sa.String(length=128), nullable=False),
    sa.Column('room', sa.String(length=128), nullable=True),
    sa.Column('game_data', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('db_room',
    sa.Column('id', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('dealer', sa.String(length=128), nullable=True),
    sa.Column('player', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('db_user',
    sa.Column('id', sa.String(length=128), nullable=False),
    sa.Column('username', sa.String(length=128), nullable=True),
    sa.Column('hashed_password', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('token', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('db_user')
    op.drop_table('db_room')
    op.drop_table('db_game')
    # ### end Alembic commands ###