from contextlib import asynccontextmanager
import datetime

from fastapi import FastAPI, HTTPException, APIRouter, Depends
from piccolo.engine import engine_finder
import uuid
from pydantic import UUID4, BaseModel
from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from helpers import diversify_key
from constants import MASTER_KEY, KEY3, SYSTEM_ID, ACCESS_TOKEN_EXPIRE_MINUTES
import secrets
from home.tables import HajInfo, NFCTable
from auth import create_access_token, create_user, authenticate_user, get_current_active_user
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated
from pydantic import Field



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

class NewHajRequest(BaseModel):
  name: Annotated[str, Field(max_length=48, )]
  date: datetime.date
  size: float
  location: str | None = None
  description: str
  pronouns: Annotated[str, Field(max_length=32)] | None = None
  gender: Annotated[str, Field(max_length=96)] | None = None
  floof: Annotated[int, Field(ge=1, le=10)] | None = None
  squish: Annotated[int, Field(ge=1, le=10)] | None = None
  lastwashed: datetime.datetime | None = None
  mloftearsabsorbed: float | None = None

class RegisterRequest(BaseModel):
  username: str
  email: str
  password: str

class NfcRequest(BaseModel):
  picc_data: str
  cmac: str

class ProvisionRequest(BaseModel):
  uid: str
  haj_id: UUID4

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
async def provision(req: ProvisionRequest, current_user = Depends(get_current_active_user)):
  if(HajInfo.exists().where((HajInfo.uuid == req.haj_id) & (current_user.id == HajInfo.human))):
    try:
      uid = bytes.fromhex(req.uid)
    except Exception:
      raise HTTPException(status_code=400, detail="Invalid UID")
    key0 = secrets.token_bytes(16) # this one is the lock, you cant write or read secret data from the tag without it
    key3= KEY3 # this one has to be the same for everyone because when we have to decrypt picc we dont know the uid yet
    key4 = diversify_key(MASTER_KEY, uid, SYSTEM_ID) # signature key

    existing = await NFCTable.exists().where(NFCTable.uid == uid.hex())
    if existing:
      raise HTTPException(status_code=403, detail="This tag uid already exists, please contact the admin if it's an issue for you")

    tag = NFCTable(uid=uid.hex(), haj_id=req.haj_id, key0=key0.hex(), key4=key4.hex(), status="active", created_at = datetime.datetime.now())
    await tag.save()

    return {
      "status": "ok",
      "inserted": {
        "haj_id": req.haj_id,
        "key0": key0.hex(),
        "key3": key3.hex(),
        "key4": key4.hex()
      }
    }
  else:
    raise HTTPException(401, "This blahaj is either not yours or doesn't exist.")


@api.post('/haj/create')
async def add_haj(req: NewHajRequest, current_user = Depends(get_current_active_user)):
  try:
    haj_id = uuid.uuid4()
    await HajInfo(
      uuid=haj_id,
      human=current_user.id,
      name=req.name,
      date=req.date,
      size = req.size,
      location = req.location,
      description = req.description,
      pronouns = req.pronouns,
      gender = req.gender,
      floof = req.floof,
      squish = req.squish,
      lastwashed = req.lastwashed,
      mloftearsabsorbed= req.mloftearsabsorbed
    ).save()
    return {
      "status": "OK",
      "inserted": {
        "uuid": haj_id,
        "human": current_user.id,
        "name": req.name,
        "date": req.date,
        "size": req.size,
        "location": req.location,
        "description": req.description,
        "pronouns": req.pronouns,
        "gender": req.gender,
        "floof": req.floof,
        "squish": req.squish,
        "lastwashed": req.lastwashed,
        "mloftearsabsorbed": req.mloftearsabsorbed
      }
    }
  except Exception as e:
    raise HTTPException(500, f"An internal error occured, please try again or contact the administrator with {e}")

@api.post('/auth/register')
async def register(req: RegisterRequest):
  res = await create_user(req)
  if not res.get('ok'):
    raise HTTPException(status_code=400, detail=str(res.get('error', 'unknown')))
  return {"status": "ok"}


@api.post('/auth/token')
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
  user = await authenticate_user(form_data.username, form_data.password)
  if not user:
    raise HTTPException(status_code=401, detail="Incorrect username or password")
  access_token = create_access_token({"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
  return {"access_token": access_token, "token_type": "bearer"}


@api.get('/auth/me')
async def me(current_user = Depends(get_current_active_user)):
  return {"username": current_user.username, "disabled": current_user.disabled}

app.include_router(api)
