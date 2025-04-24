var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import apiClient from './apiClient';
// Auth service functions
export const authService = {
    login: (credentials) => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield apiClient.post('/auth/login', credentials);
        return response.data;
    }),
    register: (userData) => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield apiClient.post('/auth/register', userData);
        return response.data;
    }),
    logout: () => __awaiter(void 0, void 0, void 0, function* () {
        // Clear token before making the request
        localStorage.removeItem('auth_token');
        yield apiClient.post('/auth/logout');
    }),
    getCurrentUser: () => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield apiClient.get('/auth/me');
        return response.data;
    }),
    // Store token in localStorage
    saveToken: (token) => {
        localStorage.setItem('auth_token', token);
        // No need to call setToken on apiClient as the interceptor will handle it
    },
    // Get token from localStorage
    getToken: () => {
        return localStorage.getItem('auth_token');
        // No need to call setToken on apiClient as the interceptor will handle it
    },
    // Remove token from localStorage
    removeToken: () => {
        localStorage.removeItem('auth_token');
        // No need to call clearToken on apiClient as the interceptor will handle it
    }
};
export default authService;
