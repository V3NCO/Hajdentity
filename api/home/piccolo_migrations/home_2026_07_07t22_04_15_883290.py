from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Integer
from piccolo.columns.column_types import Numeric
from piccolo.columns.column_types import Text
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.column_types import Varchar


ID = "2026-07-07T22:04:15:883290"
VERSION = "1.34.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="home", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="HajInfo",
        tablename="haj_info",
        column_name="location",
        db_column_name="location",
        params={"null": True},
        old_params={"null": False},
        column_class=Text,
        old_column_class=Text,
        schema=None,
    )

    manager.alter_column(
        table_class_name="HajInfo",
        tablename="haj_info",
        column_name="pronouns",
        db_column_name="pronouns",
        params={"null": True},
        old_params={"null": False},
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    manager.alter_column(
        table_class_name="HajInfo",
        tablename="haj_info",
        column_name="gender",
        db_column_name="gender",
        params={"null": True},
        old_params={"null": False},
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    manager.alter_column(
        table_class_name="HajInfo",
        tablename="haj_info",
        column_name="floof",
        db_column_name="floof",
        params={"null": True},
        old_params={"null": False},
        column_class=Integer,
        old_column_class=Integer,
        schema=None,
    )

    manager.alter_column(
        table_class_name="HajInfo",
        tablename="haj_info",
        column_name="lastwashed",
        db_column_name="lastwashed",
        params={"null": True},
        old_params={"null": False},
        column_class=Timestamptz,
        old_column_class=Timestamptz,
        schema=None,
    )

    manager.alter_column(
        table_class_name="HajInfo",
        tablename="haj_info",
        column_name="mloftearsabsorbed",
        db_column_name="mloftearsabsorbed",
        params={"null": True},
        old_params={"null": False},
        column_class=Numeric,
        old_column_class=Numeric,
        schema=None,
    )

    manager.alter_column(
        table_class_name="HajInfo",
        tablename="haj_info",
        column_name="squish",
        db_column_name="squish",
        params={"null": True},
        old_params={"null": False},
        column_class=Integer,
        old_column_class=Integer,
        schema=None,
    )

    return manager
