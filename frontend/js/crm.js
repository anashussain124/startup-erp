document.addEventListener('DOMContentLoaded', async () => {
    if (!(await requireAuth())) return;
    document.getElementById('sidebar').innerHTML = buildSidebar('crm');
    loadCustomers(); loadLeads(); loadSales();
});

function switchTab(tab) {
    document.querySelectorAll('[id$="-tab"]').forEach(el => el.classList.add('hidden'));
    document.getElementById(tab + '-tab').classList.remove('hidden');
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
}

async function loadCustomers() {
    try {
        const data = await API.get('/api/customers');
        document.getElementById('cust-table').innerHTML = `
            <table class="data-table">
                <thead><tr><th>Name</th><th>Email</th><th>Company</th><th>Segment</th><th>LTV</th><th>Status</th></tr></thead>
                <tbody>${data.map(c => `<tr><td><strong>${c.name}</strong></td><td>${c.email}</td>
                    <td>${c.company || '—'}</td><td>${statusBadge(c.segment || 'new')}</td>
                    <td class="text-success">${formatCurrency(c.lifetime_value)}</td>
                    <td>${statusBadge(c.is_active ? 'active' : 'cancelled')}</td></tr>`).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load customers', 'error'); }
}

async function loadLeads() {
    try {
        const data = await API.get('/api/leads');
        document.getElementById('lead-table').innerHTML = `
            <table class="data-table">
                <thead><tr><th>Contact</th><th>Email</th><th>Source</th><th>Status</th><th>Est. Value</th></tr></thead>
                <tbody>${data.map(l => `<tr><td><strong>${l.contact_name}</strong></td><td>${l.contact_email || '—'}</td>
                    <td>${l.source || '—'}</td><td>${statusBadge(l.status)}</td>
                    <td>${formatCurrency(l.estimated_value)}</td></tr>`).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load leads', 'error'); }
}

async function loadSales() {
    try {
        const data = await API.get('/api/sales');
        document.getElementById('sales-table').innerHTML = `
            <table class="data-table">
                <thead><tr><th>Customer</th><th>Amount</th><th>Product</th><th>Date</th><th>Payment</th></tr></thead>
                <tbody>${data.map(s => `<tr><td>${s.customer_id}</td>
                    <td class="text-success"><strong>${formatCurrency(s.amount)}</strong></td>
                    <td>${s.product_description || '—'}</td><td>${formatDate(s.date)}</td>
                    <td>${statusBadge(s.payment_status)}</td></tr>`).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load sales', 'error'); }
}

async function predictChurn(e) {
    e.preventDefault();
    try {
        const result = await API.post('/api/ml/predict/churn', {
            purchase_frequency: parseInt(document.getElementById('ml-freq').value),
            last_purchase_days: parseFloat(document.getElementById('ml-last').value),
            lifetime_value: parseFloat(document.getElementById('ml-ltv').value),
            support_tickets: parseInt(document.getElementById('ml-tickets').value),
            avg_order_value: parseFloat(document.getElementById('ml-aov').value),
            account_age_months: parseFloat(document.getElementById('ml-age').value),
        });
        const color = result.prediction === 'Will Churn' ? 'var(--danger)' : 'var(--success)';
        document.getElementById('churn-result').innerHTML = `
            <div class="prediction-result">
                <div class="prediction-value" style="background:none;-webkit-text-fill-color:${color};color:${color};">${result.prediction}</div>
                <div class="prediction-confidence">Confidence: ${result.confidence}%</div>
            </div>
            <div class="prediction-details">
                <div class="prediction-detail-item"><div class="detail-value text-success">${result.details.retain_probability}%</div><div class="detail-label">Retain</div></div>
                <div class="prediction-detail-item"><div class="detail-value text-danger">${result.details.churn_probability}%</div><div class="detail-label">Churn</div></div>
            </div>`;
    } catch (err) { showToast(err.message, 'error'); }
}

function exportReport(type) { window.open(`${API.BASE_URL}/api/reports/crm/${type}`, '_blank'); }
