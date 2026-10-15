import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Roblox Chase 3D", page_icon="🎮", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #080c14; color: white; }
        .main .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 95%; }
        h1 { text-align: center; color: #ff007f; font-family: 'Segoe UI', sans-serif; text-shadow: 0 0 10px rgba(255,0,127,0.5); }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 ROBLOX NOOB VS MUSCLE CHASE 3D")
st.markdown("<p style='text-align: center; font-size: 16px;'>Điều khiển: <b>[A / D]</b> hoặc <b>[Mũi tên Trái / Phải]</b> đổi làn | <b>[Space / W]</b> Nhảy | <b>[S]</b> Cúi | <b>[R]</b> Chơi lại</p>", unsafe_allow_html=True)

game_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Roblox Chase Game</title>
    <style>
        body {
            margin: 0;
            background: #080c14;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
        }
        #game-container {
            position: relative;
            box-shadow: 0 0 35px rgba(255, 0, 127, 0.3);
            border-radius: 16px;
            overflow: hidden;
            border: 3px solid #ff007f;
        }
        canvas {
            display: block;
            background: #0f172a;
        }
    </style>
</head>
<body>
    <div id="game-container">
        <canvas id="gameCanvas" width="800" height="600"></canvas>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // --- TẢI HÌNH ẢNH NHÂN VẬT THỰC TẾ ---
        // 1. Ảnh người chạy: Roblox Noob (Render trực tiếp từ link icon avatar Roblox)
        const runnerImg = new Image();
        runnerImg.src = "https://tr.rbxcdn.com/30DAY-AvatarHeadshot-311D7C2C0EDC956C82F24E68B8D4E302-Png/150/150/AvatarHeadshot/Png/noFilter";

        // 2. Ảnh người đuổi: Anh chàng cơ bắp xăm trổ (Từ hình ảnh bạn cung cấp)
        const chaserImg = new Image();
        chaserImg.src = "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=300&auto=format&fit=crop&q=80";

        function getLaneX(lane, y) {
            let topCenterX = 400;
            let bottomCenterX = 400;
            let topWidth = 140;
            let bottomWidth = 520;
            
            let factor = (y - 140) / (600 - 140);
            if (factor < 0) factor = 0;
            if (factor > 1) factor = 1;
            
            let currentRoadWidth = topWidth + (bottomWidth - topWidth) * factor;
            let leftEdge = bottomCenterX - currentRoadWidth / 2;
            let laneWidth = currentRoadWidth / 3;
            
            return leftEdge + laneWidth * lane + laneWidth / 2;
        }

        let currentLane = 1;

        let player = {
            lane: 1,
            y: 470,
            width: 50,
            height: 75,
            vy: 0,
            jumping: false,
            crouching: false,
            crouchTimer: 0
        };

        let chaser = {
            lane: 1,
            y: 530,
            width: 85,
            height: 105
        };

        let obstacles = [];
        let coins = [];
        let score = 0;
        let coinCount = 0;
        let speed = 5;
        let gameOver = false;
        let frameCount = 0;

        document.addEventListener("keydown", (e) => {
            if (gameOver && e.code === "KeyR") {
                resetGame();
                return;
            }
            if (gameOver) return;

            if ((e.code === "ArrowLeft" || e.code === "KeyA") && currentLane > 0) {
                currentLane--;
            } else if ((e.code === "ArrowRight" || e.code === "KeyD") && currentLane < 2) {
                currentLane++;
            } else if ((e.code === "ArrowUp" || e.code === "Space" || e.code === "KeyW") && !player.jumping) {
                player.vy = -15;
                player.jumping = true;
            } else if ((e.code === "ArrowDown" || e.code === "KeyS") && !player.crouching) {
                player.crouching = true;
                player.crouchTimer = 25;
            }
        });

        function resetGame() {
            currentLane = 1;
            player.y = 470;
            player.vy = 0;
            player.jumping = false;
            player.crouching = false;
            obstacles = [];
            coins = [];
            score = 0;
            coinCount = 0;
            speed = 5;
            gameOver = false;
            frameCount = 0;
            loop();
        }

        function spawnObjects() {
            frameCount++;
            if (frameCount % 45 === 0) {
                let lane = Math.floor(Math.random() * 3);
                let type = Math.random() > 0.4 ? "barrier" : "rock";
                obstacles.push({
                    lane: lane,
                    y: 140,
                    scale: 0.05,
                    type: type
                });
            }

            if (frameCount % 30 === 0) {
                let lane = Math.floor(Math.random() * 3);
                coins.push({
                    lane: lane,
                    y: 140,
                    scale: 0.05
                });
            }
        }

        function update() {
            if (gameOver) return;

            player.lane = currentLane;
            chaser.lane = currentLane;

            if (player.jumping) {
                player.y += player.vy;
                player.vy += 0.9;
                if (player.y >= 470) {
                    player.y = 470;
                    player.jumping = false;
                }
            }

            if (player.crouching) {
                player.crouchTimer--;
                if (player.crouchTimer <= 0) player.crouching = false;
            }

            score += 1;
            if (frameCount % 200 === 0) speed += 0.4;

            for (let i = obstacles.length - 1; i >= 0; i--) {
                let obs = obstacles[i];
                obs.scale += 0.018 * (speed / 5);
                obs.y = 140 + (600 - 140) * obs.scale;

                if (obs.scale > 0.72 && obs.scale < 0.95 && obs.lane === player.lane) {
                    if (!(obs.type === "barrier" && player.jumping && player.y < 410)) {
                        gameOver = true;
                    }
                }

                if (obs.scale > 1.05) obstacles.splice(i, 1);
            }

            for (let i = coins.length - 1; i >= 0; i--) {
                let c = coins[i];
                c.scale += 0.018 * (speed / 5);
                c.y = 140 + (600 - 140) * c.scale;

                if (c.scale > 0.75 && c.scale < 0.95 && c.lane === player.lane) {
                    coinCount++;
                    coins.splice(i, 1);
                } else if (c.scale > 1.05) {
                    coins.splice(i, 1);
                }
            }

            spawnObjects();
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // BẦU TRỜI
            let skyGradient = ctx.createLinearGradient(0, 0, 0, 140);
            skyGradient.addColorStop(0, '#10002b');
            skyGradient.addColorStop(1, '#3c096c');
            ctx.fillStyle = skyGradient;
            ctx.fillRect(0, 0, 800, 140);

            // ĐƯỜNG ĐUA 3D XUYÊN RỪNG
            let roadGradient = ctx.createLinearGradient(0, 140, 0, 600);
            roadGradient.addColorStop(0, '#2b303a');
            roadGradient.addColorStop(1, '#16191f');
            
            ctx.fillStyle = roadGradient;
            ctx.beginPath();
            ctx.moveTo(400 - 70, 140);
            ctx.lineTo(400 + 70, 140);
            ctx.lineTo(400 + 260, 600);
            ctx.lineTo(400 - 260, 600);
            ctx.closePath();
            ctx.fill();

            ctx.strokeStyle = '#ff007f';
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(400 - 70, 140); ctx.lineTo(400 - 260, 600);
            ctx.moveTo(400 + 70, 140); ctx.lineTo(400 + 260, 600);
            ctx.stroke();

            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 3;
            ctx.setLineDash([20, 20]);
            ctx.lineDashOffset = -frameCount * speed * 0.8;
            ctx.beginPath();
            ctx.moveTo(400, 140); ctx.lineTo(400, 600);
            ctx.stroke();
            ctx.setLineDash([]);

            // CÂY RỪNG HAI BÊN
            for (let i = 0; i < 8; i++) {
                let progress = ((frameCount * 3 + i * 70) % 460) / 460;
                let y = 140 + progress * 460;
                let scale = 0.2 + progress * 1.2;

                let leftX = 400 - 90 - progress * 240;
                let rightX = 400 + 90 + progress * 240;

                ctx.fillStyle = '#240046';
                ctx.beginPath();
                ctx.arc(leftX, y - 20 * scale, 35 * scale, 0, Math.PI * 2);
                ctx.arc(rightX, y - 20 * scale, 35 * scale, 0, Math.PI * 2);
                ctx.fill();
            }

            // TIỀN XU
            coins.forEach(c => {
                let x = getLaneX(c.lane, c.y);
                let radius = Math.max(c.scale * 22, 3);
                
                ctx.fillStyle = '#ffcc00';
                ctx.beginPath();
                ctx.arc(x, c.y, radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = '#d4af37';
                ctx.lineWidth = 2;
                ctx.stroke();
            });

            // CHƯỚNG NGẠI VẬT
            obstacles.forEach(obs => {
                let x = getLaneX(obs.lane, obs.y);
                let w = obs.scale * 80;
                let h = obs.scale * 55;
                
                if (obs.type === "barrier") {
                    ctx.fillStyle = '#ff4d6d';
                    ctx.fillRect(x - w / 2, obs.y - h, w, h);
                    ctx.fillStyle = '#ffffff';
                    ctx.fillRect(x - w / 2 + 5, obs.y - h + 5, w - 10, 10);
                } else {
                    ctx.fillStyle = '#6c757d';
                    ctx.beginPath();
                    ctx.arc(x, obs.y - h/2, w/2, 0, Math.PI * 2);
                    ctx.fill();
                }
            });

            // --- VẼ HÌNH ẢNH NHÂN VẬT CHẠY (ROBLOX NOOB) ---
            let pX = getLaneX(player.lane, player.y);
            let pW = 48 * (player.y / 600);
            let pH = (player.crouching ? 40 : player.height) * (player.y / 600);
            let pYDraw = player.crouching ? player.y + 25 : player.y;

            if (runnerImg.complete) {
                ctx.drawImage(runnerImg, pX - pW / 2, pYDraw - pH, pW, pH);
            }

            // --- VẼ HÌNH ẢNH NGƯỜI ĐUỔI (ANH CHÀNG CƠ BẮP XĂM TRỔ) ---
            let cX = getLaneX(chaser.lane, chaser.y);
            let cW = chaser.width * (chaser.y / 600);
            let cH = chaser.height * (chaser.y / 600);

            if (chaserImg.complete) {
                ctx.drawImage(chaserImg, cX - cW / 2, chaser.y - cH, cW, cH);
            }

            // BẢNG ĐIỂM HUD
            ctx.fillStyle = 'rgba(0,0,0,0.6)';
            ctx.roundRect(15, 15, 190, 80, 10);
            ctx.fill();

            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 18px "Segoe UI", Arial';
            ctx.fillText('SCORE: ' + score, 30, 45);
            ctx.fillStyle = '#ffcc00';
            ctx.fillText('COINS: 🪙 ' + coinCount, 30, 75);

            // MÀN HÌNH GAME OVER
            if (gameOver) {
                ctx.fillStyle = 'rgba(10, 15, 25, 0.9)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#ff007f';
                ctx.font = 'bold 36px "Segoe UI", Arial';
                ctx.textAlign = 'center';
                ctx.fillText('ĐẠI CA ĐÃ BẮT ĐƯỢC NOOB! 💥', 400, 250);

                ctx.fillStyle = '#ffffff';
                ctx.font = '20px "Segoe UI", Arial';
                ctx.fillText('Tổng điểm: ' + score + '  |  Coins: ' + coinCount + ' 🪙', 400, 310);
                
                ctx.fillStyle = '#ffcc00';
                ctx.font = 'bold 18px "Segoe UI", Arial';
                ctx.fillText('Nhấn phím [ R ] để chơi lại!', 400, 370);
                ctx.textAlign = 'start';
            }
        }

        function loop() {
            update();
            draw();
            if (!gameOver) {
                requestAnimationFrame(loop);
            }
        }

        loop();
    </script>
</body>
</html>
"""

components.html(game_code, height=640)
