"""empty message

Revision ID: 9bda16e1b568
Revises: 34cbeb8c0a3a
Create Date: 2022-03-25 12:37:05.116235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9bda16e1b568'
down_revision = '34cbeb8c0a3a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('variant', sa.Column('card_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'variant', 'card', ['card_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'variant', type_='foreignkey')
    op.drop_column('variant', 'card_id')
    # ### end Alembic commands ###
