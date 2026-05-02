from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Bytea
from piccolo.columns.column_types import Integer
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod


ID = "2026-05-02T19:03:02:529945"
VERSION = "1.33.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="home", description=DESCRIPTION
    )

    manager.add_table(
        class_name="NFCTable", tablename="nfc_table", schema=None, columns=None
    )

    manager.add_column(
        table_class_name="NFCTable",
        tablename="nfc_table",
        column_name="uid",
        db_column_name="uid",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 14,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": True,
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
        column_name="secret_key",
        db_column_name="secret_key",
        column_class_name="Bytea",
        column_class=Bytea,
        params={
            "default": b"",
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
        column_name="last_counter",
        db_column_name="last_counter",
        column_class_name="Integer",
        column_class=Integer,
        params={
            "default": 0,
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
