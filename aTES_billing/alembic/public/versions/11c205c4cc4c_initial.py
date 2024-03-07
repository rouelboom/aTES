"""Init database

Revision ID: 11c205c4cc4c
Revises: 
Create Date: 2020-05-06 14:15:43.228325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision = '11c205c4104c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'operation',
        sa.Column('id', sa.String),
        sa.Column('source_id', sa.String),  # link to task
        sa.Column('price', sa.Integer),
        sa.Column('worker_id', sa.String),  # link to table 'user'
        sa.Column('status', sa.String),
        sa.PrimaryKeyConstraint('id', name='operation__id__pkey')
    )

    op.create_table(
        'personal_account',
        sa.Column('id', sa.String),
        sa.Column('owner_id', sa.String),
        sa.Column('value', sa.Integer),
        sa.PrimaryKeyConstraint('id', name='personal_account__id__pkey')
    )

    op.create_table(
        'company_income',
        sa.Column('id', sa.String),
        sa.Column('value', sa.Integer),
        sa.PrimaryKeyConstraint('id', name='company_income__id__pkey')
    )

    op.create_table(
        'task',
        sa.Column('id', sa.String),
        sa.Column('name', sa.String),
        sa.Column('description', sa.String),
        sa.Column('assigned_worker', sa.String),
        sa.Column('price', sa.Integer),
        sa.PrimaryKeyConstraint('id', name='task__id__pkey')
    )


def downgrade():
    op.drop_table('operation')
    op.drop_table('personal_account')
    op.drop_table('company_income')
    op.drop_table('task')
