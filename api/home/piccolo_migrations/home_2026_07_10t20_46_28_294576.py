from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod


ID = "2026-07-10T20:46:28:294576"
VERSION = "1.34.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="home", description=DESCRIPTION
    )

    manager.add_column(
        table_class_name="Sessions",
        tablename="sessions",
        column_name="type",
        db_column_name="type",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 64,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.rename_column(
        table_class_name="Sessions",
        tablename="sessions",
        old_column_name="user_id",
        new_column_name="associated",
        old_db_column_name="user_id",
        new_db_column_name="associated",
        schema=None,
    )

    return manager
