window.onload = () => {
    const user = localStorage.getItem('user');
    if (user) {
        document.getElementById('userGreeting').innerText = `👤 Инспектор: ${user}`;
        document.getElementById('authBtn').innerText = "Изход";
        document.getElementById('authBtn').onclick = () => {
            localStorage.removeItem('user');
            window.location.reload();
        };
    }
};

async function verify() {
    const cfr = document.getElementById('cfrInput').value.toUpperCase();
    const resDiv = document.getElementById('res');
    if (!cfr) return;
    const res = await fetch(`/api/check_permit/${cfr}`);
    const data = await res.json();
    resDiv.style.display = 'block';
    if (res.ok) {
        resDiv.style.background = '#d4edda';
        resDiv.innerHTML = `✅ Кораб: ${data.vessel}<br>Капитан: ${data.captain}<br>До: ${data.expires}`;
    } else {
        resDiv.style.background = '#f8d7da';
        resDiv.innerHTML = `❌ Грешка`;
    }
}

async function issueTicket() {
    const select = document.getElementById('ticketType');
    const msg = document.getElementById('ticketMsg');
    const res = await fetch('/api/issue_ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: select.options[select.selectedIndex].text, price: select.value })
    });
    msg.style.display = 'block';
    msg.innerText = res.ok ? "✅ Билетът е записан в базата!" : "❌ Грешка!";
}

async function saveCatchToDB(fishType, location) {
    await fetch('/api/save_catch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fish_type: fishType, location: location })
    });
}