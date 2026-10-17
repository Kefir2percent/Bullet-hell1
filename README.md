# Bullet-hell1

Battle of Compensation

About the project

Battle of Compensation is a 2D bullet-hell game developed in Python using Pygame. The player fights a boss, avoids bullet patterns, shoots back, and tries to defeat the boss without losing all their lives.

The project also includes a website with a leaderboard and player profiles. Game results are submitted to a FastAPI server and stored in an SQLite database.

Features

Player movement, shooting, and focused movement.

Boss with multiple attack phases and bullet formations.

Player lives, score tracking, and collision detection.

Bomb mechanic that clears enemy bullets and uses score.

Different music during gameplay.

Win and lose conditions.

Website leaderboard displaying the best scores.

Player profiles showing high scores and boss-defeat status.

SQLite database for storing game results.

Technologies

Python

Pygame

FastAPI

Uvicorn

SQLite

HTML and CSS

Jinja2

Requests

Project structure
```text
Game_dev/
├── api/
│   ├── main.py
│   ├── db.py
│   ├── templates/
│   └── static/
├── assets/
├── client/
│   └── main.py
├── game/
│   ├── __init__.py
│   ├── formations.py
│   └── rules.py
├── Dizains.docx
├── README.md
├── requirements.txt
└── .gitignore
```

Requirements

Python 3

The Python packages listed in requirements.txt

Installation

Clone or download this repository.

Open a terminal in the project directory.

(Optional but recommended) Create and activate a virtual environment.

Install the required packages:
```bash
python -m pip install -r requirements.txt
```
Running the project

Start the website and API server from the project root:
```bash
python -m uvicorn api.main:app --reload
```

Open the website at:

http://127.0.0.1:8000/

To start the game, open a second terminal in the project root and run:
```bash
python -m client.main
```

The API server must be running for game results to be submitted to the leaderboard.

Controls

Arrow keys — move the player.

Shift — focused movement.

Z — shoot.

X — use a bomb.

Database

Game results are stored in an SQLite database. Each recorded run includes the player's username, score, whether the boss was defeated, and the time of the run.

The website uses the stored results to display the leaderboard and player statistics.

Win and lose conditions

Win: defeat the boss by reducing its health to zero.

Lose: lose all player lives.

Author


Created by Ralfs Riklāns and developed as a school project.
