import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Subway Forest Chase", page_icon="🌳", layout="centered")

st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: white; }
        h1 { text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌳 Forest Chase: Chạy Trốn Khỏi Đại Ca Cơ Bắp")
st.markdown("<p style='text-align: center;'>Dùng phím <b>Mũi tên Trái / Phải (A/D)</b> để đổi làn, <b>Mũi tên Lên / Space</b> để nhảy qua chướng ngại vật!</p>", unsafe_allow_html=True)

game_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Forest Chase Game</title>
    <style>
        body {
            margin: 0;
            background: #0b131f;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: white;
            font-family: Arial, sans-serif;
            overflow: hidden;
        }
        canvas {
            border: 4px solid #2d6a4f;
            border-radius: 12px;
            background: #1b4332;
            box-shadow: 0 0 25px rgba(45, 106, 79, 0.6);
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="700" height="600"></canvas>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // Tọa độ 3 làn đường theo góc nhìn phối cảnh (Perspective: trên nhỏ, dưới to)
        function getLaneX(lane, y) {
            let topCenterX = 350;
            let bottomCenterX = 350;
            let topWidth = 120;
            let bottomWidth = 420;
            
            let factor = (y - 150) / (600 - 150);
            if (factor < 0) factor = 0;
            if (factor > 1) factor = 1;
            
            let currentRoadWidth = topWidth + (bottomWidth - topWidth) * factor;
            let leftEdge = bottomCenterX - currentRoadWidth / 2;
            let laneWidth = currentRoadWidth / 3;
            
            return leftEdge + laneWidth * lane + laneWidth / 2;
        }

        let currentLane = 1; // 0: Trái, 1: Giữa, 2: Phải

        let player = {
            lane: 1,
            y: 480,
            width: 35,
            height: 55,
            vy: 0,
            jumping: false,
            crouching: false,
            crouchTimer: 0
        };

        let chaser = {
            lane: 1,
            y: 540,
            width: 40,
            height: 60
        };

        let obstacles = [];
        let coins = [];
        let score = 0;
        let coinCount = 0;
        let speed = 4;
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
                player.vy = -14;
                player.jumping = true;
            } else if ((e.code === "ArrowDown" || e.code === "KeyS") && !player.crouching) {
                player.crouching = true;
                player.crouchTimer = 25;
            }
        });

        function resetGame() {
            currentLane = 1;
            player.y = 480;
            player.vy = 0;
            player.jumping = false;
            player.crouching = false;
            obstacles = [];
            coins = [];
            score = 0;
            coinCount = 0;
            speed = 4;
            gameOver = false;
            frameCount = 0;
            loop();
        }

        function spawnObjects() {
            frameCount++;
            if (frameCount % 60 === 0) {
                let lane = Math.floor(Math.random() * 3);
                let type = Math.random() > 0.4 ? "obstacle" : "barrier";
                obstacles.push({
                    lane: lane,
                    y: 160,
                    scale: 0.1,
                    type: type
                });
            }

            if (frameCount % 40 === 0) {
                let lane = Math.floor(Math.random() * 3);
                coins.push({
                    lane: lane,
                    y: 160,
                    scale: 0.1
                });
            }
        }

        function update() {
            if (gameOver) return;

            player.lane = currentLane;
            chaser.lane = currentLane;

            if (player.jumping) {
                player.y += player.vy;
                player.vy += 0.85;
                if (player.y >= 480) {
                    player.y = 480;
                    player.jumping = false;
                }
            }

            if (player.crouching) {
                player.crouchTimer--;
                if (player.crouchTimer <= 0) player.crouching = false;
            }

            score += 1;
            if (frameCount % 300 === 0) speed += 0.5;

            // Cập nhật chướng ngại vật tiến về phía trước (tăng scale dần theo góc nhìn 3D)
            for (let i = obstacles.length - 1; i >= 0; i--) {
                let obs = obstacles[i];
                obs.scale += 0.015 * (speed / 4);
                obs.y = 160 + (600 - 160) * obs.scale;

                let obsX = getLaneX(obs.lane, obs.y);
                let playerX = getLaneX(player.lane, player.y);

                // Va chạm
                if (obs.scale > 0.75 && obs.scale < 0.98 && obs.lane === player.lane) {
                    if (!(obs.type === "barrier" && player.jumping && player.y < 430)) {
                        gameOver = true;
                    }
                }

                if (obs.scale > 1.05) obstacles.splice(i, 1);
            }

            // Cập nhật tiền xu
            for (let i = coins.length - 1; i >= 0; i--) {
                let c = coins[i];
                c.scale += 0.015 * (speed / 4);
                c.y = 160 + (600 - 160) * c.scale;

                let coinX = getLaneX(c.lane, c.y);
                let playerX = getLaneX(player.lane, player.y);

                if (c.scale > 0.8 && c.scale < 0.98 && c.lane === player.lane) {
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

            // 1. Vẽ bầu trời / nền phía trên
            ctx.fillStyle = "#2d6a4f";
            ctx.fillRect(0, 0, 700, 160);

            // 2. Vẽ con đường nhựa có phối cảnh (giống ảnh mẫu)
            ctx.fillStyle = "#343a40";
            ctx.beginPath();
            ctx.moveTo(350 - 60, 160);
            ctx.lineTo(350 + 60, 160);
            ctx.lineTo(350 + 210, 600);
            ctx.lineTo(350 - 210, 600);
            ctx.closePath();
            ctx.fill();

            // Vẽ viền lề đường
            ctx.strokeStyle = "#adb5bd";
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(350 - 60, 160); ctx.lineTo(350 - 210, 600);
            ctx.moveTo(350 + 60, 160); ctx.lineTo(350 + 210, 600);
            ctx.stroke();

            // Vẽ vạch đứt khúc giữa đường
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.setLineDash([15, 15]);
            ctx.beginPath();
            ctx.moveTo(350, 160); ctx.lineTo(350, 600);
            ctx.stroke();
            ctx.setLineDash([]); // Reset line dash

            // 3. Vẽ hàng cây xanh mát hai bên đường (Phong cách ảnh mẫu)
            for (let y = 160; y <= 600; y += 80) {
                let leftTreeX = 350 - 80 - (y - 160) * 0.45;
                let rightTreeX = 350 + 80 + (y - 160) * 0.45;
                
                // Thân cây
                ctx.fillStyle = "#5c4033";
                ctx.fillRect(leftTreeX - 10, y, 20, 70);
                ctx.fillRect(rightTreeX - 10, y, 20, 70);
                
                // Tán lá xanh đậm/nhạt
                ctx.fillStyle = "#1b4332";
                ctx.beginPath();
                ctx.arc(leftTreeX, y - 10, 35, 0, Math.PI * 2);
                ctx.arc(rightTreeX, y - 10, 35, 0, Math.PI * 2);
                ctx.fill();
            }

            // 4. Vẽ Tiền xu
            coins.forEach(c => {
                let x = getLaneX(c.lane, c.y);
                let radius = c.scale * 15;
                ctx.fillStyle = "#ffd166";
                ctx.beginPath();
                ctx.arc(x, c.y, Math.max(radius, 2), 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = "#d4af37";
                ctx.stroke();
            });

            // 5. Vẽ Chướng ngại vật
            obstacles.forEach(obs => {
                let x = getLaneX(obs.lane, obs.y);
                let w = obs.scale * 60;
                let h = obs.scale * 45;
                
                ctx.fillStyle = obs.type === "barrier" ? "#e76f51" : "#264653";
                ctx.fillRect(x - w / 2, obs.y - h, w, h);
            });

            // 6. Vẽ Người chơi chạy phía trước
            let pX = getLaneX(player.lane, player.y);
            let pW = 35 * (player.y / 600);
            let pH = (player.crouching ? 30 : player.height) * (player.y / 600);
            let pYDraw = player.crouching ? player.y + 20 : player.y;

            ctx.fillStyle = player.crouching ? "#9b59b6" : "#4ea8de";
            ctx.fillRect(pX - pW / 2, pYDraw - pH, pW, pH);
            // Đầu nhân vật chạy
            ctx.fillStyle = "#f8f9fa";
            ctx.beginPath();
            ctx.arc(pX, pYDraw - pH - 8, Math.max(6 * (player.y / 600), 2), 0, Math.PI * 2);
            ctx.fill();

            // 7. Vẽ Người đuổi theo phía sau (Anh chàng cơ bắp xăm trổ)
            let cX = getLaneX(chaser.lane, chaser.y);
            let cW = 45 * (chaser.y / 600);
            let cH = 65 * (chaser.y / 600);

            ctx.fillStyle = "#e63946"; // Áo/cơ bắp người đuổi
            ctx.fillRect(cX - cW / 2, chaser.y - cH, cW, cH);
            // Đầu người đuổi
            ctx.fillStyle = "#d90429";
            ctx.beginPath();
            ctx.arc(cX, chaser.y - cH - 10, Math.max(8 * (chaser.y / 600), 3), 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = "#ffffff";
            ctx.font = "12px Arial";
            ctx.fillText("💢", cX - 8, chaser.y - cH - 20);

            // 8. Điểm số & tiền xu hiển thị
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 18px Arial";
            ctx.fillText("Score: " + score, 20, 35);
            ctx.fillText("Coins: 🪙 " + coinCount, 20, 65);

            if (gameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#ff3333";
                ctx.font = "bold 32px Arial";
                ctx.fillText("BẮT ĐƯỢC RỒI! 💥", 180, 260);
                ctx.fillStyle = "#ffffff";
                ctx.font = "18px Arial";
                ctx.fillText("Điểm của bạn: " + score, 270, 310);
                ctx.fillText("Nhấn phím 'R' để chạy lại", 245, 360);
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

components.html(game_code, height=630)
