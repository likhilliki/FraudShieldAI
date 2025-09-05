import React from 'react';
import { Search, Building, TrendingUp, MessageCircle, AlertTriangle } from 'lucide-react';

interface VerificationCardProps {
  activeTab: 'advisor' | 'announcement' | 'social' | 'anomaly';
  inputValue: string;
  setInputValue: (value: string) => void;
  onVerify: () => void;
  loading: boolean;
}

const VerificationCard: React.FC<VerificationCardProps> = ({
  activeTab,
  inputValue,
  setInputValue,
  onVerify,
  loading
}) => {
  const getPlaceholder = () => {
    switch (activeTab) {
      case 'advisor':
        return 'Enter advisor name or email (e.g., "John Smith" or "advisor@example.com")';
      case 'announcement':
        return 'Enter announcement text or company ticker (e.g., "RELIANCE announces dividend")';
      case 'social':
        return 'Enter social media message or URL (e.g., "Buy XYZ stock for guaranteed 300% returns!")';
      case 'anomaly':
        return 'Enter stock ticker or company name (e.g., "INFY", "TCS")';
      default:
        return 'Enter information to verify...';
    }
  };

  const getIcon = () => {
    switch (activeTab) {
      case 'advisor':
        return Building;
      case 'announcement':
        return TrendingUp;
      case 'social':
        return MessageCircle;
      case 'anomaly':
        return AlertTriangle;
    }
  };

  const Icon = getIcon();

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center space-x-3 mb-4">
        <div className="bg-blue-100 p-2 rounded-lg">
          <Icon className="w-5 h-5 text-blue-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900">Enter Information</h3>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {activeTab === 'advisor' ? 'Advisor Details' :
             activeTab === 'announcement' ? 'Announcement Text' :
             activeTab === 'social' ? 'Social Media Content' :
             'Stock Information'}
          </label>
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={getPlaceholder()}
            rows={4}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200"
          />
        </div>

        <button
          onClick={onVerify}
          disabled={!inputValue.trim() || loading}
          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
        >
          {loading ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
          ) : (
            <>
              <Search className="w-5 h-5" />
              <span>Verify with AI</span>
            </>
          )}
        </button>

        <div className="text-xs text-gray-500 space-y-1">
          <p>• Analysis typically takes 2-5 seconds</p>
          <p>• Data sourced from SEBI, NSE, BSE registries</p>
          <p>• AI explanations provided in plain English</p>
        </div>
      </div>
    </div>
  );
};

export default VerificationCard;