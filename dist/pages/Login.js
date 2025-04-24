var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/api/authService';
const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const handleSubmit = (e) => __awaiter(void 0, void 0, void 0, function* () {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        try {
            const response = yield authService.login({ username, password });
            // Save the token in localStorage
            authService.saveToken(response.token);
            // Redirect to dashboard
            navigate('/dashboard');
        }
        catch (err) {
            setError('Invalid username or password');
            console.error('Login error:', err);
        }
        finally {
            setIsLoading(false);
        }
    });
    return (_jsx("div", Object.assign({ className: "min-h-screen flex items-center justify-center bg-gray-100" }, { children: _jsxs("div", Object.assign({ className: "bg-white p-8 rounded-lg shadow-md w-full max-w-md" }, { children: [_jsx("h2", Object.assign({ className: "text-2xl font-bold mb-6 text-center" }, { children: "Login to Your Account" })), error && (_jsx("div", Object.assign({ className: "bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" }, { children: error }))), _jsxs("form", Object.assign({ onSubmit: handleSubmit }, { children: [_jsxs("div", Object.assign({ className: "mb-4" }, { children: [_jsx("label", Object.assign({ className: "block text-gray-700 text-sm font-bold mb-2", htmlFor: "username" }, { children: "Username" })), _jsx("input", { id: "username", type: "text", className: "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500", value: username, onChange: (e) => setUsername(e.target.value), required: true })] })), _jsxs("div", Object.assign({ className: "mb-6" }, { children: [_jsx("label", Object.assign({ className: "block text-gray-700 text-sm font-bold mb-2", htmlFor: "password" }, { children: "Password" })), _jsx("input", { id: "password", type: "password", className: "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500", value: password, onChange: (e) => setPassword(e.target.value), required: true })] })), _jsx("button", Object.assign({ type: "submit", className: `w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`, disabled: isLoading }, { children: isLoading ? 'Logging in...' : 'Login' }))] })), _jsx("div", Object.assign({ className: "mt-6 text-center" }, { children: _jsxs("p", Object.assign({ className: "text-sm" }, { children: ["Don't have an account?", ' ', _jsx(Link, Object.assign({ to: "/register", className: "text-blue-500 hover:text-blue-700" }, { children: "Register here" }))] })) }))] })) })));
};
export default Login;
