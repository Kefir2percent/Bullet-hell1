
from api.db import init_db, save_game_run, get_connection
from api.db import get_leaderboard

init_db()

save_game_run("PotatoMan", 15000, True)

connection = get_connection()
results = connection.execute(
    "SELECT * FROM game_runs"
).fetchall()

print(results)
print(get_leaderboard())

connection.close()