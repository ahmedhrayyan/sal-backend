"""Add url to notification

Revision ID: 58845ec9c95f
Revises: 449088afffe0
Create Date: 2021-11-03 20:30:35.944679

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58845ec9c95f'
down_revision = '449088afffe0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notifications', sa.Column('url', sa.Text(), nullable=False))
    op.add_column('notifications', sa.Column('is_read', sa.Boolean(), nullable=False))
    op.drop_column('notifications', 'read')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notifications', sa.Column('read', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('notifications', 'is_read')
    op.drop_column('notifications', 'url')
    # ### end Alembic commands ###