import os
import sqlite3
from collections import namedtuple
from .entity import Entity


def namedtuple_factory(cursor, row):
    # http://peter-hoffmann.com/2010/python-sqlite-namedtuple-factory.html
    """
    Usage:
    con.row_factory = namedtuple_factory
    """
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    r = Row(*row)
    entity = Entity()

    entity.id = r.id
    entity.title = r.title
    entity.url = r.url
    entity.date = r.date
    entity.cover = r.cover
    entity.channel = r.channel
    entity.poster_id = r.poster_id
    entity.poster_name = r.poster_name
    entity.banana = r.banana
    entity.stow = r.stow
    entity.download_url = r.download_url

    return entity


class DB:
    def __init__(self, filepath):
        existence = os.path.exists(filepath)
        self.conn = sqlite3.connect(filepath)

        if not existence:
            self.conn.execute('''CREATE TABLE entity (
                id	TEXT NOT NULL,
                title	TEXT,
                url	TEXT,
                date	INTEGER,
                cover	TEXT,
                channel	TEXT,
                poster_id	TEXT,
                poster_name	TEXT,
                banana	INT,
                stow	INT,
                download_url	TEXT,
                PRIMARY KEY(id)
            );''')
            self.conn.commit()

        self.conn.row_factory = namedtuple_factory

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def save_entity(self, entity):
        c = self.conn.cursor()

        c.execute('INSERT OR REPLACE INTO entity (id, title, url, date, cover, channel, poster_id, poster_name, banana, stow, download_url) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                  (entity.id, entity.title, entity.url, entity.date,entity.cover, entity.channel, entity.poster_id, entity.poster_name, entity.banana, entity.stow, entity.download_url))

        self.conn.commit()

    def update_entity(self, entity):
        c = self.conn.cursor()
        c.execute('UPDATE OR REPLACE entity SET title = ?, url = ?, date = ?, cover = ?, channel = ?, poster_id = ?, poster_name = ?, banana = ?, stow = ?, download_url = ? where id = ?',
                  (entity.title, entity.url, entity.date,entity.cover, entity.channel, entity.poster_id, entity.poster_name, entity.banana, entity.stow, entity.download_url, entity.id))

        self.conn.commit()

    def get_all_entities(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM entity;")
        return c.fetchall()

    def get_entity_by_id(self, id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM entity WHERE id = ?", (id,))
        return c.fetchone()
