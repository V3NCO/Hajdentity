from contextlib import asynccontextmanager
import datetime
from home.tables import Humans, HajInfo, NFCTable
from fastapi import FastAPI, HTTPException, APIRouter, Depends, Form, Request, Response, UploadFile, File
from fastapi_mail import MessageSchema, MessageType
from piccolo.engine import engine_finder
import uuid
from pydantic import UUID4, BaseModel, EmailStr, NameEmail
from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from helpers import diversify_key
from config import settings, mail, s3
from PIL import Image
from io import BytesIO
import secrets
from urllib.parse import urlparse
from auth import (
  check_haj_perm, create_user, authenticate_user, get_current_active_user, get_optional_user,
  create_verification_token, verify_email_token,
  create_session, delete_session, set_session_cookie, clear_session_cookie,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from scalar_fastapi import get_scalar_api_reference
from typing import Annotated
from pydantic import Field
from emails import verify_mail_template


async def open_database_connection_pool():
    try:
        engine = engine_finder()
        if engine is None:
          print("No Piccolo engine configured; skipping")
          return
        await engine.start_connection_pool()
    except Exception:
        print("Unable to connect to the database")


async def close_database_connection_pool():
    try:
        engine = engine_finder()
        if engine is None:
          print("No Piccolo engine configured; skipping")
          return
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
  public: bool = True

def haj_from_form(
  name: Annotated[str, Form(max_length=48)],
  date: Annotated[datetime.date, Form()],
  size: Annotated[float, Form()],
  description: Annotated[str, Form()],
  location: Annotated[str | None, Form()] = None,
  pronouns: Annotated[str | None, Form(max_length=32)] = None,
  gender: Annotated[str | None, Form(max_length=96)] = None,
  floof: Annotated[int | None, Form(ge=1, le=10)] = None,
  squish: Annotated[int | None, Form(ge=1, le=10)] = None,
  lastwashed: Annotated[datetime.datetime | None, Form()] = None,
  mloftearsabsorbed: Annotated[float | None, Form()] = None,
  public: bool = True
) -> NewHajRequest:
  return NewHajRequest(
    name=name, date=date, size=size, location=location,
    description=description, pronouns=pronouns, gender=gender,
    floof=floof, squish=squish, lastwashed=lastwashed,
    mloftearsabsorbed=mloftearsabsorbed, public=public
  )

class VerifyRequest(BaseModel):
  token: str

class RegisterRequest(BaseModel):
  username: Annotated[str, Field(min_length=3, max_length=96, pattern=r'^[a-zA-Z0-9_-]+$')]
  email: EmailStr
  password: Annotated[str, Field(min_length=16)]

class NewTokenRequest(BaseModel):
  email: EmailStr

class NfcRequest(BaseModel):
  picc_data: str
  cmac: str


class ProvisionRequest(BaseModel):
  tag_id: Annotated[str, Field(min_length=14, max_length=14, pattern=r'^[0-9a-fA-F]{14}$')]
  haj_id: UUID4


@app.middleware("http")
async def check_origin(request: Request, call_next):
  if request.method in ("GET", "HEAD", "OPTIONS"):
    return await call_next(request)

  origin = request.headers.get("origin")

  if origin:
    parsed = urlparse(origin)
    expected = urlparse(str(settings.base_url))
    if parsed.hostname != expected.hostname:
      return Response(
        content='{"detail":"Invalid origin"}',
        status_code=403,
        media_type="application/json",
      )

  return await call_next(request)


@api.get("/")
async def test():
  return "API is UP!"

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
  return get_scalar_api_reference(
      openapi_url=app.openapi_url,
  )

@api.post("/nfc/auth")
async def nfc_auth(tap: NfcRequest):
  picc_bytes = bytes.fromhex(tap.picc_data)
  iv = b'\x00' * 16
  cipher = AES.new(settings.key3, AES.MODE_CBC, iv)

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


@api.post('/nfc/provision')
async def provision(req: ProvisionRequest, current_user = Depends(get_current_active_user)):
  exists = await HajInfo.exists().where(
      HajInfo.uuid == req.haj_id,
      HajInfo.human == current_user.id,
  )
  if exists:
    try:
      tag_id = bytes.fromhex(req.tag_id)
    except Exception:
      raise HTTPException(status_code=400, detail="Invalid UID")
    key0 = secrets.token_bytes(16) # this one is the lock, you cant write or read secret data from the tag without it
    key3 = settings.key3 # this one has to be the same for everyone because when we have to decrypt picc we dont know the uid yet
    key4 = diversify_key(settings.master_key, tag_id, settings.system_id) # signature key

    existing = await NFCTable.exists().where(NFCTable.uid == tag_id.hex())
    if existing:
      raise HTTPException(status_code=403, detail="This tag uid already exists, please contact the admin if it's an issue for you")

    tag = NFCTable(uid=tag_id.hex(), haj_id=req.haj_id, key0=key0.hex(), key4=key4.hex(), status="active", created_at = datetime.datetime.now())
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
async def add_haj(
  req: NewHajRequest = Depends(haj_from_form),
  image: UploadFile = File(...),
  current_user = Depends(get_current_active_user)
):
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
      mloftearsabsorbed= req.mloftearsabsorbed,
      public=req.public
    ).save()
    try:
      img = Image.open(image.file)
      img.verify()
      image.file.seek(0)
      ext = img.format.lower() if img.format is not None else None
      if ext not in ("jpeg", "png", "gif", "webp"):
        raise HTTPException(status_code=400, detail="Unsupported image format")
    except Exception:
      raise HTTPException(status_code=400, detail="Invalid or corrupted image")

    contents = await image.read()
    size = len(contents)
    if size > settings.max_image_size * 1024 * 1024:
      raise HTTPException(status_code=400, detail="Image too large")

    s3.put_object(
      bucket_name=settings.s3.bucket,
      object_name=f"hajs/{haj_id}",
      data=BytesIO(contents),
      length=size,
      content_type=f"image/{ext}",
    )

    return {"status": "ok", "uuid": str(haj_id)}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@api.get('/haj/list')
async def list_hajs(
  current_user = Depends(get_current_active_user)
):
  hajs = await HajInfo.select(
    HajInfo.uuid,
    HajInfo.pronouns,
    HajInfo.name,
    HajInfo.public,
  ).where(HajInfo.human == current_user.id)
  return {"status": "ok", "hajs": hajs}

@api.get('/haj/image/{haj_id}')
async def get_haj_image(haj_id: UUID4, current_user = Depends(get_optional_user)):
  user_id = current_user.id if current_user else None
  if await check_haj_perm(user_id, haj_id):
    try:
      obj = s3.get_object(settings.s3.bucket, f"hajs/{haj_id}")
      return StreamingResponse(
        obj.stream(),
        media_type=obj.headers.get("Content-Type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=86400"}
      )
    except Exception:
      raise HTTPException(status_code=404, detail="Image not found")
  raise HTTPException(status_code=403, detail="Not authorized")


@api.post('/auth/register')
async def register(req: RegisterRequest):
  res = await create_user(req)
  if not res.get('ok'):
    raise HTTPException(status_code=400, detail=str(res.get('error', 'unknown')))
  try:
    jwt = create_verification_token(req.email)
    await mail.send_message(MessageSchema(
        recipients = [NameEmail(name=req.username, email=req.email)],
        subject = "Verify your Hajdentity account",
        body = verify_mail_template(req.username, f"{settings.base_url}register/verify?token={jwt}"),
        subtype = MessageType.html
    ))
  except Exception:
      await Humans.delete().where(Humans.email == req.email)
      raise HTTPException(status_code=500, detail=str(res.get('error', 'An error occured while sending you an email, please try again later.')))
  return {"status": "ok"}

@api.post('/auth/new_verification_token')
async def new_verif_token(req: NewTokenRequest ):
  human = await Humans.objects().get(Humans.email == req.email)
  if human is not None and not human.verified:
    try:
      jwt = create_verification_token(req.email)
      await mail.send_message(MessageSchema(
        recipients = [NameEmail(name=human.username, email=req.email)],
        subject = "Verify your Hajdentity account",
        body = verify_mail_template(human.username, f"{settings.base_url}register/verify?token={jwt}"),
        subtype = MessageType.html
      ))
    except Exception:
      raise HTTPException(status_code=500, detail="An error occured while sending you an email, please try again later.")
  return {"status": "ok"}

@api.post('/auth/verify')
async def verify(req: VerifyRequest):
  payload = verify_email_token(req.token)
  if payload is None:
    raise HTTPException(status_code=400, detail="Invalid token")

  human = await Humans.objects().get(Humans.email == payload.email)
  if human is not None and human.verified:
    return {"status": "ok", "email": payload.email}
  if payload.exp:
    raise HTTPException(status_code=403, detail="Token expired")
  if human is not None:
    await Humans.update({Humans.verified: True}).where(Humans.email == payload.email)
    return {"status": "ok", "email": payload.email}
  raise HTTPException(status_code=404, detail="This account does not exist")

@api.post('/auth/token')
async def token(response: Response, request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
  user = await authenticate_user(form_data.username, form_data.password)
  if not user:
    raise HTTPException(status_code=401, detail="Incorrect username or password")
  if not user.verified:
    raise HTTPException(status_code=403, detail="Email not verified. Please check your inbox.")

  session_id = await create_session(str(user.id), request)
  set_session_cookie(response, session_id)

  return {"username": user.username, "disabled": user.disabled}


@api.post('/auth/logout')
async def logout(request: Request, response: Response):
  session_id = request.cookies.get("session")
  if session_id:
    await delete_session(session_id)
  clear_session_cookie(response)
  return {"status": "ok"}


@api.get('/auth/me')
async def me(current_user = Depends(get_current_active_user)):
  return {"username": current_user.username, "disabled": current_user.disabled}

app.include_router(api)
