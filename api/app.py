from contextlib import asynccontextmanager
from logging import raiseExceptions

from fastapi import FastAPI, HTTPException, APIRouter
from piccolo.engine import engine_finder

from pydantic import BaseModel
from Crypto.Cipher import AES
from Crypto.Hash import CMAC
import binascii
from home.tables import NFCTable



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



class NfcRequest(BaseModel):
    uid: str
    ctr: int
    mac: str

@api.get("/")
async def test():
    return "pong!"

@api.post("/nfc/auth")
async def nfc_auth(tap: NfcRequest):
    tag = await NFCTable.objects().get(NFCTable.uid == tap.uid)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tap.ctr <= tag.last_counter:
        raise HTTPException(status_code=403, detail="URL Already used - Please physically tap the NFC Tag!")

    try:
        key = tag.secret_key
        message = binascii.unhexlify(tap.uid) + tap.ctr.to_bytes(3, 'little')

        cobj = CMAC.new(key, ciphermod=AES)
        cobj.update(message)
        expected_mac = cobj.hexdigest()[:16]

        if tap.mac.lower() != expected_mac.lower():
            raise HTTPException(status_code=403, detail="Invalid MAC signature")

        tag.last_counter = tap.ctr
        await tag.save()

        return { "status": "success", "message": "One-time tap verified" }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(api)
