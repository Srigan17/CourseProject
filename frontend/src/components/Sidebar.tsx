import React from 'react';
import {
  LayoutDashboard,
  Building2,
  Cpu,
  Activity,
  BarChart2
} from 'lucide-react';

export type NavTab = 'overview' | 'network' | 'training' | 'testing' | 'performance';

interface SidebarProps {
  activeTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  isTraining?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  isTraining = false
}) => {
  const navItems = [
    {
      id: 'overview' as NavTab,
      label: 'Dashboard',
      icon: LayoutDashboard,
      description: 'System overview & summary'
    },
    {
      id: 'network' as NavTab,
      label: 'Hospital Network',
      icon: Building2,
      description: '3 demonstration hospital nodes'
    },
    {
      id: 'training' as NavTab,
      label: 'Model Training',
      icon: Cpu,
      description: 'Live 8-round federated training',
      isHot: isTraining
    },
    {
      id: 'testing' as NavTab,
      label: 'Activity Testing',
      icon: Activity,
      description: 'Test sensor inputs & CSV inference'
    },
    {
      id: 'performance' as NavTab,
      label: 'Results',
      icon: BarChart2,
      description: 'Experimental benchmark & metrics'
    }
  ];

  return (
    <aside className="w-64 bg-[#0B1528] text-slate-300 flex flex-col h-screen fixed left-0 top-0 border-r border-slate-800/80 z-30 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
          <Activity className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-white tracking-wide">HealthFL SecAgg</h1>
          <p className="text-[11px] text-blue-400 font-medium">Privacy-Preserving Healthcare FL</p>
        </div>
      </div>

      {/* Nav List - Exactly 5 items */}
      <nav className="flex-1 px-3 py-6 space-y-1.5 overflow-y-auto">
        <div className="px-3 pb-3 text-[11px] font-bold tracking-wider text-slate-400 uppercase">
          Navigation
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-left transition-all cursor-pointer ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/70'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <div>
                  <span className="block text-sm font-semibold">{item.label}</span>
                  <span className={`block text-[10px] ${isActive ? 'text-blue-100' : 'text-slate-500'}`}>
                    {item.description}
                  </span>
                </div>
              </div>
              {item.isHot && (
                <span className="flex h-2.5 w-2.5 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Compact System Footer */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
        <div className="flex items-center justify-between text-[11px] text-slate-400">
          <span>Security Protocol</span>
          <span className="text-blue-400 font-medium">Paillier + DP</span>
        </div>
        <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1">
          <span>Nodes</span>
          <span className="text-slate-300">3 Simulated Silos</span>
        </div>
        <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1">
          <span>Target Activities</span>
          <span className="text-slate-300">6 Physical Classes</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
