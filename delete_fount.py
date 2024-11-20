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
        id_move INTEGER,
        type_move TEXT,
        cord_from TEXT,
        cord_to TEXT,
        type_figure_from TEXT,
        type_figure_to TEXT,
        color_from TEXT
        );
        """)


add()
