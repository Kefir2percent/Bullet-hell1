from api.db import get_connection

connection = get_connection()

rows = connection.execute("""
    SELECT username, COUNT(*) AS runs
    FROM game_runs
    GROUP BY username
    ORDER BY username
""").fetchall()

for row in rows:
    print(row)

connection.close()