import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Subway Runner Streamlit", page_icon="🏃", layout="centered")

st.title("🏃 Subway Runner (Streamlit Edition)")
st.markdown("""
**Hướng dẫn chơi:**
* **Mũi tên Trái / Phải (hoặc A / D):** Đổi làn đường (3 làn)
* **Mũi tên Lên / Space (hoặc W):** Nhảy
* **Mũi tên Xuống (hoặc S):** Cúi người
* **Phím R:** Chơi lại khi Game Over
""")

# Code game HTML5 Canvas nhúng vào Streamlit
game_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            background: #111;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: white;
            font-family: Arial, sans-serif;
        }
        canvas {
            border: 3px solid #ff9800;
            border-radius: 8px;
            background: #1e1e2f;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="400" height="500"></canvas>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // 3 Làn đường X coordinates
        const lanes = [90, 200, 310];
        let currentLane = 1; // Làn giữa (0: Trái, 1: Giữa, 2: Phải)

        let player = {
            x: lanes[currentLane],
            y: 400,
            width: 30,
            height: 50,
            vy: 0,
            jumping: false,
            crouching: false,
            crouchTimer: 0
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
                player.vy = -12;
                player.jumping = true;
            } else if ((e.code === "ArrowDown" || e.code === "KeyS") && !player.crouching) {
                player.crouching = true;
                player.crouchTimer = 25; // Thời gian cúi
            }
        });

        function resetGame() {
            currentLane = 1;
            player.y = 400;
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
            // Sinh chướng ngại vật
            if (frameCount % 45 === 0) {
                let lane = Math.floor(Math.random() * 3);
                let type = Math.random() > 0.4 ? "barrier" : "train"; // barrier hoặc train
                obstacles.push({
                    lane: lane,
                    y: -60,
                    width: type === "train" ? 50 : 40,
                    height: type === "train" ? 70 : 30,
                    type: type
                });
            }

            // Sinh tiền xu
            if (frameCount % 30 === 0) {
                let lane = Math.floor(Math.random() * 3);
                coins.push({ lane: lane, y: -20 });
            }
        }

        function update() {
            if (gameOver) return;

            // Di chuyển nhân vật mượt theo làn
            player.x += (lanes[currentLane] - player.x) * 0.3;

            // Xử lý nhảy
            if (player.jumping) {
                player.y += player.vy;
                player.vy += 0.8; // Trọng lực
                if (player.y >= 400) {
                    player.y = 400;
                    player.jumping = false;
                }
            }

            // Xử lý cúi
            if (player.crouching) {
                player.crouchTimer--;
                if (player.crouchTimer <= 0) {
                    player.crouching = false;
                }
            }

            // Cập nhật tốc độ & điểm số
            score += 1;
            if (frameCount % 200 === 0) speed += 0.5;

            // Cập nhật chướng ngại vật
            for (let i = obstacles.length - 1; i >= 0; i--) {
                let obs = obstacles[i];
                obs.y += speed;

                let obsX = lanes[obs.lane];
                let playerH = player.crouching ? 25 : player.height;

                // Kiểm tra va chạm
                if (
                    Math.abs(player.x - obsX) < 25 &&
                    obs.y + obs.height > player.y &&
                    obs.y < player.y + playerH
                ) {
                    // Nếu chướng ngại vật là rào chắn thấp và đang nhảy -> Vượt qua
                    if (obs.type === "barrier" && player.jumping && player.y < 360) {
                        // Vượt qua an toàn
                    } else {
                        gameOver = true;
                    }
                }

                if (obs.y > 550) obstacles.splice(i, 1);
            }

            // Cập nhật xu
            for (let i = coins.length - 1; i >= 0; i--) {
                let c = coins[i];
                c.y += speed;

                let coinX = lanes[c.lane];
                if (Math.abs(player.x - coinX) < 25 && Math.abs(player.y - c.y) < 30) {
                    coinCount++;
                    coins.splice(i, 1);
                } else if (c.y > 550) {
                    coins.splice(i, 1);
                }
            }

            spawnObjects();
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Vẽ đường & 3 làn
            ctx.strokeStyle = "#444";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(145, 0); ctx.lineTo(145, 500);
            ctx.moveTo(255, 0); ctx.lineTo(255, 500);
            ctx.stroke();

            // Vẽ chướng ngại vật
            obstacles.forEach(obs => {
                let x = lanes[obs.lane] - obs.width / 2;
                if (obs.type === "train") {
                    ctx.fillStyle = "#e74c3c"; // Tàu hoả màu đỏ
                    ctx.fillRect(x, obs.y, obs.width, obs.height);
                    ctx.fillStyle = "#f39c12";
                    ctx.fillRect(x + 5, obs.y + 10, obs.width - 10, 15);
                } else {
                    ctx.fillStyle = "#e67e22"; // Rào chắn màu cam
                    ctx.fillRect(x, obs.y, obs.width, obs.height);
                }
            });

            // Vẽ tiền xu
            ctx.fillStyle = "#f1c40f";
            coins.forEach(c => {
                let x = lanes[c.lane];
                ctx.beginPath();
                ctx.arc(x, c.y, 8, 0, Math.PI * 2);
                ctx.fill();
            });

            // Vẽ nhân vật
            ctx.fillStyle = player.crouching ? "#9b59b6" : "#2ecc71";
            let pHeight = player.crouching ? 25 : player.height;
            let pY = player.crouching ? player.y + 25 : player.y;
            ctx.fillRect(player.x - player.width / 2, pY, player.width, pHeight);

            // Vẽ điểm số
            ctx.fillStyle = "#fff";
            ctx.font = "bold 16px Arial";
            ctx.fillText("Score: " + score, 15, 30);
            ctx.fillText("Coins: 🪙 " + coinCount, 15, 55);

            if (gameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#e74c3c";
                ctx.font = "bold 28px Arial";
                ctx.fillText("GAME OVER", 110, 220);
                ctx.fillStyle = "#fff";
                ctx.font = "16px Arial";
                ctx.fillText("Tổng điểm: " + score, 140, 260);
                ctx.fillText("Nhấn 'R' để chơi lại", 130, 300);
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

components.html(game_code, height=520)
