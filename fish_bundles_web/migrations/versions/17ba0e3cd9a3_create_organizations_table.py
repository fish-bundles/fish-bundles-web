"""create organizations table

Revision ID: 17ba0e3cd9a3
Revises: 2886754ae3e9
Create Date: 2014-08-14 23:15:14.682216

"""

# revision identifiers, used by Alembic.
revision = '17ba0e3cd9a3'
down_revision = '2886754ae3e9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('org_name', sa.String(255), nullable=False, unique=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    )

    op.create_index('idx_organizations_name', 'organizations', ['org_name'])
    op.create_index('idx_organizations_user_id', 'organizations', ['user_id'])

    op.add_column('repositories', sa.Column('organization_id', sa.Integer, sa.ForeignKey('organizations.id'), nullable=True))
    op.create_index('idx_repositories_organization', 'repositories', ['organization_id'])

    op.drop_column('bundles', 'repo_name')
    op.add_column('bundles', sa.Column('repo_id', sa.Integer, sa.ForeignKey('repositories.id'), nullable=True))
    op.create_index('idx_bundles_repository', 'bundles', ['repo_id'])


def downgrade():
    op.drop_index('idx_repositories_organization', 'repositories')
    op.drop_table('organizations')
