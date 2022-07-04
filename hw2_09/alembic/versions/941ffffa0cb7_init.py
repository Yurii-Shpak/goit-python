"""'Init'

Revision ID: 941ffffa0cb7
Revises: 
Create Date: 2022-07-04 13:38:33.682835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '941ffffa0cb7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contacts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('last_name', sa.String(length=30), nullable=False),
    sa.Column('first_name', sa.String(length=20), nullable=True),
    sa.Column('father_name', sa.String(length=20), nullable=True),
    sa.Column('phone1', sa.String(length=14), nullable=True),
    sa.Column('phone2', sa.String(length=14), nullable=True),
    sa.Column('phone3', sa.String(length=14), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('birthday', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contacts')
    # ### end Alembic commands ###
