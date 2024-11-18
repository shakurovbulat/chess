import sqlite3


def delete():
    with sqlite3.connect('mov.sqlite') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM moves;")


def add():
    with sqlite3.connect('mov.sqlite') as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE moves (
        id INTEGER,
        start TEXT NOT NULL,
        end TEXT NOT NULL,
        type_from TEXT,
        type_to TEXT,
        color TEXT,
        id_move INTEGER
        );
        """)


add()