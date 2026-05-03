from contextlib import asynccontextmanager
import datetime
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
aeskey = bytes.fromhex("508575b21dfec2d4c8b0b735d4a3edf7") # i cba to store it for now i just want a POC


class NfcRequest(BaseModel):
    uid: str
    ctr: int
    mac: str

class ProvisionRequest(BaseModel):
    uid: str
    user_id: str

async def diversify_key(uid_hex, master_key, key_no):
    uid = bytes.fromhex(uid_hex)
    div_input = b'\x01' + uid + b'\x00' * (15 - len(uid))
    c = CMAC.new(master_key, ciphermod=AES)
    c.update(div_input)
    return c.digest().hex()


@api.get("/")
async def test():
    return "pong!"

# TODO: Redo because this is not based on what we're gonna use
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

# TODO: Add authentication
@api.post('/nfc/provision')
async def provision(req: ProvisionRequest):

    if not req.uid or not req.user_id:
        raise HTTPException(status_code=400, detail="Missing data!")

    tag_key_0 = await diversify_key(req.uid, aeskey, 0)
    tag_key_4 = await diversify_key(req.uid, aeskey, 4)

    await NFCTable.insert(NFCTable(
        user_id = req.user_id,
        status= "active",
        uid = req.uid,
        created_at = datetime.datetime.now()
    ))

    return {
        "key0": tag_key_0,
        "key4": tag_key_4,
        "url": f"https://hajdentity.esther.tf/nfc/auth?u={req.user_id}&p={{PICC}}&c={{MAC}}"
    }

app.include_router(api)
