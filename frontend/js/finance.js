document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    document.getElementById('sidebar').innerHTML = buildSidebar('finance');
    loadRevenue();
    loadExpenses();
});

function switchTab(tab) {
    document.querySelectorAll('[id$="-tab"]').forEach(el => el.classList.add('hidden'));
    document.getElementById(tab + '-tab').classList.remove('hidden');
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
}

async function loadRevenue() {
    try {
        const data = await API.get('/api/revenue?limit=50');
        document.getElementById('rev-table').innerHTML = `
            <table class="data-table">
                <thead><tr><th>ID</th><th>Source</th><th>Amount</th><th>Date</th><th>Description</th></tr></thead>
                <tbody>${data.map(r => `<tr><td>${r.id}</td><td>${statusBadge(r.source)}</td><td class="text-success"><strong>${formatCurrency(r.amount)}</strong></td><td>${formatDate(r.date)}</td><td>${r.description || '—'}</td></tr>`).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load revenue', 'error'); }
}

async function loadExpenses() {
    try {
        const data = await API.get('/api/expenses?limit=50');
        document.getElementById('exp-table').innerHTML = `
            <table class="data-table">
                <thead><tr><th>ID</th><th>Category</th><th>Amount</th><th>Date</th><th>Description</th><th>Approved By</th></tr></thead>
                <tbody>${data.map(e => `<tr><td>${e.id}</td><td>${statusBadge(e.category)}</td><td class="text-danger"><strong>${formatCurrency(e.amount)}</strong></td><td>${formatDate(e.date)}</td><td>${e.description || '—'}</td><td>${e.approved_by || '—'}</td></tr>`).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load expenses', 'error'); }
}

async function addRevenue(e) {
    e.preventDefault();
    try {
        await API.post('/api/revenue', {
            source: document.getElementById('rev-source').value,
            amount: parseFloat(document.getElementById('rev-amount').value),
            date: document.getElementById('rev-date').value,
            description: document.getElementById('rev-desc').value,
        });
        closeModal('add-rev-modal');
        showToast('Revenue added', 'success');
        loadRevenue();
    } catch (err) { showToast(err.message, 'error'); }
}

async function addExpense(e) {
    e.preventDefault();
    try {
        await API.post('/api/expenses', {
            category: document.getElementById('exp-cat').value,
            amount: parseFloat(document.getElementById('exp-amount').value),
            date: document.getElementById('exp-date').value,
            description: document.getElementById('exp-desc').value,
        });
        closeModal('add-exp-modal');
        showToast('Expense added', 'success');
        loadExpenses();
    } catch (err) { showToast(err.message, 'error'); }
}

async function predictRevenue(e) {
    e.preventDefault();
    try {
        const result = await API.post('/api/ml/predict/revenue', {
            month: parseInt(document.getElementById('ml-month').value),
            prev_revenue: parseFloat(document.getElementById('ml-prev-rev').value),
            total_expenses: parseFloat(document.getElementById('ml-exp').value),
            headcount: parseInt(document.getElementById('ml-head').value),
            marketing_spend: parseFloat(document.getElementById('ml-mkt').value),
        });
        const growth = result.details.growth_pct;
        document.getElementById('revenue-result').innerHTML = `
            <div class="prediction-result">
                <div class="prediction-value">${result.prediction}</div>
                <div class="prediction-confidence">Forecasted Revenue</div>
            </div>
            <div class="prediction-details">
                <div class="prediction-detail-item">
                    <div class="detail-value">${formatCurrency(result.details.input_prev_revenue)}</div>
                    <div class="detail-label">Previous Revenue</div>
                </div>
                <div class="prediction-detail-item">
                    <div class="detail-value" style="color:${growth >= 0 ? 'var(--success)' : 'var(--danger)'}">
                        ${growth >= 0 ? '+' : ''}${growth}%
                    </div>
                    <div class="detail-label">Growth</div>
                </div>
            </div>`;
    } catch (err) { showToast(err.message, 'error'); }
}

function exportReport(type) { window.open(`${API.BASE_URL}/api/reports/finance/${type}`, '_blank'); }
