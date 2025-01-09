const mobileMenu = document.getElementById('mobile-menu');
const navList = document.querySelector('.nav-list');

mobileMenu.addEventListener('click', () => {
    navList.classList.toggle('active');
});

//=============================================================
// 非同期でPOSTリクエストを送信
//=============================================================
async function sendCommand(command) {
    try {
        const response = await fetch('/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `command=${encodeURIComponent(command)}`,
        });
        const result = await response.text();
        // レスポンスを結果表示ボックスに表示
        document.getElementById('result-box').value = result;
    } catch (error) {
        console.error('Error sending command:', error);
        document.getElementById('result-box').value = 'Error sending command.';
    }
}
//-------------------------------------------
// ページ遷移を防ぐ
function handleSubmit(event) {
    event.preventDefault();
    const command = document.getElementById('command-input').value;
    sendCommand(command);
}
