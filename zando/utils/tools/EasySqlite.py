import sqlite3


class EasySqlite():

    """
    Wraps sqlite3 to my liking.
    """


    def __init__(self, filename):
        self.con = sqlite3.connect(filename + ".db")
        self.separator = ', '
        self.filename = filename

    def create_table(self, table_name : str, *args : str) -> None:
        """
        Creates table with given arguments.
        If isn't file with given name, one is created.
        :param table_name:
        :param args:
        :return:
        """
        cursor = self.con.cursor()

        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS {0} ({1})""".format(table_name, self.separator.join(args)))
        except Exception:
            print("Table exists already.")

    def add_user(self, user_id : str, user_name : str, table_name : str) -> None:

        """
        Adds user to columns for use cases.
        :param user_id:
        :param user_name:
        :param table_name:
        :return:
        """

        valid_tables = [table_name]

        if table_name not in valid_tables:
            return

        cursor = self.con.cursor()
        code = """INSERT INTO {0} VALUES (?, ?)""".format(table_name)
        cursor.execute(code, (str(user_id), user_name))
        self.con.commit()

    def user_check(self, id : str, table_name : str) -> bool:

        cursor = self.con.cursor()
        cursor.execute("""SELECT ID FROM {0} WHERE ID=?""".format(table_name), (id, ))
        result = cursor.fetchone()
        if result is not None:
            return True
        return False




