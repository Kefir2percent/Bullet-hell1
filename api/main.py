
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)


@app.get("/")
async def leaderboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="leaderboard.html",
        context={}
    )
