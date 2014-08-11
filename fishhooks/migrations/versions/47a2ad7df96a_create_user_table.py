'''create user table

Revision ID: 47a2ad7df96a
Revises: None
Create Date: 2014-08-10 23:21:09.426281

'''

# revision identifiers, used by Alembic.
revision = '47a2ad7df96a'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(200), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
    )

    op.create_index('idx_email', 'users', ['email'])
    op.create_unique_constraint('uq_user_username', 'users', ['username'])
    op.create_unique_constraint('uq_user_email', 'users', ['email'])


def downgrade():
    op.drop_index('idx_email', 'users')
    op.drop_constraint('uq_user_username', 'users', type_='unique')
    op.drop_constraint('uq_user_email', 'users', type_='unique')
    op.drop_table('users')
