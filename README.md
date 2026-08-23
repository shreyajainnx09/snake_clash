<div align="center">

# 🐍 Snake Clash
### Real-time multiplayer Snake, built with FastAPI, WebSockets & HTML5 Canvas

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
[![WebSockets](https://img.shields.io/badge/WebSockets-black?style=for-the-badge&logo=socketdotio&logoColor=white)](https://img.shields.io/badge/WebSockets-black?style=for-the-badge&logo=socketdotio&logoColor=white)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
[![Play Now](https://img.shields.io/badge/🎮%20PLAY%20NOW-6C3EB8?style=for-the-badge)](https://snake-clash-9sb4.onrender.com)

</div>

---

## 📌 Description

A **real-time multiplayer** take on the classic Snake game. Open it in two or more browser tabs and play head-to-head — the Python server owns all game state, and every connected browser just sends direction inputs and renders whatever the server broadcasts.

- **Authoritative server**: all game logic lives in Python; clients never simulate movement themselves
- Multiple players compete live in the same arena over **WebSockets**
- Server broadcasts the game state **10 times a second** to keep everyone in sync
- Rendered client-side on an **HTML5 Canvas** with vanilla JavaScript — no frontend framework needed
- **[Play it live](https://snake-clash-9sb4.onrender.com)** — deployed on Render

## 🎮 Controls

| Key | Action |
|---|---|
| Arrow keys / WASD | Steer your snake |

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| 🐍 Python | Server-side game logic |
| ⚡ FastAPI | Web server and routing |
| 🔌 WebSockets | Real-time, bidirectional game state sync |
| 🌐 HTML5 / Canvas | Client rendering |
| 🟨 Vanilla JavaScript | Browser-side input handling and rendering |

## ⚙️ Setup

**Requirements**
- Python 3.10+ (also compatible with 3.9)

```bash
git clone https://github.com/shreyajainnx09/snake_clash.git
cd snake_clash
python3 -m venv venv
source venv/bin/activate       # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Run

```bash
uvicorn snake_clash:app --reload --port 8002
```

Then open `http://127.0.0.1:8002` in **two or more browser tabs** to play together — or just head straight to the [live deployment](https://snake-clash-9sb4.onrender.com).

## ☁️ Deploy to Render

1. Create an empty GitHub repository named `snake-clash` and push this project's contents to it.
2. In Render, choose **New → Blueprint** and select the repository, or create a Web Service manually.
3. Render uses `render.yaml`; the start command is `uvicorn app:app --host 0.0.0.0 --port $PORT`.

Railway can use the included `Procfile` with the same start command.

## 🧠 How It Works

- `snake_clash.py` runs a FastAPI app with a WebSocket endpoint that acts as the **authoritative game loop** — it tracks every connected player's snake, position, and score
- Clients send only directional input (arrow keys / WASD); the server validates moves, updates positions, and detects collisions
- The updated game state is broadcast to all connected clients ~10 times per second
- The browser client (in `static/`) is a thin renderer: it draws whatever state it receives onto an HTML5 Canvas and forwards keypresses back to the server

## 📁 Project Structure

```
snake_clash/
│
├── snake_clash.py       → FastAPI app + authoritative WebSocket game loop
├── static/              → Canvas UI, CSS, and browser client JS
├── requirements.txt     → Python dependencies
├── Procfile             → Start command for Railway
├── render.yaml          → Render deployment blueprint
└── README.md
```

## 🌟 Ideas for Extending

- Add player names, colors, and a live leaderboard
- Add power-ups (speed boost, shrink, invincibility)
- Add rooms/lobbies instead of one global arena
- Add spectator mode and match history
- Persist high scores to a database

## 👩🏻‍💻 Author

**Shreya Jain**
BCA | Data Analytics | Python | SQL | Tableau
