from piccolo.table import Table
from piccolo.columns import UUID, Timestamptz,  Numeric, Date, Varchar, Integer, Time, Text


class NFCTable(Table):
    uid = Varchar(length=14, unique=True, index=True)
    user_id = Varchar()
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
  name = Varchar(255, null=False)
  date = Date()
  size = Numeric(null=False)
  location = Text()
  description = Text()
  pronouns = Varchar(255)
  gender = Varchar(255)
  floof = Integer()
  squish = Integer(),
  lastwashed = Timestamptz()
  mloftearsabsorbed = Numeric()
