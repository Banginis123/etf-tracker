async function loadEtfs() {
    const res = await fetch("/admin/api/etfs");
    return await res.json();
}

async function loadAlerts() {
    const res = await fetch("/admin/api/alerts");
    return await res.json();
}

function renderEtfStatus(etfs, alerts) {
    const tbody = document.getElementById("etf-status-body");
    tbody.innerHTML = "";

    const lastAlertByEtf = {};
    for (const a of alerts) {
        if (!lastAlertByEtf[a.ticker]) {
            lastAlertByEtf[a.ticker] = a;
        }
    }

    for (const etf of etfs) {
        const lastAlert = lastAlertByEtf[etf.ticker];

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${etf.ticker}</td>
            <td>${etf.ath_price ?? "-"}</td>
            <td>${etf.drop_threshold}</td>
            <td>${lastAlert ? lastAlert.price : "-"}</td>
            <td>${etf.ath_alert_sent ? "YES" : "NO"}</td>
            <td><em>reset vėliau</em></td>
        `;
        tbody.appendChild(tr);
    }
}

function renderAlertHistory(alerts) {
    const tbody = document.getElementById("alert-history-body");
    tbody.innerHTML = "";

    for (const a of alerts) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${a.ticker}</td>
            <td>${a.price}</td>
            <td>${a.ath_price}</td>
            <td>${new Date(a.created_at).toLocaleString()}</td>
        `;
        tbody.appendChild(tr);
    }
}

async function initAdminAlerts() {
    const [etfs, alerts] = await Promise.all([
        loadEtfs(),
        loadAlerts(),
    ]);

    renderEtfStatus(etfs, alerts);
    renderAlertHistory(alerts);
}

document.addEventListener("DOMContentLoaded", initAdminAlerts);
