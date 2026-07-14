from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Text
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.column_types import Varchar
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.columns.indexes import IndexMethod


ID = "2026-07-14T02:52:49:564123"
VERSION = "1.34.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="home", description=DESCRIPTION
    )

    manager.add_table(
        class_name="UsedUsernames",
        tablename="used_usernames",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="UsedUsernames",
        tablename="used_usernames",
        column_name="username",
        db_column_name="username",
        column_class_name="Text",
        column_class=Text,
        params={
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

    manager.add_column(
        table_class_name="UsedUsernames",
        tablename="used_usernames",
        column_name="created_at",
        db_column_name="created_at",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": TimestamptzNow(),
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

    manager.alter_column(
        table_class_name="HajInfo",
        tablename="haj_info",
        column_name="emoji",
        db_column_name="emoji",
        params={"null": False},
        old_params={"null": True},
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    manager.alter_column(
        table_class_name="HajInfo",
        tablename="haj_info",
        column_name="species",
        db_column_name="species",
        params={"null": False},
        old_params={"null": True},
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    return manager
