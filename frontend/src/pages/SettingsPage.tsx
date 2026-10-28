import React from 'react';
import { Settings, Server, Shield, Database, CheckCircle2, HardDrive, KeyRound, Cpu } from 'lucide-react';
import { SystemStatus, DatasetInfo } from '../types';

interface SettingsPageProps {
  systemStatus: SystemStatus | null;
  datasets: DatasetInfo[];
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  systemStatus,
  datasets
}) => {
  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Platform Settings & Environment Health</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            System configuration, active security profiles, and persistent directory mappings
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-xs font-semibold">
            All Services Healthy
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Backend & Framework Status */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h4 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-3 flex items-center space-x-2">
            <Server className="w-4 h-4 text-sky-600" />
            <span>Core Framework & Services</span>
          </h4>

          <div className="space-y-2.5 text-xs">
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-500 font-medium">Research Project Title</span>
              <span className="font-semibold text-slate-900">{systemStatus?.project_name}</span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-500 font-medium">Backend Architecture</span>
              <span className="font-mono text-slate-900 font-bold">{systemStatus?.backend || 'FastAPI + Python'}</span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-500 font-medium">FHIR Interoperability Standard</span>
              <span className="font-semibold text-slate-900">{systemStatus?.fhir_interoperability}</span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-500 font-medium">Active Federated Engine</span>
              <span className="font-semibold text-slate-900">Custom FedAvg + Paillier Homomorphic Adapter</span>
            </div>
          </div>
        </div>

        {/* Cryptography & Security Profiles */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h4 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-3 flex items-center space-x-2">
            <Shield className="w-4 h-4 text-emerald-600" />
            <span>Active Cryptographic Profiles</span>
          </h4>

          <div className="space-y-2.5 text-xs">
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-500 font-medium">Homomorphic Secure Aggregation</span>
              <span className="font-semibold text-emerald-700">Paillier (Key size: 512-bit)</span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-500 font-medium">Differential Privacy Mechanism</span>
              <span className="font-semibold text-emerald-700">Gaussian with Advanced Composition</span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-500 font-medium">EHR Storage Encryption</span>
              <span className="font-semibold text-emerald-700">AES-256-GCM (Authenticated AEAD)</span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-500 font-medium">Client Authentication & RBAC</span>
              <span className="font-semibold text-emerald-700">JWT (HS256) + PBKDF2-SHA256</span>
            </div>
          </div>
        </div>
      </div>

      {/* Dataset Storage Paths */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h4 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-3 flex items-center space-x-2">
          <HardDrive className="w-4 h-4 text-indigo-600" />
          <span>Local Dataset Repositories</span>
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          {datasets.map((d) => (
            <div key={d.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <div className="flex justify-between items-center mb-1">
                <span className="font-bold text-slate-900">{d.name}</span>
                <span className="text-[10px] font-mono text-emerald-600 font-semibold">{d.status}</span>
              </div>
              <p className="font-mono text-[10px] text-slate-500 truncate">{d.file_path}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
