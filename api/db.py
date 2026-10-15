import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "game.db"


def init_db():
    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS game_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER NOT NULL,
            boss_defeated INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

def save_game_run(username, score, boss_defeated):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO game_runs (username, score, boss_defeated)
        VALUES (?, ?, ?)
        """,
        (username, score, int(boss_defeated))
    )

    connection.commit()
    connection.close()

