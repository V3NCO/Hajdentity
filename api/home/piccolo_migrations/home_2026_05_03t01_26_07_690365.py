from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Time
from piccolo.columns.column_types import Varchar
from piccolo.columns.defaults.time import TimeNow
from piccolo.columns.indexes import IndexMethod


ID = "2026-05-03T01:26:07:690365"
VERSION = "1.33.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="home", description=DESCRIPTION
    )

    manager.drop_column(
        table_class_name="NFCTable",
        tablename="nfc_table",
        column_name="secret_key",
        db_column_name="secret_key",
        schema=None,
    )

    manager.add_column(
        table_class_name="NFCTable",
        tablename="nfc_table",
        column_name="created_at",
        db_column_name="created_at",
        column_class_name="Time",
        column_class=Time,
        params={
            "default": TimeNow(),
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
        table_class_name="NFCTable",
        tablename="nfc_table",
        column_name="status",
        db_column_name="status",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
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
        table_class_name="NFCTable",
        tablename="nfc_table",
        column_name="user_id",
        db_column_name="user_id",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
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

    return manager
