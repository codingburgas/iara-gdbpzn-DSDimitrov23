window.onload = () => {
    const user = localStorage.getItem('user');
    const isAuthPage = window.location.pathname === '/login' || window.location.pathname === '/register';

    if (user) {
        if (document.body) {
            document.body.style.display = 'flex';
        }
        if (document.getElementById('userGreeting')) {
            document.getElementById('userGreeting').innerText = `👤 Инспектор: ${user}`;
        }
        loadUserProfileData(user);
        if (document.getElementById('authBtn')) {
            document.getElementById('authBtn').innerText = "Изход";
            document.getElementById('authBtn').style.background = "#c0392b";
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

async function loadUserProfileData(username) {
    const res = await fetch(`/api/user/${username}`);
    if (res.ok) {
        const data = await res.json();
        
        if (document.getElementById('prof-name')) document.getElementById('prof-name').innerText = data.fullname || data.username;
        if (document.getElementById('prof-role')) document.getElementById('prof-role').innerText = data.role || 'Любител';
        if (document.getElementById('prof-date')) document.getElementById('prof-date').innerText = `Член от: ${data.member_since}`;
        
        if (document.getElementById('detail-name')) document.getElementById('detail-name').innerText = data.fullname || '—';
        if (document.getElementById('detail-email')) document.getElementById('detail-email').innerText = data.email || '—';
        if (document.getElementById('detail-phone')) document.getElementById('detail-phone').innerText = data.phone || '—';
        if (document.getElementById('detail-role')) document.getElementById('detail-role').innerText = data.role || '—';
        if (document.getElementById('detail-vessel')) document.getElementById('detail-vessel').innerText = data.vessel || '—';
        if (document.getElementById('detail-permit')) document.getElementById('detail-permit').innerText = data.permit || '—';
        
        if (document.getElementById('avatar-initials')) {
            let initials = "??";
            if (data.fullname && data.fullname.trim().length > 0) {
                const parts = data.fullname.trim().split(' ');
                initials = parts.length > 1 ? (parts[0][0] + parts[1][0]).toUpperCase() : parts[0][0].toUpperCase();
            } else {
                initials = data.username.substring(0, 2).toUpperCase();
            }
            document.getElementById('avatar-initials').innerText = initials;
        }
    }
}

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
    const fn = document.getElementById('regFullName').value;
    const ph = document.getElementById('regPhone').value;
    const r = document.getElementById('regRole').value;
    const v = document.getElementById('regVessel').value;
    const perm = document.getElementById('regPermit').value;

    const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, email: em, password: p, fullname: fn, phone: ph, role: r, vessel: v, permit: perm })
    });

    if (res.ok) {
        alert("✅ Регистрацията е успешна!");
        window.location.href = '/login';
    } else {
        alert("❌ Потребителското име или имейл вече съществуват!");
    }
}

async function triggerEditProfile() {
    const currentUser = localStorage.getItem('user');
    if (!currentUser) return;
    const currentName = document.getElementById('detail-name').innerText;
    const currentEmail = document.getElementById('detail-email').innerText;
    const currentPhone = document.getElementById('detail-phone').innerText;

    const newName = prompt("Въведете ново Пълно Име:", currentName === '—' ? '' : currentName);
    if (newName === null) return;
    const newEmail = prompt("Въведете нов Имейл:", currentEmail === '—' ? '' : currentEmail);
    if (newEmail === null) return;
    const newPhone = prompt("Въведете нов Телефон:", currentPhone === '—' ? '' : currentPhone);
    if (newPhone === null) return;

    const res = await fetch(`/api/user/${currentUser}/edit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fullname: newName, email: newEmail, phone: newPhone })
    });

    if (res.ok) {
        alert("✅ Профилът е обновен успешно!");
        loadUserProfileData(currentUser);
    } else {
        alert("❌ Грешка при обновяване на профила.");
    }
}

async function triggerChangePassword() {
    const currentUser = localStorage.getItem('user');
    if (!currentUser) return;

    const newPass = prompt("Въведете нова парола:");
    if (!newPass) {
        alert("Паролата не може да бъде празна!");
        return;
    }

    const res = await fetch(`/api/user/${currentUser}/password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: newPass })
    });

    if (res.ok) {
        alert("✅ Паролата е сменена успешно!");
    } else {
        alert("❌ Грешка при смяна на паролата.");
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