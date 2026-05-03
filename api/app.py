from ast import Return
from contextlib import asynccontextmanager
import datetime

from fastapi import FastAPI, HTTPException, APIRouter
from piccolo.engine import engine_finder

from pydantic import BaseModel
from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from helpers import try_decrypt_p, validate_uid_hex, derive_diversified_key
from home.tables import NFCTable
import logging



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
    u: str
    p: str
    c: str

class ProvisionRequest(BaseModel):
    uid: str
    user_id: str

@api.get("/")
async def test():
    return "pong!"

@api.post("/nfc/auth")
async def nfc_auth(tap: NfcRequest):
    if not tap.u or not tap.p or not tap.c:
        raise HTTPException(status_code=400, detail="Missing data!")
    tag = await NFCTable.objects().get(NFCTable.user_id == tap.u)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    try:
        key0 = bytes.fromhex(tag.key0)
        key4 = bytes.fromhex(tag.key4)
    except Exception:
        raise HTTPException(status_code=500, detail="Stored key0/key4 invalid, please email me")

    try:
        pt = try_decrypt_p(key0, tap.p)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Failed to decrypt PICC: {e}")

    try:
        stored_uid_bytes = bytes.fromhex(tag.uid)
    except Exception:
        raise HTTPException(status_code=500, detail="Stored UID invalid, please email me")

    uid_len = len(stored_uid_bytes)
    if len(pt) < uid_len + 3:
        raise HTTPException(status_code=400, detail="Decrypted payload too short")

    uid_bytes = pt[:uid_len]
    ctr_bytes = pt[uid_len:uid_len + 3]
    ctr = int.from_bytes(ctr_bytes, 'little')

    if uid_bytes != stored_uid_bytes:
        logging.warning(f"UID mismatch between request {uid_bytes.hex()} and stored {stored_uid_bytes.hex()}")
        tag.status = "debuguidmismatch"
        # Theres been too much shenenigans in the app for now so im not confident on UID stuff

    cobj = CMAC.new(key4, ciphermod=AES)
    cobj.update(uid_bytes + ctr_bytes)
    expected_mac_trunc = cobj.digest()[:8].hex()

    if tap.c.lower() != expected_mac_trunc:
        raise HTTPException(status_code=403, detail="Invalid MAC signature")

    last_ctr = tag.last_counter
    if ctr <= last_ctr:
        raise HTTPException(status_code=403, detail="URL expired, please physically tap the NFC tag")

    tag.last_counter = ctr
    await tag.save()

    return {"status": "success", "message": "One-time tap verified"}


# TODO: Add authentication
@api.post('/nfc/provision')
async def provision(req: ProvisionRequest):

    if not req.uid or not req.user_id:
        raise HTTPException(status_code=400, detail="Missing data!")

    try:
        uid_bytes = validate_uid_hex(req.uid)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    uid_norm = uid_bytes.hex()

    existing = await NFCTable.objects().get(NFCTable.uid == uid_norm)
    if existing:
        return {
            "note": "already_exists",
            "uid": uid_norm,
            "user_id": existing.user_id,
            "key0": existing.key0,
            "key4": existing.key4,
            "url": f"https://hajdentity.esther.tf/nfc/auth?u={existing.user_id}&p={{PICC}}&c={{MAC}}"
        }

    key0_bytes = derive_diversified_key(aeskey, uid_bytes, 0)
    key4_bytes = derive_diversified_key(aeskey, uid_bytes, 4)
    key0_hex = key0_bytes.hex()
    key4_hex = key4_bytes.hex()

    final_url = f"https://hajdentity.esther.tf/nfc/auth?u={req.user_id}&p={{PICC}}&c={{MAC}}"

    try:
        await NFCTable.insert(NFCTable(
            user_id=req.user_id,
            status="active",
            uid=uid_norm,
            key0=key0_hex,
            key4=key4_hex,
            created_at=datetime.datetime.now()
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB insert failed: {str(e)}")

    return {"uid": uid_norm, "user_id": req.user_id, "key0": key0_hex, "key4": key4_hex, "url": final_url}

app.include_router(api)
