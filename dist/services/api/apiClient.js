import axios from 'axios';
// Create an Axios instance with default configuration
const apiClient = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json'
    }
});
// Request interceptor to attach authentication token to every request
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => Promise.reject(error));
// Response interceptor to handle common errors
apiClient.interceptors.response.use((response) => response, (error) => {
    if (error.response) {
        // Unauthorized, redirect to login
        if (error.response.status === 401) {
            localStorage.removeItem('auth_token');
            window.location.href = '/login';
        }
        // Server error
        if (error.response.status >= 500) {
            console.error('Server error:', error.response.data);
        }
    }
    return Promise.reject(error);
});
export default apiClient;
