/**
 * Dashboard JS — loads KPIs, charts, and ML summaries.
 */
document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    document.getElementById('sidebar').innerHTML = buildSidebar('dashboard');
    loadDashboard();
});

const chartColors = {
    blue: 'rgba(59, 130, 246, 0.85)',
    purple: 'rgba(139, 92, 246, 0.85)',
    green: 'rgba(16, 185, 129, 0.85)',
    amber: 'rgba(245, 158, 11, 0.85)',
    red: 'rgba(239, 68, 68, 0.85)',
    cyan: 'rgba(6, 182, 212, 0.85)',
    pink: 'rgba(236, 72, 153, 0.85)',
};

const chartColorsBg = {
    blue: 'rgba(59, 130, 246, 0.15)',
    purple: 'rgba(139, 92, 246, 0.15)',
    green: 'rgba(16, 185, 129, 0.15)',
    amber: 'rgba(245, 158, 11, 0.15)',
    red: 'rgba(239, 68, 68, 0.15)',
    cyan: 'rgba(6, 182, 212, 0.15)',
    pink: 'rgba(236, 72, 153, 0.15)',
};

// Chart.js global defaults
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(148, 163, 184, 0.08)';
Chart.defaults.font.family = 'Inter, sans-serif';

let charts = {};

async function loadDashboard() {
    await Promise.all([
        loadKPIs(),
        loadRevExpChart(),
        loadExpCatChart(),
        loadProjectChart(),
        loadLeadChart(),
        loadDeptChart(),
        loadMLSummary(),
    ]);
}

// ── KPIs ──────────────────────────────────────────────────────────────────
async function loadKPIs() {
    try {
        const kpis = await API.get('/api/dashboard/kpis');
        document.getElementById('kpi-grid').innerHTML = `
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-icon blue">👥</div>
                </div>
                <div class="kpi-value">${kpis.hcm.total_employees}</div>
                <div class="kpi-label">Total Employees</div>
            </div>
            <div class="kpi-card success">
                <div class="kpi-header">
                    <div class="kpi-icon green">💰</div>
                </div>
                <div class="kpi-value">${formatCurrency(kpis.finance.total_revenue)}</div>
                <div class="kpi-label">Revenue (YTD)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-icon red">📊</div>
                </div>
                <div class="kpi-value">${formatCurrency(kpis.finance.profit)}</div>
                <div class="kpi-label">Net Profit (YTD)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-icon purple">🎯</div>
                </div>
                <div class="kpi-value">${kpis.ppm.active_projects}</div>
                <div class="kpi-label">Active Projects</div>
            </div>
            <div class="kpi-card warning">
                <div class="kpi-header">
                    <div class="kpi-icon amber">⚠️</div>
                </div>
                <div class="kpi-value">${kpis.procurement.pending_purchase_orders}</div>
                <div class="kpi-label">Pending POs</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-icon cyan">🤝</div>
                </div>
                <div class="kpi-value">${kpis.crm.conversion_rate}%</div>
                <div class="kpi-label">Lead Conversion</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-icon green">⭐</div>
                </div>
                <div class="kpi-value">${kpis.hcm.avg_performance}</div>
                <div class="kpi-label">Avg Performance</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-icon red">📉</div>
                </div>
                <div class="kpi-value">${kpis.ppm.delayed_projects}</div>
                <div class="kpi-label">Delayed Projects</div>
            </div>
        `;
    } catch (err) {
        document.getElementById('kpi-grid').innerHTML = '<p class="text-danger">Failed to load KPIs</p>';
    }
}

// ── Revenue vs Expenses ──────────────────────────────────────────────────
async function loadRevExpChart() {
    try {
        const [rev, exp] = await Promise.all([
            API.get('/api/dashboard/charts/revenue-trend'),
            API.get('/api/dashboard/charts/expense-trend'),
        ]);
        if (charts.revExp) charts.revExp.destroy();
        charts.revExp = new Chart(document.getElementById('revExpChart'), {
            type: 'line',
            data: {
                labels: rev.labels,
                datasets: [
                    {
                        label: 'Revenue',
                        data: rev.data,
                        borderColor: chartColors.green,
                        backgroundColor: chartColorsBg.green,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                    },
                    {
                        label: 'Expenses',
                        data: exp.data,
                        borderColor: chartColors.red,
                        backgroundColor: chartColorsBg.red,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } },
                scales: {
                    y: { ticks: { callback: v => '$' + (v / 1000).toFixed(0) + 'k' } },
                },
            },
        });
    } catch (err) { console.error('RevExp chart error:', err); }
}

// ── Expenses by Category ─────────────────────────────────────────────────
async function loadExpCatChart() {
    try {
        const data = await API.get('/api/dashboard/charts/expenses-by-category');
        if (charts.expCat) charts.expCat.destroy();
        const colors = [chartColors.blue, chartColors.purple, chartColors.green,
                        chartColors.amber, chartColors.red, chartColors.cyan];
        charts.expCat = new Chart(document.getElementById('expCatChart'), {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: colors.slice(0, data.labels.length),
                    borderWidth: 0,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'right' } },
                cutout: '65%',
            },
        });
    } catch (err) { console.error('ExpCat chart error:', err); }
}

// ── Project Status ───────────────────────────────────────────────────────
async function loadProjectChart() {
    try {
        const data = await API.get('/api/dashboard/charts/project-status');
        if (charts.proj) charts.proj.destroy();
        const bgColors = [chartColorsBg.blue, chartColorsBg.green, chartColorsBg.cyan,
                          chartColorsBg.red, chartColorsBg.amber];
        const bdColors = [chartColors.blue, chartColors.green, chartColors.cyan,
                          chartColors.red, chartColors.amber];
        charts.proj = new Chart(document.getElementById('projChart'), {
            type: 'bar',
            data: {
                labels: data.labels.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
                datasets: [{
                    label: 'Projects',
                    data: data.data,
                    backgroundColor: bgColors,
                    borderColor: bdColors,
                    borderWidth: 1,
                    borderRadius: 6,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
            },
        });
    } catch (err) { console.error('Project chart error:', err); }
}

// ── Lead Pipeline ────────────────────────────────────────────────────────
async function loadLeadChart() {
    try {
        const data = await API.get('/api/dashboard/charts/lead-pipeline');
        if (charts.lead) charts.lead.destroy();
        charts.lead = new Chart(document.getElementById('leadChart'), {
            type: 'bar',
            data: {
                labels: data.labels.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
                datasets: [{
                    label: 'Leads',
                    data: data.data,
                    backgroundColor: [
                        chartColors.cyan, chartColors.blue, chartColors.green,
                        chartColors.purple, chartColors.green, chartColors.red,
                    ],
                    borderRadius: 6,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                indexAxis: 'y',
                scales: { x: { beginAtZero: true, ticks: { stepSize: 1 } } },
            },
        });
    } catch (err) { console.error('Lead chart error:', err); }
}

// ── Department Headcount ─────────────────────────────────────────────────
async function loadDeptChart() {
    try {
        const data = await API.get('/api/dashboard/charts/department-headcount');
        if (charts.dept) charts.dept.destroy();
        charts.dept = new Chart(document.getElementById('deptChart'), {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Employees',
                    data: data.data,
                    backgroundColor: chartColors.blue,
                    borderRadius: 6,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
            },
        });
    } catch (err) { console.error('Dept chart error:', err); }
}

// ── ML Summary ───────────────────────────────────────────────────────────
async function loadMLSummary() {
    const el = document.getElementById('ml-summary');
    try {
        // Sample predictions
        const [attrition, churn, risk] = await Promise.allSettled([
            API.post('/api/ml/predict/attrition', {
                salary: 55000, tenure_years: 2, performance_rating: 3.0,
                department_encoded: 1, overtime_hours: 8, satisfaction_score: 2.5, num_projects: 4,
            }),
            API.post('/api/ml/predict/churn', {
                purchase_frequency: 2, last_purchase_days: 90, lifetime_value: 3000,
                support_tickets: 5, avg_order_value: 500, account_age_months: 12,
            }),
            API.post('/api/ml/predict/project-risk', {
                budget_usage_pct: 85, task_completion_pct: 40, days_remaining: 15,
                team_size: 5, scope_changes: 4, complexity_score: 7,
            }),
        ]);

        const getVal = (r) => r.status === 'fulfilled' ? r.value : null;
        const a = getVal(attrition);
        const c = getVal(churn);
        const r = getVal(risk);

        el.innerHTML = `
            <div class="prediction-details" style="grid-template-columns:1fr 1fr 1fr;">
                <div class="prediction-detail-item">
                    <div class="detail-value" style="color:${a && a.prediction === 'High Risk' ? 'var(--danger)' : 'var(--success)'}">
                        ${a ? a.prediction : 'N/A'}
                    </div>
                    <div class="detail-label">Attrition Sample</div>
                    <div style="font-size:0.7rem;color:var(--text-muted);margin-top:2px;">${a ? a.confidence + '%' : ''} confidence</div>
                </div>
                <div class="prediction-detail-item">
                    <div class="detail-value" style="color:${c && c.prediction === 'Will Churn' ? 'var(--danger)' : 'var(--success)'}">
                        ${c ? c.prediction : 'N/A'}
                    </div>
                    <div class="detail-label">Churn Sample</div>
                    <div style="font-size:0.7rem;color:var(--text-muted);margin-top:2px;">${c ? c.confidence + '%' : ''} confidence</div>
                </div>
                <div class="prediction-detail-item">
                    <div class="detail-value" style="color:${r && r.prediction === 'High Risk' ? 'var(--danger)' : r && r.prediction === 'Medium Risk' ? 'var(--warning)' : 'var(--success)'}">
                        ${r ? r.prediction : 'N/A'}
                    </div>
                    <div class="detail-label">Project Risk Sample</div>
                    <div style="font-size:0.7rem;color:var(--text-muted);margin-top:2px;">${r ? r.confidence + '%' : ''} confidence</div>
                </div>
            </div>
            <p class="text-muted mt-2" style="font-size:0.75rem;text-align:center;">
                Sample predictions using trained models · Visit module pages for interactive predictions
            </p>
        `;
    } catch (err) {
        el.innerHTML = '<p class="text-muted text-center">ML models not trained yet. Run training to enable predictions.</p>';
    }
}
