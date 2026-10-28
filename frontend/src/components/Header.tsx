import React from 'react';
import { Shield, RefreshCw, Building2 } from 'lucide-react';
import { NavTab } from './Sidebar';

interface HeaderProps {
  activeTab: NavTab;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onRefresh,
  isRefreshing
}) => {
  const titles: Record<NavTab, { title: string; subtitle: string }> = {
    overview: {
      title: 'HealthFL Dashboard',
      subtitle: 'Federated physical activity classification across distributed hospital nodes'
    },
    network: {
      title: 'Hospital Network',
      subtitle: 'Three simulated hospital nodes retaining raw patient sensor data locally'
    },
    training: {
      title: 'Model Training',
      subtitle: 'Live 8-round federated training with FedProx, Differential Privacy, and Paillier Secure Aggregation'
    },
    testing: {
      title: 'Activity Testing',
      subtitle: 'Predict physical activity from individual wearable sensor values or uploaded CSV data'
    },
    performance: {
      title: 'Experimental Results',
      subtitle: 'Empirical comparison across centralized, federated, DP, and secure aggregation configurations'
    }
  };

  const current = titles[activeTab];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-20 px-8 py-3.5">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-blue-600 uppercase tracking-wider mb-0.5">
            <span>HealthFL SecAgg</span>
            <span>•</span>
            <span className="text-slate-500 capitalize">{activeTab === 'performance' ? 'Results' : activeTab === 'overview' ? 'Dashboard' : activeTab}</span>
          </div>
          <h2 className="text-lg font-bold text-slate-900 tracking-tight">{current.title}</h2>
          <p className="text-xs text-slate-500">{current.subtitle}</p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-full text-xs font-medium text-blue-700">
            <Building2 className="w-3.5 h-3.5 text-blue-600" />
            <span>3 Simulated Hospital Nodes</span>
          </div>

          <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700">
            <Shield className="w-3.5 h-3.5 text-blue-600" />
            <span>DP + Paillier PHE</span>
          </div>

          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-medium rounded-lg shadow-sm transition cursor-pointer"
            title="Refresh status"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-blue-600' : ''}`} />
            <span className="hidden md:inline">Refresh</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
