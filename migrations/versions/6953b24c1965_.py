"""empty message

Revision ID: 6953b24c1965
Revises: b2db8697a1f2
Create Date: 2020-04-23 17:40:47.527340

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6953b24c1965'
down_revision = 'b2db8697a1f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('image', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('category', 'image')
    # ### end Alembic commands ###