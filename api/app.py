from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from piccolo.engine import engine_finder
from piccolo_api.crud.serializers import create_pydantic_model
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from home.endpoints import HomeEndpoint
from home.piccolo_app import APP_CONFIG
from home.tables import Task


async def open_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.start_connection_pool()
    except Exception:
        print("Unable to connect to the database")


async def close_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.close_connection_pool()
    except Exception:
        print("Unable to connect to the database")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await open_database_connection_pool()
    yield
    await close_database_connection_pool()


app = FastAPI(lifespan=lifespan)
api = APIRouter(prefix="/api")

TaskModelIn: Any = create_pydantic_model(
    table=Task,
    model_name="TaskModelIn",
)

TaskModelOut: Any = create_pydantic_model(
    table=Task,
    include_default_columns=True,
    model_name="TaskModelOut",
)

@api.get("/")
async def test():
    return "pong!"


app.include_router(api)
