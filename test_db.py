
from api.db import init_db, save_game_run, get_connection

init_db()

save_game_run("PotatoMan", 15000, True)

connection = get_connection()
results = connection.execute(
    "SELECT * FROM game_runs"
).fetchall()

print(results)

connection.close()