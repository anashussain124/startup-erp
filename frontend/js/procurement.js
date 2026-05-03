document.addEventListener('DOMContentLoaded', async () => {
    if (!(await requireAuth())) return;
    document.getElementById('sidebar').innerHTML = buildSidebar('procurement');
    loadVendors(); loadPOs(); loadInventory();
});

function switchTab(tab) {
    document.querySelectorAll('[id$="-tab"]').forEach(el => el.classList.add('hidden'));
    document.getElementById(tab + '-tab').classList.remove('hidden');
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
}

async function loadVendors() {
    try {
        const data = await API.get('/api/vendors');
        document.getElementById('vendors-table').innerHTML = `
            <table class="data-table">
                <thead><tr><th>Name</th><th>Contact</th><th>Email</th><th>Rating</th><th>Status</th></tr></thead>
                <tbody>${data.map(v => `<tr><td><strong>${v.name}</strong></td><td>${v.contact_person || '—'}</td><td>${v.email || '—'}</td>
                    <td>⭐ ${v.rating}/5</td><td>${statusBadge(v.is_active ? 'active' : 'cancelled')}</td></tr>`).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load vendors', 'error'); }
}

async function loadPOs() {
    try {
        const data = await API.get('/api/purchase-orders');
        document.getElementById('po-table').innerHTML = `
            <table class="data-table">
                <thead><tr><th>PO#</th><th>Vendor</th><th>Amount</th><th>Status</th><th>Order Date</th><th>Expected</th></tr></thead>
                <tbody>${data.map(p => `<tr><td><strong>${p.po_number}</strong></td><td>${p.vendor_id}</td>
                    <td>${formatCurrency(p.total_amount)}</td><td>${statusBadge(p.status)}</td>
                    <td>${formatDate(p.order_date)}</td><td>${formatDate(p.expected_delivery)}</td></tr>`).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load POs', 'error'); }
}

async function loadInventory() {
    try {
        const data = await API.get('/api/inventory');
        document.getElementById('inv-table').innerHTML = `
            <table class="data-table">
                <thead><tr><th>Name</th><th>SKU</th><th>Qty</th><th>Unit Price</th><th>Reorder Level</th><th>Status</th></tr></thead>
                <tbody>${data.map(i => {
                    const lowStock = i.quantity <= i.reorder_level;
                    return `<tr><td><strong>${i.name}</strong></td><td>${i.sku}</td>
                        <td style="color:${lowStock ? 'var(--danger)' : 'var(--text-primary)'}">${i.quantity}</td>
                        <td>${formatCurrency(i.unit_price)}</td><td>${i.reorder_level}</td>
                        <td>${lowStock ? statusBadge('delayed') : statusBadge('active')}</td></tr>`;
                }).join('')}</tbody>
            </table>`;
    } catch (err) { showToast('Failed to load inventory', 'error'); }
}

function exportReport(type) { window.open(`${API.BASE_URL}/api/reports/procurement/${type}`, '_blank'); }
