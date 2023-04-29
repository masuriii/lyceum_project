import sqlite3


class Database:
    _db: sqlite3.Connection

    def __init__(self, name: str):
        self._db = sqlite3.connect(name)
        self._db.row_factory = sqlite3.Row

        self._db.execute("""CREATE TABLE IF NOT EXISTS users(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                language STRING)""")

        self._db.execute("""CREATE TABLE IF NOT EXISTS courses(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                title STRING NOT NULL,
                                text TEXT NOT NULL,
                                images_ids STRING,
                                examples TEXT,
                                additional_link STRING)""")

        self._db.commit()

    def get_user_by_userid(self, user_id: int):
        cur = self._db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cur.fetchone()

    def add_user(self, user_id: int):
        if not self.get_user_by_userid(user_id):
            self._db.execute("INSERT INTO users(user_id) VALUES (?)", (user_id,))
            self._db.commit()

    def edit_user(self, user_id: int, **kwargs):
        for k, v in kwargs.items():
            self._db.execute(f"UPDATE users SET {k} = ? WHERE user_id = ?", (v, user_id))
        self._db.commit()

    def get_courses(self):
        cur = self._db.execute("SELECT * FROM courses")
        return cur.fetchall()

    def get_course_by_id(self, course_id: int):
        cur = self._db.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        return cur.fetchone()

    def add_course(self, title: str, text: str, images_ids: str = None, examples: str = None,
                   additional_links: str = None):
        self._db.execute(
            "INSERT INTO courses(title, text, images_ids, examples, additional_link) VALUES (?, ?, ?, ?, ?)",
            (title, text, images_ids, examples, additional_links))
        self._db.commit()

    def delete_course(self, course_id: int):
        self._db.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        self._db.commit()
