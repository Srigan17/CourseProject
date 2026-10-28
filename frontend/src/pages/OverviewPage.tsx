import React from 'react';
import {
  Shield,
  Database,
  Network,
  Cpu,
  CheckCircle2,
  Lock,
  ArrowRight,
  TrendingUp,
  Activity,
  Layers,
  AlertTriangle,
  Play
} from 'lucide-react';
import { DatasetInfo, ExperimentResult, AuditEvent, SystemStatus } from '../types';

interface OverviewPageProps {
  systemStatus: SystemStatus | null;
  datasets: DatasetInfo[];
  experiments: ExperimentResult[];
  auditLogs: AuditEvent[];
  isTraining: boolean;
  onNavigate: (tab: any) => void;
  onQuickRun: () => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  systemStatus,
  datasets,
  experiments,
  auditLogs,
  isTraining,
  onNavigate,
  onQuickRun
}) => {
  const availableDatasets = datasets.filter((d) => d.is_available);
  const totalRecords = availableDatasets.reduce((acc, d) => acc + (d.num_records || 0), 0);
  const latestExp = experiments[0];

  return (
    <div className="space-y-6">
      {/* Quick Launch Banner */}
      <div className="bg-gradient-to-r from-sky-900 via-indigo-900 to-slate-900 text-white rounded-2xl p-6 shadow-md border border-sky-800/40 relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-1/3 opacity-10 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:16px_16px]"></div>
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-sky-500/20 text-sky-300 border border-sky-400/30 text-xs font-semibold uppercase tracking-wider mb-3">
            <span>Research Prototype • PeerJ cs-11-2870</span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-white mb-2">
            Privacy-Preserving Federated Healthcare Intelligence
          </h2>
          <p className="text-slate-300 text-sm leading-relaxed mb-5">
            Collaborative federated machine learning across simulated hospital organizations. Raw biometric and EHR data
            remains isolated in local hospital repositories standardized via HL7 FHIR R4, while model parameter updates are
            protected using (ε, δ)-Differential Privacy and Paillier Cryptographic Secure Aggregation.
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={onQuickRun}
              disabled={isTraining}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all shadow-md ${
                isTraining
                  ? 'bg-amber-600 text-white cursor-not-allowed'
                  : 'bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold shadow-sky-500/30'
              }`}
            >
              <Play className="w-4 h-4 fill-current" />
              <span>{isTraining ? 'Training Run Active...' : 'Launch 5-Round Privacy-Preserving FL'}</span>
            </button>
            <button
              onClick={() => onNavigate('experiments')}
              className="px-4 py-2.5 rounded-xl font-medium text-sm bg-slate-800/80 hover:bg-slate-700/80 text-white border border-slate-700 transition"
            >
              View Benchmark Results ({experiments.length})
            </button>
            <button
              onClick={() => onNavigate('fhir')}
              className="px-4 py-2.5 rounded-xl font-medium text-sm bg-slate-800/80 hover:bg-slate-700/80 text-white border border-slate-700 transition"
            >
              Inspect FHIR R4 Mappings
            </button>
          </div>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1 */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Real Datasets Loaded</span>
            <div className="p-2 rounded-lg bg-sky-50 text-sky-600">
              <Database className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-slate-900">{availableDatasets.length} / 4</span>
            <span className="text-xs text-emerald-600 font-medium">100% Real Wearable Data</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">{totalRecords.toLocaleString()} genuine records available</p>
        </div>

        {/* Card 2 */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Federation Clients</span>
            <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
              <Network className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-slate-900">3 Hospitals</span>
            <span className="text-xs text-emerald-600 font-medium">Non-IID Partitioned</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Hospitals A, B, C with local data retention</p>
        </div>

        {/* Card 3 */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Privacy & SecAgg</span>
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
              <Shield className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-slate-900">Paillier + DP</span>
            <span className="text-xs text-emerald-600 font-medium">Zero-Leakage</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Homomorphic addition + L2 clipped noise</p>
        </div>

        {/* Card 4 */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Latest Benchmark Result</span>
            <div className="p-2 rounded-lg bg-amber-50 text-amber-600">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            {latestExp ? (
              <>
                <span className="text-2xl font-bold text-slate-900">
                  {latestExp.task === 'classification'
                    ? `${(latestExp.metrics.accuracy! * 100).toFixed(1)}%`
                    : `${latestExp.metrics.rmse!.toFixed(2)} RMSE`}
                </span>
                <span className="text-xs text-slate-500 font-medium truncate max-w-[100px]">
                  {latestExp.dataset_id}
                </span>
              </>
            ) : (
              <span className="text-base text-slate-400">Ready to train</span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {latestExp ? `${latestExp.experiment_mode}` : 'Click launch above to execute first test'}
          </p>
        </div>
      </div>

      {/* Interactive System Architecture Diagram */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-base font-bold text-slate-900">End-to-End System Architecture</h3>
            <p className="text-xs text-slate-500">Live data flow and cryptographic boundary enforcement</p>
          </div>
          <span className="px-3 py-1 bg-sky-50 text-sky-700 border border-sky-200 rounded-full text-xs font-medium">
            Interactive Architecture
          </span>
        </div>

        {/* Visual Workflow Steps */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
          {/* Step 1 */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <div className="w-6 h-6 rounded-full bg-sky-600 text-white flex items-center justify-center text-xs font-bold">1</div>
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wide">Data Sources</span>
              </div>
              <h4 className="text-sm font-semibold text-slate-900 mb-1">Wearable Sensor Streams</h4>
              <p className="text-xs text-slate-500 leading-relaxed mb-3">
                Apple Watch, Fitbit, HARTH accelerometers & Mi Band continuous vitals (heart rate, steps, calories).
              </p>
            </div>
            <div className="pt-2 border-t border-slate-200 text-[11px] text-sky-700 font-mono">
              Local Hospital Storage Only
            </div>
          </div>

          {/* Step 2 */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <div className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold">2</div>
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wide">FHIR Layer</span>
              </div>
              <h4 className="text-sm font-semibold text-slate-900 mb-1">HL7 FHIR R4 Translation</h4>
              <p className="text-xs text-slate-500 leading-relaxed mb-3">
                Data Service Agent converts proprietary formats to standard Patient, Device, and Observation resources.
              </p>
            </div>
            <div className="pt-2 border-t border-slate-200 text-[11px] text-indigo-700 font-mono">
              LOINC 8867-4, 55423-8, 41981-2
            </div>
          </div>

          {/* Step 3 */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <div className="w-6 h-6 rounded-full bg-purple-600 text-white flex items-center justify-center text-xs font-bold">3</div>
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wide">Privacy Layer</span>
              </div>
              <h4 className="text-sm font-semibold text-slate-900 mb-1">DP + Paillier Encryption</h4>
              <p className="text-xs text-slate-500 leading-relaxed mb-3">
                Local weight updates are L2-clipped, perturbed with Gaussian noise, and encrypted with public key.
              </p>
            </div>
            <div className="pt-2 border-t border-slate-200 text-[11px] text-purple-700 font-mono">
              Zero Plaintext Exposure
            </div>
          </div>

          {/* Step 4 */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <div className="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold">4</div>
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wide">Global Model</span>
              </div>
              <h4 className="text-sm font-semibold text-slate-900 mb-1">Homomorphic Aggregation</h4>
              <p className="text-xs text-slate-500 leading-relaxed mb-3">
                Coordinator sums ciphertexts directly: E(w1) * E(w2). Result is decrypted and distributed to clients.
              </p>
            </div>
            <div className="pt-2 border-t border-slate-200 text-[11px] text-emerald-700 font-mono">
              Rounds 1 to T Completed
            </div>
          </div>
        </div>

        {/* Security Guarantee Banner */}
        <div className="mt-5 p-3.5 bg-emerald-50/60 rounded-xl border border-emerald-200 flex items-center justify-between text-xs text-emerald-900">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>
              <strong>Cryptographic Guarantee Verified:</strong> The central server never observes raw patient health
              records or individual plaintext model updates. Only homomorphically combined weights are decrypted.
            </span>
          </div>
          <button
            onClick={() => onNavigate('privacy')}
            className="text-emerald-700 font-semibold hover:underline flex items-center space-x-1"
          >
            <span>Verify SecAgg Proof</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Two Column Layout: Dataset Quick Peek & Recent Security Audit Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Dataset Quick Summary */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-slate-900">Configured Healthcare Datasets</h3>
            <button
              onClick={() => onNavigate('datasets')}
              className="text-xs text-sky-600 hover:text-sky-700 font-semibold flex items-center space-x-1"
            >
              <span>Manage Datasets</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="space-y-3">
            {datasets.map((d) => (
              <div
                key={d.id}
                className="p-3.5 rounded-xl border border-slate-100 hover:border-slate-200 bg-slate-50/50 flex items-center justify-between transition"
              >
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-semibold text-slate-900">{d.name}</span>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                      d.task === 'classification' ? 'bg-purple-100 text-purple-700' : 'bg-emerald-100 text-emerald-700'
                    }`}>
                      {d.task}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{d.target_description}</p>
                </div>
                <div className="text-right">
                  <span className="text-xs font-mono font-medium text-slate-700">
                    {d.num_records ? `${d.num_records.toLocaleString()} rows` : d.status}
                  </span>
                  <div className="text-[10px] text-emerald-600 font-medium">Ready</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Security & Audit Events */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-slate-900">Recent Security Audit Events</h3>
            <button
              onClick={() => onNavigate('security')}
              className="text-xs text-sky-600 hover:text-sky-700 font-semibold flex items-center space-x-1"
            >
              <span>View All Logs</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="space-y-2.5">
            {auditLogs.slice(0, 5).map((log, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl border border-slate-100 bg-slate-50/50 flex items-center justify-between text-xs"
              >
                <div className="flex items-center space-x-3">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      log.severity === 'CRITICAL'
                        ? 'bg-red-500'
                        : log.severity === 'WARNING'
                        ? 'bg-amber-500'
                        : 'bg-emerald-500'
                    }`}
                  ></span>
                  <div>
                    <span className="font-semibold text-slate-800 font-mono">{log.event_type}</span>
                    <span className="text-slate-400 ml-2">by {log.actor}</span>
                  </div>
                </div>
                <span className="text-slate-400 font-mono text-[11px]">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
            {auditLogs.length === 0 && (
              <div className="p-4 text-center text-xs text-slate-400">No audit events recorded yet.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
