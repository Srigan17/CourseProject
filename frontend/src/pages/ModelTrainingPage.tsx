import React, { useState, useEffect, useRef } from 'react';
import {
  Play,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Building2,
  Cpu,
  Shield,
  Lock,
  Clock,
  ArrowRight,
  TrendingUp,
  Award
} from 'lucide-react';
import { apiClient } from '../api/client';

interface ModelTrainingPageProps {
  onNavigateToResults: () => void;
}

export const ModelTrainingPage: React.FC<ModelTrainingPageProps> = ({ onNavigateToResults }) => {
  // Configuration settings
  const [numClients, setNumClients] = useState<number>(3);
  const [numRounds, setNumRounds] = useState<number>(8);
  const [localEpochs, setLocalEpochs] = useState<number>(12);
  const [learningRate, setLearningRate] = useState<number>(0.01);
  const [muProx, setMuProx] = useState<number>(0.005);
  const [useDP, setUseDP] = useState<boolean>(true);
  const [useSecAgg, setUseSecAgg] = useState<boolean>(true);

  // Live status polled from backend
  const [status, setStatus] = useState<any>({
    is_training: false,
    status: 'Idle',
    current_round: 0,
    total_rounds: 8,
    progress_percent: 0.0,
    current_hospital: 'None',
    current_epoch: 0,
    total_epochs: 12,
    hospitals: [],
    aggregation_status: 'Idle',
    global_model_status: 'Idle',
    current_metrics: {},
    current_experiment_id: null,
    latest_result: null,
    error: null,
    logs: [],
    elapsed_time_sec: 0.0
  });

  const [isStarting, setIsStarting] = useState<boolean>(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let isMounted = true;

    const pollStatus = async () => {
      try {
        const data = await apiClient.getTrainingStatus();
        if (isMounted) {
          setStatus(data);
          setActionError(null);
        }
      } catch (err: any) {
        // quiet fallback
      }
    };

    pollStatus();
    const interval = setInterval(pollStatus, status.is_training ? 1000 : 2500);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [status.is_training]);

  // Autoscroll logs
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [status.logs]);

  const handleStartTraining = async () => {
    if (status.is_training || isStarting) return;
    setIsStarting(true);
    setActionError(null);

    let expType = 'FL_SECAGG_DP';
    if (!useDP && !useSecAgg) expType = 'FEDPROX';
    else if (useDP && !useSecAgg) expType = 'FL_DP';
    else if (!useDP && useSecAgg) expType = 'FL_SECAGG';

    try {
      await apiClient.startTraining({
        dataset_id: 'apple_watch',
        experiment_type: expType,
        model_architecture: 'mlp',
        num_clients: numClients,
        num_rounds: numRounds,
        local_epochs: localEpochs,
        learning_rate: learningRate,
        batch_size: 32,
        mu_prox: muProx,
        dp_enabled: useDP,
        dp_clipping_norm: 8.0,
        dp_noise_multiplier: 0.01,
        secagg_enabled: useSecAgg,
        partition_strategy: 'non_iid',
        scaler_type: 'power',
        apply_smote: false
      });
      // Immediately refresh status
      const updated = await apiClient.getTrainingStatus();
      setStatus(updated);
    } catch (err: any) {
      setActionError(err.message || 'Failed to start training');
    } finally {
      setIsStarting(false);
    }
  };

  const roundsArray = Array.from({ length: numRounds }, (_, i) => i + 1);
  const currentRound = status.current_round || 0;

  const currentValAcc = status.current_metrics?.accuracy_percent ??
    (status.current_metrics?.accuracy ? (status.current_metrics.accuracy * 100).toFixed(2) : null);
  const currentMacroF1 = status.current_metrics?.macro_f1_percent ??
    (status.current_metrics?.macro_f1 ? (status.current_metrics.macro_f1 * 100).toFixed(2) : null);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      {/* Header and Controls Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-1">
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 bg-blue-50 border border-blue-200 rounded-full text-blue-700 text-xs font-semibold uppercase tracking-wider">
              <Cpu className="w-3.5 h-3.5" />
              <span>Federated Orchestrator</span>
            </div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Federated Model Training
            </h1>
            <p className="text-sm text-slate-600 max-w-2xl">
              Execute distributed federated learning across 3 simulated hospital nodes with FedProx regularization,
              Differential Privacy noise injection, and Paillier Homomorphic Secure Aggregation.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleStartTraining}
              disabled={status.is_training || isStarting}
              className={`inline-flex items-center space-x-2 px-5 py-2.5 rounded-lg text-xs font-bold shadow-sm transition cursor-pointer ${
                status.is_training || isStarting
                  ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 text-white shadow-blue-500/20'
              }`}
            >
              <Play className="w-4 h-4 fill-current" />
              <span>{status.is_training ? 'Training in Progress...' : 'Start Federated Training'}</span>
            </button>

            {status.status === 'Completed' && (
              <button
                onClick={onNavigateToResults}
                className="inline-flex items-center space-x-1.5 px-4 py-2.5 bg-emerald-50 border border-emerald-300 hover:bg-emerald-100 text-emerald-800 rounded-lg text-xs font-semibold shadow-xs transition cursor-pointer"
              >
                <Award className="w-4 h-4 text-emerald-600" />
                <span>View Results</span>
                <ArrowRight className="w-3.5 h-3.5 text-emerald-600" />
              </button>
            )}
          </div>
        </div>

        {/* Configuration Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mt-6 pt-5 border-t border-slate-100 text-xs">
          <div>
            <label className="block font-medium text-slate-500 mb-1">Rounds</label>
            <span className="font-bold text-slate-900 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded block">
              {numRounds} Communication Rounds
            </span>
          </div>
          <div>
            <label className="block font-medium text-slate-500 mb-1">Local Epochs</label>
            <span className="font-bold text-slate-900 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded block">
              {localEpochs} Epochs / Round
            </span>
          </div>
          <div>
            <label className="block font-medium text-slate-500 mb-1">FedProx μ</label>
            <span className="font-bold text-slate-900 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded block">
              μ = {muProx} (Proximal)
            </span>
          </div>
          <div>
            <label className="block font-medium text-slate-500 mb-1">Differential Privacy</label>
            <label className="flex items-center space-x-2 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded cursor-pointer">
              <input
                type="checkbox"
                checked={useDP}
                onChange={(e) => setUseDP(e.target.checked)}
                disabled={status.is_training}
                className="rounded text-blue-600"
              />
              <span className="font-semibold text-slate-800">C=8.0, σ=0.01</span>
            </label>
          </div>
          <div>
            <label className="block font-medium text-slate-500 mb-1">Secure Aggregation</label>
            <label className="flex items-center space-x-2 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded cursor-pointer">
              <input
                type="checkbox"
                checked={useSecAgg}
                onChange={(e) => setUseSecAgg(e.target.checked)}
                disabled={status.is_training}
                className="rounded text-blue-600"
              />
              <span className="font-semibold text-slate-800">Paillier 512-bit</span>
            </label>
          </div>
          <div>
            <label className="block font-medium text-slate-500 mb-1">Model Architecture</label>
            <span className="font-bold text-slate-900 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded block">
              MLP (19→128→64→6)
            </span>
          </div>
        </div>

        {actionError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
            <span>{actionError}</span>
          </div>
        )}
      </div>

      {/* Visual Round-Progress Tracker */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
              Communication Round Progression
            </h2>
            {status.current_experiment_id && (
              <span className="text-xs font-mono text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                Exp #{status.current_experiment_id}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-3 text-xs text-slate-500">
            <span>
              Status:{' '}
              <strong className={status.is_training ? 'text-blue-600' : status.status === 'Completed' ? 'text-emerald-600' : 'text-slate-700'}>
                {status.status}
              </strong>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <Clock className="w-3.5 h-3.5" />
              <span>Elapsed: {status.elapsed_time_sec || 0}s</span>
            </span>
          </div>
        </div>

        {/* Round step circles */}
        <div className="grid grid-cols-4 sm:grid-cols-8 gap-2 pt-2">
          {roundsArray.map((r) => {
            const isCompleted = r < currentRound || (r === currentRound && status.status === 'Completed');
            const isCurrent = r === currentRound && status.is_training;

            return (
              <div
                key={r}
                className={`flex flex-col items-center justify-center p-2.5 rounded-lg border text-center transition ${
                  isCurrent
                    ? 'border-blue-500 bg-blue-50 text-blue-900 shadow-sm ring-2 ring-blue-500/20'
                    : isCompleted
                    ? 'border-emerald-200 bg-emerald-50/60 text-emerald-800'
                    : 'border-slate-200 bg-slate-50 text-slate-400'
                }`}
              >
                <div className="flex items-center space-x-1 text-xs font-bold">
                  {isCompleted ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  ) : isCurrent ? (
                    <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping"></span>
                  ) : null}
                  <span>Round {r}</span>
                </div>
                <span className="text-[10px] mt-0.5">
                  {isCurrent ? 'Processing' : isCompleted ? 'Complete' : 'Pending'}
                </span>
              </div>
            );
          })}
        </div>

        {/* Overall progress bar */}
        <div className="space-y-1.5 pt-1">
          <div className="flex justify-between text-xs text-slate-500 font-medium">
            <span>Overall Training Progress</span>
            <span>{status.progress_percent}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(100, Math.max(0, status.progress_percent))}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Live Hospital Status Cards + Global Performance Card */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* 3 Hospital Cards */}
        {status.hospitals?.map((h: any, idx: number) => {
          const isTraining = h.status === 'Training';
          const isComplete = h.status === 'Completed';

          return (
            <div key={h.id || idx} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase">Hospital Node {idx + 1}</span>
                <span
                  className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                    isTraining
                      ? 'bg-blue-50 text-blue-700 animate-pulse'
                      : isComplete
                      ? 'bg-emerald-50 text-emerald-700'
                      : 'bg-slate-100 text-slate-500'
                  }`}
                >
                  {h.status || 'Ready'}
                </span>
              </div>

              <div>
                <h3 className="text-sm font-bold text-slate-900">{h.name}</h3>
                <p className="text-[11px] text-slate-500">1,670 local sensor records</p>
              </div>

              <div className="pt-2 border-t border-slate-100 space-y-1 text-xs">
                <div className="flex justify-between text-slate-600">
                  <span>Local Loss:</span>
                  <span className="font-mono text-slate-900">{h.local_loss ?? '—'}</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Training Accuracy:</span>
                  <span className="font-semibold text-slate-900">
                    {h.local_accuracy !== null && h.local_accuracy !== undefined ? `${h.local_accuracy}%` : '—'}
                  </span>
                </div>
              </div>
            </div>
          );
        })}

        {/* Global Validation Metrics Card */}
        <div className="bg-white border-2 border-blue-600/30 rounded-xl p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-blue-700 uppercase">Global Model</span>
            <span className="text-[11px] font-semibold px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full">
              Coordinator
            </span>
          </div>

          <div>
            <h3 className="text-sm font-bold text-slate-900">Global Validation Metrics</h3>
            <p className="text-[11px] text-slate-500">Evaluated on held-out test data (N=1,253)</p>
          </div>

          <div className="pt-2 border-t border-slate-100 space-y-1.5 text-xs">
            <div className="flex justify-between items-center">
              <span className="text-slate-600">Test Accuracy:</span>
              <span className="text-sm font-bold text-blue-600">
                {currentValAcc ? `${currentValAcc}%` : '—'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-600">Macro-F1 Score:</span>
              <span className="font-semibold text-slate-900">
                {currentMacroF1 ? `${currentMacroF1}%` : '—'}
              </span>
            </div>
            <div className="flex justify-between items-center text-[11px] text-slate-500 pt-1">
              <span>Aggregation:</span>
              <span className="font-medium text-slate-700 truncate max-w-[120px]">
                {status.aggregation_status || 'Waiting'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Compact Real-Time Training Logs */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
            <TrendingUp className="w-3.5 h-3.5 text-blue-600" />
            <span>Event & Training Activity Log</span>
          </h2>
          <span className="text-[11px] text-slate-400 font-mono">
            {status.logs?.length || 0} events recorded
          </span>
        </div>

        <div className="bg-slate-900 text-slate-200 font-mono text-xs rounded-lg p-3.5 h-52 overflow-y-auto space-y-1.5 select-text">
          {status.logs && status.logs.length > 0 ? (
            status.logs.map((log: string, idx: number) => (
              <div key={idx} className="flex items-start space-x-2 leading-relaxed">
                <span className="text-slate-500 text-[10px] shrink-0 select-none">
                  [{String(idx + 1).padStart(2, '0')}]
                </span>
                <span className={log.includes('accuracy') || log.includes('complete') ? 'text-blue-300' : log.includes('Error') ? 'text-red-400' : 'text-slate-300'}>
                  {log}
                </span>
              </div>
            ))
          ) : (
            <div className="text-slate-500 text-center py-16">
              Platform initialized. Training logs will stream here live.
            </div>
          )}
          <div ref={logsEndRef} />
        </div>
      </div>
    </div>
  );
};

export default ModelTrainingPage;
