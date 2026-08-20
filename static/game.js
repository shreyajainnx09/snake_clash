const canvas = document.querySelector('#game');
const ctx = canvas.getContext('2d');
const overlay = document.querySelector('#overlay');
const form = document.querySelector('#join-form');
const roundMessage = document.querySelector('#round-message');
const status = document.querySelector('#connection');
const leaderboard = document.querySelector('#leaderboard');

let socket;
let me = null;
let state = null;
let queuedDirection = null;

function connect(name) {
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
  socket = new WebSocket(`${protocol}://${location.host}/ws`);
  socket.onopen = () => {
    status.textContent = '● CONNECTED';
    status.classList.add('connected');
    socket.send(JSON.stringify({ type: 'join', name }));
  };
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'welcome') me = message.id;
    if (message.type === 'state') {
      state = message;
      renderBoard();
      renderLeaderboard();
    }
  };
  socket.onclose = () => {
    status.textContent = '● RECONNECTING';
    status.classList.remove('connected');
    setTimeout(() => connect(name), 1200);
  };
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  overlay.classList.add('hidden');
  connect(document.querySelector('#name').value.trim());
});

const controls = {
  ArrowUp: 'up', w: 'up', ArrowDown: 'down', s: 'down',
  ArrowLeft: 'left', a: 'left', ArrowRight: 'right', d: 'right',
};

addEventListener('keydown', (event) => {
  if (event.target.matches('input, textarea, select')) return;
  const direction = controls[event.key];
  if (!direction) return;
  event.preventDefault();
  if (direction !== queuedDirection && socket?.readyState === WebSocket.OPEN) {
    queuedDirection = direction;
    socket.send(JSON.stringify({ type: 'direction', direction }));
  }
});

function renderLeaderboard() {
  if (!state) return;
  leaderboard.innerHTML = state.players.length
    ? state.players.map((player) => `<li><span class="player-name"><i class="dot" style="background:${player.color}"></i>${escapeHtml(player.name)}${player.id === me ? ' (you)' : ''}</span><b class="player-score">${player.score}</b></li>`).join('')
    : '<li class="empty">Waiting for players…</li>';
}

function escapeHtml(value) {
  const element = document.createElement('div');
  element.textContent = value;
  return element.innerHTML;
}

function drawApple(x, y, cell) {
  const centerX = (x + 0.5) * cell;
  const centerY = (y + 0.54) * cell;
  ctx.fillStyle = '#d94b35';
  ctx.beginPath();
  ctx.arc(centerX - cell * 0.11, centerY, cell * 0.22, 0, Math.PI * 2);
  ctx.arc(centerX + cell * 0.11, centerY, cell * 0.22, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#5b7028';
  ctx.fillRect(centerX + cell * 0.03, centerY - cell * 0.34, cell * 0.07, cell * 0.16);
  ctx.beginPath();
  ctx.ellipse(centerX + cell * 0.17, centerY - cell * 0.27, cell * 0.13, cell * 0.06, -0.55, 0, Math.PI * 2);
  ctx.fill();
}

function renderBoard() {
  if (!state) return;
  const { width, height } = state;
  const cell = canvas.width / width;
  ctx.fillStyle = '#9fc75f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  for (let x = 0; x < width; x += 1) {
    for (let y = 0; y < height; y += 1) {
      ctx.fillStyle = (x + y) % 2 ? '#a9d169' : '#9fc75f';
      ctx.fillRect(x * cell, y * cell, cell, cell);
    }
  }
  drawApple(state.food[0], state.food[1], cell);
  for (const player of state.players) {
    if (!player.alive) continue;
    player.snake.forEach(([x, y], index) => {
      ctx.fillStyle = index === 0 ? player.color : `${player.color}dd`;
      ctx.fillRect(x * cell + 1, y * cell + 1, cell - 2, cell - 2);
      if (index === 0) {
        ctx.fillStyle = '#f9f6df';
        ctx.fillRect(x * cell + cell * 0.61, y * cell + cell * 0.25, 3, 3);
        ctx.fillRect(x * cell + cell * 0.61, y * cell + cell * 0.62, 3, 3);
      }
    });
  }
  if (state.roundOver) {
    roundMessage.innerHTML = `GAME OVER<small style="display:block;margin-top:10px;color:#e9efd2;font-size:13px;font-weight:600;letter-spacing:.12em">NEW GAME STARTS IN ${Math.ceil(state.restartIn)}</small>`;
    roundMessage.style.display = 'grid';
  } else {
    roundMessage.style.display = 'none';
  }
}
