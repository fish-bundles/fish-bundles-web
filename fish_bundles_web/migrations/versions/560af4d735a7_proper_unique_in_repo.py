"""proper unique in repo

Revision ID: 560af4d735a7
Revises: 49989f23adc6
Create Date: 2014-08-25 14:34:16.816783

"""

# revision identifiers, used by Alembic.
revision = '560af4d735a7'
down_revision = '49989f23adc6'

from alembic import op


def upgrade():
    op.drop_constraint('idx_repositories_name', 'repositories', type_='unique')
    op.drop_constraint('repo_name', 'repositories', type_='unique')
    op.create_unique_constraint('uk_repositories_repo_name', 'repositories', ['repo_name', 'user_id'])


def downgrade():
    op.drop_constraint('uk_repositories_repo_name', 'repositories')
