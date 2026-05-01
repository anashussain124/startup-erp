/**
 * Command Palette 2.0 — Smart UX with preview, fuzzy matching,
 * did-you-mean suggestions, and inline result display.
 */
const CommandPalette = (() => {
    let _overlay = null;
    let _input = null;
    let _results = null;
    let _preview = null;
    let _selectedIdx = 0;

    const commands = [
        { type: 'nav', label: 'Go to Dashboard', keywords: 'dashboard home overview', desc: 'Navigate to the main dashboard', action: () => navigate('/static/dashboard.html') },
        { type: 'nav', label: 'Go to Employees', keywords: 'hcm employees people hr team', desc: 'Manage your team and track performance', action: () => navigate('/static/hcm.html') },
        { type: 'nav', label: 'Go to Finance', keywords: 'finance money revenue expenses', desc: 'Track revenue and expenses', action: () => navigate('/static/finance.html') },
        { type: 'nav', label: 'Go to Procurement', keywords: 'procurement inventory vendors purchase', desc: 'Manage vendors, POs, inventory', action: () => navigate('/static/procurement.html') },
        { type: 'nav', label: 'Go to Projects', keywords: 'projects ppm tasks', desc: 'Track projects and tasks', action: () => navigate('/static/ppm.html') },
        { type: 'nav', label: 'Go to Customers', keywords: 'crm customers leads sales', desc: 'Manage customers, leads, and sales', action: () => navigate('/static/crm.html') },
        { type: 'nav', label: 'API Documentation', keywords: 'api docs swagger', desc: 'Open Swagger API docs', action: () => window.open(API.BASE_URL + '/docs', '_blank') },
        { type: 'action', label: 'Refresh Dashboard', keywords: 'refresh reload update', desc: 'Reload all dashboard data', action: () => { navigate('/static/dashboard.html'); } },
        { type: 'action', label: 'Train ML Models', keywords: 'train ml machine learning retrain', desc: 'Retrain all prediction models (admin)', action: trainModels },
        { type: 'action', label: 'Sign Out', keywords: 'logout sign out exit', desc: 'End your session', action: () => { API.clearAuth(); navigate('/static/index.html'); } },
        { type: 'query', label: 'Show Revenue Summary', keywords: 'revenue income money total how much', desc: 'Display current revenue and profit', action: queryRevenue },
        { type: 'query', label: 'Show Employee Count', keywords: 'employees how many people headcount staff', desc: 'Show total active employees', action: queryEmployees },
        { type: 'query', label: 'Show Inventory Status', keywords: 'inventory stock items low reorder', desc: 'Check for low stock alerts', action: queryInventory },
        { type: 'query', label: 'Show Pending Orders', keywords: 'purchase orders pending po', desc: 'Check pending purchase orders', action: queryPendingPOs },
        { type: 'query', label: 'Show Active Projects', keywords: 'projects active status delayed', desc: 'View project overview', action: queryProjects },
        { type: 'query', label: 'Show AI Insights', keywords: 'insights ai intelligence alerts health', desc: 'Navigate to dashboard insights', action: () => navigate('/static/dashboard.html') },
        { type: 'query', label: 'Business Health Score', keywords: 'health score gauge status overall', desc: 'Show overall business health', action: queryHealth },
    ];

    const typeIcons = {
        nav: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>',
        action: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
        query: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    };

    function init() {
        _overlay = document.createElement('div');
        _overlay.className = 'cmd-overlay';
        _overlay.innerHTML = `
            <div class="cmd-modal">
                <div class="cmd-input-wrap">
                    <svg class="cmd-search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                    <input class="cmd-input" type="text" placeholder="Type a command or search..." autocomplete="off" spellcheck="false" />
                    <kbd class="cmd-esc">ESC</kbd>
                </div>
                <div class="cmd-results"></div>
                <div class="cmd-preview"></div>
                <div class="cmd-footer">
                    <span><kbd>&uarr;</kbd><kbd>&darr;</kbd> navigate</span>
                    <span><kbd>Enter</kbd> select</span>
                    <span><kbd>Esc</kbd> close</span>
                </div>
            </div>`;
        document.body.appendChild(_overlay);

        _input = _overlay.querySelector('.cmd-input');
        _results = _overlay.querySelector('.cmd-results');
        _preview = _overlay.querySelector('.cmd-preview');

        _input.addEventListener('input', () => { _selectedIdx = 0; render(_input.value); });
        _input.addEventListener('keydown', handleKeydown);
        _overlay.addEventListener('click', (e) => { if (e.target === _overlay) close(); });

        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); open(); }
            if (e.key === 'Escape' && _overlay.classList.contains('active')) close();
        });
    }

    function open() {
        _overlay.classList.add('active');
        _input.value = '';
        _selectedIdx = 0;
        _preview.innerHTML = '';
        render('');
        setTimeout(() => _input.focus(), 50);
    }

    function close() {
        _overlay.classList.remove('active');
        _input.value = '';
        _results.innerHTML = '';
        _preview.innerHTML = '';
    }

    function navigate(url) { close(); window.location.href = url; }

    // ── Scoring-based fuzzy match ────────────────────────────────────────
    function scoreMatch(query, cmd) {
        if (!query) return 1;
        const q = query.toLowerCase();
        const searchText = (cmd.label + ' ' + cmd.keywords + ' ' + cmd.desc).toLowerCase();

        // Exact substring = highest score
        if (searchText.includes(q)) return 10;

        // All words match
        const words = q.split(/\s+/);
        const allMatch = words.every(w => searchText.includes(w));
        if (allMatch) return 8;

        // Most words match (fuzzy)
        const matchCount = words.filter(w => searchText.includes(w)).length;
        if (matchCount > 0) return matchCount / words.length * 6;

        // Character-level fuzzy (typo tolerance)
        let qi = 0;
        for (let i = 0; i < searchText.length && qi < q.length; i++) {
            if (searchText[i] === q[qi]) qi++;
        }
        if (qi === q.length) return 3;

        return 0;
    }

    function getMatches(query) {
        return commands
            .map(c => ({ ...c, score: scoreMatch(query, c) }))
            .filter(c => c.score > 0)
            .sort((a, b) => b.score - a.score);
    }

    function render(query) {
        const matches = getMatches(query);

        if (matches.length === 0 && query.length > 0) {
            // Did you mean?
            const suggestions = getMatches(query.slice(0, -1));
            const hint = suggestions.length > 0 ? suggestions[0].label : null;
            _results.innerHTML = `<div class="cmd-empty">
                No matching commands${hint ? `<br><span style="color:var(--primary);font-size:0.8rem;cursor:pointer" onclick="document.querySelector('.cmd-input').value='${hint.toLowerCase()}';document.querySelector('.cmd-input').dispatchEvent(new Event('input'))">Did you mean: "${hint}"?</span>` : ''}
            </div>`;
            _preview.innerHTML = '';
            return;
        }

    function highlightMatch(text, query) {
        if (!query) return text;
        const q = query.toLowerCase();
        const idx = text.toLowerCase().indexOf(q);
        if (idx >= 0) return text.slice(0, idx) + '<mark style="background:rgba(59,130,246,0.2);color:inherit;border-radius:2px;padding:0 1px">' + text.slice(idx, idx + q.length) + '</mark>' + text.slice(idx + q.length);
        return text;
    }

        _results.innerHTML = matches.slice(0, 8).map((c, i) => `
            <div class="cmd-item ${i === _selectedIdx ? 'selected' : ''}" data-idx="${i}">
                <span class="cmd-item-icon">${typeIcons[c.type] || ''}</span>
                <span class="cmd-item-label">${highlightMatch(c.label, query)}</span>
                <span class="cmd-item-type">${c.type}</span>
            </div>`).join('');

        // Show preview for selected item
        const sel = matches[_selectedIdx];
        if (sel && sel.desc) {
            _preview.innerHTML = `<div style="padding:8px 16px;font-size:0.78rem;color:var(--text-muted);border-top:1px solid var(--border-color);">${sel.desc}</div>`;
        } else {
            _preview.innerHTML = '';
        }

        _results.querySelectorAll('.cmd-item').forEach((el, i) => {
            el.addEventListener('click', () => executeMatch(matches, i));
            el.addEventListener('mouseenter', () => {
                _selectedIdx = i;
                updateSelection(_results.querySelectorAll('.cmd-item'));
                const s = matches[i];
                if (s && s.desc) _preview.innerHTML = `<div style="padding:8px 16px;font-size:0.78rem;color:var(--text-muted);border-top:1px solid var(--border-color);">${s.desc}</div>`;
            });
        });
    }

    function handleKeydown(e) {
        const items = _results.querySelectorAll('.cmd-item');
        const matches = getMatches(_input.value);
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            _selectedIdx = Math.min(_selectedIdx + 1, Math.min(items.length, 7));
            updateSelection(items);
            const sel = matches[_selectedIdx];
            if (sel) _preview.innerHTML = `<div style="padding:8px 16px;font-size:0.78rem;color:var(--text-muted);border-top:1px solid var(--border-color);">${sel.desc || ''}</div>`;
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            _selectedIdx = Math.max(_selectedIdx - 1, 0);
            updateSelection(items);
            const sel = matches[_selectedIdx];
            if (sel) _preview.innerHTML = `<div style="padding:8px 16px;font-size:0.78rem;color:var(--text-muted);border-top:1px solid var(--border-color);">${sel.desc || ''}</div>`;
        } else if (e.key === 'Enter') {
            e.preventDefault();
            executeMatch(matches, _selectedIdx);
        }
    }

    function updateSelection(items) {
        items.forEach((el, i) => el.classList.toggle('selected', i === _selectedIdx));
        items[_selectedIdx]?.scrollIntoView({ block: 'nearest' });
    }

    function executeMatch(matches, idx) { if (matches[idx]) matches[idx].action(); }

    // ── Query Handlers ──────────────────────────────────────────────────
    async function queryRevenue() {
        close();
        try {
            const kpis = await API.get('/api/dashboard/kpis');
            showToast(`Revenue: ${formatCurrency(kpis.finance.total_revenue)} | Profit: ${formatCurrency(kpis.finance.profit)}`, 'info');
        } catch { showToast('Failed to fetch revenue', 'error'); }
    }

    async function queryEmployees() {
        close();
        try {
            const kpis = await API.get('/api/dashboard/kpis');
            showToast(`Total Employees: ${kpis.hcm.total_employees} | Avg Performance: ${kpis.hcm.avg_performance}`, 'info');
        } catch { showToast('Failed to fetch data', 'error'); }
    }

    async function queryInventory() {
        close();
        try {
            const kpis = await API.get('/api/dashboard/kpis');
            const msg = kpis.procurement.low_stock_alerts > 0
                ? `${kpis.procurement.low_stock_alerts} item(s) below reorder level` : 'All inventory levels healthy';
            showToast(msg, kpis.procurement.low_stock_alerts > 0 ? 'warning' : 'success');
        } catch { showToast('Failed to fetch inventory', 'error'); }
    }

    async function queryPendingPOs() {
        close();
        try {
            const kpis = await API.get('/api/dashboard/kpis');
            showToast(`Pending Purchase Orders: ${kpis.procurement.pending_purchase_orders}`, 'info');
        } catch { showToast('Failed to fetch data', 'error'); }
    }

    async function queryProjects() {
        close();
        try {
            const kpis = await API.get('/api/dashboard/kpis');
            showToast(`Active: ${kpis.ppm.active_projects} | Delayed: ${kpis.ppm.delayed_projects}`, 'info');
        } catch { showToast('Failed to fetch data', 'error'); }
    }

    async function queryHealth() {
        close();
        try {
            const data = await API.get('/api/insights/summary');
            const h = data.health;
            const emoji = h.status === 'healthy' ? 'Healthy' : h.status === 'caution' ? 'Caution' : 'Critical';
            showToast(`Business Health: ${h.score}/100 (${emoji})`, h.status === 'healthy' ? 'success' : h.status === 'caution' ? 'warning' : 'error');
        } catch { showToast('Failed to fetch health', 'error'); }
    }

    async function trainModels() {
        close();
        showToast('Training ML models...', 'info');
        try {
            await API.post('/api/ml/train');
            showToast('ML models trained successfully!', 'success');
        } catch (err) { showToast(err.message || 'Training failed', 'error'); }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    return { open, close };
})();
