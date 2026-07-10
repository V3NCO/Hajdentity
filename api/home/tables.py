from piccolo.table import Table
from piccolo.columns import UUID, Timestamptz,  Numeric, Date, Varchar, Integer, Time, Text, Boolean


class NFCTable(Table):
  uid = Varchar(length=14, unique=True, index=True)
  haj_id = UUID()
  key0 = Text()
  key4 = Text()
  last_counter = Integer(default=0)
  status = Varchar()
  created_at = Time()


# From former Blahaj Identity:
# export const blahajsTable = pgTable('blahajs', {
# 	id: integer().primaryKey().generatedAlwaysAsIdentity(), // the primary key
# 	uuid: uuid(), // the profile id
# 	name: varchar({ length: 255 }).notNull(), // the name of the haj
# 	date: date(), // the date the blahaj was adopted
# 	size: varchar({ length: 255 }).notNull(), // the size of the haj
# 	location: text(), // where the blahaj was adopted
# 	description: text(),
# 	pronouns: varchar({ length: 255 }).notNull(), // the blahaj's pronouns!
# 	gender: varchar({ length: 255 }).notNull(), // the blahaj's gender!
# 	floof: integer(), // level of floofiness on a scale of 1-10 (stars with halves)
# 	squish: integer(), // The level of squishiness on a scale of 1-10 (stars with halves)
# 	lastwashed: date(), // last time the haj has been washed
# 	mloftearsabsorbed: real() //i want to make this an easter egg
# });


class HajInfo(Table):
  uuid = UUID(unique=True, null=False, index=True)
  human = UUID(null=False)
  displayname = Varchar(255, null=False)
  username = Varchar(255, null=False)
  date = Date(null=False)
  size = Numeric(null=False)
  location = Text(null=True)
  description = Text(null=False)
  pronouns = Varchar(255,null=True)
  gender = Varchar(255,null=True)
  floof = Integer(null=True)
  squish = Integer(null=True)
  lastwashed = Timestamptz(null=True)
  mloftearsabsorbed = Numeric(null=True)


class Humans(Table):
  id = UUID(primary_key=True, null=False)
  username = Varchar(length=100, unique=True, null=False)
  email = Varchar(length=256, unique=True, null=False)
  hashed_password = Varchar(length=512, null=True)
  verified = Boolean(default=False)
  disabled = Boolean(default=False)

class Sessions(Table):
  id = UUID(primary_key=True, null=False)
  user_id = UUID(null=False)
  session_id = Varchar(length=64, unique=True, null=False, index=True)
  created_at = Timestamptz(null=False)
  last_seen_at = Timestamptz(null=False)
  user_agent = Text(null=True)
  ip_address = Varchar(length=45, null=True)

class SharkeyUsers(Table):
  id = UUID(primary_key=True, null=False)
  haj = UUID(null=False)
  sharkey_id = Varchar(length=128, unique=True, null=False)
  sharkey_key = Text(null=False)

class Posts(Table):
  id = UUID(primary_key=True, null=False)
  haj = UUID(null=False)
  sharkey_id = Varchar(length=128, unique=True, null=False)
  sharkey_file = Varchar(length=128, null=False)
  text = Text()
  cw = Text(null=True)
  created_at = Timestamptz(null=False)
