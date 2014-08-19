"""add install count column

Revision ID: 521232efdc0b
Revises: 17ba0e3cd9a3
Create Date: 2014-08-18 22:54:33.361648

"""

# revision identifiers, used by Alembic.
revision = '521232efdc0b'
down_revision = '17ba0e3cd9a3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('bundles', sa.Column('install_count', sa.Integer, nullable=False, server_default='0'))


def downgrade():
    op.drop_column('bundles', 'install_count')
