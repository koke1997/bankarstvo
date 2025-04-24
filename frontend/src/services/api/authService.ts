import apiClient from './apiClient';

// Types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: number;
    username: string;
  };
}

export interface RegisterData {
  username: string;
  password: string;
  email: string;
  fullName?: string;
}

// Auth service functions
export const authService = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },

  register: async (userData: RegisterData): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register', userData);
    return response.data;
  },

  logout: async (): Promise<void> => {
    // Clear token before making the request
    localStorage.removeItem('auth_token');
    await apiClient.post<void>('/auth/logout');
  },

  getCurrentUser: async (): Promise<AuthResponse['user']> => {
    const response = await apiClient.get<AuthResponse['user']>('/auth/me');
    return response.data;
  },

  // Store token in localStorage
  saveToken: (token: string): void => {
    localStorage.setItem('auth_token', token);
    // No need to call setToken on apiClient as the interceptor will handle it
  },

  // Get token from localStorage
  getToken: (): string | null => {
    return localStorage.getItem('auth_token');
    // No need to call setToken on apiClient as the interceptor will handle it
  },

  // Remove token from localStorage
  removeToken: (): void => {
    localStorage.removeItem('auth_token');
    // No need to call clearToken on apiClient as the interceptor will handle it
  }
};

export default authService;