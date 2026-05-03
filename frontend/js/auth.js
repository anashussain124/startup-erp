/**
 * Authentication Logic — using Supabase Client
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
    loginLabel.textContent = isRegistering ? 'Email Address' : 'Email Address';
    loginBtn.textContent = isRegistering ? 'Create Account' : 'Sign In';
    toggleBtn.textContent = isRegistering ? 'Already have an account? Sign in' : "Don't have an account? Sign up";
});

loginBtn.addEventListener('click', async () => {
    const email = document.getElementById('username').value; // Using username field as email
    const password = document.getElementById('password').value;

    if (!email || !password) {
        showToast('Please fill in all required fields', 'error');
        return;
    }

    try {
        if (isRegistering) {
            const full_name = document.getElementById('full_name').value;

            const { data, error } = await supabaseClient.auth.signUp({
                email,
                password,
                options: {
                    data: {
                        full_name: full_name || email.split('@')[0],
                    }
                }
            });

            if (error) throw error;

            alert('Registration successful! Please check your email to activate your account.');
            isRegistering = false;
            toggleBtn.click(); // Switch back to login
        } else {
            const { data, error } = await supabaseClient.auth.signInWithPassword({
                email,
                password
            });

            if (error) {
                if (error.message.includes('Invalid login credentials')) {
                    throw new Error('Incorrect email or password');
                }
                throw error;
            }

            // Save basic user info and redirect
            API.setUser({
                id: data.user.id,
                username: data.user.email.split('@')[0],
                role: 'user' // Actual role will be fetched from backend on first request
            });
            
            window.location.href = 'dashboard.html';
        }
    } catch (error) {
        console.error('Auth error:', error);
        showToast(error.message || 'Authentication failed.', 'error');
    }
});
