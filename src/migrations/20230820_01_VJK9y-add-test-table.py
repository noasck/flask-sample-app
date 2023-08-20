"""
Add test table
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        apply="""
        CREATE TABLE test_table (
            id integer PRIMARY KEY,
            value varchar not null
        );
        """,
        rollback="""
            DROP TABLE IF EXISTS test_table CASCADE;
        """,
    ),
]
