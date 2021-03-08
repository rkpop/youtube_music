import os
import sqlite3


class DB:

    __instance = None
    __instantiation_key = "THIS_IS_TO_STUPIDLY_ENFORCE_SINGLETON_IN_PYTHON"

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = DB(instantiation_key=DB.__instantiation_key)
        return cls.__instance

    def __init__(self, instantiation_key=None):
        assert (
            instantiation_key == DB.__instantiation_key
        ), "Use the DB.get() method to connect to the database"
        self.conn = sqlite3.connect(os.environ["DB_PATH"])

    def get_playlist(self, month, year):
        c = self.conn.cursor()
        c.execute(
            'SELECT playlist_id FROM "playlists" WHERE "month"=? AND "year"=?',
            (
                month,
                year,
            ),
        )
        result = c.fetchone()
        if result is None:
            return None
        return result[0]

    def add_playlist(self, playlist_id, name, month, year):
        c = self.conn.cursor()
        c.execute(
            'INSERT INTO "playlists" (playlist_id, name, month, year) VALUES (?, ?, ?, ?)',
            (playlist_id, name, month, year),
        )
        self.conn.commit()
        c.close()

    def is_processed(self, release_uri):
        c = self.conn.cursor()
        c.execute(
            'SELECT 1 FROM "processed" WHERE "uri"=?',
            (release_uri,),
        )
        return c.fetchone() is not None

    def mark_processed(self, release_uri):
        c = self.conn.cursor()
        c.execute(
            'INSERT INTO "processed" (uri) VALUES (?)',
            (release_uri,),
        )
        self.conn.commit()
        c.close()
