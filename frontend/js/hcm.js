document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    document.getElementById('sidebar').innerHTML = buildSidebar('hcm');
    loadEmployees();
    loadAttendance();
    loadPayroll();
    loadPerformance();
});

function switchTab(tab) {
    document.querySelectorAll('[id$="-tab"]').forEach(el => el.classList.add('hidden'));
    document.getElementById(tab + '-tab').classList.remove('hidden');
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
}

async function loadEmployees() {
    try {
        const data = await API.get('/api/employees');
        document.getElementById('emp-table-body').innerHTML = `
            <table class="data-table">
                <thead><tr><th>Code</th><th>Name</th><th>Department</th><th>Position</th><th>Salary</th><th>Hire Date</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>${data.map(e => `
                    <tr>
                        <td><strong>${e.employee_code}</strong></td>
                        <td>${e.first_name} ${e.last_name}</td>
                        <td>${e.department}</td>
                        <td>${e.position}</td>
                        <td>${formatCurrency(e.salary)}</td>
                        <td>${formatDate(e.hire_date)}</td>
                        <td>${statusBadge(e.is_active ? 'active' : 'absent')}</td>
                        <td>
                            <button class="btn btn-ghost btn-sm" onclick="deleteEmp(${e.id})">🗑️</button>
                        </td>
                    </tr>
                `).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load employees', 'error'); }
}

async function addEmployee(e) {
    e.preventDefault();
    try {
        await API.post('/api/employees', {
            employee_code: document.getElementById('emp-code').value,
            first_name: document.getElementById('emp-fname').value,
            last_name: document.getElementById('emp-lname').value,
            email: document.getElementById('emp-email').value,
            department: document.getElementById('emp-dept').value,
            position: document.getElementById('emp-pos').value,
            salary: parseFloat(document.getElementById('emp-salary').value),
            hire_date: document.getElementById('emp-hire').value,
        });
        closeModal('add-emp-modal');
        showToast('Employee added successfully', 'success');
        loadEmployees();
    } catch (err) { showToast(err.message, 'error'); }
}

async function deleteEmp(id) {
    if (!confirm('Delete this employee?')) return;
    try {
        await API.del('/api/employees/' + id);
        showToast('Employee deleted', 'success');
        loadEmployees();
    } catch (err) { showToast(err.message, 'error'); }
}

async function loadAttendance() {
    try {
        const data = await API.get('/api/attendance?limit=50');
        document.getElementById('att-table-body').innerHTML = `
            <table class="data-table">
                <thead><tr><th>Employee ID</th><th>Date</th><th>Check In</th><th>Check Out</th><th>Status</th></tr></thead>
                <tbody>${data.map(a => `
                    <tr>
                        <td>${a.employee_id}</td>
                        <td>${formatDate(a.date)}</td>
                        <td>${a.check_in || '—'}</td>
                        <td>${a.check_out || '—'}</td>
                        <td>${statusBadge(a.status)}</td>
                    </tr>
                `).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load attendance', 'error'); }
}

async function loadPayroll() {
    try {
        const data = await API.get('/api/payroll?limit=50');
        document.getElementById('pay-table-body').innerHTML = `
            <table class="data-table">
                <thead><tr><th>Employee ID</th><th>Period</th><th>Basic</th><th>Deductions</th><th>Bonuses</th><th>Net Salary</th><th>Status</th></tr></thead>
                <tbody>${data.map(p => `
                    <tr>
                        <td>${p.employee_id}</td>
                        <td>${p.month}/${p.year}</td>
                        <td>${formatCurrency(p.basic_salary)}</td>
                        <td class="text-danger">${formatCurrency(p.deductions)}</td>
                        <td class="text-success">${formatCurrency(p.bonuses)}</td>
                        <td><strong>${formatCurrency(p.net_salary)}</strong></td>
                        <td>${statusBadge(p.paid ? 'paid' : 'pending')}</td>
                    </tr>
                `).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load payroll', 'error'); }
}

async function loadPerformance() {
    try {
        const data = await API.get('/api/performance?limit=50');
        document.getElementById('perf-table-body').innerHTML = `
            <table class="data-table">
                <thead><tr><th>Employee ID</th><th>Period</th><th>Rating</th><th>Goals</th><th>Progress</th><th>Notes</th></tr></thead>
                <tbody>${data.map(p => {
                    const pct = p.goals_total > 0 ? Math.round(p.goals_met / p.goals_total * 100) : 0;
                    const color = pct >= 70 ? 'success' : pct >= 40 ? 'warning' : 'danger';
                    return `
                    <tr>
                        <td>${p.employee_id}</td>
                        <td>Q${p.quarter} ${p.year}</td>
                        <td><strong>${p.rating}</strong>/5</td>
                        <td>${p.goals_met}/${p.goals_total}</td>
                        <td style="min-width:120px;">
                            <div class="progress-bar"><div class="progress-fill ${color}" style="width:${pct}%"></div></div>
                            <span style="font-size:0.7rem;color:var(--text-muted);">${pct}%</span>
                        </td>
                        <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;">${p.review_notes || '—'}</td>
                    </tr>`;
                }).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load performance', 'error'); }
}

async function predictAttrition(e) {
    e.preventDefault();
    try {
        const result = await API.post('/api/ml/predict/attrition', {
            salary: parseFloat(document.getElementById('ml-salary').value),
            tenure_years: parseFloat(document.getElementById('ml-tenure').value),
            performance_rating: parseFloat(document.getElementById('ml-perf').value),
            department_encoded: 1,
            overtime_hours: parseFloat(document.getElementById('ml-overtime').value),
            satisfaction_score: parseFloat(document.getElementById('ml-satisfaction').value),
            num_projects: parseInt(document.getElementById('ml-projects').value),
        });
        const color = result.prediction === 'High Risk' ? 'var(--danger)' : 'var(--success)';
        document.getElementById('attrition-result').innerHTML = `
            <div class="prediction-result">
                <div class="prediction-value" style="background:none;-webkit-text-fill-color:${color};color:${color};">${result.prediction}</div>
                <div class="prediction-confidence">Confidence: ${result.confidence}%</div>
            </div>
            <div class="prediction-details">
                <div class="prediction-detail-item">
                    <div class="detail-value text-success">${result.details.stay_probability}%</div>
                    <div class="detail-label">Stay Probability</div>
                </div>
                <div class="prediction-detail-item">
                    <div class="detail-value text-danger">${result.details.leave_probability}%</div>
                    <div class="detail-label">Leave Probability</div>
                </div>
            </div>`;
    } catch (err) { showToast(err.message, 'error'); }
}

function exportReport(type) {
    window.open(`${API.BASE_URL}/api/reports/hcm/${type}`, '_blank');
}
