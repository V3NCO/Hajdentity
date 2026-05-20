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
    picc_data: str
    cmac: str

class ProvisionRequest(BaseModel):
    uid: str
    user_id: str

@api.get("/")
async def test():
    return "API is UP!"

@api.post("/nfc/auth")
async def nfc_auth(tap: NfcRequest):
    picc_bytes = bytes.fromhex(tap.picc_data)
    iv = b'\x00' * 16
    cipher = AES.new(KEY3, AES.MODE_CBC, iv)

    decrypted = cipher.decrypt(picc_bytes)

    if decrypted[0] != 0xC7:
        raise HTTPException(status_code=400, detail="Invalid PICC data format. Bad KEY3?")

    uid_bytes = decrypted[1:8]
    ctr_bytes = decrypted[8:11]

    uid_hex = uid_bytes.hex()
    counter = int.from_bytes(ctr_bytes, byteorder='little')

    tag = await NFCTable.objects().get(NFCTable.uid == uid_hex)
    if not tag:
        raise HTTPException(status_code=404, detail="Unrecognized Tag")

    k4 = bytes.fromhex(tag.key4)

    csdm = CMAC.new(k4, ciphermod=AES)
    csdm.update(b'\x3c\xc3\x00\x01\x00\x80' + uid_bytes + ctr_bytes)
    k_sdm_mac = csdm.digest()

    mac_obj = CMAC.new(k_sdm_mac, ciphermod=AES)
    full_mac = mac_obj.digest()

    calculated_mac_bytes = bytes([full_mac[i] for i in range(1, 16, 2)])
    calculated_mac_hex = calculated_mac_bytes.hex().upper()

    if tap.cmac.upper() != calculated_mac_hex:
        raise HTTPException(status_code=400, detail="CMAC invalid")


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
