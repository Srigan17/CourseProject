import React from 'react';
import { Cpu, CheckCircle2, Layers, HardDrive, Shield, Activity, ArrowRight } from 'lucide-react';
import { ExperimentResult } from '../types';

interface GlobalModelPageProps {
  latestResult: ExperimentResult | null;
  onNavigateToFL: () => void;
}

export const GlobalModelPage: React.FC<GlobalModelPageProps> = ({
  latestResult,
  onNavigateToFL
}) => {
  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Global Aggregated Model State</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Consolidated global parameters updated via homomorphic secure aggregation across hospital clients
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-xs font-semibold">
            {latestResult ? 'Active Checkpoint Available' : 'No Model Checkpoint Yet'}
          </span>
        </div>
      </div>

      {latestResult ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Metadata & Architecture (1 col) */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h4 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-3 flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-sky-600" />
              <span>Model Architecture & Checkpoint</span>
            </h4>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-slate-400 text-[10px] uppercase font-semibold">Algorithm</span>
                <div className="font-bold text-slate-800 mt-0.5">
                  {latestResult.task === 'classification'
                    ? 'Softmax Multi-Class Neural Linear Layer'
                    : 'Ridge Continuous Gradient Regressor'}
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-slate-400 text-[10px] uppercase font-semibold">Source Dataset</span>
                <div className="font-bold text-slate-800 mt-0.5">{latestResult.dataset_id}</div>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-slate-400 text-[10px] uppercase font-semibold">Total Completed Rounds</span>
                <div className="font-bold text-slate-800 mt-0.5">{latestResult.rounds_completed || latestResult.epochs}</div>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-slate-400 text-[10px] uppercase font-semibold">Privacy Protection Level</span>
                <div className="font-bold text-emerald-700 mt-0.5">
                  {latestResult.differential_privacy_enabled && latestResult.secure_aggregation_enabled
                    ? 'Differential Privacy + Paillier SecAgg'
                    : latestResult.differential_privacy_enabled
                    ? 'Differential Privacy (Gaussian)'
                    : latestResult.secure_aggregation_enabled
                    ? 'Paillier Secure Aggregation'
                    : 'Standard FedAvg (No additional privacy)'}
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Performance & Validation on Genuine Test Split (2 cols) */}
          <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h4 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-3 flex items-center justify-between">
              <span className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-emerald-600" />
                <span>Held-Out Real Test Partition (20%) Evaluation Metrics</span>
              </span>
              <span className="text-xs font-mono text-slate-400">Experiment #{latestResult.id}</span>
            </h4>

            {/* Metrics cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
              {latestResult.task === 'classification' ? (
                <>
                  <div className="bg-sky-50 p-4 rounded-xl border border-sky-100">
                    <span className="text-[10px] uppercase font-semibold text-sky-700">Accuracy</span>
                    <p className="text-xl font-bold text-sky-900 mt-1">
                      {(latestResult.metrics.accuracy! * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-xl border border-purple-100">
                    <span className="text-[10px] uppercase font-semibold text-purple-700">F1-Score</span>
                    <p className="text-xl font-bold text-purple-900 mt-1">
                      {(latestResult.metrics.f1_score! * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-indigo-50 p-4 rounded-xl border border-indigo-100">
                    <span className="text-[10px] uppercase font-semibold text-indigo-700">Precision</span>
                    <p className="text-xl font-bold text-indigo-900 mt-1">
                      {(latestResult.metrics.precision! * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-emerald-50 p-4 rounded-xl border border-emerald-100">
                    <span className="text-[10px] uppercase font-semibold text-emerald-700">Recall</span>
                    <p className="text-xl font-bold text-emerald-900 mt-1">
                      {(latestResult.metrics.recall! * 100).toFixed(1)}%
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <div className="bg-emerald-50 p-4 rounded-xl border border-emerald-100">
                    <span className="text-[10px] uppercase font-semibold text-emerald-700">RMSE</span>
                    <p className="text-xl font-bold text-emerald-900 mt-1">
                      {latestResult.metrics.rmse?.toFixed(2)}
                    </p>
                  </div>
                  <div className="bg-sky-50 p-4 rounded-xl border border-sky-100">
                    <span className="text-[10px] uppercase font-semibold text-sky-700">MAE</span>
                    <p className="text-xl font-bold text-sky-900 mt-1">
                      {latestResult.metrics.mae?.toFixed(2)}
                    </p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-xl border border-purple-100">
                    <span className="text-[10px] uppercase font-semibold text-purple-700">R² Score</span>
                    <p className="text-xl font-bold text-purple-900 mt-1">
                      {latestResult.metrics.r2_score?.toFixed(3)}
                    </p>
                  </div>
                  <div className="bg-amber-50 p-4 rounded-xl border border-amber-100">
                    <span className="text-[10px] uppercase font-semibold text-amber-700">MAPE</span>
                    <p className="text-xl font-bold text-amber-900 mt-1">
                      {(latestResult.metrics.mape! * 100).toFixed(1)}%
                    </p>
                  </div>
                </>
              )}
            </div>

            {/* Confusion Matrix if classification */}
            {latestResult.metrics.confusion_matrix && (
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-xs font-bold text-slate-800 block mb-2">Confusion Matrix (Class Predictions)</span>
                <div className="overflow-x-auto">
                  <table className="text-center text-xs font-mono mx-auto">
                    <tbody>
                      {latestResult.metrics.confusion_matrix.map((row, rIdx) => (
                        <tr key={rIdx}>
                          {row.map((val, cIdx) => (
                            <td
                              key={cIdx}
                              className={`p-2 border border-slate-200 rounded ${
                                rIdx === cIdx ? 'bg-sky-100 font-bold text-sky-900' : 'bg-white text-slate-600'
                              }`}
                            >
                              {val}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center shadow-sm">
          <Cpu className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h4 className="text-base font-bold text-slate-800">No Global Model Checkpoint Available</h4>
          <p className="text-xs text-slate-500 max-w-md mx-auto mt-1 mb-5 leading-relaxed">
            Execute a training experiment in the Federated Learning tab to produce an aggregated global model checkpoint.
          </p>
          <button
            onClick={onNavigateToFL}
            className="px-5 py-2.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-bold shadow-md transition"
          >
            Train a Model Now →
          </button>
        </div>
      )}
    </div>
  );
};
