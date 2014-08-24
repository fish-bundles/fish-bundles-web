"""add configuration to repos

Revision ID: 263d18612078
Revises: 11a32e6c9a2a
Create Date: 2014-08-24 10:50:24.687720

"""

# revision identifiers, used by Alembic.
revision = '263d18612078'
down_revision = '11a32e6c9a2a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('bundles', sa.Column('config', sa.Text, nullable=False))
    op.add_column('bundles', sa.Column('last_updated_config', sa.DateTime))


def downgrade():
    op.drop_column('bundles', 'config')
    op.drop_column('bundles', 'last_updated_config')
