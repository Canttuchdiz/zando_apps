from EasySqlite import *
import sqlite3
from functools import cached_property



instance = EasySqlite("user_data")
# instance.add_user("3123123", "Baka", "mod_list")
# instance.create_table("mod_list", "ID", "Username")
value = instance.user_check("520741459478052886", "mod_list")

print(value)
