import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import AppRouter from './router/AppRouter';
import { authService } from './services/api/authService';
import TestComponent from './components/TestComponent';
// Initialize auth token from localStorage if available
authService.getToken();
const App = () => {
    return (_jsxs("div", Object.assign({ className: "App" }, { children: [_jsx(TestComponent, {}), _jsx(AppRouter, {})] })));
};
export default App;
