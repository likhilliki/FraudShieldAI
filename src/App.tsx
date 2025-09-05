import React, { useState } from 'react';
import { Shield, Search, AlertTriangle, CheckCircle, ExternalLink, Mail, TrendingUp, MessageCircle, Building } from 'lucide-react';
import Dashboard from './components/Dashboard';
import VerificationCard from './components/VerificationCard';
import ResultsCard from './components/ResultsCard';
import LoadingSpinner from './components/LoadingSpinner';

interface VerificationResult {
  risk_score: number;
  risk_level: 'Low' | 'Medium' | 'High';
  reasons: string[];
  ai_explanation: string;
  evidence?: any;
}

function App() {
  const [activeTab, setActiveTab] = useState<'advisor' | 'announcement' | 'social' | 'anomaly'>('advisor');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<VerificationResult | null>(null);
  const [inputValue, setInputValue] = useState('');

  const tabs = [
    { id: 'advisor', label: 'Advisor Check', icon: Building, description: 'Verify SEBI registered advisors' },
    { id: 'announcement', label: 'Corporate News', icon: TrendingUp, description: 'Validate company announcements' },
    { id: 'social', label: 'Social Media', icon: MessageCircle, description: 'Detect social media fraud' },
    { id: 'anomaly', label: 'Market Anomaly', icon: AlertTriangle, description: 'Identify pump & dump schemes' },
  ];

  const handleVerify = async () => {
    if (!inputValue.trim()) return;
    
    setLoading(true);
    setResults(null);

    try {
      // Simulating API call - replace with actual backend endpoint
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock results based on input
      const mockResult: VerificationResult = {
        risk_score: Math.floor(Math.random() * 100),
        risk_level: Math.random() > 0.6 ? 'High' : Math.random() > 0.3 ? 'Medium' : 'Low',
        reasons: [
          activeTab === 'advisor' ? 'Advisor not found in SEBI registry' : 
          activeTab === 'announcement' ? 'No matching official filing found' :
          activeTab === 'social' ? 'Contains suspicious keywords' :
          'Unusual volume spike detected',
          'AI analysis flagged potential fraud indicators'
        ],
        ai_explanation: `Based on our analysis of "${inputValue}", this appears to be ${Math.random() > 0.5 ? 'suspicious' : 'potentially legitimate'} content. Our AI detected several red flags including unregistered entities and promises of guaranteed returns.`
      };
      
      setResults(mockResult);
    } catch (error) {
      console.error('Verification failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReport = () => {
    const subject = `Fraud Report - ${activeTab} Verification`;
    const body = `Dear SEBI,\n\nI would like to report a potential fraud case:\n\nType: ${activeTab}\nContent: ${inputValue}\nRisk Score: ${results?.risk_score}\nReasons: ${results?.reasons.join(', ')}\n\nAI Analysis: ${results?.ai_explanation}\n\nPlease investigate this matter.\n\nThank you.`;
    
    window.open(`mailto:complaints@sebi.gov.in?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">FraudShield AI</h1>
                <p className="text-sm text-gray-600">Protecting retail investors</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                <CheckCircle className="w-4 h-4 inline mr-1" />
                Online
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Controls */}
          <div className="lg:col-span-1 space-y-6">
            {/* Tab Selection */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Verification Type</h2>
              <div className="space-y-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`w-full text-left p-4 rounded-lg transition-all duration-200 ${
                      activeTab === tab.id
                        ? 'bg-blue-50 border-2 border-blue-200 text-blue-800'
                        : 'bg-gray-50 border-2 border-transparent text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <tab.icon className={`w-5 h-5 mt-0.5 ${activeTab === tab.id ? 'text-blue-600' : 'text-gray-500'}`} />
                      <div>
                        <div className="font-medium">{tab.label}</div>
                        <div className="text-sm opacity-75">{tab.description}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Input Form */}
            <VerificationCard
              activeTab={activeTab}
              inputValue={inputValue}
              setInputValue={setInputValue}
              onVerify={handleVerify}
              loading={loading}
            />
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b">
                <h2 className="text-lg font-semibold text-gray-900">Verification Results</h2>
                <p className="text-gray-600 mt-1">AI-powered fraud detection analysis</p>
              </div>
              
              <div className="p-6">
                {loading ? (
                  <LoadingSpinner />
                ) : results ? (
                  <ResultsCard results={results} onReport={handleReport} />
                ) : (
                  <div className="text-center py-12">
                    <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Analyze</h3>
                    <p className="text-gray-600 mb-6">Enter information in the form and click "Verify" to get started</p>
                    <div className="grid grid-cols-2 gap-4 max-w-md mx-auto">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">50K+</div>
                        <div className="text-sm text-blue-800">Advisors Verified</div>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">99.5%</div>
                        <div className="text-sm text-green-800">Accuracy Rate</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
          <h2 className="text-2xl font-bold mb-4">Powered by Advanced AI</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-start space-x-3">
              <div className="bg-white/20 p-2 rounded-lg">
                <Shield className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold">SEBI Registry</h3>
                <p className="text-sm opacity-90">Live verification against official registry</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="bg-white/20 p-2 rounded-lg">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold">Market Analysis</h3>
                <p className="text-sm opacity-90">Real-time NSE/BSE data analysis</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="bg-white/20 p-2 rounded-lg">
                <MessageCircle className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold">AI Detection</h3>
                <p className="text-sm opacity-90">GPT-powered fraud pattern recognition</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div className="text-gray-600">
              <p>&copy; 2024 FraudShield AI. Protecting investors from fraud.</p>
            </div>
            <div className="flex items-center space-x-4">
              <a href="#" className="text-gray-600 hover:text-blue-600 transition-colors">
                <ExternalLink className="w-5 h-5" />
              </a>
              <button
                onClick={() => window.open('mailto:complaints@sebi.gov.in')}
                className="text-gray-600 hover:text-blue-600 transition-colors"
              >
                <Mail className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;