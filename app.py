const dino = document.getElementById("dino");
const cactus = document.getElementById("cactus");
const scoreDisplay = document.getElementById("score");

let score = 0;
let isAlive = setInterval(function () {
    // Lấy vị trí Y hiện tại của nhân vật
    let dinoTop = parseInt(window.getComputedStyle(dino).getPropertyValue("bottom"));
    // Lấy vị trí X hiện tại của chướng ngại vật
    let cactusLeft = parseInt(window.getComputedStyle(cactus).getPropertyValue("left"));

    // Kiểm tra va chạm (Nếu chướng ngại vật đâm trúng nhân vật khi chưa nhảy đủ cao)
    if (cactusLeft > 50 && cactusLeft < 90 && dinoTop <= 40) {
        alert("Game Over! Số điểm của bạn là: " + score);
        score = 0;
        scoreDisplay.innerText = "Điểm: " + score;
    } else if (cactusLeft < 0) {
        // Mỗi lần vượt qua chướng ngại vật thành công (block đi hết màn hình bên trái)
        score++;
        scoreDisplay.innerText = "Điểm: " + score;
    }
}, 10);

// Hàm xử lý nhảy
function jump() {
    if (!dino.classList.contains("jump")) {
        dino.classList.add("jump");
        setTimeout(function () {
            dino.classList.remove("jump");
        }, 500);
    }
}

// Bắt sự kiện phím Space
document.addEventListener("keydown", function (event) {
    if (event.code === "Space") {
        jump();
    }
});

// Hỗ trợ click chuột hoặc chạm màn hình trên điện thoại
document.addEventListener("click", jump);
