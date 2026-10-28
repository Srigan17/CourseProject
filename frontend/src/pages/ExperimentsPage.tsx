import React, { useState } from 'react';
import {
  FlaskConical,
  Download,
  Trash2,
  TrendingUp,
  BarChart3,
  Clock,
  HardDrive,
  Shield,
  Layers,
  ArrowRight,
  Play
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { ExperimentResult, DatasetInfo } from '../types';
import { apiClient } from '../api/client';

interface ExperimentsPageProps {
  experiments: ExperimentResult[];
  onRefreshExperiments: () => void;
  onNavigateToFL: () => void;
  datasets: DatasetInfo[];
}

export const ExperimentsPage: React.FC<ExperimentsPageProps> = ({
  experiments,
  onRefreshExperiments,
  onNavigateToFL,
  datasets
}) => {
  const [selectedExpId, setSelectedExpId] = useState<string | null>(
    experiments.length > 0 ? experiments[0].id || null : null
  );

  const selectedExp = experiments.find((e) => e.id === selectedExpId) || experiments[0];

  const handleDelete = async (id: string) => {
    if (!confirm(`Delete experiment #${id}?`)) return;
    try {
      await apiClient.deleteExperiment(id);
      onRefreshExperiments();
      if (selectedExpId === id) setSelectedExpId(null);
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleExportCSV = () => {
    window.open('/api/experiments/export/csv', '_blank');
  };

  // Prepare comparison bar chart data
  const chartData = experiments.map((exp) => {
    const isClf = exp.task === 'classification';
    return {
      name: `#${exp.id?.slice(0, 4)} (${exp.experiment_mode.replace('Federated Learning', 'FL').slice(0, 15)})`,
      accuracy: exp.metrics.accuracy ? parseFloat((exp.metrics.accuracy * 100).toFixed(1)) : undefined,
      f1: exp.metrics.f1_score ? parseFloat((exp.metrics.f1_score * 100).toFixed(1)) : undefined,
      rmse: exp.metrics.rmse ? parseFloat(exp.metrics.rmse.toFixed(1)) : undefined,
      comm_kb: exp.communication_cost_kb || 0,
      time_sec: exp.elapsed_time_sec || 0
    };
  });

  return (
    <div className="space-y-6">
      {/* Top Header & Actions */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Experimental Evaluation & Benchmarks</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Comparative performance across Centralized Learning, Standard FL, and Privacy-Enhanced FL modes
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleExportCSV}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={onNavigateToFL}
            className="flex items-center space-x-1.5 px-4 py-1.5 bg-sky-600 hover:bg-sky-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>New Experiment</span>
          </button>
        </div>
      </div>

      {experiments.length === 0 ? (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center shadow-sm">
          <FlaskConical className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h4 className="text-base font-bold text-slate-800">No Experiments Recorded Yet</h4>
          <p className="text-xs text-slate-500 max-w-md mx-auto mt-1 mb-5 leading-relaxed">
            Execute a centralized or federated learning training run with differential privacy and Paillier secure aggregation to populate real metrics.
          </p>
          <button
            onClick={onNavigateToFL}
            className="px-5 py-2.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-bold shadow-md transition"
          >
            Launch Your First Experiment →
          </button>
        </div>
      ) : (
        <>
          {/* Comparative Metrics Bar Chart */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <BarChart3 className="w-4 h-4 text-sky-600" />
                <span>Performance & Privacy Trade-off Across Completed Runs</span>
              </h4>
              <span className="text-xs text-slate-400 font-mono">Held-Out Test Set Evaluations</span>
            </div>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="accuracy" fill="#0284c7" name="Accuracy (%)" />
                  <Bar dataKey="f1" fill="#8b5cf6" name="F1-Score (%)" />
                  <Bar dataKey="time_sec" fill="#f59e0b" name="Duration (s)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Master Table of Experiments */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-slate-200 flex items-center justify-between">
              <h4 className="text-sm font-bold text-slate-900">Completed Experiment Records</h4>
              <span className="text-xs font-mono text-slate-500">{experiments.length} runs saved</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                    <th className="p-3">ID</th>
                    <th className="p-3">Mode</th>
                    <th className="p-3">Dataset</th>
                    <th className="p-3">Task</th>
                    <th className="p-3">Rounds</th>
                    <th className="p-3">DP Guaranteed</th>
                    <th className="p-3">SecAgg</th>
                    <th className="p-3">Accuracy / RMSE</th>
                    <th className="p-3">F1 / MAE</th>
                    <th className="p-3">Duration</th>
                    <th className="p-3">Comm.</th>
                    <th className="p-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {experiments.map((e) => {
                    const isSelected = e.id === selectedExpId;
                    const isClf = e.task === 'classification';
                    return (
                      <tr
                        key={e.id}
                        onClick={() => setSelectedExpId(e.id || null)}
                        className={`cursor-pointer transition ${
                          isSelected ? 'bg-sky-50/70 font-medium' : 'hover:bg-slate-50'
                        }`}
                      >
                        <td className="p-3 font-mono font-bold text-sky-700">#{e.id}</td>
                        <td className="p-3">
                          <span className="font-semibold text-slate-900">{e.experiment_mode}</span>
                        </td>
                        <td className="p-3 font-mono text-slate-600">{e.dataset_id}</td>
                        <td className="p-3">
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                            isClf ? 'bg-purple-100 text-purple-800' : 'bg-emerald-100 text-emerald-800'
                          }`}>
                            {e.task}
                          </span>
                        </td>
                        <td className="p-3 font-mono">{e.rounds_completed || e.epochs}</td>
                        <td className="p-3">
                          {e.differential_privacy_enabled ? (
                            <span className="text-emerald-700 font-bold font-mono">
                              Yes (ε={e.dp_budget?.epsilon ?? 'N/A'})
                            </span>
                          ) : (
                            <span className="text-slate-400">Disabled</span>
                          )}
                        </td>
                        <td className="p-3">
                          {e.secure_aggregation_enabled ? (
                            <span className="text-indigo-700 font-bold">Paillier HE</span>
                          ) : (
                            <span className="text-slate-400">Plaintext</span>
                          )}
                        </td>
                        <td className="p-3 font-bold font-mono text-slate-900">
                          {isClf ? `${(e.metrics.accuracy! * 100).toFixed(1)}%` : e.metrics.rmse?.toFixed(2)}
                        </td>
                        <td className="p-3 font-mono text-slate-600">
                          {isClf ? `${(e.metrics.f1_score! * 100).toFixed(1)}%` : e.metrics.mae?.toFixed(2)}
                        </td>
                        <td className="p-3 font-mono text-slate-600">{e.elapsed_time_sec}s</td>
                        <td className="p-3 font-mono text-slate-600">{e.communication_cost_kb} KB</td>
                        <td className="p-3 text-right">
                          <button
                            onClick={(evt) => {
                              evt.stopPropagation();
                              handleDelete(e.id!);
                            }}
                            className="p-1 text-slate-400 hover:text-rose-600 rounded transition"
                            title="Delete Record"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
