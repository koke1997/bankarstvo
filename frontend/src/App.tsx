import React from 'react';
import AppRouter from './router/AppRouter';
import { authService } from './services/api/authService';
import TestComponent from './components/TestComponent';

// Initialize auth token from localStorage if available
authService.getToken();

const App: React.FC = () => {
  return (
    <div className="App">
      <TestComponent />
      <AppRouter />
    </div>
  );
};

export default App;