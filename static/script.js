async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        document.getElementById('stat-vessels').innerText = data.total_vessels;
        document.getElementById('stat-permits').innerText = data.active_permits;
        document.getElementById('stat-inspections').innerText = data.recent_inspections;
        document.getElementById('stat-tickets').innerText = data.tickets_sold;
    } catch (e) {
        console.error(e);
    }
}

async function verify() {
    const cfr = document.getElementById('cfrInput').value;
    const resDiv = document.getElementById('res');
    if (!cfr) return;

    try {
        const response = await fetch(`/api/check_permit/${cfr}`);
        const data = await response.json();
        if (response.ok) {
            resDiv.style.color = "green";
            resDiv.innerHTML = `✅ VALID: ${data.vessel} (Expires: ${data.expires})`;
        } else {
            resDiv.style.color = "red";
            resDiv.innerHTML = `❌ INVALID: ${data.error}`;
        }
    } catch (e) {
        resDiv.innerText = "Server Error";
    }
}

window.onload = loadStats;