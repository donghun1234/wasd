import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit WASD 닷지 게임", page_icon="🎮", layout="centered")

st.title("🎮 WASD 총알 피하기 게임")
st.caption("방향키 `W`, `A`, `S`, `D`로 중앙의 플레이어를 조종하여 날아오는 총알을 피하세요!")

# HTML/JS 기반 Canvas 게임 코드
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #0e1117;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: sans-serif;
            color: white;
        }
        canvas {
            border: 2px solid #ff4b4b;
            background-color: #161b22;
            border-radius: 8px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.5);
        }
        .info {
            margin-top: 10px;
            font-size: 14px;
            color: #8b949e;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="500" height="400"></canvas>
    <div class="info">이동: <b>W, A, S, D</b> | 재시작: <b>R</b></div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // 로컬 스토리지에서 최고 기록 불러오기 (없으면 0.0)
        let highScore = parseFloat(localStorage.getItem('dodge_high_score')) || 0.0;

        // 플레이어 설정
        const player = {
            x: canvas.width / 2,
            y: canvas.height / 2,
            radius: 8,
            speed: 4,
            color: '#00d4ff'
        };

        // 키 상태 관리
        const keys = { w: false, a: false, s: false, d: false };

        // 총알 목록
        let bullets = [];
        let score = 0;
        let gameOver = false;
        let startTime = Date.now();

        // 키 이벤트 리스너
        window.addEventListener('keydown', (e) => {
            const key = e.key.toLowerCase();
            if (['w', 'a', 's', 'd'].includes(key)) keys[key] = true;
            if (key === 'r' && gameOver) resetGame();
        });

        window.addEventListener('keyup', (e) => {
            const key = e.key.toLowerCase();
            if (['w', 'a', 's', 'd'].includes(key)) keys[key] = false;
        });

        // 총알 생성 함수
        function spawnBullet() {
            if (gameOver) return;
            
            let x, y;
            if (Math.random() < 0.5) {
                x = Math.random() < 0.5 ? 0 : canvas.width;
                y = Math.random() * canvas.height;
            } else {
                x = Math.random() * canvas.width;
                y = Math.random() < 0.5 ? 0 : canvas.height;
            }

            const angle = Math.atan2(player.y - y, player.x - x);
            const speed = 2 + Math.random() * 2 + (score / 10);

            bullets.push({
                x: x,
                y: y,
                dx: Math.cos(angle) * speed,
                dy: Math.sin(angle) * speed,
                radius: 4,
                color: '#ff4b4b'
            });
        }

        setInterval(spawnBullet, 300);

        // 게임 리셋
        function resetGame() {
            player.x = canvas.width / 2;
            player.y = canvas.height / 2;
            bullets = [];
            score = 0;
            gameOver = false;
            startTime = Date.now();
            update();
        }

        // 업데이트 및 렌더링 루프
        function update() {
            if (gameOver) return;

            // 현재 스코어 계산 (생존 시간)
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
            for (let i = bullets.length - 1; i >= 0; i--) {
                const b = bullets[i];
                b.x += b.dx;
                b.y += b.dy;

                // 총알 그리기
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
                ctx.fillStyle = b.color;
                ctx.fill();
                ctx.closePath();

                // 충돌 검사
                const dist = Math.hypot(player.x - b.x, player.y - b.y);
                if (dist < player.radius + b.radius) {
                    gameOver = true;
                    // 최고 기록 업데이트 및 로컬스토리지 저장
                    if (score > highScore) {
                        highScore = score;
                        localStorage.setItem('dodge_high_score', highScore.toFixed(1));
                    }
                }

                // 화면 밖으로 나간 총알 제거
                if (b.x < -10 || b.x > canvas.width + 10 || b.y < -10 || b.y > canvas.height + 10) {
                    bullets.splice(i, 1);
                }
            }

            // 현재 점수 및 최고 점수 상단 표시
            ctx.fillStyle = '#ffffff';
            ctx.font = '16px sans-serif';
            ctx.fillText(`TIME: ${score.toFixed(1)}s`, 15, 30);
            
            ctx.fillStyle = '#ffbd45';
            ctx.fillText(`BEST: ${highScore.toFixed(1)}s`, 15, 52);

            if (gameOver) {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#ff4b4b';
                ctx.font = 'bold 30px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2 - 20);

                ctx.fillStyle = '#ffffff';
                ctx.font = '16px sans-serif';
                ctx.fillText(`최종 생존 시간: ${score.toFixed(1)}초`, canvas.width / 2, canvas.height / 2 + 15);
                
                ctx.fillStyle = '#ffbd45';
                ctx.fillText(`최고 기록: ${highScore.toFixed(1)}초`, canvas.width / 2, canvas.height / 2 + 40);

                ctx.fillStyle = '#8b949e';
                ctx.fillText('R 키를 눌러 다시 시작', canvas.width / 2, canvas.height / 2 + 75);
                ctx.textAlign = 'start';
            } else {
                requestAnimationFrame(update);
            }
        }

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
### 🕹️ 조작법
* **`W`** : 위로 이동
* **`A`** : 왼쪽으로 이동
* **`S`** : 아래로 이동
* **`D`** : 오른쪽으로 이동
* **`R`** : 게임 오버 시 재시작
""")
