// Initialize Supabase Client
const supabaseClient = supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY);

const API = (() => {
    // For local dev, use the FastAPI port. For production/Vercel, use /api prefix
    const BASE_URL = CONFIG.API_BASE_URL;

    // Simple GET cache (30s TTL)
    const _cache = new Map();
    const CACHE_TTL = 30000;

    async function getToken() { 
        const { data, error } = await supabaseClient.auth.getSession();
        if (error || !data.session) return null;
        return data.session.access_token;
    }
    
    function setUser(user) { localStorage.setItem('erp_user', JSON.stringify(user)); }
    function getUser() { const u = localStorage.getItem('erp_user'); return u ? JSON.parse(u) : null; }
    function clearAuth() { supabaseClient.auth.signOut(); localStorage.removeItem('erp_user'); }
    async function isAuthenticated() { const t = await getToken(); return !!t; }

    async function request(method, path, body = null) {
        const headers = { 'Content-Type': 'application/json' };
        const token = await getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const config = { method, headers };
        if (body && method !== 'GET') config.body = JSON.stringify(body);

        // Check GET cache
        const cacheKey = method === 'GET' ? path : null;
        if (cacheKey && _cache.has(cacheKey)) {
            const cached = _cache.get(cacheKey);
            if (Date.now() < cached.expires) return cached.data;
            _cache.delete(cacheKey);
        }

        try {
            const res = await fetch(`${BASE_URL}${path}`, config);

            if (res.status === 401 || res.status === 403) {
                clearAuth();
                window.location.href = '/static/index.html';
                return null;
            }
            if (res.status === 204) return null;

            let data;
            const contentType = res.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                data = await res.json();
            } else {
                const text = await res.text();
                if (!res.ok) throw new Error(`Server Error (${res.status}): ${text.slice(0, 100)}...`);
                return text;
            }

            if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);

            // Cache GET responses
            if (cacheKey) {
                _cache.set(cacheKey, { data, expires: Date.now() + CACHE_TTL });
            }

            return data;
        } catch (err) {
            if (err.message === 'Failed to fetch') {
                showToast('Cannot connect to server', 'error');
            }
            throw err;
        }
    }

    function invalidateCache(prefix) {
        for (const key of _cache.keys()) {
            if (key.startsWith(prefix || '/')) _cache.delete(key);
        }
    }

    const get = (path) => request('GET', path);
    const post = (path, body) => { invalidateCache(); return request('POST', path, body); };
    const put = (path, body) => { invalidateCache(); return request('PUT', path, body); };
    const del = (path) => { invalidateCache(); return request('DELETE', path); };

    return { get, post, put, del, getToken, setToken, setUser, getUser, clearAuth, isAuthenticated, BASE_URL, invalidateCache };
})();


// ── Toast Notification System ────────────────────────────────────────────────
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = { success: '\u2713', error: '\u2715', warning: '!', info: 'i' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span class="toast-icon">${icons[type] || 'i'}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}


// ── Auth Guard ───────────────────────────────────────────────────────────────
async function requireAuth() {
    const authed = await API.isAuthenticated();
    if (!authed) {
        window.location.href = '/static/index.html';
        return false;
    }
    return true;
}


// ── Sidebar Builder ──────────────────────────────────────────────────────────
function buildSidebar(activePage) {
    const user = API.getUser();
    const initials = user ? user.username.slice(0, 2).toUpperCase() : 'U';

    return `
    <div class="sidebar">
        <div class="sidebar-brand">
            <div class="brand-icon">S</div>
            <div>
                <div class="brand-name">StartupERP</div>
                <div class="brand-tag">Business Suite</div>
            </div>
        </div>
        <nav class="sidebar-nav">
            <div class="nav-section">
                <div class="nav-section-title">Overview</div>
                <a href="/static/dashboard.html" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">
                    <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg></span>
                    <span class="nav-text">Dashboard</span>
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Modules</div>
                <a href="/static/hcm.html" class="nav-item ${activePage === 'hcm' ? 'active' : ''}">
                    <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></span>
                    <span class="nav-text">Employees</span>
                </a>
                <a href="/static/finance.html" class="nav-item ${activePage === 'finance' ? 'active' : ''}">
                    <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></span>
                    <span class="nav-text">Finance</span>
                </a>
                <a href="/static/procurement.html" class="nav-item ${activePage === 'procurement' ? 'active' : ''}">
                    <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg></span>
                    <span class="nav-text">Procurement</span>
                </a>
                <a href="/static/ppm.html" class="nav-item ${activePage === 'ppm' ? 'active' : ''}">
                    <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg></span>
                    <span class="nav-text">Projects</span>
                </a>
                <a href="/static/crm.html" class="nav-item ${activePage === 'crm' ? 'active' : ''}">
                    <span class="nav-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg></span>
                    <span class="nav-text">Customers</span>
                </a>
            </div>
        </nav>
        <div class="sidebar-footer">
            <div class="sidebar-shortcut" onclick="window.CommandPalette && CommandPalette.open()">
                <span>Search / Commands</span>
                <kbd>Ctrl K</kbd>
            </div>
            <div class="user-info">
                <div class="user-avatar">${initials}</div>
                <div class="user-details">
                    <div class="user-name">${user ? user.username : 'User'}</div>
                    <div class="user-role">${user ? user.role : ''}</div>
                </div>
                <button class="btn-icon-sm" onclick="logout()" title="Sign Out">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                </button>
            </div>
        </div>
    </div>`;
}

function logout() {
    API.clearAuth();
    window.location.href = '/static/index.html';
}


// ── Skeleton Loader ──────────────────────────────────────────────────────────
function showSkeleton(elementId, type = 'table', rows = 5) {
    const el = document.getElementById(elementId);
    if (!el) return;

    if (type === 'kpi') {
        el.innerHTML = Array(8).fill(0).map(() => `
            <div class="kpi-card skeleton-card">
                <div class="skeleton skeleton-sm" style="width:40px;height:40px;border-radius:8px;"></div>
                <div class="skeleton skeleton-lg" style="width:60%;margin-top:16px;"></div>
                <div class="skeleton skeleton-sm" style="width:40%;margin-top:8px;"></div>
            </div>`).join('');
    } else if (type === 'chart') {
        el.innerHTML = '<div class="skeleton" style="width:100%;height:280px;border-radius:8px;"></div>';
    } else if (type === 'insights') {
        el.innerHTML = Array(3).fill(0).map(() => `
            <div class="insight-card skeleton-card">
                <div class="skeleton skeleton-sm" style="width:30%;"></div>
                <div class="skeleton skeleton-md" style="width:90%;margin-top:8px;"></div>
            </div>`).join('');
    } else {
        el.innerHTML = `<table class="data-table"><thead><tr>${Array(5).fill('<th><div class="skeleton skeleton-sm"></div></th>').join('')}</tr></thead>
            <tbody>${Array(rows).fill(0).map(() => `<tr>${Array(5).fill('<td><div class="skeleton skeleton-sm"></div></td>').join('')}</tr>`).join('')}</tbody></table>`;
    }
}


// ── Empty State ──────────────────────────────────────────────────────────────
function showEmptyState(elementId, message = 'No data yet', action = '') {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/>
                </svg>
            </div>
            <h3>${message}</h3>
            ${action ? `<p class="text-muted" style="margin-top:4px;font-size:0.8rem;">${action}</p>` : ''}
        </div>`;
}


// ── Status Badge Helper ─────────────────────────────────────────────────────
function statusBadge(status) {
    const map = {
        active: 'badge-success', completed: 'badge-info', present: 'badge-success',
        absent: 'badge-danger', late: 'badge-warning', leave: 'badge-purple',
        pending: 'badge-warning', approved: 'badge-success', shipped: 'badge-info',
        delivered: 'badge-success', cancelled: 'badge-danger',
        planning: 'badge-muted', delayed: 'badge-danger', on_hold: 'badge-warning',
        todo: 'badge-muted', in_progress: 'badge-primary', review: 'badge-purple', done: 'badge-success',
        new: 'badge-info', contacted: 'badge-primary', qualified: 'badge-success',
        proposal: 'badge-purple', converted: 'badge-success', lost: 'badge-danger',
        paid: 'badge-success', overdue: 'badge-danger',
        'Low Risk': 'badge-success', 'Medium Risk': 'badge-warning', 'High Risk': 'badge-danger',
        'Will Retain': 'badge-success', 'Will Churn': 'badge-danger',
    };
    return `<span class="badge ${map[status] || 'badge-muted'}">${status}</span>`;
}


// ── Format Helpers ───────────────────────────────────────────────────────────
function formatCurrency(n) { return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n); }
function formatDate(d) { if (!d) return '\u2014'; return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }); }
function formatNumber(n) { return new Intl.NumberFormat('en-US').format(n); }


// ── ML Result Renderer ───────────────────────────────────────────────────────
function renderMLResult(containerId, result) {
    const el = document.getElementById(containerId);
    if (!el || !result) return;

    const predColor = result.prediction.includes('High') || result.prediction.includes('Churn')
        ? 'var(--danger)' : result.prediction.includes('Medium')
        ? 'var(--warning)' : 'var(--success)';

    let html = `
        <div class="ml-result">
            <div class="ml-prediction" style="color:${predColor}">${result.prediction}</div>`;

    if (result.confidence != null) {
        html += `
            <div class="ml-confidence">
                <div class="ml-confidence-bar">
                    <div class="ml-confidence-fill" style="width:${result.confidence}%;background:${predColor}"></div>
                </div>
                <span class="ml-confidence-label">${result.confidence}% confidence</span>
            </div>`;
    }

    if (result.factors && result.factors.length > 0) {
        html += `
            <div class="ml-factors">
                <div class="ml-factors-title">Key Contributing Factors</div>
                <ul class="ml-factors-list">
                    ${result.factors.map(f => `<li>${f}</li>`).join('')}
                </ul>
            </div>`;
    }

    if (result.details) {
        html += `<div class="prediction-details">`;
        for (const [key, val] of Object.entries(result.details)) {
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            const display = typeof val === 'number' && key.includes('pct') ? `${val}%`
                : typeof val === 'number' && (key.includes('revenue') || key.includes('value')) ? formatCurrency(val)
                : val;
            html += `<div class="prediction-detail-item"><div class="detail-value">${display}</div><div class="detail-label">${label}</div></div>`;
        }
        html += `</div>`;
    }

    html += `</div>`;
    el.innerHTML = html;
}


// ── Modal Helpers ────────────────────────────────────────────────────────────
function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
