"""
Test migrations step by step
"""
from alembic.command import upgrade, downgrade

from m7_pytest_postgres.alembic_utils import get_revisions


def test_migrations_staircase(get_alembic_config):
    """
    Performs staircase test for all migrations
    """
    alembic_config = get_alembic_config('public')
    revisions = get_revisions(alembic_config)
    for revision in revisions:
        upgrade(alembic_config, revision.revision)

        # We need -1 for downgrading first migration (its down_revision is None)
        downgrade(alembic_config, revision.down_revision or '-1')
        upgrade(alembic_config, revision.revision)
