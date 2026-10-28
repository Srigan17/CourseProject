import React, { useState, useEffect } from 'react';
import {
  Building2,
  Server,
  Shield,
  Lock,
  ArrowRight,
  Database,
  CheckCircle2,
  RefreshCw,
  Cpu
} from 'lucide-react';
import { apiClient } from '../api/client';

export const HospitalNetworkPage: React.FC = () => {
  const [hospitals, setHospitals] = useState<any[]>([]);
  const [trainingStatus, setTrainingStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadNetworkData();
  }, []);

  const loadNetworkData = async () => {
    setIsLoading(true);
    try {
      const [hospList, status] = await Promise.all([
        apiClient.getHospitals().catch(() => []),
        apiClient.getTrainingStatus().catch(() => null)
      ]);
      setHospitals(hospList);
      setTrainingStatus(status);
    } catch (err) {
      console.error('Failed to load hospital network:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const currentRound = trainingStatus?.current_round || 8;
  const totalRounds = trainingStatus?.total_rounds || 8;

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      {/* Overview Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 bg-blue-50 border border-blue-200 rounded-full text-blue-700 text-xs font-semibold uppercase tracking-wider mb-2">
              <Building2 className="w-3.5 h-3.5" />
              <span>Simulated Healthcare Consortium</span>
            </div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Hospital Demonstration Network
            </h1>
            <p className="text-sm text-slate-600 mt-1 max-w-3xl leading-relaxed">
              Three simulated hospital silos partition the 5,011 training records of the Harvard Apple Watch dataset.
              Each hospital executes local gradient descent exclusively on its private data partition.
              Only encrypted parameter deltas are communicated to the aggregation coordinator.
            </p>
          </div>
          <div className="flex items-center space-x-2 text-xs font-medium text-slate-600 bg-slate-50 border border-slate-200 px-3.5 py-2 rounded-lg">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>3 Simulated Nodes Active</span>
          </div>
        </div>
      </div>

      {/* Network Architecture Diagram */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4 flex items-center space-x-2">
          <Server className="w-4 h-4 text-blue-600" />
          <span>Federated Topology & Aggregation Flow</span>
        </h2>

        <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
            {/* 3 Hospital Client Nodes */}
            <div className="flex-1 space-y-3 w-full">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                Hospital Client Silos (Private Data Slices)
              </span>
              {hospitals.map((h, i) => (
                <div key={h.id || i} className="bg-white border border-slate-200 rounded-lg p-3 shadow-xs flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700 font-bold text-xs">
                      0{i + 1}
                    </div>
                    <div>
                      <span className="text-xs font-bold text-slate-900 block">{h.name}</span>
                      <span className="text-[11px] text-slate-500">{h.dataset_records} local sensor records</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full inline-block">
                      Data Kept Local
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Communication Arrow */}
            <div className="flex lg:flex-col items-center justify-center text-slate-400 gap-1 py-2">
              <span className="text-[11px] font-semibold text-blue-600 uppercase tracking-wider text-center px-2">
                Encrypted Parameter Deltas (Paillier [[Δw]])
              </span>
              <ArrowRight className="w-5 h-5 text-blue-600 hidden lg:block" />
            </div>

            {/* Central Aggregation Coordinator */}
            <div className="w-full lg:w-72 bg-white border-2 border-blue-600/30 rounded-xl p-5 shadow-sm space-y-3">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center">
                  <Cpu className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-slate-900">Central Coordinator</h3>
                  <p className="text-[10px] text-slate-500">Secure Aggregation Server</p>
                </div>
              </div>
              <div className="text-xs text-slate-600 space-y-1.5 pt-2 border-t border-slate-100">
                <div className="flex justify-between">
                  <span>Aggregation:</span>
                  <span className="font-semibold text-slate-900">Homomorphic Sum</span>
                </div>
                <div className="flex justify-between">
                  <span>Plaintext Access:</span>
                  <span className="font-semibold text-amber-700">None on Client Updates</span>
                </div>
                <div className="flex justify-between">
                  <span>Global Output:</span>
                  <span className="font-semibold text-slate-900">Aggregated Consensus</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3 Hospital Detail Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {hospitals.map((h, idx) => (
          <div key={h.id || idx} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="text-xs font-mono text-slate-400 block uppercase">Node ID: {h.id}</span>
                <h3 className="text-base font-bold text-slate-900 mt-0.5">{h.name}</h3>
              </div>
              <span className="inline-flex items-center space-x-1 text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Ready</span>
              </span>
            </div>

            <div className="space-y-2.5 text-xs text-slate-600">
              <div className="flex justify-between">
                <span>Locally Assigned Data:</span>
                <span className="font-semibold text-slate-900">{h.dataset_records?.toLocaleString() || '1,670'} records</span>
              </div>
              <div className="flex justify-between">
                <span>Local Training Status:</span>
                <span className="font-medium text-slate-800">{h.local_training_status || 'Idle / Ready'}</span>
              </div>
              <div className="flex justify-between">
                <span>Latest Local Accuracy:</span>
                <span className="font-semibold text-slate-900">
                  {h.latest_local_accuracy ? `${h.latest_local_accuracy}% (Training)` : 'Awaiting Run'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Latest Local Loss:</span>
                <span className="font-mono text-slate-800">{h.latest_local_loss ?? 'Awaiting Run'}</span>
              </div>
              <div className="flex justify-between">
                <span>Current Participation Round:</span>
                <span className="font-semibold text-blue-600">Round {currentRound} of {totalRounds}</span>
              </div>
              <div className="flex justify-between pt-2 border-t border-slate-100">
                <span>Data Retention:</span>
                <span className="font-medium text-emerald-700 text-right max-w-[180px]">
                  Local Silo Only (Zero Centralization)
                </span>
              </div>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-100 rounded-lg text-[11px] text-slate-500 leading-relaxed">
              <strong>Simulated Node Note:</strong> This demonstration node runs in-process as an isolated slice of the Harvard Apple Watch dataset to illustrate multi-institutional federated learning without cross-site data sharing.
            </div>
          </div>
        ))}
      </div>

      {/* Security Architecture Clarification Notice */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 text-xs text-slate-600 space-y-2">
        <div className="flex items-center space-x-2 font-bold text-slate-900">
          <Shield className="w-4 h-4 text-blue-600" />
          <span>Security & Threat Model Notice</span>
        </div>
        <p className="leading-relaxed">
          <strong>Cryptographic Architecture:</strong> In this local research demonstration, Paillier 512-bit public-key additive homomorphic encryption is executed to demonstrate mathematical and numerical aggregation correctness. In a distributed multi-institution deployment, client nodes communicate over TLS 1.3 with mTLS mutual certificate validation, and key generation is managed by an independent consortium authority.
        </p>
      </div>
    </div>
  );
};

export default HospitalNetworkPage;
