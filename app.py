import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Roblox Duo Chase 3D", page_icon="🎮", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #080c14; color: white; }
        .main .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 95%; }
        h1 { text-align: center; color: #ff6584; font-family: 'Segoe UI', sans-serif; text-shadow: 0 0 10px rgba(255,101,132,0.5); }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 ROBLOX DUO: CHASE & ESCAPE 3D")
st.markdown("<p style='text-align: center; font-size: 16px;'>Điều khiển: <b>[A / D]</b> hoặc <b>[Mũi tên Trái / Phải]</b> đổi làn | <b>[Space / W]</b> Nhảy | <b>[S]</b> Cúi | <b>[R]</b> Chơi lại</p>", unsafe_allow_html=True)

game_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Roblox Duo Chase Game</title>
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
            box-shadow: 0 0 35px rgba(255, 101, 132, 0.3);
            border-radius: 16px;
            overflow: hidden;
            border: 3px solid #ff6584;
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
            width: 48,
            height: 75,
            vy: 0,
            jumping: false,
            crouching: false,
            crouchTimer: 0
        };

        let chaser = {
            lane: 1,
            y: 530,
            width: 55,
            height: 85
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
            skyGradient.addColorStop(0, '#2b0938');
            skyGradient.addColorStop(1, '#190324');
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

            ctx.strokeStyle = '#ff6584';
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

                ctx.fillStyle = '#3a0ca3';
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

            // --- 1. NHÂN VẬT CHẠY TRỐN (NHÂN VẬT NỮ TÓC ĐEN NƠ HỒNG, TRANG PHỤC TRẮNG HỒNG) ---
            let pX = getLaneX(player.lane, player.y);
            let pW = 45 * (player.y / 600);
            let pH = (player.crouching ? 35 : player.height) * (player.y / 600);
            let pYDraw = player.crouching ? player.y + 20 : player.y;

            // Thân áo trắng viền hồng
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(pX - pW / 2, pYDraw - pH + 18, pW, pH - 38);
            ctx.strokeStyle = '#ffb3c6';
            ctx.lineWidth = 2;
            ctx.strokeRect(pX - pW / 2, pYDraw - pH + 18, pW, pH - 38);

            // Quần trắng
            ctx.fillRect(pX - pW / 2, pYDraw - 20, pW, 20);

            // Tóc đen dài & Nơ hồng xinh xắn trên đầu
            ctx.fillStyle = '#111111';
            ctx.beginPath();
            ctx.arc(pX, pYDraw - pH - 10, 15, 0, Math.PI * 2);
            ctx.fill();
            // Nơ hồng
            ctx.fillStyle = '#ff758c';
            ctx.beginPath();
            ctx.arc(pX - 8, pYDraw - pH - 24, 6, 0, Math.PI * 2);
            ctx.arc(pX + 8, pYDraw - pH - 24, 6, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillRect(pX - 4, pYDraw - pH - 27, 8, 6);


            // --- 2. NGƯỜI ĐUỔI PHÍA SAU (NHÂN VẬT NAM PHONG CÁCH ĐEN - TRẮNG NGẦU) ---
            let cX = getLaneX(chaser.lane, chaser.y);
            let cW = chaser.width * (chaser.y / 600);
            let cH = chaser.height * (chaser.y / 600);

            ctx.fillStyle = 'rgba(0,0,0,0.4)';
            ctx.beginPath();
            ctx.ellipse(cX, chaser.y + 5, cW / 2, 10, 0, 0, Math.PI * 2);
            ctx.fill();

            // Áo phối đen - trắng phong cách
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(cX - cW / 2, chaser.y - cH + 16, cW / 2, cH - 36);
            ctx.fillStyle = '#f0f0f0';
            ctx.fillRect(cX, chaser.y - cH + 16, cW / 2, cH
