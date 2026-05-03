document.addEventListener('DOMContentLoaded', async () => {
    if (!(await requireAuth())) return;
    document.getElementById('sidebar').innerHTML = buildSidebar('ppm');
    loadProjects(); loadTasks();
});

function switchTab(tab) {
    document.querySelectorAll('[id$="-tab"]').forEach(el => el.classList.add('hidden'));
    document.getElementById(tab + '-tab').classList.remove('hidden');
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
}

async function loadProjects() {
    try {
        const data = await API.get('/api/projects');
        document.getElementById('proj-table').innerHTML = `
            <table class="data-table">
                <thead><tr><th>Project</th><th>Status</th><th>Priority</th><th>Budget</th><th>Spent</th><th>Progress</th><th>Timeline</th></tr></thead>
                <tbody>${data.map(p => {
                    const pct = p.budget > 0 ? Math.round(p.spent / p.budget * 100) : 0;
                    const color = pct > 100 ? 'danger' : pct > 75 ? 'warning' : 'success';
                    return `<tr>
                        <td><strong>${p.name}</strong><br><span style="font-size:0.75rem;color:var(--text-muted);">${p.manager || ''}</span></td>
                        <td>${statusBadge(p.status)}</td>
                        <td>${statusBadge(p.priority)}</td>
                        <td>${formatCurrency(p.budget)}</td>
                        <td>${formatCurrency(p.spent)}</td>
                        <td style="min-width:120px;">
                            <div class="progress-bar"><div class="progress-fill ${color}" style="width:${Math.min(pct, 100)}%"></div></div>
                            <span style="font-size:0.7rem;color:var(--text-muted);">${pct}% budget used</span>
                        </td>
                        <td style="font-size:0.8rem;">${formatDate(p.start_date)} → ${formatDate(p.end_date)}</td>
                    </tr>`;
                }).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load projects', 'error'); }
}

async function loadTasks() {
    try {
        const data = await API.get('/api/tasks?limit=50');
        document.getElementById('task-table').innerHTML = `
            <table class="data-table">
                <thead><tr><th>Task</th><th>Project</th><th>Assignee</th><th>Status</th><th>Priority</th><th>Due Date</th></tr></thead>
                <tbody>${data.map(t => `<tr>
                    <td><strong>${t.title}</strong></td><td>${t.project_id}</td>
                    <td>${t.assignee || '—'}</td><td>${statusBadge(t.status)}</td>
                    <td>${statusBadge(t.priority)}</td><td>${formatDate(t.due_date)}</td>
                </tr>`).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load tasks', 'error'); }
}

async function predictRisk(e) {
    e.preventDefault();
    try {
        const result = await API.post('/api/ml/predict/project-risk', {
            budget_usage_pct: parseFloat(document.getElementById('ml-budget').value),
            task_completion_pct: parseFloat(document.getElementById('ml-tasks').value),
            days_remaining: parseInt(document.getElementById('ml-days').value),
            team_size: parseInt(document.getElementById('ml-team').value),
            scope_changes: parseInt(document.getElementById('ml-scope').value),
            complexity_score: parseFloat(document.getElementById('ml-complex').value),
        });
        const colors = { 'Low Risk': 'var(--success)', 'Medium Risk': 'var(--warning)', 'High Risk': 'var(--danger)' };
        document.getElementById('risk-result').innerHTML = `
            <div class="prediction-result">
                <div class="prediction-value" style="background:none;-webkit-text-fill-color:${colors[result.prediction]};color:${colors[result.prediction]};">${result.prediction}</div>
                <div class="prediction-confidence">Confidence: ${result.confidence}%</div>
            </div>
            <div class="prediction-details" style="grid-template-columns:1fr 1fr 1fr;">
                <div class="prediction-detail-item"><div class="detail-value text-success">${result.details.low_risk_pct}%</div><div class="detail-label">Low Risk</div></div>
                <div class="prediction-detail-item"><div class="detail-value text-warning">${result.details.medium_risk_pct}%</div><div class="detail-label">Medium Risk</div></div>
                <div class="prediction-detail-item"><div class="detail-value text-danger">${result.details.high_risk_pct}%</div><div class="detail-label">High Risk</div></div>
            </div>`;
    } catch (err) { showToast(err.message, 'error'); }
}

function exportReport(type) { window.open(`${API.BASE_URL}/api/reports/ppm/${type}`, '_blank'); }
