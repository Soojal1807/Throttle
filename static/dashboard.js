const ctxGlobal = document.getElementById('globalChart').getContext('2d');
const ctxIp = document.getElementById('ipChart').getContext('2d');

let globalChart = new Chart(ctxGlobal, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Global Requests/Sec', data: [], borderColor: 'blue' }] },
    options: { animation: false, scales: { y: { beginAtZero: true } } }
});

let ipChart = new Chart(ctxIp, {
    type: 'bar',
    data: { labels: [], datasets: [{ label: 'IP Activity', data: [], backgroundColor: 'red' }] },
    options: { animation: false }
});

async function updateDashboard() {
    // 1. Global Graph
    const res = await fetch('/api/stats/global');
    const data = await res.json();

    // Bucket timestamps
    const now = Math.floor(Date.now() / 1000);
    const buckets = {};
    for (let i = 0; i < 30; i++) buckets[now - i] = 0;
    data.timestamps.forEach(t => {
        const sec = Math.floor(t);
        if (buckets[sec] !== undefined) buckets[sec]++;
    });

    globalChart.data.labels = Object.keys(buckets).sort();
    globalChart.data.datasets[0].data = Object.keys(buckets).sort().map(k => buckets[k]);
    globalChart.update();

    // 2. Flagged List
    const flagRes = await fetch('/api/stats/flagged');
    const flagged = await flagRes.json();
    const listDiv = document.getElementById('flaggedList');
    listDiv.innerHTML = '';
    Object.keys(flagged).forEach(ip => {
        const item = document.createElement('div');
        item.className = 'flagged-item';
        item.innerText = `${ip} - ${flagged[ip].reason}`;
        item.onclick = () => showIpDetail(ip);
        listDiv.appendChild(item);
    });
}

async function showIpDetail(ip) {
    document.getElementById('selectedIp').innerText = `History for: ${ip}`;
    const res = await fetch(`/api/stats/ip/${ip}`);
    const data = await res.json();

    const now = Math.floor(Date.now() / 1000);
    const buckets = {};
    for (let i = 0; i < 60; i++) buckets[now - i] = 0;
    data.history.forEach(t => {
        const sec = Math.floor(t);
        if (buckets[sec] !== undefined) buckets[sec]++;
    });

    ipChart.data.labels = Object.keys(buckets).sort();
    ipChart.data.datasets[0].data = Object.keys(buckets).sort().map(k => buckets[k]);
    ipChart.update();
}

setInterval(updateDashboard, 2000);