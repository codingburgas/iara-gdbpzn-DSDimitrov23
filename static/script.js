function showSection(sectionId) {
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('tickets-section').style.display = 'none';
    document.getElementById('inspections-section').style.display = 'none';

    document.getElementById(sectionId + '-section').style.display = 'block';
}

async function verify() {
    const cfr = document.getElementById('cfrInput').value.toUpperCase();
    const resDiv = document.getElementById('res');
    
    if (!cfr) {
        resDiv.innerHTML = "⚠️ Моля, въведете номер";
        return;
    }

    try {
        const response = await fetch(`/api/check_permit/${cfr}`);
        const data = await response.json();
        
        if (response.ok) {
            resDiv.innerHTML = `<div style="color: green; padding: 10px; border: 1px solid green;">
                ✅ Валиден лиценз! <br> Кораб: ${data.vessel} <br> Валиден до: ${data.expires}
            </div>`;
        } else {
            resDiv.innerHTML = `<div style="color: red; padding: 10px; border: 1px solid red;">
                ❌ Грешка: ${data.error || data.status}
            </div>`;
        }
    } catch (e) {
        resDiv.innerHTML = "❌ Сървърна грешка";
    }
}

function issueTicket() {
    const price = document.getElementById('ticketType').value;
    const msg = document.getElementById('ticketMsg');
    
    if (price === "0") {
        msg.style.color = "blue";
        msg.innerText = "✅ Билетът е безплатен (изисква се ТЕЛК решение).";
    } else {
        msg.style.color = "green";
        msg.innerText = `✅ Успешно издаден билет. Дължима сума: ${price}.00 лв.`;
    }
}