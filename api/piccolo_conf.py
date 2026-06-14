from piccolo.engine.postgres import PostgresEngine
from config import settings
from piccolo.conf.apps import AppRegistry


DB = PostgresEngine(
    config={
        "database": settings.db.database,
        "user": settings.db.user,
        "password": settings.db.password,
        "host": settings.db.host,
        "port": settings.db.port,
    }
)

APP_REGISTRY = AppRegistry(
    apps=["home.piccolo_app"]
)
