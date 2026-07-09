from contextlib import asynccontextmanager
import datetime
import httpx
import string
from home.tables import Humans, HajInfo, NFCTable, SharkeyUsers
from fastapi import FastAPI, HTTPException, APIRouter, Depends, Form, Request, Response, UploadFile, File
from fastapi_mail import MessageSchema, MessageType
from piccolo.engine import engine_finder
import uuid
from pydantic import UUID4, BaseModel, EmailStr, NameEmail
from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from Crypto.Random import get_random_bytes
import base64
from helpers import diversify_key, decrypt_token
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
from typing import Annotated, Any
from pydantic import Field, field_validator
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
client = httpx.AsyncClient()

class HajListItem(BaseModel):
  uuid: UUID4
  displayname: str
  pronouns: str | None = None
  public: bool = True

class HajItem(BaseModel):
  uuid: UUID4
  human: UUID4
  displayname: str
  username: str
  date: datetime.date
  size: int
  description: str
  location: str| None = None
  pronouns: str | None = None
  gender: str | None = None
  floof: int | None = None
  squish: int | None = None
  lastwashed: datetime.datetime | None = None
  mloftearsabsorbed: int | None = None
  public: bool = True

class HajListResponse(BaseModel):
  status: str
  hajs: list[HajListItem]

class HajResponse(BaseModel):
  status: str
  haj: HajItem
  sharkey: dict[str, Any] | None = None

class NewHajRequest(BaseModel):
  username: Annotated[str, Field(pattern=r"^[a-z0-9_-]{3,48}$")]
  displayname: Annotated[str, Field(min_length=1, max_length=48)]
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

  @field_validator("displayname", mode="before")
  @classmethod
  def clean_displayname(cls, v: str) -> str:
    cleaned = v.strip()
    if not cleaned:
      raise ValueError("Display name cannot be blank")
    return cleaned

def haj_from_form(
  displayname: Annotated[str, Form(min_length=1, max_length=48)],
  username: Annotated[str, Form(pattern=r"^[a-z0-9_-]{3,48}$")],
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
    displayname=displayname,username=username, date=date, size=size,
    location=location, description=description, pronouns=pronouns,
    gender=gender, floof=floof, squish=squish, lastwashed=lastwashed,
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


@api.get("/", tags=["General"])
async def test():
  return "API is UP!"

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
  return get_scalar_api_reference(
      openapi_url=app.openapi_url,
  )

@api.post("/nfc/auth", tags=["NFC"])
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

  await tag.update({NFCTable.last_counter: counter})

  return {'status': 'ok', 'haj': tag.haj_id}

@api.post('/nfc/provision', tags=["NFC"])
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


@api.post('/hajs', tags=["Haj"])
async def add_haj(
  req: NewHajRequest = Depends(haj_from_form),
  image: UploadFile = File(...),
  pfp: UploadFile = File(...),
  current_user = Depends(get_current_active_user)
):
  haj_id = uuid.uuid4()
  i = None
  try:
    if await HajInfo.exists().where(HajInfo.username == req.username):
      raise HTTPException(status_code=400, detail="Username taken")
    await HajInfo( uuid=haj_id, human=current_user.id, displayname=req.displayname, username=req.username, date=req.date, size = req.size, location = req.location,
      description = req.description, pronouns = req.pronouns, gender = req.gender, floof = req.floof, squish = req.squish, lastwashed = req.lastwashed, mloftearsabsorbed= req.mloftearsabsorbed, public=req.public
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

    s3.put_object(bucket_name=settings.s3.bucket,object_name=f"hajs/{haj_id}", data=BytesIO(contents), length=size, content_type=f"image/{ext}")


    try:
      pfpimg = Image.open(pfp.file)
      pfpimg.verify()
      pfp.file.seek(0)
      pfpext = pfpimg.format.lower() if pfpimg.format is not None else None
      if pfpext not in ("jpeg", "png", "gif", "webp"):
        raise HTTPException(status_code=400, detail="Unsupported image format")
    except Exception:
      raise HTTPException(status_code=400, detail="Invalid or corrupted image")

    pfpcontents = await pfp.read()
    pfpsize = len(pfpcontents)
    if pfpsize > settings.max_image_size * 1024 * 1024:
      raise HTTPException(status_code=400, detail="Image too large")

    s3.put_object(
      bucket_name=settings.s3.bucket,
      object_name=f"pfp/{haj_id}",
      data=BytesIO(pfpcontents),
      length=pfpsize,
      content_type=f"image/{pfpext}",
    )

    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(chars) for _ in range(secrets.randbelow(65) + 64))

    await client.post(
      url=f"{settings.sharkey.base_url}api/admin/accounts/create",
      json={"username": req.username, "password": password},
      headers={"Authorization": f"Bearer {settings.sharkey.admin_api_token}"}
    )

    i = await client.post(
      url=f"{settings.sharkey.base_url}api/signin-flow",
      json={
        "username": req.username,
        "password": password,
        "frc-captcha-solution": None, "hcaptcha-response": None, "g-recaptcha-response": None, "m-captcha-response": None, "turnstile-response": None, "testcaptcha-response": None
      }
    )

    userid = i.json()["id"]
    userauth = i.json()["i"]


    tokenreq = await client.post(
      url=f"{settings.sharkey.base_url}api/miauth/gen-token",
      json={
        "session":None,
        "name":"Hajdentity",
        "permission":["read:account","write:account","read:blocks","write:blocks","read:drive","write:drive","read:favorites","write:favorites","read:following","write:following","read:messaging","write:messaging","read:mutes","write:mutes","write:notes","read:notes-schedule","write:notes-schedule","read:notifications","write:notifications","read:reactions","write:reactions","write:votes","read:pages","write:pages","write:page-likes","read:page-likes","read:user-groups","write:user-groups","read:channels","write:channels","read:gallery","write:gallery","read:gallery-likes","write:gallery-likes","read:flash","write:flash","read:flash-likes","write:flash-likes","write:invite-codes","read:invite-codes","write:clip-favorite","read:clip-favorite","read:federation","write:report-abuse","write:chat","read:chat"]
      },
      headers={"Authorization": f"Bearer {userauth}"}
    )

    token = tokenreq.json()["token"]
    image.file.seek(0)
    pfp.file.seek(0)

    pfpreq = await client.post(url=f"{settings.sharkey.base_url}api/drive/files/create", data = {"i": token, "force": True, "name": "pfp.png"}, files = {'file': ("pfp.png", pfp.file, "image/png")})
    bannerreq = await client.post(url=f"{settings.sharkey.base_url}api/drive/files/create", data = {"i": token, "force": True, "name": "banner.png"}, files = {'file': ("banner.png", image.file, "image/png")})

    parts = []
    pronouns_gender = f"{req.pronouns} - {req.gender}" if req.pronouns and req.gender else (req.pronouns or req.gender or None)
    if pronouns_gender:
      parts.append(pronouns_gender)
    parts.append(req.description)
    if req.size:
      parts.append(f"📏 {req.size}cm")
    if req.floof:
      floof_bar = '█' * req.floof + '░' * (10 - req.floof)
      parts.append(f"☁️ Fluffiness | {floof_bar} | {req.floof}/10")
    if req.squish:
      squish_bar = '█' * req.squish + '░' * (10 - req.squish)
      parts.append(f"🧸 Squishiness | {squish_bar} | {req.squish}/10")
    if req.lastwashed:
      parts.append(f"🧽 Last washed on {req.lastwashed.strftime('%c')}")
    parts.append(f"---\n⚠️🦈 This account is automated via [Hajdentity]({settings.base_url}plush/{haj_id}))!🦈⚠️")

    description_block = "\n\n".join(parts)

    await client.post(
      url=f"{settings.sharkey.base_url}api/i/update",
      json={
        "bannerId": bannerreq.json()["id"], "avatarId": pfpreq.json()["id"],
        "noCrawle":not req.public, "noindex": not req.public, "requireSigninToViewContents": not req.public,
        "enableRss":req.public, "isExplorable":req.public, "publicReactions": req.public,
        "makeNotesFollowersOnlyBefore":None if req.public else 1, "makeNotesHiddenBefore":None if req.public else 0,
        "followingVisibility":"public" if req.public else "private", "followersVisibility":"public" if req.public else "private",
        "chatScope":"mutual" if req.public else "none",
        "name": req.displayname, "birthday": req.date.strftime("%Y-%m-%d"), "location": req.location, "description": description_block,
        "attributionDomains": [settings.base_url.host],
        "autoAcceptFollowed":True,
        "preventAiLearning":True,
        "hideOnlineStatus":True,
        "isBot": True,
        "isCat": False
      },
      headers={"Authorization": f"Bearer {token}"}
    )

    await client.post(
      url=f"{settings.sharkey.base_url}api/i/registry/set",
      json={"scope":["client","base"],"key":"accountSetupWizard","value":-1},
      headers={"Authorization": f"Bearer {userauth}"}
    )

    nonce=get_random_bytes(12)
    cipher = AES.new(bytes.fromhex(settings.token_enc), AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(token.encode())

    blob = nonce + tag + ciphertext

    await SharkeyUsers(
      haj = haj_id,
      sharkey_id = userid,
      sharkey_key = base64.b64encode(blob).decode()
    ).save()

    return {"status": "ok", "uuid": str(haj_id)}
  except Exception as e:
    await HajInfo.delete().where(HajInfo.uuid == haj_id)
    s3.remove_object(settings.s3.bucket, f"hajs/{haj_id}")
    if i is not None:
      await client.post(
        url=f"{settings.sharkey.base_url}api/admin/delete-account",
        json={"userId":i.json()["id"]},
        headers={"Authorization": f"Bearer {settings.sharkey.admin_api_token}"}
      )
    print(e)
    raise HTTPException(status_code=500, detail="Something went wrong, try again later.")

@api.get('/hajs', response_model=HajListResponse, tags=["Haj"])
async def list_hajs(
  current_user = Depends(get_current_active_user)
):
  hajs = await HajInfo.select(
    HajInfo.uuid,
    HajInfo.pronouns,
    HajInfo.displayname,
    HajInfo.public,
  ).where(HajInfo.human == current_user.id)
  return {"status": "ok", "hajs": hajs}

@api.get('/hajs/{haj_id}', response_model=HajResponse, tags=["Haj"])
async def haj_info(haj_id: UUID4, current_user = Depends(get_optional_user)):
  user_id = current_user.id if current_user else None
  if await check_haj_perm(user_id, haj_id):
    haj = await HajInfo.select().where(HajInfo.uuid == haj_id).first()
    token_in_db = await SharkeyUsers.select(SharkeyUsers.sharkey_key).where(SharkeyUsers.haj == haj_id).first()
    if token_in_db is not None and haj is not None:
      try:
        token = decrypt_token(token_in_db["sharkey_key"])
        sharkey_user = await client.post(
          f"{settings.sharkey.base_url}api/users/show",
          json={'username': haj["username"]},
          headers={'Authorization': token}
        )
        return {"status": "ok", "haj": haj, "sharkey": sharkey_user.json()}
      except Exception:
        return {"status": "ok", "haj": haj}
    return {"status": "ok", "haj": haj}
  raise HTTPException(status_code=403, detail="Not authorized")

@api.get('/hajs/{haj_id}/image', tags=["Haj"])
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


@api.post('/auth/register', tags=["Auth"])
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

@api.post('/auth/new_verification_token', tags=["Auth"])
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

@api.post('/auth/verify', tags=["Auth"])
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

@api.post('/auth/token', tags=["Auth"])
async def token(response: Response, request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
  user = await authenticate_user(form_data.username, form_data.password)
  if not user:
    raise HTTPException(status_code=401, detail="Incorrect username or password")
  if not user.verified:
    raise HTTPException(status_code=403, detail="Email not verified. Please check your inbox.")

  session_id = await create_session(str(user.id), request)
  set_session_cookie(response, session_id)

  return {"username": user.username, "disabled": user.disabled}


@api.post('/auth/logout', tags=["Auth"])
async def logout(request: Request, response: Response):
  session_id = request.cookies.get("session")
  if session_id:
    await delete_session(session_id)
  clear_session_cookie(response)
  return {"status": "ok"}


@api.get('/auth/me', tags=["Auth"])
async def me(current_user = Depends(get_current_active_user)):
  return {"username": current_user.username, "disabled": current_user.disabled}

app.include_router(api)
