"""Server-authoritative multiplayer Snake Arena."""

import asyncio
import random
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

GRID_WIDTH, GRID_HEIGHT = 36, 24
TICK_SECONDS = 0.15
SPAWN_DELAY = 3.0
COLORS = ["#4f8f23", "#e59b23", "#8b4d99", "#277b9e", "#bf4242", "#6f7825"]
Point = Tuple[int, int]


@dataclass
class Player:
    name: str
    color: str
    snake: List[Point] = field(default_factory=list)
    direction: Point = (1, 0)
    next_direction: Point = (1, 0)
    score: int = 0
    alive: bool = False
    respawn_at: float = 0.0


class Arena:
    def __init__(self) -> None:
        self.players: Dict[str, Player] = {}
        self.clients: Dict[str, WebSocket] = {}
        self.food: Point = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.round_ends_at: Optional[float] = None
        self.lock = asyncio.Lock()

    def occupied(self) -> Set[Point]:
        return {cell for player in self.players.values() for cell in player.snake if player.alive}

    def spawn_food(self) -> None:
        free = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if (x, y) not in self.occupied()]
        self.food = random.choice(free) if free else (GRID_WIDTH // 2, GRID_HEIGHT // 2)

    def spawn_player(self, player: Player) -> None:
        for _ in range(100):
            x, y = random.randrange(3, GRID_WIDTH - 3), random.randrange(3, GRID_HEIGHT - 3)
            direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            tail = [(x - direction[0] * i, y - direction[1] * i) for i in range(4)]
            if all(0 <= a < GRID_WIDTH and 0 <= b < GRID_HEIGHT for a, b in tail) and not (set(tail) & self.occupied()):
                player.snake = tail
                player.direction = player.next_direction = direction
                player.alive = True
                return
        player.respawn_at = time.monotonic() + 1

    def state(self) -> dict:
        players = [
            {"id": key, "name": player.name, "color": player.color, "snake": player.snake,
             "score": player.score, "alive": player.alive}
            for key, player in self.players.items()
        ]
        players.sort(key=lambda item: item["score"], reverse=True)
        restart_in = max(0, (self.round_ends_at or 0) - time.monotonic())
        return {"type": "state", "width": GRID_WIDTH, "height": GRID_HEIGHT, "food": self.food, "players": players,
                "roundOver": self.round_ends_at is not None, "restartIn": round(restart_in, 1)}

    def start_new_round(self) -> None:
        self.round_ends_at = None
        for player in self.players.values():
            player.score = 0
            player.snake = []
            player.alive = False
        for player in self.players.values():
            self.spawn_player(player)
        self.spawn_food()

    async def broadcast(self) -> None:
        payload = self.state()
        stale = []
        for player_id, socket in self.clients.items():
            try:
                await socket.send_json(payload)
            except Exception:
                stale.append(player_id)
        for player_id in stale:
            self.clients.pop(player_id, None)
            self.players.pop(player_id, None)

    async def tick(self) -> None:
        async with self.lock:
            now = time.monotonic()
            if self.round_ends_at is not None:
                if now >= self.round_ends_at:
                    self.start_new_round()
                await self.broadcast()
                return
            for player in self.players.values():
                if not player.alive and now >= player.respawn_at:
                    self.spawn_player(player)

            moving = {key: player for key, player in self.players.items() if player.alive}
            next_heads = {}
            for key, player in moving.items():
                if (player.next_direction[0] != -player.direction[0] or player.next_direction[1] != -player.direction[1]):
                    player.direction = player.next_direction
                head_x, head_y = player.snake[0]
                dx, dy = player.direction
                next_heads[key] = (head_x + dx, head_y + dy)

            bodies = {cell for player in moving.values() for cell in player.snake}
            head_counts = {head: list(next_heads.values()).count(head) for head in next_heads.values()}
            dead = set()
            for key, head in next_heads.items():
                x, y = head
                if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT) or head in bodies or head_counts[head] > 1:
                    dead.add(key)

            ate = []
            if dead:
                for player in self.players.values():
                    player.alive = False
                    player.snake = []
                self.round_ends_at = now + SPAWN_DELAY
                await self.broadcast()
                return

            for key, player in moving.items():
                head = next_heads[key]
                player.snake.insert(0, head)
                if head == self.food:
                    player.score += 10
                    ate.append(key)
                else:
                    player.snake.pop()
            if ate:
                self.spawn_food()
        await self.broadcast()


arena = Arena()


async def game_loop() -> None:
    while True:
        started = time.monotonic()
        await arena.tick()
        await asyncio.sleep(max(0, TICK_SECONDS - (time.monotonic() - started)))


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(game_loop())
    yield
    task.cancel()


app = FastAPI(title="Snake Arena", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/")
async def home():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    player_id: Optional[str] = None
    try:
        join = await asyncio.wait_for(websocket.receive_json(), timeout=15)
        if join.get("type") != "join":
            await websocket.close(code=1008)
            return
        name = "".join(char for char in str(join.get("name", "Pilot")) if char.isalnum() or char in " _-").strip()[:18] or "Pilot"
        player_id = uuid.uuid4().hex[:8]
        async with arena.lock:
            player = Player(name=name, color=COLORS[len(arena.players) % len(COLORS)])
            arena.players[player_id] = player
            arena.clients[player_id] = websocket
            arena.spawn_player(player)
        await websocket.send_json({"type": "welcome", "id": player_id})
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "direction":
                direction = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}.get(message.get("direction"))
                if direction and player_id in arena.players:
                    arena.players[player_id].next_direction = direction
    except (WebSocketDisconnect, asyncio.TimeoutError):
        pass
    finally:
        if player_id:
            async with arena.lock:
                arena.clients.pop(player_id, None)
                arena.players.pop(player_id, None)

