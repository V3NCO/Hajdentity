from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.column_types import UUID
from piccolo.columns.column_types import Varchar


ID = "2026-07-11T19:30:43:367564"
VERSION = "1.34.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="home", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="HajInfo",
        tablename="haj_info",
        column_name="human",
        db_column_name="human",
        params={"index": True},
        old_params={"index": False},
        column_class=UUID,
        old_column_class=UUID,
        schema=None,
    )

    manager.alter_column(
        table_class_name="HajInfo",
        tablename="haj_info",
        column_name="username",
        db_column_name="username",
        params={"index": True},
        old_params={"index": False},
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    manager.alter_column(
        table_class_name="Posts",
        tablename="posts",
        column_name="haj",
        db_column_name="haj",
        params={"index": True},
        old_params={"index": False},
        column_class=UUID,
        old_column_class=UUID,
        schema=None,
    )

    manager.alter_column(
        table_class_name="Sessions",
        tablename="sessions",
        column_name="associated",
        db_column_name="associated",
        params={"index": True},
        old_params={"index": False},
        column_class=UUID,
        old_column_class=UUID,
        schema=None,
    )

    manager.alter_column(
        table_class_name="Sessions",
        tablename="sessions",
        column_name="last_seen_at",
        db_column_name="last_seen_at",
        params={"index": True},
        old_params={"index": False},
        column_class=Timestamptz,
        old_column_class=Timestamptz,
        schema=None,
    )

    return manager
