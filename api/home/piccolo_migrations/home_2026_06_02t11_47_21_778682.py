from piccolo.apps.migrations.auto.migration_manager import MigrationManager

ID = "2026-06-02T11:47:21:778682"
VERSION = "1.33.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="home", description=DESCRIPTION
    )

    manager.rename_column(
        table_class_name="NFCTable",
        tablename="nfc_table",
        old_column_name="user_id",
        new_column_name="haj_id",
        old_db_column_name="user_id",
        new_db_column_name="haj_id",
        schema=None,
    )

    return manager
