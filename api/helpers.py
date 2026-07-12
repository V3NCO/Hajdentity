from Crypto.Cipher import AES
from Crypto.Hash import CMAC
import base64
from home.tables import Friends, HajInfo, Sessions, Humans
from config import settings
import datetime
from auth import User
import app

def diversify_key(master_key, uid, system_id):
  div_data = b'\x01' + uid + settings.desfire_aid + system_id
  cobj = CMAC.new(master_key, ciphermod=AES)
  cobj.update(div_data)
  return cobj.digest()

def decrypt_token(blob: str) -> str:
    raw = base64.b64decode(blob)

    nonce = raw[:12]
    tag = raw[12:28]
    ciphertext = raw[28:]

    cipher = AES.new(bytes.fromhex(settings.token_enc), AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

    return plaintext.decode()

async def cleanup_codes():
  codes = await Friends.objects().where(Friends.code.is_not_null())
  for code in codes:
    now = datetime.datetime.now(datetime.timezone.utc)
    expiry = now - datetime.timedelta(minutes=settings.nfc_session_minutes)

    if code.created_at < expiry:
      await code.remove()

async def delete_user(user: User):
  hajs = await HajInfo.select().where(HajInfo.human == user.id)
  for haj in hajs:
    await app.delete_haj(haj['uuid'], user)
  await Sessions.delete().where((Sessions.associated == user.id) & (Sessions.type == 'user'))
  await Humans.delete().where(Humans.id == user.id)
