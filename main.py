import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit WASD 닷지 게임", page_icon="🎮", layout="centered")

st.title("🎮 WASD 총알 피하기 게임")
st.caption("방향키 `W, A, S, D`로 조종 | `E`: 보호막 | `Space`/`Q`: 시간 정지 (코인 3개 필요)")

# 1. 목숨 개수 및 난이도 선택 UI
col1, col2 = st.columns(2)

with col1:
    lives_setting = st.slider("❤️ 목숨 개수 설정", min_value=1, max_value=3, value=1, step=1)

with col2:
    difficulty = st.radio(
        "🎯 난이도 선택",
        ["쉬움 (Easy)", "보통 (Normal)", "어려움 (Hard - 15초 생존!)"],
        index=2
    )

# 난이도별 게임 변수 설정
difficulty_settings = {
    "쉬움 (Easy)": {"spawn_rate": 400, "base_speed": 1.5, "speed_inc": 0.05, "key": "easy", "target_time": "null"},
    "보통 (Normal)": {"spawn_rate": 250, "base_speed": 2.2, "speed_inc": 0.1, "key": "normal", "target_time": "null"},
    "어려움 (Hard - 15초 생존!)": {"spawn_rate": 150, "base_speed": 3.0, "speed_inc": 0.2, "key": "hard", "target_time": "15.0"}
}

cfg = difficulty_settings[difficulty]
spawn_rate_val = cfg['spawn_rate']
base_speed_val = cfg['base_speed']
speed_inc_val = cfg['speed_inc']
key_val = cfg['key']
target_time_val = cfg['target_time']

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
    <div class="info">이동: <b>W,A,S,D</b> | 보호막: <b>E</b> | 시간정지: <b>Space</b> / <b>Q</b> (코인 3개) | 재시작: <b>R</b></div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        const storageKey = 'dodge_high_score_' + '{key_val}';
        let highScore = parseFloat(localStorage.getItem(storageKey)) || 0.0;

        const spawnInterval = {spawn_rate_val};
        const baseBulletSpeed = {base_speed_val};
        const speedInc = {speed_inc_val};
        const targetTime = {target_time_val};
        const maxLives = {lives_setting};

        let lives = maxLives;
        let invulnerable = false;
        let invulnerableTimer = 0;

        let coins = [];
        let coinCount = 0;
        let freezeActive = false;
        let freezeUntil = 0;

        const player = {{
            x: canvas.width / 2,
            y: canvas.height / 2,
            radius: 8,
            speed: 4,
            color: '#00d4ff'
        }};

        const shield = {{
            active: false,
            duration: 3000,
            cooldown: 10000,
            lastUsed: -10000,
            activeUntil: 0
        }};

        const keys = {{ w: false, a: false, s: false, d: false }};
        let bullets = [];
        let score = 0;
        let gameOver = false;
        let gameClear = false;
        let startTime = Date.now();

        window.addEventListener('keydown', (e) => {{
            const key = e.key.toLowerCase();
            if (['w', 'a', 's', 'd'].includes(key)) keys[key] = true;
            if (key === 'e' && !gameOver && !gameClear) triggerShield();
            if ((key === ' ' || key === 'q') && !gameOver && !gameClear) triggerTimeFreeze();
            if (key === 'r' && (gameOver || gameClear)) resetGame();
        }});

        window.addEventListener('keyup', (e) => {{
            const key = e.key.toLowerCase();
            if (['w', 'a', 's', 'd'].includes(key)) keys[key] = false;
        }});

        function triggerShield() {{
            const now = Date.now();
            if (now - shield.lastUsed >= shield.cooldown) {{
                shield.active = true;
                shield.lastUsed = now;
                shield.activeUntil = now + shield.duration;
            }}
        }}

        function triggerTimeFreeze() {{
            const now = Date.now();
            if (coinCount >= 3 && !freezeActive) {{
                coinCount -= 3;
                freezeActive = true;
                freezeUntil = now + 2000; // 2초간 정지
            }}
        }}

        function spawnCoin() {{
            if (gameOver || gameClear || coins.length >= 3) return;
            coins.push({{
                x: 30 + Math.random() * (canvas.width - 60),
                y: 30 + Math.random() * (canvas.height - 60),
                radius: 6
            }});
        }}

        setInterval(spawnCoin, 3000);

        function spawnBullet() {{
            if (gameOver || gameClear || freezeActive) return;
            
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
                type = 'normal';
                radius = 5;
                color = '#ff4b4b';
            }} else if (rand < 0.65) {{
                type = 'fast';
                radius = 3;
                speed *= 1.6;
                color = '#ffee55';
            }} else if (rand < 0.85) {{
                type = 'big';
                radius = 12;
                speed *= 0.65;
                color = '#ff9900';
            }} else {{
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

        function resetGame() {{
            player.x = canvas.width / 2;
            player.y = canvas.height / 2;
            bullets = [];
            coins = [];
            coinCount = 0;
            score = 0;
            lives = maxLives;
            invulnerable = false;
            freezeActive = false;
            gameOver = false;
            gameClear = false;
            shield.active = false;
            shield.lastUsed = -10000;
            startTime = Date.now();
            update();
        }}

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

        function update() {{
            if (gameOver || gameClear) return;

            const now = Date.now();
            score = Math.floor((now - startTime) / 100) / 10;

            if (targetTime !== null && score >= targetTime) {{
                gameClear = true;
                score = targetTime;
                if (score > highScore) {{
                    highScore = score;
                    localStorage.setItem(storageKey, highScore.toFixed(1));
                }}
            }}

            if (shield.active && now > shield.activeUntil) {{
                shield.active = false;
            }}

            if (invulnerable && now > invulnerableTimer) {{
                invulnerable = false;
            }}

            if (freezeActive && now > freezeUntil) {{
                freezeActive = false;
            }}

            if (keys.w && player.y - player.radius > 0) player.y -= player.speed;
            if (keys.s && player.y + player.radius < canvas.height) player.y += player.speed;
            if (keys.a && player.x - player.radius > 0) player.x -= player.speed;
            if (keys.d && player.x + player.radius < canvas.width) player.x += player.speed;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 시간 정지 배경 효과
            if (freezeActive) {{
                ctx.fillStyle = 'rgba(0, 150, 255, 0.1)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }}

            // 코인 그리기 및 습득 판정
            for (let i = coins.length - 1; i >= 0; i--) {{
                const c = coins[i];
                ctx.beginPath();
                ctx.arc(c.x, c.y, c.radius, 0, Math.PI * 2);
                ctx.fillStyle = '#ffd700';
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = '#ffaa00';
                ctx.stroke();
                ctx.closePath();

                const dist = Math.hypot(player.x - c.x, player.y - c.y);
                if (dist < player.radius + c.radius) {{
                    coinCount++;
                    coins.splice(i, 1);
                }}
            }}

            // 플레이어 그리기
            if (!invulnerable || Math.floor(now / 100) % 2 === 0) {{
                ctx.beginPath();
                ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
                ctx.fillStyle = player.color;
                ctx.fill();
                ctx.closePath();
            }}

            if (shield.active) {{
                ctx.beginPath();
                ctx.arc(player.x, player.y, player.radius + 8, 0, Math.PI * 2);
                ctx.strokeStyle = '#00ffff';
                ctx.lineWidth = 3;
                ctx.stroke();
                ctx.fillStyle = 'rgba(0, 255, 255, 0.2)';
                ctx.fill();
                ctx.closePath();
            }}

            // 총알 로직 및 충돌
            for (let i = bullets.length - 1; i >= 0; i--) {{
                const b = bullets[i];

                if (!freezeActive) {{
                    if (b.type === 'homing') {{
                        const targetAngle = Math.atan2(player.y - b.y, player.x - b.x);
                        const currentAngle = Math.atan2(b.dy, b.dx);
                        const newAngle = currentAngle + (targetAngle - currentAngle) * 0.03;
                        b.dx = Math.cos(newAngle) * b.speed;
                        b.dy = Math.sin(newAngle) * b.speed;
                        b.rotation += 0.1;
                    }}
                    b.x += b.dx;
                    b.y += b.dy;
                }}

                if (b.type === 'homing') {{
                    drawDiamond(b.x, b.y, b.radius, b.rotation, freezeActive ? '#888888' : b.color);
                }} else {{
                    ctx.beginPath();
                    ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
                    ctx.fillStyle = freezeActive ? '#888888' : b.color;
                    ctx.fill();
                    ctx.closePath();
                }}

                const dist = Math.hypot(player.x - b.x, player.y - b.y);
                if (dist < player.radius + b.radius) {{
                    if (!shield.active && !invulnerable && !freezeActive) {{
                        lives--;
                        bullets.splice(i, 1);
                        
                        if (lives <= 0) {{
                            gameOver = true;
                            if (score > highScore) {{
                                highScore = score;
                                localStorage.setItem(storageKey, highScore.toFixed(1));
                            }}
                        }} else {{
                            invulnerable = true;
                            invulnerableTimer = now + 1500;
                        }}
                        continue;
                    }}
                }}

                if (b.x < -20 || b.x > canvas.width + 20 || b.y < -20 || b.y > canvas.height + 20) {{
                    bullets.splice(i, 1);
                }}
            }}

            // UI 표시
            ctx.fillStyle = '#ffffff';
            ctx.font = '16px sans-serif';
            if (targetTime !== null) {{
                ctx.fillText('TIME: ' + score.toFixed(1) + 's / ' + targetTime.toFixed(1) + 's', 15, 30);
            }} else {{
                ctx.fillText('TIME: ' + score.toFixed(1) + 's', 15, 30);
            }}
            
            ctx.fillStyle = '#ffbd45';
            ctx.fillText('BEST: ' + highScore.toFixed(1) + 's', 15, 52);

            ctx.fillStyle = '#ff4b4b';
            ctx.fillText('LIFE: ' + '❤️'.repeat(lives), 15, 74);

            ctx.fillStyle = '#ffd700';
            ctx.fillText('COIN: 🪙 ' + coinCount, 15, 96);

            // 보호막 게이지
            const timeSinceLastUsed = now - shield.lastUsed;
            const cooldownProgress = Math.min(1, timeSinceLastUsed / shield.cooldown);
            
            ctx.fillStyle = '#333333';
            ctx.fillRect(15, 105, 100, 8);
            
            if (shield.active) {{
                const activeProgress = (shield.activeUntil - now) / shield.duration;
                ctx.fillStyle = '#00ffff';
                ctx.fillRect(15, 105, 100 * activeProgress, 8);
                ctx.fillStyle = '#00ffff';
                ctx.font = '10px sans-serif';
                ctx.fillText('SHIELD ACTIVE', 122, 113);
            }} else {{
                ctx.fillStyle = cooldownProgress === 1 ? '#00d4ff' : '#ffbd45';
                ctx.fillRect(15, 105, 100 * cooldownProgress, 8);
                ctx.fillStyle = '#8b949e';
                ctx.font = '10px sans-serif';
                ctx.fillText(cooldownProgress === 1 ? 'SHIELD READY (E)' : 'CHARGING...', 122, 113);
            }}

            // 시간 정지 알림
            if (freezeActive) {{
                const remainFreeze = ((freezeUntil - now) / 1000).toFixed(1);
                ctx.fillStyle = '#00ffff';
                ctx.font = 'bold 16px sans-serif';
                ctx.fillText('⏱️ TIME FREEZE! (' + remainFreeze + 's)', canvas.width / 2 - 80, 30);
            }}

            if (gameClear) {{
                ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#00ff88';
                ctx.font = 'bold 32px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('🎉 STAGE CLEAR! 🎉', canvas.width / 2, canvas.height / 2 - 20);

                ctx.fillStyle = '#ffffff';
                ctx.font = '16px sans-serif';
                ctx.fillText('어려움 모드 15초 생존 성공!', canvas.width / 2, canvas.height / 2 + 15);

                ctx.fillStyle = '#8b949e';
                ctx.fillText('R 키를 눌러 다시 도전', canvas.width / 2, canvas.height / 2 + 60);
                ctx.textAlign = 'start';
            }} else if (gameOver) {{
                ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#ff4b4b';
                ctx.font = 'bold 30px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2 - 20);

                ctx.fillStyle = '#ffffff';
                ctx.font = '16px sans-serif';
                ctx.fillText('최종 생존 시간: ' + score.toFixed(1) + '초', canvas.width / 2, canvas.height / 2 + 15);
                
                ctx.fillStyle = '#ffbd45';
                ctx.fillText('최고 기록: ' + highScore.toFixed(1) + '초', canvas.width / 2, canvas.height / 2 + 40);

                ctx.fillStyle = '#8b949e';
                ctx.fillText('R 키를 눌러 다시 시작', canvas.width / 2, canvas.height / 2 + 75);
                ctx.textAlign = 'start';
            }} else {{
                requestAnimationFrame(update);
            }}
        }}

        update();
    </script>
</body>
</html>
"""

components.html(game_code, height=480)

st.markdown("""
---
### 🕹️ 조작법 및 규칙
* **`W, A, S, D`** : 이동 | **`R`** : 재시작
* **`E`** : **보호막 스킬** (3초간 무적 / 쿨타임 10초)
* **`Space` 또는 `Q`** : **시간 정지 스킬** (🪙 코인 3개 사용 시 2초간 모든 총알 멈춤)
* **🪙 코인**: 필드에 생성되는 노란색 코인을 모으세요.
""")
