from piccolo.table import Table
from piccolo.columns import Varchar, Integer, Bytea


class NFCTable(Table):
    uid = Varchar(length=14, unique=True, index=True)
    secret_key = Bytea()
    last_counter = Integer(default=0)
