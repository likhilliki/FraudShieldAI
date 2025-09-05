import React from 'react';
import { AlertTriangle, CheckCircle, Mail, ExternalLink, Shield, Info } from 'lucide-react';

interface VerificationResult {
  risk_score: number;
  risk_level: 'Low' | 'Medium' | 'High';
  reasons: string[];
  ai_explanation: string;
  evidence?: any;
}

interface ResultsCardProps {
  results: VerificationResult;
  onReport: () => void;
}

const ResultsCard: React.FC<ResultsCardProps> = ({ results, onReport }) => {
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'High':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'Medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'Low':
        return 'text-green-600 bg-green-50 border-green-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'High':
        return AlertTriangle;
      case 'Medium':
        return AlertTriangle;
      case 'Low':
        return CheckCircle;
      default:
        return Info;
    }
  };

  const getScoreColor = (score: number) => {
    if (score < 40) return 'text-red-600';
    if (score < 70) return 'text-yellow-600';
    return 'text-green-600';
  };

  const RiskIcon = getRiskIcon(results.risk_level);

  return (
    <div className="space-y-6">
      {/* Risk Score Header */}
      <div className={`border-2 rounded-xl p-6 ${getRiskColor(results.risk_level)}`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <RiskIcon className="w-8 h-8" />
            <div>
              <h3 className="text-xl font-bold">Risk Level: {results.risk_level}</h3>
              <p className="opacity-75">AI-powered analysis complete</p>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${getScoreColor(results.risk_score)}`}>
              {results.risk_score}
            </div>
            <div className="text-sm opacity-75">Risk Score</div>
          </div>
        </div>
        
        <div className="w-full bg-white/50 rounded-full h-3">
          <div
            className="h-3 rounded-full transition-all duration-500"
            style={{
              width: `${results.risk_score}%`,
              backgroundColor: results.risk_score < 40 ? '#DC2626' : 
                             results.risk_score < 70 ? '#D97706' : '#16A34A'
            }}
          ></div>
        </div>
      </div>

      {/* Reasons */}
      <div className="bg-white border rounded-xl p-6">
        <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
          <Shield className="w-5 h-5 mr-2 text-blue-600" />
          Detection Results
        </h4>
        <div className="space-y-3">
          {results.reasons.map((reason, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 rounded-full bg-blue-600 mt-2 flex-shrink-0"></div>
              <p className="text-gray-700">{reason}</p>
            </div>
          ))}
        </div>
      </div>

      {/* AI Explanation */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-xl p-6">
        <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
          <div className="w-6 h-6 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 mr-2 flex items-center justify-center">
            <span className="text-white text-xs font-bold">AI</span>
          </div>
          AI Explanation
        </h4>
        <div className="bg-white/70 rounded-lg p-4 border">
          <p className="text-gray-800 leading-relaxed">{results.ai_explanation}</p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={onReport}
          className="flex-1 bg-gradient-to-r from-red-600 to-red-700 text-white font-semibold py-3 px-6 rounded-lg hover:from-red-700 hover:to-red-800 transition-all duration-200 flex items-center justify-center space-x-2"
        >
          <Mail className="w-5 h-5" />
          <span>Report to SEBI</span>
        </button>
        
        <button
          onClick={() => window.open('https://sebi.gov.in', '_blank')}
          className="flex-1 bg-gray-100 text-gray-700 font-semibold py-3 px-6 rounded-lg hover:bg-gray-200 transition-all duration-200 flex items-center justify-center space-x-2"
        >
          <ExternalLink className="w-5 h-5" />
          <span>Visit SEBI</span>
        </button>
      </div>

      {/* Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <Info className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-amber-800">
            <p className="font-medium mb-1">Important Disclaimer</p>
            <p>This analysis is for informational purposes only. Always conduct your own research and consult with qualified financial advisors before making investment decisions.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsCard;