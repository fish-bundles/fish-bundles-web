"""create repository table

Revision ID: 2886754ae3e9
Revises: 22377ea227db
Create Date: 2014-08-14 22:29:21.954650

"""

# revision identifiers, used by Alembic.
revision = '2886754ae3e9'
down_revision = '22377ea227db'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'repositories',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('repo_name', sa.String(255), nullable=False, unique=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    )

    op.create_index('idx_repositories_name', 'repositories', ['repo_name'])
    op.create_index('idx_repositories_user_id', 'repositories', ['user_id'])

    op.add_column('users', sa.Column('last_synced_repos', sa.DateTime, nullable=True))


def downgrade():
    op.drop_table('repositories')
