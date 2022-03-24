"""cards table

Revision ID: 34cbeb8c0a3a
Revises: 73776afc7dd7
Create Date: 2022-03-24 12:53:47.349636

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34cbeb8c0a3a'
down_revision = '73776afc7dd7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('card', sa.Column('translation', sa.String(length=1000), nullable=True))
    op.create_index(op.f('ix_card_translation'), 'card', ['translation'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_card_translation'), table_name='card')
    op.drop_column('card', 'translation')
    # ### end Alembic commands ###
