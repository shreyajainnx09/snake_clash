# Snake Clash

Real-time multiplayer Snake Clash built with FastAPI, WebSockets, HTML5 Canvas, and vanilla JavaScript. The Python server owns all game state; browsers only send direction inputs and render server updates.

## Run locally

Requires Python 3.10+ for the documented setup (the code is also compatible with Python 3.9).

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn snake_clash:app --reload --port 8002
```

Open http://127.0.0.1:8002 in two or more browser tabs to play together. Use arrow keys or WASD. Pressing a direction updates the server, which broadcasts game state ten times a second.

## Deploy to Render

1. Create an empty GitHub repository named `snake-clash` and push this folder's contents to it.
2. In Render, choose **New → Blueprint** and select the repository, or create a Web Service manually.
3. Render will use `render.yaml`; the start command is `uvicorn app:app --host 0.0.0.0 --port $PORT`.

Railway can use the included `Procfile` with the same start command.

## Project layout

```text
python/
├── snake_clash.py      # FastAPI + authoritative WebSocket game loop
├── static/             # Canvas interface, CSS, and browser client
├── requirements.txt
├── Procfile
└── render.yaml
```
