/**
 * Common Utilities — using backend API
 */

async function checkAuth() {
    if (!API.isAuthenticated()) {
        window.location.href = 'index.html';
        return null;
    }
    
    try {
        const user = await API.get('/auth/me');
        return user;
    } catch (err) {
        console.error("Auth sync failed:", err);
        API.clearAuth();
        window.location.href = 'index.html';
        return null;
    }
}

const logoutLink = document.getElementById('logout-link');
if (logoutLink) {
    logoutLink.addEventListener('click', (e) => {
        e.preventDefault();
        API.clearAuth();
        window.location.href = 'index.html';
    });
}
