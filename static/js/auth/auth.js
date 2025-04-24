// Authentication module
import { ApiClient } from '../api/api-client';
// Main authentication functions
export function initializeAuthentication() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
}
async function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const credentials = {
        username: formData.get('username'),
        password: formData.get('password')
    };
    try {
        const apiClient = new ApiClient();
        const response = await apiClient.login(credentials);
        // Store token in local storage
        localStorage.setItem('auth_token', response.token);
        // Redirect to dashboard
        window.location.href = '/dashboard';
    }
    catch (error) {
        console.error('Login failed:', error);
        showError('Invalid username or password. Please try again.');
    }
}
async function handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const registerData = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password'),
        passwordConfirm: formData.get('password_confirm')
    };
    // Validate passwords match
    if (registerData.password !== registerData.passwordConfirm) {
        showError('Passwords do not match');
        return;
    }
    try {
        const apiClient = new ApiClient();
        const response = await apiClient.register(registerData);
        // Show success message
        showSuccess('Registration successful! You can now log in.');
        // Redirect to login page after a delay
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    }
    catch (error) {
        console.error('Registration failed:', error);
        showError('Registration failed. Please check your information and try again.');
    }
}
// Helper functions
function showError(message) {
    const errorElement = document.querySelector('.error-message');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
    }
}
function showSuccess(message) {
    const successElement = document.querySelector('.success-message');
    if (successElement) {
        successElement.textContent = message;
        successElement.classList.remove('hidden');
    }
}
//# sourceMappingURL=auth.js.map