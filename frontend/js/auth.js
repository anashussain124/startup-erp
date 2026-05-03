/**
 * Authentication Logic
 */

let isRegistering = false;

const loginBtn = document.getElementById('login-btn');
const toggleBtn = document.getElementById('toggle-auth');
const registerFields = document.getElementById('register-fields');

toggleBtn.addEventListener('click', () => {
    isRegistering = !isRegistering;
    registerFields.style.display = isRegistering ? 'block' : 'none';
    loginBtn.textContent = isRegistering ? 'Create Account' : 'Sign In';
    toggleBtn.textContent = isRegistering ? 'Already have an account? Sign in' : "Don't have an account? Sign up";
});

loginBtn.addEventListener('click', async () => {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (isRegistering) {
        const full_name = document.getElementById('full_name').value;
        const company_id = document.getElementById('company_id').value;

        const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: { full_name, company_id, role: 'admin' }
            }
        });

        if (error) alert(error.message);
        else {
            alert('Registration successful! Please check your email for confirmation.');
            location.reload();
        }
    } else {
        const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password
        });

        if (error) alert(error.message);
        else {
            // Save session and redirect
            localStorage.setItem('supabase_session', JSON.stringify(data.session));
            window.location.href = 'dashboard.html';
        }
    }
});
