from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import UUID
from piccolo.columns.column_types import Varchar
from piccolo.columns.defaults.uuid import UUID4

ID = "2026-06-02T12:22:21:775703"
VERSION = "1.33.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="home", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="NFCTable",
        tablename="nfc_table",
        column_name="haj_id",
        db_column_name="haj_id",
        params={"default": UUID4()},
        old_params={"default": ""},
        column_class=UUID,
        old_column_class=Varchar,
        schema=None,
    )

    return manager
