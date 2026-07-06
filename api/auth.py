import asyncio
import hashlib
import secrets
import uuid
import jwt
from datetime import datetime, timedelta, timezone
from typing import Literal, TypedDict
from pwdlib import PasswordHash
from pydantic import UUID4, BaseModel
from fastapi import Depends, HTTPException, Request, Response
from home.tables import HajInfo, Humans, Sessions
from config import settings

password_hash = PasswordHash.recommended()
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

class CookieKwargs(TypedDict):
  httponly: bool
  secure: bool
  samesite: Literal["lax", "strict", "none"]
  path: str
  domain: str | None

DOMAIN = settings.cookie_domain

def _cookie_kwargs() -> CookieKwargs:
  return {
    "httponly": True,
    "secure": settings.cookie_secure,
    "samesite": "strict",
    "path": "/api",
    "domain": DOMAIN,
  }


class VerifPayload(BaseModel):
  email: str | None
  exp: bool


class User(BaseModel):
  id: UUID4
  username: str
  public_key: str | None = None
  disabled: bool | None = None
  verified: bool | None = None


class UserInDB(User):
  hashed_password: str


def verify_password(plain_password, hashed_password):
  return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
  return password_hash.hash(password)


def _create_session_id() -> str:
  return hashlib.sha256(secrets.token_bytes(64)).hexdigest()


async def create_session(user_id: str, request: Request) -> str:
  session_id = _create_session_id()
  now = datetime.now(timezone.utc)
  await Sessions.insert(Sessions(
    id=uuid.uuid4(),
    user_id=user_id,
    session_id=session_id,
    created_at=now,
    last_seen_at=now,
    user_agent=request.headers.get("user-agent"),
    ip_address=request.client.host if request.client else None,
  ))
  return session_id


def set_session_cookie(response: Response, session_id: str):
  max_age = settings.session_absolute_days * 86400
  response.set_cookie(
    "session", session_id,
    max_age=max_age, **_cookie_kwargs()
  )


def clear_session_cookie(response: Response):
  response.delete_cookie("session", **_cookie_kwargs())


async def delete_session(session_id: str):
  await Sessions.delete().where(Sessions.session_id == session_id)


async def touch_session(session_id: str):
  now = datetime.now(timezone.utc)
  await Sessions.update({Sessions.last_seen_at: now}).where(
    Sessions.session_id == session_id
  )


async def validate_session(session_id: str) -> UserInDB | None:
    session_row = await Sessions.select().where(Sessions.session_id == session_id).first()
    if not session_row:
      return None

    now = datetime.now(timezone.utc)
    idle_cutoff = now - timedelta(minutes=settings.session_idle_minutes)
    absolute_cutoff = now - timedelta(days=settings.session_absolute_days)

    if session_row["last_seen_at"] < idle_cutoff or session_row["created_at"] < absolute_cutoff:
      await Sessions.delete().where(Sessions.id == session_row["id"])
      return None

    user_dict = await Humans.select().where(Humans.id == session_row["user_id"]).first()
    if not user_dict:
      return None

    await touch_session(session_id)
    return UserInDB(**user_dict)

async def get_user(username: str | None):
  if username is None:
    return None
  user_dict = await Humans.select().where(Humans.username == username).first()
  if user_dict:
    return UserInDB(**user_dict)
  return None


async def authenticate_user(username: str, password: str):
  user = await get_user(username)
  if not user:
    return False
  verified = await asyncio.to_thread(verify_password, password, user.hashed_password)
  if not verified:
    return False
  return user


async def create_user(form_data):
  # form_data is expected to have 'username' and 'password' attributes
  unameexists = await Humans.exists().where(Humans.username == form_data.username)
  emailexists = await Humans.exists().where(Humans.email == form_data.email)
  if unameexists:
    return {"ok": False, "error": "This username is taken!"}
  if emailexists:
      return {"ok": False, "error": "This email is taken!"}
  try:
    pwd = get_password_hash(form_data.password)
    # create with explicit UUID to avoid depending on DB defaults
    user_id = uuid.uuid4()
    await Humans.insert(Humans(
      id=user_id,
      email=form_data.email,
      username=form_data.username,
      hashed_password=pwd
    ))
    return {"ok": True}
  except Exception:
    return {"ok": False, "error": "An internal error occurred. Please try again."}


async def get_current_user(request: Request):
  session_id = request.cookies.get("session")
  if not session_id:
    raise HTTPException(status_code=401, detail="Not authenticated")

  user = await validate_session(session_id)
  if not user:
    clear_session_cookie(Response())
    raise HTTPException(status_code=401, detail="Session expired")
  return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
  if current_user.disabled:
    raise HTTPException(status_code=403, detail="Inactive user")
  if not current_user.verified:
    raise HTTPException(status_code=403, detail="User not verified")
  return current_user

def create_verification_token(email: str) -> str:
  return jwt.encode({
    "sub": email,
    "type": "verify",
    "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.verification_token_expire_minutes)
  }, SECRET_KEY, algorithm=ALGORITHM)

def verify_email_token(token: str) -> VerifPayload | None:
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("type") != "verify":
      return None
    return VerifPayload(email=str(payload.get("sub")), exp=False)
  except jwt.ExpiredSignatureError:
    return VerifPayload(email=None, exp=True)
  except jwt.PyJWTError:
    return None

async def check_haj_perm(user_id: UUID4, haj_id: UUID4):
  haj = await HajInfo.objects().get(HajInfo.uuid == haj_id)
  if not haj:
    return False
  if not haj.public:
    if haj.human == user_id:
      return True
    return False
  return True
