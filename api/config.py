from pydantic import AfterValidator, Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated

def hex_to_bytes(v: str | bytes) -> bytes:
    if isinstance(v, bytes):
        return v
    try:
        return bytes.fromhex(v)
    except ValueError:
        raise ValueError("Must be a valid hexadecimal string")

def ascii_encode(v: str) -> bytes:
    if isinstance(v, bytes):
        print(v)
        return v
    try:
        return v.encode("ASCII")
    except ValueError:
        raise ValueError("System ID must have ASCII character, make it more basic")

MKeyStr = Annotated[str, Field(min_length=32, max_length=32)]
MasterKey = Annotated[bytes, AfterValidator(hex_to_bytes), MKeyStr]

DesAIDStr = Annotated[str, Field(min_length=6, max_length=6)]
DesfireAID = Annotated[bytes, AfterValidator(hex_to_bytes), DesAIDStr]

SystemIDStr = Annotated[str, Field(max_length=32)]
SystemID = Annotated[bytes, AfterValidator(ascii_encode), SystemIDStr]

Key3Str = Annotated[str, Field(min_length=32, max_length=32)]
Key3 = Annotated[bytes, AfterValidator(hex_to_bytes), Key3Str]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='hajdentity_')
    master_key: MasterKey # 16 bytes AES 128 master key
    desfire_aid: DesfireAID = bytes.fromhex("48414A") # The application id, like its the global project
    system_id: SystemID # The ASCII bytes of the system identifier for this specific instance of the app, it shouldnt be changed to "prod", rather something describing the instance
    base_url: HttpUrl = HttpUrl("https://id.blahaj.engineering/api/nfc/auth") # The base URL written to the tag
    key3: Key3 # Key 3 is used to encode and decode the URL
    secret_key: Annotated[str, Field(min_length=128, max_length=128)]  # Secret key for encryption of user passwords in database
    access_token_expire_minutes: int = 30 # Minutes until user sessions expires
    algorithm: str = "HS256" # encryption algorithm of user passwords in database

settings = Settings()  # type: ignore[reportCallIssue]
