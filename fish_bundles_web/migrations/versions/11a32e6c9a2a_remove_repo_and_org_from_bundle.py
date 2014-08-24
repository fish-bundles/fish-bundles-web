'''remove repo and org from bundle

Revision ID: 11a32e6c9a2a
Revises: 16a56f702449
Create Date: 2014-08-23 22:00:25.913823

'''

# revision identifiers, used by Alembic.
revision = '11a32e6c9a2a'
down_revision = '16a56f702449'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint('bundles_ibfk_2', 'bundles', type_="foreignkey")
    op.drop_index('idx_bundles_repository', 'bundles')
    op.drop_column('bundles', 'repo_id')
    op.add_column('bundles', sa.Column('repo_name', sa.String(255), nullable=False, unique=False))
    op.add_column('bundles', sa.Column('org_name', sa.String(255), nullable=False, unique=False))

    op.create_unique_constraint('uk_bundles_repo_org', 'bundles', ['repo_name', 'org_name'])

    op.create_index('idx_bundles_repo_name', 'bundles', ['repo_name'])

    op.create_table(
        'releases',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('tag_name', sa.String(255), nullable=False),
        sa.Column('commit_hash', sa.String(255), nullable=False),
        sa.Column('zip_url', sa.String(2000), nullable=False),
        sa.Column('bundle_id', sa.Integer, sa.ForeignKey('bundles.id'), nullable=False)
    )

    op.create_index('idx_releases_bundle', 'releases', ['bundle_id'])


def downgrade():
    op.drop_constraint('uk_bundles_repo_org', 'bundles', type_="unique")

    op.drop_column('bundles', 'repo_name')
    op.drop_column('bundles', 'org_name')

    op.drop_table('releases')
