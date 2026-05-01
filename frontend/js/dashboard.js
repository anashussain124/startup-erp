/**
 * Dashboard JS — Clean, minimal, decision-focused.
 */
document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    document.getElementById('sidebar').innerHTML = buildSidebar('dashboard');
    loadDashboard();
});

const C = {
    blue: 'rgba(59, 130, 246, 0.85)', purple: 'rgba(139, 92, 246, 0.85)',
    green: 'rgba(16, 185, 129, 0.85)', amber: 'rgba(245, 158, 11, 0.85)',
    red: 'rgba(239, 68, 68, 0.85)', cyan: 'rgba(6, 182, 212, 0.85)',
};
const Cbg = {
    blue: 'rgba(59, 130, 246, 0.15)', purple: 'rgba(139, 92, 246, 0.15)',
    green: 'rgba(16, 185, 129, 0.15)', amber: 'rgba(245, 158, 11, 0.15)',
    red: 'rgba(239, 68, 68, 0.15)', cyan: 'rgba(6, 182, 212, 0.15)',
};

Chart.defaults.color = '#6b7280';
Chart.defaults.borderColor = '#e5e7eb';
Chart.defaults.font.family = 'Inter, sans-serif';
let charts = {};

async function loadDashboard() {
    showSkeleton('insights-grid', 'insights');
    showSkeleton('kpi-grid', 'kpi');
    await Promise.all([
        loadInsightsAndSummary(),
        loadKPIs(),
        loadForecast(),
        loadRevExpChart(),
        loadExpCatChart(),
        loadProjectChart(),
        loadLeadChart(),
        loadDeptChart(),
        loadMLSummary(),
    ]);
}

// ── Executive Summary + Health Bar + Insights ───────────────────────────
async function loadInsightsAndSummary() {
    try {
        const data = await API.get('/api/insights/summary');
        renderExecSummary(data);
        renderInsights(data.insights);
    } catch {
        document.getElementById('exec-summary').innerHTML = '';
        document.getElementById('insights-grid').innerHTML =
            '<div class="empty-state"><p>Insights unavailable. Add data to generate intelligence.</p></div>';
    }
}

function renderExecSummary(data) {
    const el = document.getElementById('exec-summary');
    const h = data.health || { score: 75, status: 'healthy' };
    const s = data.executive_summary || { status: 'Stable', risk: 'No issues.', action: 'Keep going.' };

    const statusClass = s.status === 'Stable' ? 'stable' : s.status === 'Warning' ? 'warning' : 'critical';
    const statusLabel = s.status === 'Stable' ? 'Your business is stable.' : s.status === 'Warning' ? 'Your business needs attention.' : 'Your business has critical issues.';

    el.innerHTML = `
        <div class="exec-summary">
            <div style="font-size:1rem;font-weight:600;color:var(--text-primary);margin-bottom:8px">${statusLabel}</div>
            <div style="font-size:0.88rem;color:var(--text-secondary);line-height:1.6">${s.risk} ${s.action}</div>
            <div class="health-bar-wrap">
                <span style="font-size:0.75rem;color:var(--text-muted)">Business Health</span>
                <div class="health-bar-track">
                    <div class="health-bar-fill ${h.status}" style="width:${h.score}%"></div>
                </div>
                <span class="health-bar-score ${h.status}">${h.score}%</span>
            </div>
        </div>`;
}

function renderInsights(insights) {
    const el = document.getElementById('insights-grid');
    if (!insights || insights.length === 0) {
        el.innerHTML = `<div class="empty-state"><p>No issues detected. Operations running smoothly.</p></div>`;
        return;
    }
    el.innerHTML = insights.map(i => `
        <div class="insight-card ${i.severity}">
            <div class="insight-title">${i.title}</div>
            <div class="insight-desc">${i.description}</div>
            <span class="insight-badge">${i.severity}</span>
        </div>`).join('');
}

// ── Revenue Forecast Chart ──────────────────────────────────────────────
async function loadForecast() {
    try {
        const data = await API.get('/api/forecast/revenue');
        const tag = document.getElementById('forecast-model-tag');
        if (tag) tag.textContent = data.model === 'ml' ? 'ML Powered' : 'Trend';

        const fmt = d => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const allLabels = [...data.past.dates.map(fmt), ...data.forecast.dates.map(fmt)];
        const pastData = [...data.past.values, ...Array(30).fill(null)];
        const forecastData = [...Array(29).fill(null), data.past.values[data.past.values.length - 1], ...data.forecast.values];

        if (charts.forecast) charts.forecast.destroy();
        charts.forecast = new Chart(document.getElementById('forecastChart'), {
            type: 'line',
            data: {
                labels: allLabels,
                datasets: [
                    { label: 'Actual', data: pastData, borderColor: C.green, backgroundColor: Cbg.green, fill: true, tension: 0.4, pointRadius: 0, borderWidth: 2 },
                    { label: 'Forecast', data: forecastData, borderColor: C.purple, backgroundColor: 'rgba(139,92,246,0.06)', borderDash: [6, 4], fill: true, tension: 0.4, pointRadius: 0, borderWidth: 2 },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'top' }, tooltip: { callbacks: { label: ctx => ctx.parsed.y != null ? `${ctx.dataset.label}: $${ctx.parsed.y.toLocaleString()}` : '' } } },
                scales: { x: { ticks: { maxTicksLimit: 8 } }, y: { ticks: { callback: v => '$' + (v / 1000).toFixed(0) + 'k' } } },
            },
        });
    } catch (err) { console.error('Forecast:', err); }
}

// ── KPIs ─────────────────────────────────────────────────────────────────
async function loadKPIs() {
    try {
        const kpis = await API.get('/api/dashboard/kpis');
        const items = [
            { icon: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>', value: kpis.hcm.total_employees, label: 'Employees', color: 'blue' },
            { icon: '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>', value: formatCurrency(kpis.finance.total_revenue), label: 'Revenue', color: 'green' },
            { icon: '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>', value: formatCurrency(kpis.finance.profit), label: 'Profit', color: kpis.finance.profit >= 0 ? 'green' : 'red' },
            { icon: '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/>', value: kpis.ppm.active_projects, label: 'Active Projects', color: 'purple' },
        ];
        document.getElementById('kpi-grid').innerHTML = items.map(k => `
            <div class="kpi-card">
                <div class="kpi-header"><div class="kpi-icon ${k.color}"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${k.icon}</svg></div></div>
                <div class="kpi-value">${k.value}</div>
                <div class="kpi-label">${k.label}</div>
            </div>`).join('');
    } catch {
        document.getElementById('kpi-grid').innerHTML = '<div class="empty-state"><p>Failed to load metrics.</p></div>';
    }
}

// ── Charts ──────────────────────────────────────────────────────────────
async function loadRevExpChart() {
    try {
        const [rev, exp] = await Promise.all([API.get('/api/dashboard/charts/revenue-trend'), API.get('/api/dashboard/charts/expense-trend')]);
        if (charts.revExp) charts.revExp.destroy();
        charts.revExp = new Chart(document.getElementById('revExpChart'), {
            type: 'line',
            data: { labels: rev.labels, datasets: [
                { label: 'Revenue', data: rev.data, borderColor: C.green, backgroundColor: Cbg.green, fill: true, tension: 0.4, pointRadius: 2 },
                { label: 'Expenses', data: exp.data, borderColor: C.red, backgroundColor: Cbg.red, fill: true, tension: 0.4, pointRadius: 2 },
            ]},
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } }, scales: { y: { ticks: { callback: v => '$' + (v / 1000).toFixed(0) + 'k' } } } },
        });
    } catch (err) { console.error('RevExp:', err); }
}

async function loadExpCatChart() {
    try {
        const data = await API.get('/api/dashboard/charts/expenses-by-category');
        if (charts.expCat) charts.expCat.destroy();
        charts.expCat = new Chart(document.getElementById('expCatChart'), {
            type: 'doughnut',
            data: { labels: data.labels, datasets: [{ data: data.data, backgroundColor: [C.blue, C.purple, C.green, C.amber, C.red, C.cyan], borderWidth: 0 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } }, cutout: '65%' },
        });
    } catch (err) { console.error('ExpCat:', err); }
}

async function loadProjectChart() {
    try {
        const data = await API.get('/api/dashboard/charts/project-status');
        if (charts.proj) charts.proj.destroy();
        charts.proj = new Chart(document.getElementById('projChart'), {
            type: 'bar',
            data: { labels: data.labels.map(s => s.charAt(0).toUpperCase() + s.slice(1)), datasets: [{ data: data.data, backgroundColor: [Cbg.blue, Cbg.green, Cbg.cyan, Cbg.red, Cbg.amber], borderColor: [C.blue, C.green, C.cyan, C.red, C.amber], borderWidth: 1, borderRadius: 4 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } },
        });
    } catch (err) { console.error('Proj:', err); }
}

async function loadLeadChart() {
    try {
        const data = await API.get('/api/dashboard/charts/lead-pipeline');
        if (charts.lead) charts.lead.destroy();
        charts.lead = new Chart(document.getElementById('leadChart'), {
            type: 'bar',
            data: { labels: data.labels.map(s => s.charAt(0).toUpperCase() + s.slice(1)), datasets: [{ data: data.data, backgroundColor: [C.cyan, C.blue, C.green, C.purple, C.green, C.red], borderRadius: 4 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, indexAxis: 'y', scales: { x: { beginAtZero: true, ticks: { stepSize: 1 } } } },
        });
    } catch (err) { console.error('Lead:', err); }
}

async function loadDeptChart() {
    try {
        const data = await API.get('/api/dashboard/charts/department-headcount');
        if (charts.dept) charts.dept.destroy();
        charts.dept = new Chart(document.getElementById('deptChart'), {
            type: 'bar',
            data: { labels: data.labels, datasets: [{ data: data.data, backgroundColor: C.blue, borderRadius: 4 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } },
        });
    } catch (err) { console.error('Dept:', err); }
}

// ── ML Summary ──────────────────────────────────────────────────────────
async function loadMLSummary() {
    const el = document.getElementById('ml-summary');
    try {
        const [attrition, churn, risk] = await Promise.allSettled([
            API.post('/api/ml/predict/attrition', { salary: 55000, tenure_years: 2, performance_rating: 3.0, department_encoded: 1, overtime_hours: 8, satisfaction_score: 2.5, num_projects: 4 }),
            API.post('/api/ml/predict/churn', { purchase_frequency: 2, last_purchase_days: 90, lifetime_value: 3000, support_tickets: 5, avg_order_value: 500, account_age_months: 12 }),
            API.post('/api/ml/predict/project-risk', { budget_usage_pct: 85, task_completion_pct: 40, days_remaining: 15, team_size: 5, scope_changes: 4, complexity_score: 7 }),
        ]);
        const v = r => r.status === 'fulfilled' ? r.value : null;
        const mini = (label, r) => {
            if (!r) return `<div class="prediction-detail-item"><div class="detail-value text-muted">N/A</div><div class="detail-label">${label}</div></div>`;
            const c = r.prediction.includes('High') || r.prediction.includes('Churn') ? 'var(--danger)' : r.prediction.includes('Medium') ? 'var(--warning)' : 'var(--success)';
            return `<div class="prediction-detail-item"><div class="detail-value" style="color:${c}">${r.prediction}</div><div class="detail-label">${label}</div>${r.confidence ? `<div style="font-size:0.7rem;color:var(--text-muted);margin-top:2px">${r.confidence}%</div>` : ''}</div>`;
        };
        el.innerHTML = `<div class="prediction-details" style="grid-template-columns:1fr 1fr 1fr">${mini('Attrition', v(attrition))}${mini('Churn', v(churn))}${mini('Risk', v(risk))}</div><p class="text-muted" style="font-size:0.7rem;text-align:center;margin-top:8px">Sample predictions from trained models</p>`;
    } catch {
        el.innerHTML = '<div class="empty-state"><p>ML models not trained yet. Train from command palette.</p></div>';
    }
}
