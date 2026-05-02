from piccolo.table import Table
from piccolo.columns import Varchar, Integer, Time


class NFCTable(Table):
    user_id = Varchar()
    status = Varchar()
    uid = Varchar(length=14, unique=True, index=True)
    created_at = Time()
    last_counter = Integer(default=0)
