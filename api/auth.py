import asyncio
import uuid
import jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from pydantic import UUID4, BaseModel
import smtplib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from email.mime.text import MIMEText
from home.tables import Humans
import constants

password_hash = PasswordHash.recommended()
SECRET_KEY = constants.SECRET_KEY
ALGORITHM = constants.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = constants.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class Token(BaseModel):
  access_token: str
  token_type: str


class TokenData(BaseModel):
  username: str | None = None


class User(BaseModel):
  id: UUID4
  username: str
  public_key: str | None = None
  disabled: bool | None = None


class UserInDB(User):
  hashed_password: str


def verify_password(plain_password, hashed_password):
  return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
  return password_hash.hash(password)


async def get_user(username: str | None):
  if username is None:
    return None
  is_in_db = await Humans.exists().where(Humans.username == username)
  if is_in_db:
    user_dict = await Humans.select().where(Humans.username == username)
    return UserInDB(**user_dict[0])


async def authenticate_user(username: str, password: str):
  user = await get_user(username)
  if not user:
    return False
  verified = await asyncio.to_thread(verify_password, password, user.hashed_password)
  if not verified:
    return False
  return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt


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
  except Exception as error:
    return {"ok": False, "error": str(error)}


async def get_current_user(token: str = Depends(oauth2_scheme)):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str | None = payload.get("sub")
    if username is None:
      raise credentials_exception
    token_data = TokenData(username=username)
  except jwt.PyJWTError:
    raise credentials_exception
  user = await get_user(token_data.username)
  if user is None:
    raise credentials_exception
  return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
  if current_user.disabled:
    raise HTTPException(status_code=400, detail="Inactive user")
  return current_user
