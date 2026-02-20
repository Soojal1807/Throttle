let spamInterval = null;

async function sendRequest() {
    const log = document.getElementById('log');
    try {
        const res = await fetch('/api/request');
        const data = await res.json();
        const time = new Date().toLocaleTimeString();
        log.innerHTML = `<div>[${time}] Status: <strong>${data.status}</strong> (Active: ${data.active || 0})</div>` + log.innerHTML;
    } catch (e) {
        log.innerHTML = `<div>Error connecting to server</div>` + log.innerHTML;
    }
}

function toggleSpam() {
    const btn = document.getElementById('spamBtn');
    if (spamInterval) {
        clearInterval(spamInterval);
        spamInterval = null;
        btn.innerText = "Start Spam Mode";
    } else {
        // 4 requests/sec
        spamInterval = setInterval(sendRequest, 250);
        btn.innerText = "Stop Spam Mode";
    }
}