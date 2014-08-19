"""create tags table

Revision ID: 16a56f702449
Revises: 521232efdc0b
Create Date: 2014-08-18 23:06:06.986558

"""

# revision identifiers, used by Alembic.
revision = '16a56f702449'
down_revision = '521232efdc0b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('tag_name', sa.String(255), nullable=False),
        sa.Column('commit_hash', sa.String(255), nullable=False),
        sa.Column('zip_url', sa.String(2000), nullable=False),
        sa.Column('repository_id', sa.Integer, sa.ForeignKey('repositories.id'), nullable=False)
    )

    op.create_index('idx_tags_repository', 'tags', ['repository_id'])
    op.add_column('repositories', sa.Column('last_updated_tags', sa.DateTime, nullable=True))


def downgrade():
    op.drop_column('repositories', 'last_updated_tags')
    op.drop_table('tags')
