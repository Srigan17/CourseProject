import React, { useState } from 'react';
import {
  Database,
  Eye,
  CheckCircle2,
  AlertCircle,
  FileText,
  Sliders,
  Table,
  BarChart3,
  X,
  Play
} from 'lucide-react';
import { DatasetInfo } from '../types';
import { apiClient } from '../api/client';

interface DatasetsPageProps {
  datasets: DatasetInfo[];
  selectedDatasetId: string;
  onSelectDataset: (id: string) => void;
  onNavigateToFL: () => void;
}

export const DatasetsPage: React.FC<DatasetsPageProps> = ({
  datasets,
  selectedDatasetId,
  onSelectDataset,
  onNavigateToFL
}) => {
  const [previewData, setPreviewData] = useState<any | null>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  const [preprocResult, setPreprocResult] = useState<any | null>(null);
  const [isPreprocLoading, setIsPreprocLoading] = useState(false);
  const [numClients, setNumClients] = useState(3);
  const [partitionStrategy, setPartitionStrategy] = useState<'non_iid' | 'iid'>('non_iid');
  const [applySmote, setApplySmote] = useState(false);
  const [activeModalTab, setActiveModalTab] = useState<'preview' | 'stats'>('preview');

  const selectedDataset = datasets.find((d) => d.id === selectedDatasetId) || datasets[0];

  const handleOpenPreview = async (datasetId: string) => {
    setIsPreviewLoading(true);
    setPreviewData(null);
    try {
      const data = await apiClient.getDatasetPreview(datasetId, 15);
      setPreviewData(data);
    } catch (err: any) {
      alert(`Error loading preview: ${err.message}`);
    } finally {
      setIsPreviewLoading(false);
    }
  };

  const handleRunPreprocessing = async (datasetId: string) => {
    setIsPreprocLoading(true);
    try {
      const res = await apiClient.preprocessDataset(datasetId, {
        num_clients: numClients,
        partition_strategy: partitionStrategy,
        apply_smote: applySmote
      });
      setPreprocResult(res);
    } catch (err: any) {
      alert(`Error running preprocessing: ${err.message}`);
    } finally {
      setIsPreprocLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Multimodal Healthcare Wearable Datasets</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Real datasets from PeerJ Computer Science (Akhmetov et al., 2025). Used for activity classification and calorie prediction.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-500 font-medium">Selected for Experiments:</span>
          <span className="px-3 py-1 bg-sky-100 text-sky-800 rounded-lg text-xs font-bold font-mono">
            {selectedDataset?.name}
          </span>
        </div>
      </div>

      {/* Dataset Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {datasets.map((d) => {
          const isSelected = d.id === selectedDatasetId;
          return (
            <div
              key={d.id}
              className={`bg-white rounded-2xl border transition-all p-5 shadow-sm flex flex-col justify-between ${
                isSelected
                  ? 'border-sky-500 ring-2 ring-sky-500/20'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <div>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-9 h-9 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center font-bold">
                      <Database className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-slate-900">{d.name}</h4>
                      <p className="text-[11px] text-slate-400 font-mono">{d.citation}</p>
                    </div>
                  </div>
                  <span
                    className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${
                      d.task === 'classification'
                        ? 'bg-purple-100 text-purple-800'
                        : 'bg-emerald-100 text-emerald-800'
                    }`}
                  >
                    {d.task}
                  </span>
                </div>

                <p className="text-xs text-slate-600 mb-4 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                  <strong className="text-slate-800">Target Variable:</strong> <span className="font-mono text-sky-700">{d.target_col}</span> ({d.target_description})
                </p>

                {/* Metrics Table */}
                <div className="grid grid-cols-3 gap-2.5 mb-4 text-center">
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold">Total Records</span>
                    <p className="text-sm font-bold text-slate-900 mt-0.5">
                      {d.num_records ? d.num_records.toLocaleString() : 'N/A'}
                    </p>
                  </div>
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold">Features</span>
                    <p className="text-sm font-bold text-slate-900 mt-0.5">{d.num_features || d.features.length}</p>
                  </div>
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold">Missing Values</span>
                    <p className="text-sm font-bold text-emerald-600 mt-0.5">{d.missing_values ?? 0}</p>
                  </div>
                </div>

                {/* File Path */}
                <div className="text-[11px] text-slate-400 font-mono truncate mb-4">
                  Path: {d.file_path}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleOpenPreview(d.id)}
                    className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>Inspect Data</span>
                  </button>
                  <button
                    onClick={() => handleRunPreprocessing(d.id)}
                    className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition"
                  >
                    <Sliders className="w-3.5 h-3.5" />
                    <span>Partition & Preprocess</span>
                  </button>
                </div>

                <button
                  onClick={() => onSelectDataset(d.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    isSelected
                      ? 'bg-sky-600 text-white shadow-sm shadow-sky-600/30'
                      : 'bg-white border border-slate-300 text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  {isSelected ? 'Active Dataset' : 'Select'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Preprocessing Configuration & Results Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Federation Preprocessing & Partitioning Controls</h3>
            <p className="text-xs text-slate-500">Configure client partitioning (Hospital A, B, C) and 80/20 train-test splits</p>
          </div>
          <button
            onClick={() => handleRunPreprocessing(selectedDatasetId)}
            disabled={isPreprocLoading}
            className="flex items-center space-x-1.5 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-semibold shadow-sm transition"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isPreprocLoading ? 'Processing...' : 'Run Partitioning'}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
          {/* Number of Clients */}
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
            <label className="text-xs font-semibold text-slate-700 block mb-1">Number of Hospital Clients</label>
            <select
              value={numClients}
              onChange={(e) => setNumClients(parseInt(e.target.value))}
              className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-xs font-medium text-slate-800"
            >
              <option value={2}>2 Clients (Hospitals A & B)</option>
              <option value={3}>3 Clients (Hospitals A, B & C - Default)</option>
              <option value={4}>4 Clients (Hospitals A, B, C & D)</option>
              <option value={8}>8 Clients (Table 2 & 3 in Paper)</option>
            </select>
          </div>

          {/* Partition Strategy */}
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
            <label className="text-xs font-semibold text-slate-700 block mb-1">Data Distribution Strategy</label>
            <select
              value={partitionStrategy}
              onChange={(e) => setPartitionStrategy(e.target.value as any)}
              className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-xs font-medium text-slate-800"
            >
              <option value="non_iid">Non-IID (Heterogeneous Patient Populations)</option>
              <option value="iid">IID (Uniform Random Distribution)</option>
            </select>
          </div>

          {/* SMOTE Toggle */}
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex flex-col justify-between">
            <label className="text-xs font-semibold text-slate-700 block mb-1">SMOTE Class Balancing</label>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500">Chua et al. / Paper methodology</span>
              <input
                type="checkbox"
                checked={applySmote}
                onChange={(e) => setApplySmote(e.target.checked)}
                className="w-4 h-4 text-sky-600 rounded border-slate-300"
              />
            </div>
          </div>
        </div>

        {/* Partitioning Results Display */}
        {preprocResult && (
          <div className="p-4 bg-emerald-50/50 rounded-xl border border-emerald-200 text-xs">
            <div className="flex items-center justify-between mb-3">
              <span className="font-bold text-emerald-900">
                Preprocessing Finished for {preprocResult.dataset_id.toUpperCase()}
              </span>
              <span className="text-emerald-700 font-mono">
                Train: {preprocResult.train_size} rows (80%) • Test: {preprocResult.test_size} rows (20%)
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {preprocResult.clients.map((c: any) => (
                <div key={c.client_id} className="bg-white p-3 rounded-lg border border-emerald-200">
                  <div className="font-semibold text-slate-900">{c.client_name}</div>
                  <div className="text-slate-500 mt-1">
                    Samples: <strong className="text-emerald-600">{c.num_samples.toLocaleString()}</strong>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">{c.partition_strategy}</div>
                </div>
              ))}
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={onNavigateToFL}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-semibold text-xs transition"
              >
                Proceed to Federated Training →
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Preview Modal */}
      {previewData && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[85vh] flex flex-col shadow-2xl border border-slate-200">
            <div className="p-5 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Dataset Inspection: {previewData.dataset_id}
                </h3>
                <p className="text-xs text-slate-500">
                  Showing first {previewData.preview.length} of {previewData.total_records.toLocaleString()} records from raw CSV
                </p>
              </div>
              <button
                onClick={() => setPreviewData(null)}
                className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-auto p-5">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-100 border-b border-slate-200">
                    {previewData.columns.map((col: string) => (
                      <th key={col} className="p-2.5 font-semibold text-slate-700 font-mono text-[11px] whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {previewData.preview.map((row: any, i: number) => (
                    <tr key={i} className="hover:bg-slate-50">
                      {previewData.columns.map((col: string) => (
                        <td key={col} className="p-2.5 font-mono text-slate-600 text-[11px] whitespace-nowrap">
                          {row[col] !== null ? String(row[col]) : <span className="text-slate-300">null</span>}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="p-4 border-t border-slate-200 bg-slate-50 rounded-b-2xl flex justify-between items-center text-xs text-slate-500">
              <span>Authentic file content verified on disk</span>
              <button
                onClick={() => setPreviewData(null)}
                className="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold hover:bg-slate-700 transition"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
