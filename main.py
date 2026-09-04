import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit WASD 닷지 게임", page_icon="🎮", layout="centered")

st.title("🎮 WASD 다양한 총알 피하기 게임")
st.caption("방향키 `W`, `A`, `S`, `D`로 조종하여 다양한 특성의 총알들을 피하세요!")

# 1. 난이도 선택 UI
difficulty = st.radio(
    "난이도를 선택하세요",
    ["쉬움 (Easy)", "보통 (Normal)", "어려움 (Hard)"],
    index=1,
    horizontal=True
)

# 난이도별 게임 변수 설정
difficulty_settings = {
    "쉬움 (Easy)": {"spawn_rate": 400, "base_speed": 1.5, "speed_inc": 0.05, "key": "easy"},
    "보통 (Normal)": {"spawn_rate": 250, "base_speed": 2.2, "speed_inc": 0.1, "key": "normal"},
    "어려움 (Hard)": {"spawn_rate": 150, "base_speed": 3.0, "speed_inc": 0.2, "key": "hard"}
}

cfg = difficulty_settings[difficulty]

# 2. HTML/JS 기반 Canvas 게임 코드
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
    <div class="info">이동: <b>W, A, S, D</b> | 재시작: <b>R</b></div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // 난이도별 로컬스토리지 키 설정
        const storageKey = 'dodge_high_score_' + '{cfg['key']}';
        let highScore = parseFloat(localStorage.getItem(storageKey)) || 0.0;

        // 난이도 세팅 변수
        const spawnInterval = {cfg['spawn_rate']};
        const baseBulletSpeed = {cfg['base_speed']};
        const speedInc = {cfg['speed_inc']};

        // 플레이어 설정
        const player = {{
            x: canvas.width / 2,
            y: canvas.height / 2,
            radius: 8,
            speed: 4,
            color: '#00d4ff'
        }};

        // 키 상태 관리
        const keys = {{ w: false, a: false, s: false, d: false }};

        // 총알 및 상태 변수
        let bullets = [];
        let score = 0;
        let gameOver = false;
        let startTime = Date.now();

        // 키 이벤트 리스너
        window.addEventListener('keydown', (e) => {{
            const key = e.key.toLowerCase();
            if (['w', 'a', 's', 'd'].includes(key)) keys[key] = true;
            if (key === 'r' && gameOver) resetGame();
        }});

        window.addEventListener('keyup', (e) => {{
            const key = e.key.toLowerCase();
            if (['w', 'a', 's', 'd'].includes(key)) keys[key] = false;
        }});

        // 총알 생성 함수 (특성/타입 랜덤)
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
            const rand = Math.random();

            let type = 'normal';
            let radius = 5;
            let speed = baseBulletSpeed + Math.random() * 1.5 + (score * speedInc);
            let color = '#ff4b4b';

            if (rand < 0.4) {{
                // 1. 일반 총알 (빨강 원)
                type = 'normal';
                radius = 5;
                color = '#ff4b4b';
            }} else if (rand < 0.65) {{
                // 2. 고속 미니 총알 (노랑 작은 원)
                type = 'fast';
                radius = 3;
                speed *= 1.6;
                color = '#ffee55';
            }} else if (rand < 0.85) {{
                // 3. 대형 왕총알 (주황 큰 원)
                type = 'big';
                radius = 12;
                speed *= 0.65;
                color = '#ff9900';
            }} else {{
                // 4. 유도 다이아몬드 총알 (보라색 네모/다이아몬드)
                type = 'homing';
                radius = 6;
                speed *= 0.8;
                color = '#bc13fe';
            }}

            bullets.push({{
                x: x,
                y: y,
                dx: Math.cos(angle) * speed,
                dy: Math.sin(angle) * speed,
                radius: radius,
                color: color,
                type: type,
                speed: speed,
                rotation: 0
            }});
        }}

        setInterval(spawnBullet, spawnInterval);

        // 게임 리셋
        function resetGame() {{
            player.x = canvas.width / 2;
            player.y = canvas.height / 2;
            bullets = [];
            score = 0;
            gameOver = false;
            startTime = Date.now();
            update();
        }}

        // 다이아몬드(사각형) 그리기 함수
        function drawDiamond(x, y, size, angle, color) {{
            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(angle);
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.rect(-size, -size, size * 2, size * 2);
            ctx.fill();
            ctx.closePath();
            ctx.restore();
        }}

        // 메인 업데이트 및 렌더링 루프
        function update() {{
            if (gameOver) return;

            score = Math.floor((Date.now() - startTime) / 100) / 10;

            // 플레이어 이동
            if (keys.w && player.y - player.radius > 0) player.y -= player.speed;
            if (keys.s && player.y + player.radius < canvas.height) player.y += player.speed;
            if (keys.a && player.x - player.radius > 0) player.x -= player.speed;
            if (keys.d && player.x + player.radius < canvas.width) player.x += player.speed;

            // 화면 초기화
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 플레이어 그리기
            ctx.beginPath();
            ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
            ctx.fillStyle = player.color;
            ctx.fill();
            ctx.closePath();

            // 총알 이동 및 충돌 체크
            for (let i = bullets.length - 1; i >= 0; i--) {{
                const b = bullets[i];

                // 유도 총알 패턴 처리 (조금씩 플레이어를 향해 꺾임)
                if (b.type === 'homing') {{
                    const targetAngle = Math.atan2(player.y - b.y, player.x - b.x);
                    const currentAngle = Math.atan2(b.dy, b.dx);
                    // 서서히 각도 변경
                    const newAngle = currentAngle + (targetAngle - currentAngle) * 0.03;
                    b.dx = Math.cos(newAngle) * b.speed;
                    b.dy = Math.sin(newAngle) * b.speed;
                    b.rotation += 0.1;
                }}

                b.x += b.dx;
                b.y += b.dy;

                // 총알 그리기 (타입별 분기)
                if (b.type === 'homing') {{
                    drawDiamond(b.x, b.y, b.radius, b.rotation, b.color);
                }} else {{
                    ctx.beginPath();
                    ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
                    ctx.fillStyle = b.color;
                    ctx.fill();
                    ctx.closePath();
                }}

                // 충돌 검사
                const dist = Math.hypot(player.x - b.x, player.y - b.y);
                if (dist < player.radius + b.radius) {{
                    gameOver = true;
                    if (score > highScore) {{
                        highScore = score;
                        localStorage.setItem(storageKey, highScore.toFixed(1));
                    }}
                }}

                // 화면 밖으로 나간 총알 제거
                if (b.x < -20 || b.x > canvas.width + 20 || b.y < -20 || b.y > canvas.height + 20) {{
                    bullets.splice(i, 1);
                }}
            }}

            // 현재 점수 및 최고 점수 상단 표시
            ctx.fillStyle = '#ffffff';
            ctx.font = '16px sans-serif';
            ctx.fillText(`TIME: ${{score.toFixed(1)}}s`, 15, 30);
            
            ctx.fillStyle = '#ffbd45';
            ctx.fillText(`BEST: ${{highScore.toFixed(1)}}s`, 15, 52);

            if (gameOver) {{
                ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#ff4b4b';
                ctx.font = 'bold 30px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2 - 20);

                ctx.fillStyle = '#ffffff';
                ctx.font = '16px sans-serif';
                ctx.fillText(`최종 생존 시간: ${{score.toFixed(1)}}초`, canvas.width / 2, canvas.height / 2 + 15);
                
                ctx.fillStyle = '#ffbd45';
                ctx.fillText(`최고 기록: ${{highScore.toFixed(1)}}초`, canvas.width / 2, canvas.height / 2 + 40);

                ctx.fillStyle = '#8b949e';
                ctx.fillText('R 키를 눌러 다시 시작', canvas.width / 2, canvas.height / 2 + 75);
                ctx.textAlign = 'start';
            }} else {{
                requestAnimationFrame(update);
            }}
        }}

        // 게임 시작
        update();
    </script>
</body>
</html>
"""

# Streamlit 컴포넌트로 게임 탑재
components.html(game_code, height=480)

# 가이드 섹션
st.markdown("""
---
### 🕹️ 조작법 및 총알 종류
* **`W, A, S, D`** : 이동 | **`R`** : 재시작
* 🔴 **일반 총알**: 기본 속도 및 크기
* 🟡 **고속 총알**: 작고 빠르게 날아옴
* 🟠 **대형 총알**: 느리지만 피하기 힘든 큰 총알
* 🟣 **유도 다이아몬드**: 플레이어를 서서히 쫓아오는 회전 총알
""")
