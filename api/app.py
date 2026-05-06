from ast import Return
from contextlib import asynccontextmanager
import datetime
from email.policy import HTTP

from fastapi import FastAPI, HTTPException, APIRouter
from piccolo.engine import engine_finder

from pydantic import BaseModel
from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from helpers import diversify_key
from constants import MASTER_KEY, KEY3, SYSTEM_ID
import secrets
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


class NfcRequest(BaseModel):
    u: str
    p: str
    c: str

class ProvisionRequest(BaseModel):
    uid: str
    user_id: str

@api.get("/")
async def test():
    return "API is UP!"

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


# TODO: Add authentication and input validation
@api.post('/nfc/provision')
async def provision(req: ProvisionRequest):
  try:
    uid = bytes.fromhex(req.uid)
  except Exception:
    raise HTTPException(status_code=400, detail="Invalid UID")
  key0 = secrets.token_bytes(16) # this one is the lock, you cant write or read secret data from the tag without it
  key3= KEY3 # this one has to be the same for everyone because when we have to decrypt picc we dont know the uid yet
  key4 = diversify_key(MASTER_KEY, uid, SYSTEM_ID) # signature key

  existing = await NFCTable.objects().get(NFCTable.uid == uid.hex())
  if existing:
    raise HTTPException(status_code=403, detail="This tag uid already exists, please contact the admin if it's an issue for you")

  tag = NFCTable(uid=uid.hex(), user_id=req.user_id, key0=key0.hex(), key4=key4.hex(), status="active", created_at = datetime.datetime.now())
  await tag.save()

  return {
    "status": "ok",
    "user_id": req.user_id,
    "key0": key0.hex(),
    "key3": key3.hex(),
    "key4": key4.hex()
  }
app.include_router(api)
