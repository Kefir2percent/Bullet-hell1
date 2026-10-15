
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from api.db import init_db

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
    return templates.TemplateResponse(
        request=request,
        name="leaderboard.html",
        context={}
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
    player = {
        "username": name,
        "score": 245800,
        "defeated_boss": True
    }

    return templates.TemplateResponse(
        request=request,
        name="player.html",
        context={"player": player}
    )
