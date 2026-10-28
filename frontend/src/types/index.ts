export interface DatasetInfo {
  id: string;
  name: string;
  citation: string;
  task: 'classification' | 'regression';
  target_col: string;
  target_description: string;
  file_path: string;
  is_available: boolean;
  status: string;
  file_size_kb: number;
  features: string[];
  num_records?: number;
  num_features?: number;
  missing_values?: number;
  duplicate_rows?: number;
  columns?: string[];
  dtypes?: Record<string, string>;
  class_distribution?: Record<string, number>;
  target_stats?: {
    min: number;
    max: number;
    mean: number;
    std: number;
  };
}

export interface TrainingRequest {
  dataset_id: string;
  experiment_type: string;
  model_architecture?: string;
  num_clients: number;
  num_rounds: number;
  local_epochs: number;
  learning_rate: number;
  batch_size: number;
  mu_prox?: number;
  scaler_type?: string;
  partition_strategy: string;
  apply_smote: boolean;
  dp_enabled?: boolean;
  dp_clipping_norm: number;
  dp_noise_multiplier: number;
  secagg_enabled?: boolean;
}

export interface HospitalTrainingStatus {
  id: string;
  name: string;
  status: 'Waiting' | 'Training' | 'Completed';
  update_submitted: boolean;
  local_loss?: number | null;
  local_accuracy?: number | null;
}

export interface TrainingStatus {
  is_training: boolean;
  status?: 'Idle' | 'Starting' | 'Training' | 'Completed' | 'Failed';
  current_round: number;
  total_rounds: number;
  progress_percent?: number;
  current_hospital?: string;
  current_epoch?: number;
  total_epochs?: number;
  hospitals?: HospitalTrainingStatus[];
  aggregation_status?: string;
  global_model_status?: string;
  current_metrics?: {
    accuracy?: number;
    accuracy_percent?: number;
    macro_f1?: number;
    loss?: number;
    rmse?: number;
  };
  current_experiment_id: string | null;
  error: string | null;
  latest_logs: string[];
  latest_result: ExperimentResult | null;
  elapsed_time_sec?: number;
}

export interface ExperimentResult {
  id?: string;
  experiment_mode: string;
  task: string;
  dataset_id: string;
  train_samples?: number;
  test_samples?: number;
  num_clients?: number;
  rounds_completed?: number;
  epochs?: number;
  local_epochs?: number;
  differential_privacy_enabled: boolean;
  dp_budget?: {
    is_private: boolean;
    epsilon: number;
    delta: number;
    guarantee: string;
    mechanism: string;
  };
  secure_aggregation_enabled: boolean;
  secagg_protocol?: string;
  communication_cost_kb: number;
  elapsed_time_sec: number;
  metrics: {
    accuracy?: number;
    accuracy_percent?: number;
    precision?: number;
    recall?: number;
    f1_score?: number;
    macro_f1?: number;
    roc_auc?: number;
    mae?: number;
    mse?: number;
    rmse?: number;
    r2_score?: number;
    mape?: number;
    confusion_matrix?: number[][];
  };
  round_history?: Array<{
    round: number;
    elapsed_sec: number;
    secagg_time_sec?: number;
    eval_metrics: Record<string, number>;
    client_metrics: Array<{
      client_id: string;
      client_name: string;
      num_samples: number;
      local_loss: number;
    }>;
  }>;
  created_at?: string;
}

export interface AuditEvent {
  timestamp: string;
  event_type: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  actor: string;
  client_id?: string;
  round_num?: number;
  details: Record<string, any>;
  security_verified: boolean;
}

export interface FHIRBundleResponse {
  dataset_id: string;
  source_record: Record<string, any>;
  fhir_bundle: {
    patient: Record<string, any>;
    device: Record<string, any>;
    observations: Array<Record<string, any>>;
  };
  validation: {
    patient_valid: boolean;
    device_valid: boolean;
    observations_valid: boolean;
    errors: string[];
  };
}

export interface SystemStatus {
  project_name: string;
  version: string;
  backend: string;
  security_services: {
    jwt_auth: string;
    aes_gcm: string;
    tls_mtls: string;
    audit_logging: string;
    update_validator: string;
  };
  privacy_services: {
    differential_privacy: string;
    secure_aggregation: string;
  };
  fhir_interoperability: string;
  datasets: {
    total: number;
    available: number;
    items: Array<{ id: string; name: string; status: string }>;
  };
}
