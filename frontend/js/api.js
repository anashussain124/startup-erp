/**
 * API Client — centralized HTTP wrapper with JWT injection.
 * All frontend modules use this for backend communication.
 */
const API = (() => {
    const BASE_URL = window.location.origin;

    function getToken() {
        return localStorage.getItem('erp_token');
    }

    function setToken(token) {
        localStorage.setItem('erp_token', token);
    }

    function setUser(user) {
        localStorage.setItem('erp_user', JSON.stringify(user));
    }

    function getUser() {
        const u = localStorage.getItem('erp_user');
        return u ? JSON.parse(u) : null;
    }

    function clearAuth() {
        localStorage.removeItem('erp_token');
        localStorage.removeItem('erp_user');
    }

    function isAuthenticated() {
        return !!getToken();
    }

    async function request(method, path, body = null) {
        const headers = { 'Content-Type': 'application/json' };
        const token = getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = { method, headers };
        if (body && method !== 'GET') {
            config.body = JSON.stringify(body);
        }

        try {
            const res = await fetch(`${BASE_URL}${path}`, config);

            if (res.status === 401) {
                clearAuth();
                window.location.href = '/static/index.html';
                return null;
            }

            if (res.status === 204) return null;

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || `HTTP ${res.status}`);
            }

            return data;
        } catch (err) {
            if (err.message === 'Failed to fetch') {
                showToast('Cannot connect to server', 'error');
            }
            throw err;
        }
    }

    const get = (path) => request('GET', path);
    const post = (path, body) => request('POST', path, body);
    const put = (path, body) => request('PUT', path, body);
    const del = (path) => request('DELETE', path);

    return { get, post, put, del, getToken, setToken, setUser, getUser, clearAuth, isAuthenticated, BASE_URL };
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

    const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span> ${message}`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}


// ── Auth Guard ───────────────────────────────────────────────────────────────
function requireAuth() {
    if (!API.isAuthenticated()) {
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
            <div class="brand-icon">⚡</div>
            <div>
                <div class="brand-name">StartupERP</div>
                <div class="brand-tag">Intelligence Platform</div>
            </div>
        </div>
        <nav class="sidebar-nav">
            <div class="nav-section">
                <div class="nav-section-title">Overview</div>
                <a href="/static/dashboard.html" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">
                    <span class="nav-icon">📊</span>
                    <span class="nav-text">Dashboard</span>
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Modules</div>
                <a href="/static/hcm.html" class="nav-item ${activePage === 'hcm' ? 'active' : ''}">
                    <span class="nav-icon">👥</span>
                    <span class="nav-text">HCM</span>
                </a>
                <a href="/static/finance.html" class="nav-item ${activePage === 'finance' ? 'active' : ''}">
                    <span class="nav-icon">💰</span>
                    <span class="nav-text">Finance</span>
                </a>
                <a href="/static/procurement.html" class="nav-item ${activePage === 'procurement' ? 'active' : ''}">
                    <span class="nav-icon">📦</span>
                    <span class="nav-text">Procurement</span>
                </a>
                <a href="/static/ppm.html" class="nav-item ${activePage === 'ppm' ? 'active' : ''}">
                    <span class="nav-icon">🎯</span>
                    <span class="nav-text">Projects</span>
                </a>
                <a href="/static/crm.html" class="nav-item ${activePage === 'crm' ? 'active' : ''}">
                    <span class="nav-icon">🤝</span>
                    <span class="nav-text">CRM</span>
                </a>
            </div>
        </nav>
        <div class="sidebar-footer">
            <div class="user-info">
                <div class="user-avatar">${initials}</div>
                <div class="user-details">
                    <div class="user-name">${user ? user.username : 'User'}</div>
                    <div class="user-role">${user ? user.role : ''}</div>
                </div>
            </div>
            <button class="btn btn-ghost btn-sm" onclick="logout()" style="width:100%;margin-top:8px;">
                🚪 <span class="nav-text">Sign Out</span>
            </button>
        </div>
    </div>`;
}

function logout() {
    API.clearAuth();
    window.location.href = '/static/index.html';
}


// ── Status Badge Helper ─────────────────────────────────────────────────────
function statusBadge(status) {
    const map = {
        // Common
        active: 'badge-success', completed: 'badge-info', present: 'badge-success',
        // HCM
        absent: 'badge-danger', late: 'badge-warning', leave: 'badge-purple',
        // Procurement
        pending: 'badge-warning', approved: 'badge-success', shipped: 'badge-info',
        delivered: 'badge-success', cancelled: 'badge-danger',
        // PPM
        planning: 'badge-muted', delayed: 'badge-danger', on_hold: 'badge-warning',
        todo: 'badge-muted', in_progress: 'badge-primary', review: 'badge-purple', done: 'badge-success',
        // CRM
        new: 'badge-info', contacted: 'badge-primary', qualified: 'badge-success',
        proposal: 'badge-purple', converted: 'badge-success', lost: 'badge-danger',
        // Finance
        paid: 'badge-success', overdue: 'badge-danger',
        // Risk
        'Low Risk': 'badge-success', 'Medium Risk': 'badge-warning', 'High Risk': 'badge-danger',
        'Will Retain': 'badge-success', 'Will Churn': 'badge-danger',
    };
    return `<span class="badge ${map[status] || 'badge-muted'}">${status}</span>`;
}


// ── Format Helpers ───────────────────────────────────────────────────────────
function formatCurrency(n) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);
}

function formatDate(d) {
    if (!d) return '—';
    return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatNumber(n) {
    return new Intl.NumberFormat('en-US').format(n);
}


// ── Modal Helpers ────────────────────────────────────────────────────────────
function openModal(id) {
    document.getElementById(id).classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}
