import React, { useState, useEffect } from 'react';
import {
  Shield,
  Activity,
  ArrowRight,
  TrendingUp,
  Award,
  Building2,
  Cpu,
  Lock,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { NavTab } from '../components/Sidebar';
import { apiClient } from '../api/client';

interface DashboardPageProps {
  onNavigate: (tab: NavTab) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [hospitals, setHospitals] = useState<any[]>([]);
  const [latestExp, setLatestExp] = useState<any>(null);
  const [trainingStatus, setTrainingStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [hospData, statusData, expList] = await Promise.all([
        apiClient.getHospitals().catch(() => []),
        apiClient.getTrainingStatus().catch(() => null),
        apiClient.getExperiments().catch(() => [])
      ]);

      setHospitals(hospData);
      setTrainingStatus(statusData);

      if (expList && expList.length > 0) {
        setLatestExp(expList[0]);
      } else if (statusData?.latest_result) {
        setLatestExp(statusData.latest_result);
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const activityClasses = [
    { name: 'Lying', label: 'Lying Down', desc: 'Resting supine state', icon: '🛌' },
    { name: 'Sitting', label: 'Sitting', desc: 'Sedentary state', icon: '🪑' },
    { name: 'Self Pace walk', label: 'Walking', desc: 'Light aerobic locomotion', icon: '🚶' },
    { name: 'Running 3 METs', label: 'Running 3 METs', desc: 'Light jogging pace', icon: '🏃' },
    { name: 'Running 5 METs', label: 'Running 5 METs', desc: 'Moderate endurance run', icon: '🏃‍♂️' },
    { name: 'Running 7 METs', label: 'Running 7 METs', desc: 'Vigorous interval running', icon: '⚡' }
  ];

  // Chart data from real round history if available
  const roundHistory = latestExp?.round_history || [];
  const chartData = roundHistory.map((rh: any) => ({
    round: `Round ${rh.round}`,
    accuracy: rh.eval_metrics?.accuracy_percent ?? (rh.eval_metrics?.accuracy ? roundDec(rh.eval_metrics.accuracy * 100, 1) : null)
  })).filter((d: any) => d.accuracy !== null);

  function roundDec(val: number, d = 1) {
    return Number(val.toFixed(d));
  }

  const latestAccuracy = latestExp?.metrics?.accuracy_percent ?? (latestExp?.metrics?.accuracy ? (latestExp.metrics.accuracy * 100).toFixed(1) + '%' : null);
  const completedRounds = latestExp?.rounds_completed ?? (trainingStatus?.current_round ? `${trainingStatus.current_round} of ${trainingStatus.total_rounds || 8}` : null);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      {/* Top Project Introduction Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1.5 max-w-3xl">
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 bg-blue-50 border border-blue-200 rounded-full text-blue-700 text-xs font-semibold uppercase tracking-wider">
            <Shield className="w-3.5 h-3.5" />
            <span>HealthFL SecAgg Framework</span>
          </div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Privacy-Preserving Federated Healthcare Activity Recognition
          </h1>
          <p className="text-sm text-slate-600 leading-relaxed">
            Collaborative machine learning across 3 simulated hospital nodes using wearable biometric sensor data.
            Raw patient records remain on local hospital nodes while model updates are secured using FedProx,
            Differential Privacy, and Paillier Homomorphic Encryption.
          </p>
        </div>
        <div className="flex flex-wrap gap-2.5">
          <button
            onClick={() => onNavigate('training')}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition cursor-pointer"
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>Model Training</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => onNavigate('testing')}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-medium shadow-sm transition cursor-pointer"
          >
            <Activity className="w-3.5 h-3.5 text-blue-600" />
            <span>Activity Testing</span>
          </button>
        </div>
      </div>

      {/* 4 Concise Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Participating Hospitals */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Participating Hospitals</span>
            <Building2 className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {hospitals.length || 3} <span className="text-sm font-normal text-slate-500">Nodes</span>
          </div>
          <div className="text-xs text-slate-500 mt-1 flex items-center space-x-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block"></span>
            <span>All demonstration nodes online</span>
          </div>
        </div>

        {/* Card 2: Latest Global Accuracy */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Latest Global Test Accuracy</span>
            <Award className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {latestAccuracy !== null ? latestAccuracy : <span className="text-base font-normal text-slate-400">Not run yet</span>}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            {latestExp ? `Evaluated on 1,253 held-out test records` : 'Run training to compute metric'}
          </div>
        </div>

        {/* Card 3: Completed Training Rounds */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Training Rounds</span>
            <Cpu className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {completedRounds ? completedRounds : '8 Rounds'}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            {trainingStatus?.status === 'Training' ? 'Training in progress...' : 'Standard 8-round protocol'}
          </div>
        </div>

        {/* Card 4: Security Configuration */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Security Configuration</span>
            <Lock className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-base font-bold text-slate-900 truncate">
            Paillier PHE + DP
          </div>
          <div className="text-xs text-slate-500 mt-1">
            C=8.0, σ=0.01, 512-bit key
          </div>
        </div>
      </div>

      {/* Main Section: 3 Hospital Nodes + Convergence Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Hospital Nodes */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
              <Building2 className="w-4 h-4 text-blue-600" />
              <span>Simulated Hospital Demonstration Nodes</span>
            </h2>
            <button
              onClick={() => onNavigate('network')}
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 inline-flex items-center space-x-1 cursor-pointer"
            >
              <span>View Network Details</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {hospitals.map((h, idx) => (
              <div key={h.id || idx} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                    Node 0{idx + 1}
                  </span>
                  <span className="inline-flex items-center space-x-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Online</span>
                  </span>
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">{h.name}</h3>
                  <p className="text-xs text-slate-500 mt-0.5">{h.region || 'Simulated Hospital Silo'}</p>
                </div>
                <div className="pt-2 border-t border-slate-100 space-y-1.5 text-xs">
                  <div className="flex justify-between text-slate-600">
                    <span>Local Data:</span>
                    <span className="font-semibold text-slate-900">{h.dataset_records?.toLocaleString() || '1,670'} records</span>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span>Training Status:</span>
                    <span className="text-slate-700 font-medium">{h.local_training_status || 'Idle / Ready'}</span>
                  </div>
                  {h.latest_local_accuracy && (
                    <div className="flex justify-between text-slate-600">
                      <span>Local Train Acc:</span>
                      <span className="font-semibold text-slate-900">{h.latest_local_accuracy}%</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Validation Performance Across Rounds */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Global Validation Performance Across Rounds</h3>
                <p className="text-xs text-slate-500">Evaluation on held-out test data after each communication round</p>
              </div>
              {chartData.length > 0 && (
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-md">
                  {chartData.length} Rounds Evaluated
                </span>
              )}
            </div>

            {chartData.length > 0 ? (
              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="round" tick={{ fontSize: 11, fill: '#64748b' }} />
                    <YAxis domain={[30, 85]} tick={{ fontSize: 11, fill: '#64748b' }} unit="%" />
                    <Tooltip
                      formatter={(val: any) => [`${val}%`, 'Validation Accuracy']}
                      contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', fontSize: '12px' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="accuracy"
                      stroke="#2563eb"
                      strokeWidth={2.5}
                      dot={{ r: 4, fill: '#2563eb' }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-44 flex flex-col items-center justify-center border border-dashed border-slate-200 rounded-lg bg-slate-50/50 text-center px-4">
                <AlertCircle className="w-6 h-6 text-slate-400 mb-1" />
                <p className="text-xs font-medium text-slate-600">No completed experiment yet</p>
                <p className="text-[11px] text-slate-400 max-w-sm mt-0.5">
                  Click 'Model Training' in the sidebar or banner above to start an 8-round federated training run.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Right 1 Col: 6 Target Physical Activity Classes */}
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
            <Activity className="w-4 h-4 text-blue-600" />
            <span>6 Supported Activity Classes</span>
          </h2>

          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-2.5">
            <p className="text-xs text-slate-500 mb-3">
              Target physical activities recognized from Harvard Apple Watch wearable accelerometer and telemetry sensors:
            </p>
            {activityClasses.map((ac, idx) => (
              <div key={idx} className="flex items-center space-x-3 p-2.5 rounded-lg border border-slate-100 bg-slate-50/60 hover:bg-slate-50 transition">
                <span className="text-lg">{ac.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-900 truncate">{ac.label}</span>
                    <span className="text-[10px] font-mono text-slate-400">Class {idx}</span>
                  </div>
                  <p className="text-[11px] text-slate-500 truncate">{ac.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
