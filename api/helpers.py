from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from config import settings

def diversify_key(master_key, uid, system_id):
  div_data = b'\x01' + uid + settings.desfire_aid + system_id
  cobj = CMAC.new(master_key, ciphermod=AES)
  cobj.update(div_data)
  return cobj.digest()
