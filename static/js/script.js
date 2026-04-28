async function verify() {
    const cfr = document.getElementById('cfrInput').value.toUpperCase();
    const resDiv = document.getElementById('res');
    
    if (!cfr) {
        resDiv.style.display = 'block';
        resDiv.innerHTML = "⚠️ Моля, въведете номер";
        return;
    }

    try {
        const response = await fetch(`/api/check_permit/${cfr}`);
        const data = await response.json();
        
        resDiv.style.display = 'block';
        if (response.ok) {
            resDiv.style.background = '#d4edda';
            resDiv.innerHTML = `<div style="color: #155724;">
                <strong>✅ Валиден лиценз!</strong><br>
                Съд: ${data.vessel}<br>
                Капитан: ${data.captain}<br>
                Валидност до: ${data.expires}
            </div>`;
        } else {
            resDiv.style.background = '#f8d7da';
            resDiv.innerHTML = `<div style="color: #721c24;">❌ ${data.error || 'Невалиден лиценз'}</div>`;
        }
    } catch (e) {
        resDiv.style.display = 'block';
        resDiv.innerHTML = "❌ Грешка при връзка със сървъра.";
    }
}

async function issueTicket() {
    const select = document.getElementById('ticketType');
    const price = select.value;
    const typeText = select.options[select.selectedIndex].text;
    const msg = document.getElementById('ticketMsg');
    
    try {
        const response = await fetch('/api/issue_ticket', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: typeText, price: price })
        });

        msg.style.display = 'block';
        if (response.ok) {
            msg.style.background = '#d4edda';
            msg.style.color = "#155724";
            msg.innerText = `✅ Успешно записан: ${typeText}`;
        } else {
            msg.style.background = '#f8d7da';
            msg.innerText = "❌ Грешка при запис в базата.";
        }
    } catch (e) {
        msg.style.display = 'block';
        msg.innerText = "❌ Сървърът не отговаря.";
    }
}