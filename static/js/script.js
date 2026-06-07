window.onload = () => {
    const user = localStorage.getItem('user');
    const isAuthPage = window.location.pathname === '/' || window.location.pathname === '/login' || window.location.pathname === '/register';

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
        if (window.location.pathname === '/dashboard') {
            loadDashboardData();
        }
        if (window.location.pathname === '/fines') {
            loadFineData();
        }
        if (document.getElementById('ticketHistory')) {
            loadTicketHistory();
        }
        if (document.getElementById('inspectionHistory')) {
            loadInspectionHistory();
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
        if (document.getElementById('detail-username')) document.getElementById('detail-username').innerText = data.username || '—';
        
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
    try {
        console.log('Attempting login for', u);
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: u, password: p })
        });

        if (!res.ok) {
            const errText = await res.text().catch(() => '');
            console.warn('Login failed', res.status, errText);
            alert('❌ Грешно потребителско име или парола!');
            return;
        }

        const data = await res.json().catch(err => {
            console.error('Failed to parse login response JSON', err);
            return null;
        });
        if (!data || !data.username) {
            alert('❌ Невалиден отговор от сървъра при логин. Вижте конзолата.');
            return;
        }
        localStorage.setItem('user', data.username);
        window.location.href = '/dashboard';
    } catch (err) {
        console.error('Login error', err);
        alert('❌ Грешка при връзка със сървъра. Проверете конзолата.');
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

    try {
        console.log('Registering', u, em);
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: u, email: em, password: p, fullname: fn, phone: ph, role: r, vessel: v, permit: perm })
        });

        if (res.ok) {
            alert('✅ Регистрацията е успешна!');
            window.location.href = '/login';
        } else {
            const txt = await res.text().catch(() => '');
            console.warn('Register failed', res.status, txt);
            alert('❌ Потребителското име или имейл вече съществуват! Вижте конзолата.');
        }
    } catch (err) {
        console.error('Register error', err);
        alert('❌ Грешка при връзка със сървъра. Проверете конзолата.');
    }
}

async function triggerEditProfile() {
    const currentUser = localStorage.getItem('user');
    if (!currentUser) return;
    const currentName = document.getElementById('detail-name').innerText;
    const currentEmail = document.getElementById('detail-email').innerText;
    const currentPhone = document.getElementById('detail-phone').innerText;

    const newName = prompt('Въведете ново Пълно Име:', currentName === '—' ? '' : currentName);
    if (newName === null) return;
    const newEmail = prompt('Въведете нов Имейл:', currentEmail === '—' ? '' : currentEmail);
    if (newEmail === null) return;
    const newPhone = prompt('Въведете нов Телефон:', currentPhone === '—' ? '' : currentPhone);
    if (newPhone === null) return;

    const res = await fetch(`/api/user/${currentUser}/edit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fullname: newName, email: newEmail, phone: newPhone })
    });

    if (res.ok) {
        alert('✅ Профилът е обновен успешно!');
        loadUserProfileData(currentUser);
    } else {
        alert('❌ Грешка при обновяване на профила.');
    }
}

async function triggerChangePassword() {
    const currentUser = localStorage.getItem('user');
    if (!currentUser) return;

    const newPass = prompt('Въведете нова парола:');
    if (!newPass) {
        alert('Паролата не може да бъде празна!');
        return;
    }

    const res = await fetch(`/api/user/${currentUser}/password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: newPass })
    });

    if (res.ok) {
        alert('✅ Паролата е сменена успешно!');
    } else {
        alert('❌ Грешка при смяна на паролата.');
    }
}

async function verify() {
    const cfrInput = document.getElementById('cfrInput');
    if (!cfrInput) return;
    const cfr = cfrInput.value.toUpperCase();
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
        resDiv.innerHTML = '❌ Кораб с такъв CFR не е намерен в базата данни.';
    }
}

async function issueTicket() {
    const select = document.getElementById('ticketType');
    const msg = document.getElementById('ticketMsg');
    if (!select || !msg) return;
    const res = await fetch('/api/issue_ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: select.options[select.selectedIndex].text, price: select.value })
    });
    msg.style.display = 'block';
    msg.innerText = res.ok ? '✅ Билетът е записан в базата!' : '❌ Грешка!';
    if (document.getElementById('ticketHistory')) {
        loadTicketHistory();
    }
}

async function loadTicketHistory() {
    const list = document.getElementById('ticketHistory');
    if (!list) return;
    list.innerHTML = '<li style="color: var(--muted);">Зареждане...</li>';
    const res = await fetch('/api/tickets');
    if (!res.ok) {
        list.innerHTML = '<li style="color: #ff6b6b;">Неуспешно зареждане на историята.</li>';
        return;
    }
    const tickets = await res.json();
    if (!tickets.length) {
        list.innerHTML = '<li style="color: var(--muted);">Няма издадени билети към момента.</li>';
        return;
    }
        list.innerHTML = tickets.map(ticket => `
            <li style="background: rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:14px; display:flex; justify-content:space-between; gap:12px;">
                <div>
                    <strong>${ticket.ticket_type}</strong><br>
                    <span style="color: var(--muted); font-size:0.95rem;">${ticket.timestamp}</span>
                </div>
                <div style="font-weight:700;">${ticket.price.toFixed(2)} €</div>
            </li>
        `).join('');
}

async function loadDashboardData() {
    const res = await fetch('/api/dashboard_stats');
    if (!res.ok) {
        console.warn('Неуспешно зареждане на статистики за таблото');
        return;
    }
    const data = await res.json();
    document.getElementById('stat-vessels').innerText = data.total_vessels;
    document.getElementById('stat-permits').innerText = data.active_permits;
    document.getElementById('stat-inspections').innerText = data.total_inspections;
    document.getElementById('stat-tickets').innerText = data.total_tickets;
    document.getElementById('stat-revenue').innerText = `${data.total_revenue.toFixed(2)} €`;

    const operations = document.getElementById('recentOperations');
    if (operations) {
        operations.innerHTML = data.recent_operations.length ? data.recent_operations.map(op => `
            <li>
                <div class="transaction-info">
                    <strong>${op.title}</strong>
                    <span>${op.timestamp}</span>
                </div>
                <div class="amount positive">${op.status}</div>
            </li>
        `).join('') : '<li style="color: var(--muted);">Няма последни операции.</li>';
    }
}

async function submitInspection() {
    const location = document.getElementById('inspectionLocation').value.trim();
    const inspector = document.getElementById('inspectionInspector').value.trim();
    const type = document.getElementById('inspectionTargetType').value.trim();
    const targetId = document.getElementById('inspectionTargetId').value.trim();
    const notes = document.getElementById('inspectionNotes').value.trim();
    const msg = document.getElementById('inspectionMsg');

    if (!location || !inspector || !type || !targetId) {
        msg.innerText = '❗ Попълнете всички задължителни полета.';
        return;
    }

    const res = await fetch('/api/inspection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inspector: inspector, target_type: type, target_id: targetId, location: location, notes: notes })
    });

    if (res.ok) {
        msg.innerText = '✅ Инспекцията е записана успешно!';
        document.getElementById('inspectionLocation').value = '';
        document.getElementById('inspectionInspector').value = '';
        document.getElementById('inspectionTargetType').value = '';
        document.getElementById('inspectionTargetId').value = '';
        document.getElementById('inspectionNotes').value = '';
        loadInspectionHistory();
        loadDashboardData();
    } else {
        msg.innerText = '❌ Възникна проблем при запис на инспекцията.';
    }
}

async function loadInspectionHistory() {
    const list = document.getElementById('inspectionHistory');
    if (!list) return;
    list.innerHTML = '<li style="color: var(--muted);">Зареждане...</li>';
    const res = await fetch('/api/inspections');
    if (!res.ok) {
        list.innerHTML = '<li style="color: #ff6b6b;">Неуспешно зареждане на инспекции.</li>';
        return;
    }
    const inspections = await res.json();
    if (!inspections.length) {
        list.innerHTML = '<li style="color: var(--muted);">Няма записани инспекции към момента.</li>';
        return;
    }
    list.innerHTML = inspections.map(ins => `
            <li style="background: rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:14px;">
                <div style="display:flex; justify-content:space-between; gap:12px; align-items:center;">
                    <div>
                        <strong>Инспектор: ${ins.inspector}</strong><br>
                        <span style="color: var(--muted); font-size:0.95rem;">${ins.timestamp}</span>
                    </div>
                    <div style="font-weight:700;">${ins.target_type} ${ins.target_id}</div>
                </div>
                <div style="margin-top: 8px; color: var(--muted);">${ins.notes || 'Няма бележки'}</div>
            </li>
        `).join('');
}

async function saveCatchToDB(fishType, location) {
    await fetch('/api/save_catch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fish_type: fishType, location: location })
    });
}

async function loadFineData() {
    const res = await fetch('/api/fines');
    const list = document.getElementById('fineList');
    const count = document.getElementById('fineCount');
    const total = document.getElementById('fineTotal');
    const paidCount = document.getElementById('finePaidCount');
    const unpaidCount = document.getElementById('fineUnpaidCount');

    if (!res.ok) {
        if (list) list.innerHTML = '<li style="color: #ff6b6b;">Грешка при зареждане на глоби.</li>';
        return;
    }

    const fines = await res.json();
    const sum = fines.reduce((acc, fine) => acc + parseFloat(fine.amount), 0);
    const paid = fines.filter(fine => fine.paid).length;
    const unpaid = fines.length - paid;

    if (count) count.innerText = fines.length;
    if (total) total.innerText = `${sum.toFixed(2)} €`;
    if (paidCount) paidCount.innerText = paid;
    if (unpaidCount) unpaidCount.innerText = unpaid;

    if (!list) return;
    if (!fines.length) {
        list.innerHTML = '<li style="color: var(--muted);">Няма записани глоби към момента.</li>';
        return;
    }

    list.innerHTML = fines.map(fine => `
        <li style="background: rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:18px; display:grid; gap:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:12px;">
                <div>
                    <strong>Глоба #${fine.id}</strong><br>
                    <span style="color: var(--muted); font-size:0.95rem;">Издадена: ${fine.issued_at}</span>
                </div>
                <div style="font-weight:700;">${fine.amount.toFixed(2)} €</div>
            </div>
            <div style="display:grid; gap:6px; color: var(--muted);">
                <span>Издадено на: ${fine.issued_to || '—'}</span>
                <span>Инспекция: ${fine.inspection_id || '—'}</span>
                <span>Статус: ${fine.paid ? 'Платена' : 'Неплатена'}</span>
            </div>
            <div style="display:flex; justify-content:flex-end;">
                ${fine.paid ? '<button disabled style="opacity:.55; padding:10px 16px; border-radius:12px; border:none; background:#6c757d; color:#fff;">Платена</button>' : `<button class="primary" style="padding:10px 16px; border-radius:12px;" onclick="payFine(${fine.id})">Отбележи като платена</button>`}
            </div>
        </li>
    `).join('');
}

async function submitFine() {
    const inspectionId = document.getElementById('fineInspectionId').value.trim();
    const issuedTo = document.getElementById('fineIssuedTo').value.trim();
    const amount = document.getElementById('fineAmount').value.trim();
    const notes = document.getElementById('fineNotes').value.trim();
    const msg = document.getElementById('fineMsg');

    if (!issuedTo || !amount) {
        msg.innerText = '❗ Попълнете полето за получател и сумата.';
        return;
    }

    const res = await fetch('/api/issue_fine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inspection_id: inspectionId || null, amount: amount, issued_to: issuedTo, notes: notes })
    });

    if (res.ok) {
        msg.innerText = '✅ Глобата е издадена успешно!';
        document.getElementById('fineInspectionId').value = '';
        document.getElementById('fineIssuedTo').value = '';
        document.getElementById('fineAmount').value = '';
        document.getElementById('fineNotes').value = '';
        loadFineData();
    } else {
        msg.innerText = '❌ Възникна проблем при издаване на глобата.';
    }
}

async function payFine(id) {
    const res = await fetch('/api/fine/pay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    });

    if (res.ok) {
        loadFineData();
    } else {
        alert('❌ Неуспешно отбелязване на плащането.');
    }
}
