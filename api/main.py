
from pathlib import Path

from pydantic import BaseModel

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from api.db import init_db, get_leaderboard, get_player_best_score, save_game_run, get_player_boss_status, debug_game_runs

print("LOADED THE CORRECT api/main.py")

BASE_DIR = Path(__file__).resolve().parent




app = FastAPI()

init_db()

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

app.mount(
    "/assets",
    StaticFiles(directory=str(BASE_DIR.parent / "assets")),
    name="assets"
)


@app.get("/")
async def leaderboard(request: Request):
    scores = get_leaderboard()


    return templates.TemplateResponse(
        request=request,
        name="leaderboard.html",
        context={"scores": scores}
    )


@app.get("/rules")
async def rules(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="rules.html",
        context={}
    )


class GameResult(BaseModel):
    username: str
    score: int
    boss_defeated: bool


@app.post("/submit-score")
async def submit_score(result: GameResult):
    print(
    "Received result:",
    result.username,
    result.boss_defeated,
    )
    save_game_run(
        result.username,
        result.score,
        result.boss_defeated
    )
    debug_game_runs(result.username)
    return {"message": "Score saved"}


@app.get("/players/{name}")
async def player_profile(request: Request, name: str):
    best_score = get_player_best_score(name)
    defeated_boss = get_player_boss_status(name)


    print("PROFILE DEBUG:")
    print("Requested username:", repr(name))
    print("Best score:", best_score)
    print("Boss status:", repr(defeated_boss))

    player = {
        "username": name,
        "score": best_score,
        "defeated_boss": defeated_boss
    }

    return templates.TemplateResponse(
        request=request,
        name="player.html",
        context={"player": player}
    )