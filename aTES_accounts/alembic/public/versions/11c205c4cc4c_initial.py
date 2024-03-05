"""Init database

Revision ID: 11c205c32alec
Revises: 
Create Date: 2020-05-06 14:15:43.228325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision = '11c205c32alec'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        'user',
        sa.Column('id', sa.String),
        sa.Column('login', sa.String),
        sa.Column('role', sa.String),
        sa.Column('beak_shape', sa.String),
        sa.PrimaryKeyConstraint('id', name='user__id__pkey')
    )


def downgrade():
    op.drop_table('user')
