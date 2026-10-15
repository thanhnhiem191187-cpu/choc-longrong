import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Subway Chase Game", page_icon="🏃", layout="centered")

st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: white; }
        h1 { text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏃‍♂️ Subway Chase: Chạy Khỏi " + "Đại Ca Cơ Bắp")
st.markdown("<p style='text-align: center;'>Dùng phím <b>Mũi tên Trái / Phải (hoặc A/D)</b> để đổi làn, <b>Mũi tên Lên / Space</b> để nhảy, <b>Mũi tên Xuống</b> để cúi!</p>", unsafe_allow_html=True)

game_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Subway Chase Game</title>
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
            overflow: hidden;
        }
        canvas {
            border: 4px solid #ffcc00;
            border-radius: 12px;
            background: linear-gradient(to bottom, #1a1a2e, #16213e);
            box-shadow: 0 0 20px rgba(255, 204, 0, 0.5);
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="400" height="550"></canvas>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // 3 làn đường (Tọa độ X trung tâm mỗi làn)
        const lanes = [95, 200, 305];
        let currentLane = 1;

        // Nhân vật chạy trốn (người chơi)
        let player = {
            x: lanes[currentLane],
            y: 420,
            width: 28,
            height: 45,
            vy: 0,
            jumping: false,
            crouching: false,
            crouchTimer: 0
        };

        // Người đuổi theo (Phía sau)
        let chaser = {
            lane: 1,
            x: lanes[1],
            y: 480,
            width: 32,
            height: 50
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
                player.vy = -13;
                player.jumping = true;
            } else if ((e.code === "ArrowDown" || e.code === "KeyS") && !player.crouching) {
                player.crouching = true;
                player.crouchTimer = 25;
            }
        });

        function resetGame() {
            currentLane = 1;
            player.y = 420;
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
            // Sinh chướng ngại vật (Tàu hỏa hoặc Rào chắn)
            if (frameCount % 50 === 0) {
                let lane = Math.floor(Math.random() * 3);
                let type = Math.random() > 0.4 ? "train" : "barrier";
                obstacles.push({
                    lane: lane,
                    y: -70,
                    width: type === "train" ? 55 : 45,
                    height: type === "train" ? 80 : 35,
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

            // Di chuyển mượt nhân vật theo làn
            player.x += (lanes[currentLane] - player.x) * 0.3;
            chaser.lane = currentLane; // Người đuổi bám theo làn của người chơi
            chaser.x += (lanes[chaser.lane] - chaser.x) * 0.2;

            // Xử lý nhảy
            if (player.jumping) {
                player.y += player.vy;
                player.vy += 0.85;
                if (player.y >= 420) {
                    player.y = 420;
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

            score += 1;
            if (frameCount % 250 === 0) speed += 0.5;

            // Cập nhật chướng ngại vật
            for (let i = obstacles.length - 1; i >= 0; i--) {
                let obs = obstacles[i];
                obs.y += speed;

                let obsX = lanes[obs.lane];
                let pHeight = player.crouching ? 25 : player.height;

                // Kiểm tra va chạm với chướng ngại vật
                if (
                    Math.abs(player.x - obsX) < 25 &&
                    obs.y + obs.height > player.y &&
                    obs.y < player.y + pHeight
                ) {
                    if (!(obs.type === "barrier" && player.jumping && player.y < 370)) {
                        gameOver = true;
                    }
                }

                if (obs.y > 600) obstacles.splice(i, 1);
            }

            // Cập nhật tiền xu
            for (let i = coins.length - 1; i >= 0; i--) {
                let c = coins[i];
                c.y += speed;

                let coinX = lanes[c.lane];
                if (Math.abs(player.x - coinX) < 25 && Math.abs(player.y - c.y) < 30) {
                    coinCount++;
                    coins.splice(i, 1);
                } else if (c.y > 600) {
                    coins.splice(i, 1);
                }
            }

            spawnObjects();
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Vẽ đường ray và 3 làn đường
            ctx.strokeStyle = "#33334d";
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(145, 0); ctx.lineTo(145, 550);
            ctx.moveTo(255, 0); ctx.lineTo(255, 550);
            ctx.stroke();

            // Vẽ hiệu ứng đường chạy (thanh ngang chuyển động)
            ctx.strokeStyle = "#22223b";
            ctx.lineWidth = 1;
            for (let y = (frameCount * speed) % 30; y < 550; y += 30) {
                ctx.beginPath();
                ctx.moveTo(95, y); ctx.lineTo(305, y);
                ctx.stroke();
            }

            // Vẽ chướng ngại vật
            obstacles.forEach(obs => {
                let x = lanes[obs.lane] - obs.width / 2;
                if (obs.type === "train") {
                    ctx.fillStyle = "#e63946"; // Tàu hỏa
                    ctx.fillRect(x, obs.y, obs.width, obs.height);
                    ctx.fillStyle = "#ffb703"; // Kính tàu
                    ctx.fillRect(x + 6, obs.y + 10, obs.width - 12, 18);
                } else {
                    ctx.fillStyle = "#fb8500"; // Rào chắn
                    ctx.fillRect(x, obs.y, obs.width, obs.height);
                    ctx.fillStyle = "#ffffff";
                    ctx.fillRect(x + 5, obs.y + 5, obs.width - 10, 8);
                }
            });

            // Vẽ tiền xu
            ctx.fillStyle = "#ffd166";
            coins.forEach(c => {
                let x = lanes[c.lane];
                ctx.beginPath();
                ctx.arc(x, c.y, 8, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = "#f3722c";
                ctx.stroke();
            });

            // Vẽ Nhân vật chạy trốn (Bạn tự làm - màu xanh lá sáng)
            ctx.fillStyle = player.crouching ? "#7209b7" : "#4cc9f0";
            let pHeight = player.crouching ? 25 : player.height;
            let pY = player.crouching ? player.y + 20 : player.y;
            ctx.fillRect(player.x - player.width / 2, pY, player.width, pHeight);
            // Đầu nhân vật chạy
            ctx.fillStyle = "#f8f9fa";
            ctx.beginPath();
            ctx.arc(player.x, pY - 6, 8, 0, Math.PI * 2);
            ctx.fill();

            // Vẽ Người đuổi theo (Ảnh 1 - Đại ca cơ bắp xăm trổ màu cam đỏ hung dữ phía sau)
            ctx.fillStyle = "#ff5964";
            ctx.fillRect(chaser.x - chaser.width / 2, chaser.y, chaser.width, chaser.height);
            // Đầu người đuổi
            ctx.fillStyle = "#d90429";
            ctx.beginPath();
            ctx.arc(chaser.x, chaser.y - 8, 10, 0, Math.PI * 2);
            ctx.fill();
            // Ký hiệu "Xăm" hoặc mắt đỏ ngầu gầm gừ
            ctx.fillStyle = "#ffffff";
            ctx.font = "10px Arial";
            ctx.fillText("💢", chaser.x - 6, chaser.y - 15);

            // Vẽ thông tin điểm số & tiền
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 15px Arial";
            ctx.fillText("Score: " + score, 15, 30);
            ctx.fillText("Coins: 🪙 " + coinCount, 15, 55);

            if (gameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#ff3333";
                ctx.font = "bold 26px Arial";
                ctx.fillText("BẮT ĐƯỢC RỒI! 💥", 100, 210);
                ctx.fillStyle = "#ffffff";
                ctx.font = "15px Arial";
                ctx.fillText("Điểm số của bạn: " + score, 130, 255);
                ctx.fillText("Nhấn 'R' để chạy trốn lại", 115, 295);
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

components.html(game_code, height=580)
