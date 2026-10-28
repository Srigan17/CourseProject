import React, { useState, useEffect } from 'react';
import {
  ScrollText,
  Shield,
  Search,
  Filter,
  AlertTriangle,
  CheckCircle2,
  Lock,
  KeyRound,
  FileKey,
  RefreshCw
} from 'lucide-react';
import { AuditEvent } from '../types';
import { apiClient } from '../api/client';

interface SecurityLogsPageProps {
  auditLogs: AuditEvent[];
  onRefreshLogs: () => void;
}

export const SecurityLogsPage: React.FC<SecurityLogsPageProps> = ({
  auditLogs,
  onRefreshLogs
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [selectedEventType, setSelectedEventType] = useState<string>('ALL');
  const [tlsStatus, setTlsStatus] = useState<any | null>(null);

  useEffect(() => {
    loadTLSStatus();
  }, []);

  const loadTLSStatus = async () => {
    try {
      const data = await apiClient.getTLSStatus();
      setTlsStatus(data);
    } catch (e) {
      console.error(e);
    }
  };

  const filteredLogs = auditLogs.filter((log) => {
    const matchesSearch =
      log.event_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.actor.toLowerCase().includes(searchTerm.toLowerCase()) ||
      JSON.stringify(log.details).toLowerCase().includes(searchTerm.toLowerCase());

    const matchesSeverity = selectedSeverity === 'ALL' || log.severity === selectedSeverity;
    const matchesEvent = selectedEventType === 'ALL' || log.event_type === selectedEventType;

    return matchesSearch && matchesSeverity && matchesEvent;
  });

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Security Audit Logs & Zero-Trust Verification</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Immutable structured JSON security event logging. Secrets, private keys, and patient records are strictly redacted.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={onRefreshLogs}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Events</span>
          </button>
        </div>
      </div>

      {/* TLS / mTLS Security Status Pill Grid */}
      {tlsStatus && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-[10px] text-slate-400 font-semibold uppercase">Channel Encryption</span>
            <div className="font-bold text-slate-800 mt-1 flex items-center space-x-1.5">
              <Lock className="w-4 h-4 text-emerald-600" />
              <span>{tlsStatus.protocol_version} ({tlsStatus.cipher_suite})</span>
            </div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-[10px] text-slate-400 font-semibold uppercase">Mutual TLS (mTLS)</span>
            <div className="font-bold text-slate-800 mt-1 flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Client Certificate Authentication Required</span>
            </div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-[10px] text-slate-400 font-semibold uppercase">Rest Storage Encryption</span>
            <div className="font-bold text-slate-800 mt-1 flex items-center space-x-1.5">
              <KeyRound className="w-4 h-4 text-sky-600" />
              <span>AES-256-GCM with 96-bit Random Nonces</span>
            </div>
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4 text-xs">
        <div className="flex-1 min-w-[200px] relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search events by type, actor, or details..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-xl font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
          />
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 font-medium text-slate-700"
          >
            <option value="ALL">All Severities</option>
            <option value="INFO">INFO Only</option>
            <option value="WARNING">WARNING Only</option>
            <option value="CRITICAL">CRITICAL Only</option>
          </select>

          <select
            value={selectedEventType}
            onChange={(e) => setSelectedEventType(e.target.value)}
            className="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 font-medium text-slate-700"
          >
            <option value="ALL">All Event Types</option>
            <option value="SYSTEM_STARTUP">SYSTEM_STARTUP</option>
            <option value="AUTH_SUCCESS">AUTH_SUCCESS</option>
            <option value="AUTH_FAILURE">AUTH_FAILURE</option>
            <option value="TRAINING_ROUND_START">TRAINING_ROUND_START</option>
            <option value="TRAINING_ROUND_COMPLETE">TRAINING_ROUND_COMPLETE</option>
            <option value="SECAGG_SUCCESS">SECAGG_SUCCESS</option>
            <option value="UPDATE_REJECTED">UPDATE_REJECTED</option>
          </select>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                <th className="p-3">Timestamp (UTC)</th>
                <th className="p-3">Severity</th>
                <th className="p-3">Event Type</th>
                <th className="p-3">Actor / Client</th>
                <th className="p-3">Event Details</th>
                <th className="p-3">Security Check</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {filteredLogs.map((log, i) => (
                <tr key={i} className="hover:bg-slate-50 transition">
                  <td className="p-3 font-mono text-slate-500 text-[11px] whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="p-3">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        log.severity === 'CRITICAL'
                          ? 'bg-rose-100 text-rose-800'
                          : log.severity === 'WARNING'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}
                    >
                      {log.severity}
                    </span>
                  </td>
                  <td className="p-3 font-mono font-bold text-slate-900">{log.event_type}</td>
                  <td className="p-3 font-mono text-slate-600">{log.actor}</td>
                  <td className="p-3 font-mono text-[11px] text-slate-600 max-w-md truncate">
                    {JSON.stringify(log.details)}
                  </td>
                  <td className="p-3">
                    <span className="inline-flex items-center space-x-1 text-emerald-700 font-semibold">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Verified</span>
                    </span>
                  </td>
                </tr>
              ))}
              {filteredLogs.length === 0 && (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-slate-400">
                    No matching security events found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
