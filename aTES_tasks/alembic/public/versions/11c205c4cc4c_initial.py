"""Init database

Revision ID: 11c205c4cc4c
Revises: 
Create Date: 2020-05-06 14:15:43.228325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision = '11c205c4cc4c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # TODO delete 'sample_table' definition and add your tables here
    op.create_table(
        'task',
        sa.Column('id', sa.String),
        sa.Column('name', sa.String),
        sa.PrimaryKeyConstraint('id', name='task__id__pkey')
    )


def downgrade():
    # TODO delete 'sample_table' and add your drop statements here
    op.drop_table('task')
