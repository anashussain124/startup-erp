/**
 * Common Utilities
 */

async function checkAuth() {
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
        window.location.href = 'index.html';
        return null;
    }
    
    // Get local user info from backend
    const res = await fetch(`${CONFIG.API_BASE_URL}/auth/me`, {
        headers: {
            'Authorization': `Bearer ${session.access_token}`
        }
    });
    
    if (!res.ok) {
        console.error("Failed to sync user session with backend");
    }
    
    return await res.json();
}

const logoutLink = document.getElementById('logout-link');
if (logoutLink) {
    logoutLink.addEventListener('click', async (e) => {
        e.preventDefault();
        await supabase.auth.signOut();
        localStorage.removeItem('supabase_session');
        window.location.href = 'index.html';
    });
}
