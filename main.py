import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit WASD 닷지 게임", page_icon="🎮", layout="centered")

st.title("🎮 WASD 총알 피하기 게임")
st.caption("방향키 `W`, `A`, `S`, `D`로 조종하고, `Spacebar`로 대시를 사용하세요!")

# 난이도 선택 UI
difficulty = st.radio(
    "난이도를 선택하세요",
    ["쉬움 (Easy)", "보통 (Normal)", "어려움 (Hard)"],
    index=1,
    horizontal=True
)

# 난이도별 파라미터 설정
difficulty_settings = {
    "쉬움 (Easy)": {"spawn_rate": 400, "bullet_speed": 1.5, "speed_inc": 0.05},
    "보통 (Normal)": {"spawn_rate": 250, "bullet_speed": 2.5, "speed_inc": 0.1},
    "어려움 (Hard)": {"spawn_rate": 150, "bullet_speed": 3.8, "speed_inc": 0.2}
}

current_setting = difficulty_settings[difficulty]

# Canvas 내 게임 코드 (JS)
game_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #0e1117;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: sans-serif;
            color: white;
        }}
        canvas {{
            border: 2px solid #ff4b4b;
            background-color: #161b22;
            border-radius: 8px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.5);
        }}
        .info {{
            margin-top: 10px;
            font-size: 14px;
            color: #8b949e;
        }}
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="500" height="400"></canvas>
    <div class="info">이동: <b>W, A, S, D</b> | 대시: <b>Space</b> | 재시작: <b>R</b></div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // 난이도 설정 적용
        const spawnInterval = {current_setting['spawn_rate']};
        const baseBulletSpeed = {current_setting['bullet_speed']};
        const speedInc = {current_setting['speed_inc']};

        // 플레이어 상태
        const player = {{
            x: canvas.width / 2,
            y: canvas.height / 2,
            radius: 8,
            speed: 3.5,
            color: '#00d4ff'
        }};

        // 대시 관련 변수
        const dash = {{
            distance: 60,
            cooldown: 1500, // 쿨타임 (밀리초)
            lastUsed: 0,
            isReady: true
        }};

        const keys = {{ w: false, a: false, s: false, d: false, space: false }};
        let bullets = [];
        let score = 0;
        let gameOver = false;
        let startTime = Date.now();

        // 키 입력 제어
        window.addEventListener('keydown', (e) => {{
            if (e.code === 'Space') {{
                keys.space = true;
                e.preventDefault();
            }}
            const key = e.key.toLowerCase();
            if (['w', 'a', 's', 'd'].includes(key)) keys[key] = true;
            if (key === 'r' && gameOver) resetGame();
        }});

        window.addEventListener('keyup', (e) => {{
            if (e.code === 'Space') keys.space = false;
            const key = e.key.toLowerCase();
            if (['w', 'a', 's', 'd'].includes(key)) keys[key] = false;
        }});

        // 대시 로직
        function triggerDash() {{
            const now = Date.now();
            if (now - dash.lastUsed < dash.cooldown) return;

            let dx = 0;
            let dy = 0;
            if (keys.w) dy -= 1;
            if (keys.s) dy += 1;
            if (keys.a) dx -= 1;
            if (keys.d) dx += 1;

            // 이동 방향이 입력된 경우에만 대시
            if (dx !== 0 || dy !== 0) {{
                // 대각선 이동 시 속도 정규화
                const length = Math.hypot(dx, dy);
                dx /= length;
                dy /= length;

                player.x = Math.min(Math.max(player.radius, player.x + dx * dash.distance), canvas.width - player.radius);
                player.y = Math.min(Math.max(player.radius, player.y + dy * dash.distance), canvas.height - player.radius);
                
                dash.lastUsed = now;
            }}
        }}

        // 총알 생성
        function spawnBullet() {{
            if (gameOver) return;
            
            let x, y;
            if (Math.random() < 0.5) {{
                x = Math.random() < 0.5 ? 0 : canvas.width;
                y = Math.random() * canvas.height;
            }} else {{
                x = Math.random() * canvas.width;
                y = Math.random() < 0.5 ? 0 : canvas.height;
            }}

            const angle = Math.atan2(player.y - y, player.x - x);
            const speed = baseBulletSpeed + Math.random() * 1.5 + (score * speedInc);

            bullets.push({{
                x: x,
                y: y,
                dx: Math.cos(angle) * speed,
                dy: Math.sin(angle) * speed,
                radius: 4,
                color: '#ff4b4b'
            }});
        }}

        let spawnTimer = setInterval(spawnBullet, spawnInterval);

        function resetGame() {{
            player.x = canvas.width / 2;
            player.y = canvas.height / 2;
            bullets = [];
            score = 0;
            gameOver = false;
            dash.lastUsed = 0;
            startTime = Date.now();
            update();
        }}

        function update() {{
            if (gameOver) return;

            score = Math.floor((Date.now() - startTime) / 100) / 10;

            // 대시 실행
            if (keys.space) {{
                triggerDash();
            }}

            // 플레이어 일반 이동
            if (keys.w && player.y - player.radius > 0) player.y -= player.speed;
            if (keys.s && player.y + player.radius < canvas.height) player.y += player.speed;
            if (keys.a && player.x - player.radius > 0) player.x -= player.speed;
            if (keys.d && player.x + player.radius < canvas.width) player.x += player.speed;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 플레이어그리기
            ctx.beginPath();
            ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
            ctx.fillStyle = player.color;
            ctx.fill();
            ctx.closePath();

            // 총알 처리 및 충돌 검사
            for (let i = bullets.length - 1; i >= 0; i--) {{
                const b = bullets[i];
                b.x += b.dx;
                b.y += b.dy;

                ctx.beginPath();
                ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
                ctx.fillStyle = b.color;
                ctx.fill();
                ctx.closePath();

                const dist = Math.hypot(player.x - b.x, player.y - b.y);
                if (dist < player.radius + b.radius) {{
                    gameOver = true;
                }}

                if (b.x < -10 || b.x > canvas.width + 10 || b.y < -10 || b.y > canvas.height + 10) {{
                    bullets.splice(i, 1);
                }}
            }}

            // UI (생존시간 및 대시 쿨다운 게이지) 표시
            ctx.fillStyle = '#ffffff';
            ctx.font = '16px sans-serif';
            ctx.fillText(`TIME: ${{score.toFixed(1)}}s`, 15, 30);

            // 대시 쿨타임 표시
            const now = Date.now();
            const dashProgress = Math.min(1, (now - dash.lastUsed) / dash.cooldown);
            
            ctx.fillStyle = '#333';
            ctx.fillRect(15, 40, 100, 8);
            ctx.fillStyle = dashProgress === 1 ? '#00d4ff' : '#ffbd45';
            ctx.fillRect(15, 40,
