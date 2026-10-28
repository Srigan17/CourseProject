import React, { useState, useEffect } from 'react';
import {
  Play,
  Network,
  Shield,
  Layers,
  Terminal,
  Clock,
  Cpu,
  CheckCircle2,
  AlertCircle,
  Activity,
  ArrowRight
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { DatasetInfo, TrainingRequest, TrainingStatus, ExperimentResult } from '../types';
import { apiClient } from '../api/client';

interface FederatedLearningPageProps {
  datasets: DatasetInfo[];
  selectedDatasetId: string;
  onSelectDataset: (id: string) => void;
  trainingStatus: TrainingStatus;
  onRefreshStatus: () => void;
  onNavigateToExperiments: () => void;
}

export const FederatedLearningPage: React.FC<FederatedLearningPageProps> = ({
  datasets,
  selectedDatasetId,
  onSelectDataset,
  trainingStatus,
  onRefreshStatus,
  onNavigateToExperiments
}) => {
  const [experimentType, setExperimentType] = useState('FL_SECAGG_DP');
  const [modelArchitecture, setModelArchitecture] = useState('mlp');
  const [numClients, setNumClients] = useState(3);
  const [numRounds, setNumRounds] = useState(5);
  const [localEpochs, setLocalEpochs] = useState(5);
  const [learningRate, setLearningRate] = useState(0.01);
  const [batchSize, setBatchSize] = useState(32);
  const [partitionStrategy, setPartitionStrategy] = useState('non_iid');
  const [applySmote, setApplySmote] = useState(false);
  const [dpClippingNorm, setDpClippingNorm] = useState(5.0);
  const [dpNoiseMultiplier, setDpNoiseMultiplier] = useState(0.02);

  const selectedDataset = datasets.find((d) => d.id === selectedDatasetId) || datasets[0];

  const handleStartTraining = async () => {
    try {
      const isSingleRound = experimentType === 'CENTRALIZED' || experimentType.startsWith('PAPER_');
      const req: TrainingRequest = {
        dataset_id: selectedDatasetId,
        experiment_type: experimentType,
        model_architecture: experimentType.startsWith('PAPER_') ? 'tree_ensemble' : modelArchitecture,
        num_clients: numClients,
        num_rounds: isSingleRound ? 1 : numRounds,
        local_epochs: localEpochs,
        learning_rate: learningRate,
        batch_size: batchSize,
        partition_strategy: partitionStrategy,
        apply_smote: applySmote,
        dp_clipping_norm: dpClippingNorm,
        dp_noise_multiplier: dpNoiseMultiplier
      };
      await apiClient.startTraining(req);
      onRefreshStatus();
    } catch (err: any) {
      alert(`Failed to start training: ${err.message}`);
    }
  };

  // Prepare chart data from latest experiment round history
  const roundData =
    trainingStatus.latest_result?.round_history?.map((r) => {
      const evalM = r.eval_metrics || {};
      return {
        round: `Round ${r.round}`,
        accuracy: evalM.accuracy ? parseFloat((evalM.accuracy * 100).toFixed(2)) : undefined,
        rmse: evalM.rmse ? parseFloat(evalM.rmse.toFixed(2)) : undefined,
        f1: evalM.f1_score ? parseFloat((evalM.f1_score * 100).toFixed(2)) : undefined,
        secagg_time: r.secagg_time_sec || 0
      };
    }) || [];

  return (
    <div className="space-y-6">
      {/* Top Controls Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Configuration Form (2 cols) */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Federated Experiment Setup</h3>
              <p className="text-xs text-slate-500">Configure parameters for simulated healthcare organizations</p>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 bg-slate-100 text-slate-700 rounded-md font-semibold">
              Mode: {experimentType}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            {/* Dataset Selector */}
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Target Healthcare Dataset</label>
              <select
                value={selectedDatasetId}
                onChange={(e) => onSelectDataset(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 font-medium text-slate-800"
              >
                {datasets.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} ({d.task.toUpperCase()})
                  </option>
                ))}
              </select>
            </div>

            {/* Experiment Mode */}
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Experiment Mode</label>
              <select
                value={experimentType}
                onChange={(e) => setExperimentType(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 font-medium text-slate-800"
              >
                <option value="FL_SECAGG_DP">5. Federated Learning + DP + Secure Aggregation (Proposed)</option>
                <option value="FL_SECAGG">4. Federated Learning + Secure Aggregation (Paillier HE)</option>
                <option value="FL_DP">3. Federated Learning + Differential Privacy (Gaussian)</option>
                <option value="STANDARD_FL">2. Standard Federated Learning (FedAvg Baseline)</option>
                <option value="CENTRALIZED">1. Centralized Learning Baseline</option>
                <option value="PAPER_EXTRA_TREES_FL">6. Paper Baseline: Federated Extra Trees Ensemble (FedEnsemble ~87%)</option>
                <option value="PAPER_EXTRA_TREES_CL">7. Paper Baseline: Centralized Extra Trees (~85-87%)</option>
              </select>
            </div>

            {/* Model Architecture */}
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Model Architecture</label>
              <select
                value={modelArchitecture}
                onChange={(e) => setModelArchitecture(e.target.value)}
                disabled={experimentType.startsWith('PAPER_')}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 font-medium text-slate-800 disabled:opacity-50"
              >
                <option value="mlp">Multi-Layer Perceptron (Neural continuous - DP & Paillier compatible)</option>
                <option value="tree_ensemble">Extra Trees Ensemble (Paper FedEnsemble rule trees)</option>
                <option value="logistic">Softmax Regression / Linear</option>
              </select>
            </div>

            {/* Rounds */}
            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Federation Training Rounds: <span className="font-mono text-sky-600">{numRounds}</span>
              </label>
              <input
                type="range"
                min={1}
                max={15}
                value={numRounds}
                onChange={(e) => setNumRounds(parseInt(e.target.value))}
                className="w-full accent-sky-600"
                disabled={experimentType === 'CENTRALIZED'}
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                <span>1 round</span>
                <span>5 (default)</span>
                <span>15 rounds</span>
              </div>
            </div>

            {/* Local Epochs */}
            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Local Client Epochs: <span className="font-mono text-sky-600">{localEpochs}</span>
              </label>
              <input
                type="range"
                min={1}
                max={5}
                value={localEpochs}
                onChange={(e) => setLocalEpochs(parseInt(e.target.value))}
                className="w-full accent-sky-600"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                <span>1 epoch</span>
                <span>2 (default)</span>
                <span>5 epochs</span>
              </div>
            </div>

            {/* Clients */}
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Participating Hospital Clients</label>
              <select
                value={numClients}
                onChange={(e) => setNumClients(parseInt(e.target.value))}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 font-medium text-slate-800"
                disabled={experimentType === 'CENTRALIZED'}
              >
                <option value={2}>2 Clients (k = 2)</option>
                <option value={3}>3 Clients (Hospitals A, B, C - Default)</option>
                <option value={4}>4 Clients (k = 4)</option>
                <option value={8}>8 Clients (k = 8)</option>
              </select>
            </div>

            {/* Partition Strategy */}
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Data Partitioning Strategy</label>
              <select
                value={partitionStrategy}
                onChange={(e) => setPartitionStrategy(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 font-medium text-slate-800"
              >
                <option value="non_iid">Non-IID (Skewed Patient Population)</option>
                <option value="iid">IID (Uniform Random Partition)</option>
              </select>
            </div>
          </div>

          {/* Privacy Parameters (when DP is active) */}
          {(experimentType.includes('DP') || experimentType === 'FL_SECAGG_DP') && (
            <div className="p-4 bg-sky-50/60 rounded-xl border border-sky-200">
              <div className="flex items-center space-x-2 mb-2">
                <Shield className="w-4 h-4 text-sky-600" />
                <span className="text-xs font-bold text-sky-900 uppercase">Differential Privacy Hyperparameters</span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <label className="text-slate-600 block mb-1 font-medium">
                    L2 Clipping Bound (C): <span className="font-mono text-sky-700">{dpClippingNorm}</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    max="10.0"
                    value={dpClippingNorm}
                    onChange={(e) => setDpClippingNorm(parseFloat(e.target.value))}
                    className="w-full bg-white border border-slate-300 rounded-lg p-2 text-xs"
                  />
                </div>
                <div>
                  <label className="text-slate-600 block mb-1 font-medium">
                    Noise Multiplier (σ): <span className="font-mono text-sky-700">{dpNoiseMultiplier}</span>
                  </label>
                  <input
                    type="number"
                    step="0.05"
                    min="0.05"
                    max="2.0"
                    value={dpNoiseMultiplier}
                    onChange={(e) => setDpNoiseMultiplier(parseFloat(e.target.value))}
                    className="w-full bg-white border border-slate-300 rounded-lg p-2 text-xs"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Start Action Button */}
          <div className="pt-2">
            <button
              onClick={handleStartTraining}
              disabled={trainingStatus.is_training}
              className={`w-full py-3 rounded-xl font-bold text-sm flex items-center justify-center space-x-2 shadow-md transition-all ${
                trainingStatus.is_training
                  ? 'bg-amber-500 text-white cursor-not-allowed animate-pulse'
                  : 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-600/30'
              }`}
            >
              <Play className="w-4 h-4 fill-current" />
              <span>
                {trainingStatus.is_training
                  ? `Training in Progress (Round ${trainingStatus.current_round} of ${trainingStatus.total_rounds})...`
                  : 'Start Real Federated Training'}
              </span>
            </button>
          </div>
        </div>

        {/* Right: Hospital Node Simulation Panels (1 col) */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <h3 className="text-base font-bold text-slate-900">Federation Clients</h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold">
                Local Silos Intact
              </span>
            </div>

            <div className="space-y-3">
              {Array.from({ length: numClients }).map((_, i) => {
                const cname = `Hospital ${String.fromCharCode(65 + i)}`;
                const cid = `hospital_${String.fromCharCode(97 + i)}`;
                return (
                  <div
                    key={cid}
                    className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center font-bold">
                        H{String.fromCharCode(65 + i)}
                      </div>
                      <div>
                        <div className="font-bold text-slate-900">{cname}</div>
                        <div className="text-[10px] text-slate-500 font-mono">ID: {cid}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-200 text-slate-700">
                        {trainingStatus.is_training ? 'Training...' : 'Ready'}
                      </span>
                      <div className="text-[10px] text-emerald-600 mt-1 font-mono">Zero raw egress</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-4 p-3 bg-slate-50 rounded-xl border border-slate-200 text-[11px] text-slate-600">
            <strong>Security Boundary:</strong> Each hospital holds its own partition. Gradients are computed on-premises
            and sent as Paillier ciphertexts.
          </div>
        </div>
      </div>

      {/* Progress & Live Terminal Output */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Metric Progression Chart */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-slate-900">Model Metric Convergence Over Rounds</h3>
            <span className="text-xs text-slate-400 font-mono">Held-Out Test Set (20%)</span>
          </div>

          {roundData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={roundData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="round" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  {selectedDataset.task === 'classification' ? (
                    <>
                      <Line type="monotone" dataKey="accuracy" stroke="#0284c7" strokeWidth={2} name="Accuracy (%)" />
                      <Line type="monotone" dataKey="f1" stroke="#8b5cf6" strokeWidth={2} name="F1-Score (%)" />
                    </>
                  ) : (
                    <Line type="monotone" dataKey="rmse" stroke="#10b981" strokeWidth={2} name="RMSE (Calories)" />
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-400 border border-dashed border-slate-200 rounded-xl">
              <Activity className="w-8 h-8 mb-2 opacity-50" />
              <p className="text-xs">Execute a federated experiment above to display convergence curves</p>
            </div>
          )}
        </div>

        {/* Live Training Execution Console */}
        <div className="bg-slate-900 text-slate-100 p-5 rounded-2xl border border-slate-800 shadow-sm flex flex-col justify-between font-mono text-xs">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
              <div className="flex items-center space-x-2 text-slate-400">
                <Terminal className="w-4 h-4 text-sky-400" />
                <span className="font-semibold text-white">Federation Execution Logs</span>
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded ${trainingStatus.is_training ? 'bg-amber-900 text-amber-200 animate-pulse' : 'bg-slate-800 text-slate-400'}`}>
                {trainingStatus.is_training ? 'ACTIVE' : 'IDLE'}
              </span>
            </div>

            <div className="space-y-1.5 overflow-y-auto max-h-56 pr-2">
              {trainingStatus.latest_logs.length > 0 ? (
                trainingStatus.latest_logs.map((log, idx) => (
                  <div key={idx} className="leading-relaxed">
                    <span className="text-slate-500">[{new Date().toLocaleTimeString()}]</span>{' '}
                    <span className={log.includes('Error') ? 'text-rose-400' : log.includes('completed') ? 'text-emerald-400' : 'text-slate-300'}>
                      {log}
                    </span>
                  </div>
                ))
              ) : (
                <div className="text-slate-500 italic">No execution logs yet. Configure settings and click Start.</div>
              )}
            </div>
          </div>

          {trainingStatus.latest_result && (
            <div className="pt-3 border-t border-slate-800 mt-3 flex items-center justify-between text-[11px]">
              <span className="text-emerald-400">
                Experiment #{trainingStatus.latest_result.id} Completed
              </span>
              <button
                onClick={onNavigateToExperiments}
                className="text-sky-400 hover:text-sky-300 underline flex items-center space-x-1"
              >
                <span>Compare in Experiments Table</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
