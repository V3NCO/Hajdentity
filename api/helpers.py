from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from constants import DIVERSITY_CONSTANT, DESFIRE_AID

def diversify_key(master_key, uid, system_id):
    div_data = DIVERSITY_CONSTANT + uid + DESFIRE_AID + system_id
    cobj = CMAC.new(master_key, ciphermod=AES)
    cobj.update(div_data)
    return cobj.digest()
