from pydantic import AfterValidator, EmailStr, Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated
from fastapi_mail import FastMail, ConnectionConfig

def hex_to_bytes(v: str | bytes) -> bytes:
    if isinstance(v, bytes):
        return v
    try:
        return bytes.fromhex(v)
    except ValueError:
        raise ValueError("Must be a valid hexadecimal string")

def ascii_encode(v: str) -> bytes:
    if isinstance(v, bytes):
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

class MailSettings(BaseSettings):
    username: str = "default"
    password: SecretStr = SecretStr("password")
    from_address: EmailStr = "from@example.com"
    from_name: str = "default"
    port: int = 587
    server: str = "default"
    starttls: bool = True
    ssl_tls: bool = False
    use_creds: bool = True
    validate_certs : bool = True

class DatabaseSettings(BaseSettings):
    database: str = "hajdentity"
    user: str = "postgres"
    password: str = ""
    host: str = "localhost"
    port: int = 5432

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='HAJDENTITY_',  env_nested_delimiter='__')
    master_key: MasterKey # 16 bytes AES 128 master key
    desfire_aid: DesfireAID = bytes.fromhex("48414A") # The application id, like its the global project
    system_id: SystemID # The ASCII bytes of the system identifier for this specific instance of the app, it shouldnt be changed to "prod", rather something describing the instance
    base_url: HttpUrl = HttpUrl("https://id.blahaj.engineering/") # The base URL
    key3: Key3 # Key 3 is used to encode and decode the URL
    secret_key: Annotated[str, Field(min_length=128, max_length=128)]  # Secret key for encryption of user passwords in database
    access_token_expire_minutes: int = 30 # Minutes until user sessions expires
    verification_token_expire_minutes: int = 1440 # Minutes until verification token expires
    algorithm: str = "HS256" # encryption algorithm of user passwords in database
    mail: MailSettings = MailSettings()
    db: DatabaseSettings = DatabaseSettings()

settings = Settings()  # type: ignore[reportCallIssue]


mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.mail.username,
    MAIL_PASSWORD=settings.mail.password,
    MAIL_FROM=settings.mail.from_address,
    MAIL_PORT=settings.mail.port,
    MAIL_SERVER=settings.mail.server,
    MAIL_FROM_NAME=settings.mail.from_name,
    MAIL_STARTTLS=settings.mail.starttls,
    MAIL_SSL_TLS=settings.mail.ssl_tls,
    USE_CREDENTIALS=settings.mail.use_creds,
    VALIDATE_CERTS=settings.mail.validate_certs,
    # TEMPLATE_FOLDER=Path(BASE_DIR, "templates"),
)


mail = FastMail(config=mail_config)
