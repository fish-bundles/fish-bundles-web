"""proper unique in organizations

Revision ID: 49989f23adc6
Revises: 263d18612078
Create Date: 2014-08-25 14:18:02.611448

"""

# revision identifiers, used by Alembic.
revision = '49989f23adc6'
down_revision = '263d18612078'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.drop_constraint('organizations_ibfk_1', 'organizations', type_='foreignkey')
    op.drop_constraint('idx_organizations_name', 'organizations', type_='unique')
    op.drop_constraint('idx_organizations_user_id', 'organizations', type_='unique')
    op.drop_constraint('org_name', 'organizations', type_='unique')
    op.create_unique_constraint('uk_organizations', 'organizations', ['org_name', 'user_id'])
    op.create_foreign_key('fk_organizations_user', 'organizations', 'users', ['user_id'], ['id'])


def downgrade():
    op.drop_constraint('uk_organizations', 'organizations')
