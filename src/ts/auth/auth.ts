// Authentication module
import { ApiClient } from '../api/api-client';

// Types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterForm {
  username: string;
  email: string;
  password: string;
  passwordConfirm: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    username: string;
    email: string;
  };
}

// Main authentication functions
export function initializeAuthentication(): void {
  const loginForm = document.getElementById('login-form') as HTMLFormElement;
  const registerForm = document.getElementById('register-form') as HTMLFormElement;
  
  if (loginForm) {
    loginForm.addEventListener('submit', handleLogin);
  }
  
  if (registerForm) {
    registerForm.addEventListener('submit', handleRegister);
  }
}

async function handleLogin(event: Event): Promise<void> {
  event.preventDefault();
  const form = event.target as HTMLFormElement;
  const formData = new FormData(form);
  
  const credentials: LoginCredentials = {
    username: formData.get('username') as string,
    password: formData.get('password') as string
  };
  
  try {
    const apiClient = new ApiClient();
    const response = await apiClient.login(credentials);
    
    // Store token in local storage
    localStorage.setItem('auth_token', response.token);
    
    // Redirect to dashboard
    window.location.href = '/dashboard';
  } catch (error) {
    console.error('Login failed:', error);
    showError('Invalid username or password. Please try again.');
  }
}

async function handleRegister(event: Event): Promise<void> {
  event.preventDefault();
  const form = event.target as HTMLFormElement;
  const formData = new FormData(form);
  
  const registerData: RegisterForm = {
    username: formData.get('username') as string,
    email: formData.get('email') as string,
    password: formData.get('password') as string,
    passwordConfirm: formData.get('password_confirm') as string
  };
  
  // Validate passwords match
  if (registerData.password !== registerData.passwordConfirm) {
    showError('Passwords do not match');
    return;
  }
  
  try {
    const apiClient = new ApiClient();
    await apiClient.register(registerData);
    
    // Show success message
    showSuccess('Registration successful! You can now log in.');
    
    // Redirect to login page after a delay
    setTimeout(() => {
      window.location.href = '/login';
    }, 2000);
  } catch (error) {
    console.error('Registration failed:', error);
    showError('Registration failed. Please check your information and try again.');
  }
}

// Helper functions
function showError(message: string): void {
  const errorElement = document.querySelector('.error-message');
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
  }
}

function showSuccess(message: string): void {
  const successElement = document.querySelector('.success-message');
  if (successElement) {
    successElement.textContent = message;
    successElement.classList.remove('hidden');
  }
}