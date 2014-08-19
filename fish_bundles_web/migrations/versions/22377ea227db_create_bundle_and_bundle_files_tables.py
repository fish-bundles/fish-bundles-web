"""create bundle and bundle files tables

Revision ID: 22377ea227db
Revises: 47a2ad7df96a
Create Date: 2014-08-13 22:05:58.835932

"""

# revision identifiers, used by Alembic.
revision = '22377ea227db'
down_revision = '47a2ad7df96a'

from alembic import op
import sqlalchemy as sa
import sqlalchemy.sql.functions as func


def upgrade():
    op.create_table(
        'bundles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('repo_name', sa.String(255), nullable=False, unique=True),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('readme', sa.UnicodeText, nullable=True),
        sa.Column('category', sa.Integer, nullable=False),
        sa.Column('author_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=func.now()),
        sa.Column('last_updated_at', sa.DateTime, server_default=func.now())
    )

    op.create_index('idx_bundles_name', 'bundles', ['repo_name'])
    op.create_index('idx_bundles_author_id', 'bundles', ['author_id'])

    op.create_table(
        'bundle_files',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('path', sa.String(2000), nullable=False),
        sa.Column('file_type', sa.Integer, nullable=False),
        sa.Column('contents', sa.UnicodeText, nullable=False),
        sa.Column('bundle_id', sa.Integer, sa.ForeignKey('bundles.id'), nullable=False),
    )

    op.create_index('idx_bundle_files_bundle_id', 'bundle_files', ['bundle_id'])


def downgrade():
    op.drop_table('bundle_files')
    op.drop_table('bundles')
