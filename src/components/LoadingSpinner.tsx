import React from 'react';
import { Shield, Search, TrendingUp, Brain } from 'lucide-react';

const LoadingSpinner: React.FC = () => {
  const steps = [
    { icon: Search, label: 'Scanning Input', delay: 0 },
    { icon: Shield, label: 'Checking SEBI Registry', delay: 500 },
    { icon: TrendingUp, label: 'Analyzing Market Data', delay: 1000 },
    { icon: Brain, label: 'AI Processing', delay: 1500 },
  ];

  return (
    <div className="py-12">
      <div className="text-center mb-8">
        <div className="w-16 h-16 mx-auto mb-4">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600"></div>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Analyzing with AI</h3>
        <p className="text-gray-600">Please wait while we verify the information...</p>
      </div>

      <div className="space-y-4 max-w-md mx-auto">
        {steps.map((step, index) => (
          <div
            key={index}
            className="flex items-center space-x-3 p-3 rounded-lg bg-gray-50 animate-pulse"
            style={{ animationDelay: `${step.delay}ms` }}
          >
            <div className="bg-blue-100 p-2 rounded-lg">
              <step.icon className="w-4 h-4 text-blue-600" />
            </div>
            <span className="text-sm text-gray-700">{step.label}</span>
            <div className="ml-auto">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-ping"></div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 text-center text-sm text-gray-500">
        <p>Powered by GPT-4o-mini • Live data from SEBI, NSE, BSE</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;