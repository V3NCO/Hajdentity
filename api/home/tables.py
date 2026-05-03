from piccolo.table import Table
from piccolo.columns import Varchar, Integer, Time, Text


class NFCTable(Table):
    uid = Varchar(length=14, unique=True, index=True)
    user_id = Varchar()
    key0 = Text()
    key4 = Text()
    last_counter = Integer(default=0)
    status = Varchar()
    created_at = Time()
