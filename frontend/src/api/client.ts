import {
  DatasetInfo,
  TrainingRequest,
  TrainingStatus,
  ExperimentResult,
  AuditEvent,
  FHIRBundleResponse,
  SystemStatus
} from '../types';

const API_BASE = '/api';

export const apiClient = {
  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error('Failed to fetch system status');
    return res.json();
  },

  async getDatasets(): Promise<DatasetInfo[]> {
    const res = await fetch(`${API_BASE}/datasets/`);
    if (!res.ok) throw new Error('Failed to fetch datasets');
    return res.json();
  },

  async getDatasetPreview(datasetId: string, limit = 10): Promise<any> {
    const res = await fetch(`${API_BASE}/datasets/${datasetId}/preview?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch preview');
    return res.json();
  },

  async preprocessDataset(datasetId: string, params: { num_clients: number; partition_strategy: string; apply_smote: boolean }): Promise<any> {
    const query = new URLSearchParams({
      num_clients: params.num_clients.toString(),
      partition_strategy: params.partition_strategy,
      apply_smote: params.apply_smote ? 'true' : 'false'
    });
    const res = await fetch(`${API_BASE}/datasets/${datasetId}/preprocess?${query}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to preprocess dataset');
    return res.json();
  },

  async startTraining(req: TrainingRequest): Promise<any> {
    const res = await fetch(`${API_BASE}/fl/train`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to start training');
    }
    return res.json();
  },

  async getTrainingStatus(): Promise<TrainingStatus> {
    const res = await fetch(`${API_BASE}/fl/status`);
    if (!res.ok) throw new Error('Failed to fetch training status');
    return res.json();
  },

  async getPrivacyStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/privacy/status`);
    if (!res.ok) throw new Error('Failed to fetch privacy status');
    return res.json();
  },

  async calculateDPBudget(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/privacy/dp/calculate-budget`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to calculate DP budget');
    return res.json();
  },

  async testSecAggVerification(numClients = 3, paramCount = 20): Promise<any> {
    const res = await fetch(`${API_BASE}/privacy/secagg/test-verification?num_clients=${numClients}&param_count=${paramCount}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to run SecAgg cryptographic test');
    return res.json();
  },

  async getFHIRStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/fhir/status`);
    if (!res.ok) throw new Error('Failed to fetch FHIR status');
    return res.json();
  },

  async getFHIRMappings(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/fhir/mappings`);
    if (!res.ok) throw new Error('Failed to fetch FHIR mappings');
    return res.json();
  },

  async generateFHIR(datasetId: string, recordIndex = 0): Promise<FHIRBundleResponse> {
    const res = await fetch(`${API_BASE}/fhir/generate/${datasetId}?record_index=${recordIndex}`);
    if (!res.ok) throw new Error('Failed to generate FHIR resources');
    return res.json();
  },

  async validateFHIR(resource: any): Promise<any> {
    const res = await fetch(`${API_BASE}/fhir/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(resource)
    });
    if (!res.ok) throw new Error('Failed to validate FHIR resource');
    return res.json();
  },

  async getExperiments(): Promise<ExperimentResult[]> {
    const res = await fetch(`${API_BASE}/experiments/`);
    if (!res.ok) throw new Error('Failed to fetch experiments');
    return res.json();
  },

  async getExperiment(expId: string): Promise<ExperimentResult> {
    const res = await fetch(`${API_BASE}/experiments/${expId}`);
    if (!res.ok) throw new Error('Failed to fetch experiment');
    return res.json();
  },

  async deleteExperiment(expId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/experiments/${expId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete experiment');
    return res.json();
  },

  async getAuditLogs(params?: { event_type?: string; severity?: string; client_id?: string; limit?: number }): Promise<AuditEvent[]> {
    const query = new URLSearchParams();
    if (params?.event_type) query.append('event_type', params.event_type);
    if (params?.severity) query.append('severity', params.severity);
    if (params?.client_id) query.append('client_id', params.client_id);
    if (params?.limit) query.append('limit', params.limit.toString());
    const res = await fetch(`${API_BASE}/security/audit-logs?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },

  async testAESGCM(payload: { plaintext: string; associated_data: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/security/crypto/aes-gcm/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to run AES-GCM test');
    return res.json();
  },

  async testAnomalyDetection(): Promise<any> {
    const res = await fetch(`${API_BASE}/security/validation/test-anomaly-detection`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to run anomaly test');
    return res.json();
  },

  async getTLSStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/security/tls-status`);
    if (!res.ok) throw new Error('Failed to fetch TLS status');
    return res.json();
  },

  async predictActivity(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/fl/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to execute activity prediction');
    }
    return res.json();
  },

  async predictActivityCSV(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/fl/predict/csv`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to execute CSV batch prediction');
    }
    return res.json();
  },

  async getPredictionMetadata(): Promise<any> {
    const res = await fetch(`${API_BASE}/fl/predict/metadata`);
    if (!res.ok) throw new Error('Failed to fetch prediction metadata');
    return res.json();
  },

  async getBenchmarkResults(): Promise<any> {
    const res = await fetch(`${API_BASE}/fl/benchmark-results`);
    if (!res.ok) throw new Error('Failed to fetch benchmark results');
    return res.json();
  },

  async getSecAggComparativeConfigurations(): Promise<any> {
    const res = await fetch(`${API_BASE}/fl/secagg-comparative-configurations`);
    if (!res.ok) throw new Error('Failed to fetch SecAgg configurations');
    return res.json();
  },

  async getSecAggBandwidth(): Promise<any> {
    const res = await fetch(`${API_BASE}/fl/secagg-bandwidth`);
    if (!res.ok) throw new Error('Failed to fetch SecAgg bandwidth');
    return res.json();
  },

  async runSecAggCryptoBenchmark(): Promise<any> {
    const res = await fetch(`${API_BASE}/fl/secagg-crypto-benchmark`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to run SecAgg cryptographic benchmark');
    return res.json();
  },

  async getSamplePatients(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/fl/sample-patients`);
    if (!res.ok) throw new Error('Failed to fetch sample patients');
    return res.json();
  },

  async getHospitals(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/fl/hospitals`);
    if (!res.ok) throw new Error('Failed to fetch hospitals');
    return res.json();
  },

  async syncHospital(id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/fl/hospitals/${id}/sync`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to sync hospital');
    return res.json();
  },

  async toggleHospital(id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/fl/hospitals/${id}/toggle`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to toggle hospital');
    return res.json();
  }
};
