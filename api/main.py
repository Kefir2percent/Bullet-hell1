
from pathlib import Path

from pydantic import BaseModel

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from api.db import init_db, get_leaderboard, get_player_best_score, save_game_run

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

@app.get("/players/{name}")
async def player_profile(request: Request, name: str):
    best_score = get_player_best_score(name)

    player = {
        "username": name,
        "score": best_score,
        "defeated_boss": False  # Temporary until we query the database
    }

    return templates.TemplateResponse(
        request=request,
        name="player.html",
        context={"player": player}
    )


class GameResult(BaseModel):
    username: str
    score: int
    boss_defeated: bool


@app.post("/submit-score")
async def submit_score(result: GameResult):
    save_game_run(
        result.username,
        result.score,
        result.boss_defeated
    )
    return {"message": "Score saved"}
