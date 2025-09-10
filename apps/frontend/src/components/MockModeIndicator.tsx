import React from 'react';

const MockModeIndicator: React.FC = () => {
  const isVisible = import.meta.env.VITE_ENABLE_MOCK_DATA === 'true' && 
                   import.meta.env.VITE_MOCK_MODE_INDICATOR === 'true';

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-4 left-4 z-50">
      <div className="bg-amber-100 border border-amber-300 text-amber-800 px-3 py-2 rounded-lg shadow-lg text-sm flex items-center space-x-2">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
        </span>
        <span className="font-medium">Demo Mode</span>
        <span className="text-amber-600">Using mock data</span>
      </div>
    </div>
  );
};

export default MockModeIndicator;