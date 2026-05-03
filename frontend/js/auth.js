/**
 * Authentication Logic — using Supabase Client
 */

const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const fullNameInput = document.getElementById('full_name');
const companyNameInput = document.getElementById('company_name');
const forgotPasswordBtn = document.getElementById('forgot-password');

let isRegistering = false;

toggleBtn.addEventListener('click', () => {
    isRegistering = !isRegistering;
    registerFields.style.display = isRegistering ? 'block' : 'none';
    forgotPasswordBtn.style.display = isRegistering ? 'none' : 'block';
    loginBtn.textContent = isRegistering ? 'Create Account' : 'Sign In';
    toggleBtn.textContent = isRegistering ? 'Already have an account? Sign in' : "Don't have an account? Sign up";
    loginLabel.textContent = 'Email Address';
});

forgotPasswordBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();
    if (!email) {
        showToast('Please enter your email address first.', 'warning');
        return;
    }

    try {
        const { error } = await supabaseClient.auth.resetPasswordForEmail(email, {
            redirectTo: window.location.origin + '/static/index.html',
        });
        if (error) throw error;
        showToast('Password reset link sent to your email!', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
});

loginBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const fullName = fullNameInput.value.trim();
    const companyName = companyNameInput.value.trim();

    if (!email || !password) {
        showToast('Please fill in all required fields.', 'warning');
        return;
    }

    loginBtn.disabled = true;
    loginBtn.textContent = isRegistering ? 'Creating Account...' : 'Signing In...';

    try {
        if (isRegistering) {
            if (!fullName || !companyName) {
                throw new Error('Full Name and Company Name are required for registration.');
            }

            const { data, error } = await supabaseClient.auth.signUp({
                email,
                password,
                options: {
                    data: {
                        full_name: fullName,
                        company_name: companyName
                    }
                }
            });
            
            if (error) throw error;

            showToast('Registration successful! Please check your email to confirm your account.', 'success');
            // Switch back to login mode
            isRegistering = false;
            registerFields.style.display = 'none';
            loginBtn.textContent = 'Sign In';
            toggleBtn.textContent = "Don't have an account? Sign up";
        } else {
            const { data, error } = await supabaseClient.auth.signInWithPassword({
                email,
                password,
            });

            if (error) {
                if (error.message.includes('Email not confirmed')) {
                    throw new Error('Please confirm your email address before logging in.');
                }
                throw error;
            }

            // Success! Store user info (optional, API.js handles session)
            API.setUser({ 
                email: data.user.email,
                username: data.user.user_metadata.full_name || data.user.email.split('@')[0],
                role: 'Admin' 
            });

            showToast('Welcome back!', 'success');
            setTimeout(() => {
                window.location.href = '/static/dashboard.html';
            }, 800);
        }
    } catch (error) {
        console.error('Auth error:', error);
        showToast(error.message || 'Authentication failed.', 'error');
    }
});
