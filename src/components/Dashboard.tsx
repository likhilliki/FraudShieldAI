import React from 'react';
import { Shield, TrendingUp, Users, AlertTriangle } from 'lucide-react';

const Dashboard: React.FC = () => {
  const stats = [
    {
      title: 'Total Verifications',
      value: '12,543',
      change: '+12%',
      icon: Shield,
      color: 'blue',
    },
    {
      title: 'Fraud Cases Detected',
      value: '892',
      change: '+8%',
      icon: AlertTriangle,
      color: 'red',
    },
    {
      title: 'Verified Advisors',
      value: '5,231',
      change: '+15%',
      icon: Users,
      color: 'green',
    },
    {
      title: 'Market Alerts',
      value: '234',
      change: '-5%',
      icon: TrendingUp,
      color: 'purple',
    },
  ];

  const getColorClasses = (color: string) => {
    const colors = {
      blue: 'text-blue-600 bg-blue-50',
      red: 'text-red-600 bg-red-50',
      green: 'text-green-600 bg-green-50',
      purple: 'text-purple-600 bg-purple-50',
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, index) => (
        <div key={index} className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">{stat.title}</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
              <p className={`text-sm mt-2 ${stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                {stat.change} from last month
              </p>
            </div>
            <div className={`p-3 rounded-lg ${getColorClasses(stat.color)}`}>
              <stat.icon className="w-6 h-6" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Dashboard;