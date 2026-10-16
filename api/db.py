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


def get_leaderboard():
    connection = get_connection()

    results = connection.execute("""
        SELECT username, MAX(score) AS best_score
        FROM game_runs
        GROUP BY username
        ORDER BY best_score DESC
        LIMIT 5
    """).fetchall()

    connection.close()
    return results

def get_player_best_score(username):
    connection = get_connection()

    result = connection.execute(
        """
        SELECT MAX(score)
        FROM game_runs
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    connection.close()
    return result[0]

def get_player_boss_status(username):
    connection = get_connection()

    result = connection.execute(
        """
        SELECT MAX(boss_defeated)
        FROM game_runs
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    connection.close()
    return bool(result[0]) if result[0] is not None else False

def debug_game_runs(username):
    connection = get_connection()

    results = connection.execute(
        """
        SELECT username, score, boss_defeated
        FROM game_runs
        WHERE username = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (username,)
    ).fetchall()

    connection.close()
    print("Saved game runs:", results)