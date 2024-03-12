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
        sa.Column('billing_cycle_id', sa.String),
        sa.Column('worker_id', sa.String),  # link to table 'user'
        sa.Column('description', sa.String),
        sa.Column('debit', sa.Integer),
        sa.Column('credit', sa.Integer),
        sa.Column('time', sa.DateTime),
        sa.PrimaryKeyConstraint('id', name='operation__id__pkey')
    )

    op.create_table(
        'billing_cycle',
        sa.Column('id', sa.DateTime),
        sa.Column('start_date', sa.DateTime),
        sa.Column('end_date', sa.DateTime),  # link to task
        sa.Column('status', sa.Integer),  # opened | closed
        sa.PrimaryKeyConstraint('id', name='operation__id__pkey')
    )

    op.create_table(
        'personal_balance',
        sa.Column('user_id', sa.String),
        sa.Column('value', sa.Integer),
        sa.PrimaryKeyConstraint('id', name='personal_account__user_id__pkey')
        )

    op.create_table(
        'task',
        sa.Column('id', sa.String),
        sa.Column('assigned_worker', sa.String),
        sa.Column('price', sa.Integer),
        sa.PrimaryKeyConstraint('id', name='task__id__pkey')
    )


def downgrade():
    op.drop_table('operation')
    op.drop_table('billing_cycle')
    op.drop_table('personal_balance')
    op.drop_table('task')
