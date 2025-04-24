import React from 'react';

const TestComponent: React.FC = () => {
  return (
    <div className="p-4 bg-blue-100 rounded-lg shadow">
      <h1 className="text-xl font-bold text-blue-800">React Component Test</h1>
      <p className="mt-2 text-gray-700">
        If you can see this message, your React application is working correctly!
      </p>
    </div>
  );
};

export default TestComponent;