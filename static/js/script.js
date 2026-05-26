window.onload = () => {
    const user = localStorage.getItem('user');
    const isAuthPage = window.location.pathname === '/login' || window.location.pathname === '/register';

    if (user) {
        if (document.getElementById('userGreeting')) {
            document.getElementById('userGreeting').innerText = `👤 Инспектор: ${user}`;
        }
        if (document.getElementById('authBtn')) {
            document.getElementById('authBtn').innerText = "Изход";
            document.getElementById('authBtn').onclick = () => {
                localStorage.removeItem('user');
                window.location.href = '/login';
            };
        }
    } else {
        if (!isAuthPage) {
            window.location.href = '/login';
        }
    }
};

async function handleLogin(e) {
    e.preventDefault();
    const u = document.getElementById('loginUser').value;
    const p = document.getElementById('loginPass').value;

    const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p })
    });

    if (res.ok) {
        const data = await res.json();
        localStorage.setItem('user', data.username);
        window.location.href = '/';
    } else {
        alert("❌ Грешно потребителско име или парола!");
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const u = document.getElementById('regUser').value;
    const em = document.getElementById('regEmail').value;
    const p = document.getElementById('regPass').value;

    const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, email: em, password: p })
    });

    if (res.ok) {
        alert("✅ Регистрацията е успешна!");
        window.location.href = '/login';
    } else {
        alert("❌ Потребителското име или имейл вече съществуват!");
    }
}

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
        resDiv.innerHTML = `❌ Кораб с такъв CFR не е намерен в базата данни.`;
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