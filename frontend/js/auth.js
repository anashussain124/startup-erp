/**
 * Authentication Logic — using backend API
 */

let isRegistering = false;

const loginBtn = document.getElementById('login-btn');
const toggleBtn = document.getElementById('toggle-auth');
const registerFields = document.getElementById('register-fields');
const emailField = document.getElementById('email-field');
const loginLabel = document.getElementById('login-label');

toggleBtn.addEventListener('click', () => {
    isRegistering = !isRegistering;
    registerFields.style.display = isRegistering ? 'block' : 'none';
    emailField.style.display = isRegistering ? 'block' : 'none';
    loginLabel.textContent = isRegistering ? 'Username' : 'Username or Email';
    loginBtn.textContent = isRegistering ? 'Create Account' : 'Sign In';
    toggleBtn.textContent = isRegistering ? 'Already have an account? Sign in' : "Don't have an account? Sign up";
});

loginBtn.addEventListener('click', async () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        alert('Please fill in all required fields');
        return;
    }

    try {
        if (isRegistering) {
            const email = document.getElementById('email').value;
            const full_name = document.getElementById('full_name').value;
            const company_id = document.getElementById('company_id').value;

            if (!email) {
                alert('Email is required for registration');
                return;
            }

            const data = await API.post('/auth/register', {
                username,
                email,
                password,
                full_name,
                role: 'admin' // Default to admin for first user of a company
            });

            alert('Registration successful! You can now sign in.');
            isRegistering = false;
            toggleBtn.click(); // Switch back to login
        } else {
            const data = await API.post('/auth/login', {
                username,
                password
            });

            // Save session and redirect
            API.setToken(data.access_token);
            API.setUser({
                id: data.user_id,
                username: data.username,
                role: data.role
            });
            
            window.location.href = 'dashboard.html';
        }
    } catch (error) {
        console.error('Auth error:', error);
        alert(error.message || 'Authentication failed. Please check your credentials.');
    }
});
