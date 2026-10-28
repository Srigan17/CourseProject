import React, { useState, useEffect } from 'react';
import {
  Activity,
  User,
  Heart,
  Flame,
  Footprints,
  Compass,
  CheckCircle2,
  AlertCircle,
  Clock,
  Shield,
  Upload,
  FileText,
  BarChart2,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { apiClient } from '../api/client';

interface SamplePatient {
  id: string;
  name: string;
  expected_activity: string;
  values: {
    age: number;
    gender: string;
    height: number;
    weight: number;
    steps: number;
    heart_rate: number;
    calories: number;
    distance: number;
    resting_heart: number;
  };
}

export const PatientActivityTestingPage: React.FC = () => {
  const [activeMode, setActiveMode] = useState<'manual' | 'csv'>('manual');
  const [samples, setSamples] = useState<SamplePatient[]>([]);
  const [selectedSampleId, setSelectedSampleId] = useState<string>('');
  const [metadata, setMetadata] = useState<any>(null);

  // Form values
  const [inputs, setInputs] = useState({
    steps: 820,
    heart_rate: 88,
    calories: 12.5,
    distance: 0.8,
    resting_heart: 62,
    age: 24,
    gender: 'male',
    height: 172,
    weight: 68
  });

  // Advanced sensor features toggle
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [advancedInputs, setAdvancedInputs] = useState({
    entropy_heart: 4.0,
    entropy_setps: 3.5,
    corr_heart_steps: 0.5,
    norm_heart: 1.0,
    intensity_karvonen: 0.3,
    sd_norm_heart: 0.15
  });

  // CSV upload state
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [csvResult, setCsvResult] = useState<any>(null);
  const [isCsvLoading, setIsCsvLoading] = useState(false);

  // Prediction states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [predictionResult, setPredictionResult] = useState<any>(null);

  useEffect(() => {
    loadMetadataAndSamples();
  }, []);

  const loadMetadataAndSamples = async () => {
    try {
      const [meta, sampleList] = await Promise.all([
        apiClient.getPredictionMetadata().catch(() => null),
        apiClient.getSamplePatients().catch(() => [])
      ]);
      setMetadata(meta);
      setSamples(sampleList);

      if (sampleList && sampleList.length > 0) {
        // Default to Patient 3 (Walking)
        const def = sampleList.find((s: any) => s.id === 'sample-walk') || sampleList[0];
        handleSelectSample(def);
      }
    } catch (err) {
      console.error('Failed to load metadata/samples:', err);
    }
  };

  const handleSelectSample = (sample: SamplePatient) => {
    setSelectedSampleId(sample.id);
    setInputs({
      steps: sample.values.steps,
      heart_rate: sample.values.heart_rate,
      calories: sample.values.calories,
      distance: sample.values.distance,
      resting_heart: sample.values.resting_heart,
      age: sample.values.age,
      gender: sample.values.gender,
      height: sample.values.height,
      weight: sample.values.weight
    });
    if ((sample.values as any).entropy_heart !== undefined) {
      setAdvancedInputs({
        entropy_heart: (sample.values as any).entropy_heart,
        entropy_setps: (sample.values as any).entropy_setps ?? 6.1,
        corr_heart_steps: (sample.values as any).corr_heart_steps ?? 0.3,
        norm_heart: (sample.values as any).norm_heart ?? ((sample.values as any).heart_rate - (sample.values as any).resting_heart),
        intensity_karvonen: (sample.values as any).intensity_karvonen ?? 0.08,
        sd_norm_heart: (sample.values as any).sd_norm_heart ?? 5.5
      });
    }
    setError(null);
  };

  const handleInputChange = (field: string, val: any) => {
    setInputs((prev) => ({ ...prev, [field]: val }));
    setSelectedSampleId('');
  };

  const handlePredictManual = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const payload = {
        steps: Number(inputs.steps),
        heart_rate: Number(inputs.heart_rate),
        calories: Number(inputs.calories),
        distance: Number(inputs.distance),
        resting_heart: Number(inputs.resting_heart),
        age: Number(inputs.age),
        gender: inputs.gender,
        height: Number(inputs.height),
        weight: Number(inputs.weight),
        ...advancedInputs
      };

      const res = await apiClient.predictActivity(payload);
      setPredictionResult(res);
    } catch (err: any) {
      setError(err.message || 'Inference failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCsvUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setCsvFile(file);
    setIsCsvLoading(true);
    setError(null);

    try {
      const res = await apiClient.predictActivityCSV(file);
      setCsvResult(res);
    } catch (err: any) {
      setError(err.message || 'CSV prediction failed');
      setCsvResult(null);
    } finally {
      setIsCsvLoading(false);
    }
  };

  // Activity colors for bar chart
  const getActivityColor = (actName: string) => {
    if (actName.includes('Lying')) return '#64748b';
    if (actName.includes('Sitting')) return '#0284c7';
    if (actName.includes('walk')) return '#10b981';
    if (actName.includes('3 METs')) return '#f59e0b';
    if (actName.includes('5 METs')) return '#f97316';
    if (actName.includes('7 METs')) return '#ef4444';
    return '#3b82f6';
  };

  const chartData = predictionResult?.probabilities
    ? Object.entries(predictionResult.probabilities).map(([name, prob]: any) => ({
        name,
        probability: Number((prob * 100).toFixed(1))
      }))
    : [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      {/* Top Header Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 bg-blue-50 border border-blue-200 rounded-full text-blue-700 text-xs font-semibold uppercase tracking-wider mb-2">
              <Activity className="w-3.5 h-3.5" />
              <span>Inference Testing</span>
            </div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Wearable Activity Classification Testing
            </h1>
            <p className="text-sm text-slate-600 mt-1 max-w-3xl leading-relaxed">
              Test wearable biometric sensor inputs against the trained federated global model.
              Input physiological sensor measurements manually or upload a sensor CSV file.
            </p>
          </div>

          {/* Mode Switcher */}
          <div className="flex p-1 bg-slate-100 rounded-lg border border-slate-200 text-xs font-medium">
            <button
              onClick={() => setActiveMode('manual')}
              className={`px-3 py-1.5 rounded-md transition cursor-pointer ${
                activeMode === 'manual'
                  ? 'bg-white text-blue-700 font-bold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Option A: Enter Sensor Values
            </button>
            <button
              onClick={() => setActiveMode('csv')}
              className={`px-3 py-1.5 rounded-md transition cursor-pointer ${
                activeMode === 'csv'
                  ? 'bg-white text-blue-700 font-bold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Option B: Upload Sensor CSV
            </button>
          </div>
        </div>
      </div>

      {/* Main Form & Output Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (Inputs): 7 Cols */}
        <div className="lg:col-span-7 space-y-6">
          {activeMode === 'manual' ? (
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-5">
              {/* Preset Sample Pills */}
              <div>
                <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">
                  Quick Load Authentic Sensor Samples:
                </span>
                <div className="flex flex-wrap gap-2">
                  {samples.map((s) => (
                    <button
                      key={s.id}
                      type="button"
                      onClick={() => handleSelectSample(s)}
                      className={`text-xs px-2.5 py-1.5 rounded-lg border transition cursor-pointer ${
                        selectedSampleId === s.id
                          ? 'bg-blue-50 border-blue-400 text-blue-800 font-bold shadow-xs'
                          : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                      }`}
                    >
                      {s.name}
                    </button>
                  ))}
                </div>
              </div>

              <form onSubmit={handlePredictManual} className="space-y-4 pt-2 border-t border-slate-100">
                <span className="text-xs font-bold text-slate-900 uppercase tracking-wider block">
                  Primary Sensor & Demographic Inputs
                </span>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3.5 text-xs">
                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Steps Count</label>
                    <input
                      type="number"
                      step="any"
                      value={inputs.steps}
                      onChange={(e) => handleInputChange('steps', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 focus:ring-1 focus:ring-blue-500 font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Heart Rate (bpm)</label>
                    <input
                      type="number"
                      step="any"
                      value={inputs.heart_rate}
                      onChange={(e) => handleInputChange('heart_rate', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 focus:ring-1 focus:ring-blue-500 font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Resting HR (bpm)</label>
                    <input
                      type="number"
                      step="any"
                      value={inputs.resting_heart}
                      onChange={(e) => handleInputChange('resting_heart', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 focus:ring-1 focus:ring-blue-500 font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Calories Burned (kcal)</label>
                    <input
                      type="number"
                      step="any"
                      value={inputs.calories}
                      onChange={(e) => handleInputChange('calories', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 focus:ring-1 focus:ring-blue-500 font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Distance (miles)</label>
                    <input
                      type="number"
                      step="any"
                      value={inputs.distance}
                      onChange={(e) => handleInputChange('distance', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 focus:ring-1 focus:ring-blue-500 font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Gender</label>
                    <select
                      value={inputs.gender}
                      onChange={(e) => handleInputChange('gender', e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 focus:ring-1 focus:ring-blue-500"
                    >
                      <option value="male">Male (1)</option>
                      <option value="female">Female (0)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Age (years)</label>
                    <input
                      type="number"
                      value={inputs.age}
                      onChange={(e) => handleInputChange('age', e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Height (cm)</label>
                    <input
                      type="number"
                      value={inputs.height}
                      onChange={(e) => handleInputChange('height', e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-600 font-medium mb-1">Weight (kg)</label>
                    <input
                      type="number"
                      value={inputs.weight}
                      onChange={(e) => handleInputChange('weight', e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 font-mono"
                    />
                  </div>
                </div>

                {/* Collapsible fine-grained features */}
                <div className="pt-2">
                  <button
                    type="button"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="text-xs text-blue-600 hover:text-blue-700 font-semibold inline-flex items-center space-x-1 cursor-pointer"
                  >
                    <span>{showAdvanced ? 'Hide Sensor Entropy Settings' : 'Show Advanced Entropy Parameters'}</span>
                    {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {showAdvanced && (
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-3 p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs">
                      <div>
                        <label className="block text-slate-500 mb-0.5">Entropy Heart</label>
                        <input
                          type="number"
                          step="any"
                          value={advancedInputs.entropy_heart}
                          onChange={(e) => setAdvancedInputs({ ...advancedInputs, entropy_heart: Number(e.target.value) })}
                          className="w-full px-2 py-1 border border-slate-300 rounded bg-white text-slate-800 font-mono"
                        />
                      </div>
                      <div>
                        <label className="block text-slate-500 mb-0.5">Entropy Steps</label>
                        <input
                          type="number"
                          step="any"
                          value={advancedInputs.entropy_setps}
                          onChange={(e) => setAdvancedInputs({ ...advancedInputs, entropy_setps: Number(e.target.value) })}
                          className="w-full px-2 py-1 border border-slate-300 rounded bg-white text-slate-800 font-mono"
                        />
                      </div>
                      <div>
                        <label className="block text-slate-500 mb-0.5">Corr Heart/Steps</label>
                        <input
                          type="number"
                          step="any"
                          value={advancedInputs.corr_heart_steps}
                          onChange={(e) => setAdvancedInputs({ ...advancedInputs, corr_heart_steps: Number(e.target.value) })}
                          className="w-full px-2 py-1 border border-slate-300 rounded bg-white text-slate-800 font-mono"
                        />
                      </div>
                    </div>
                  )}
                </div>

                <div className="pt-3">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-sm transition cursor-pointer flex items-center justify-center space-x-2"
                  >
                    <Activity className="w-4 h-4" />
                    <span>{isLoading ? 'Running Inference...' : 'Classify Physical Activity'}</span>
                  </button>
                </div>
              </form>
            </div>
          ) : (
            /* Option B: Upload CSV */
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
              <span className="text-xs font-bold text-slate-900 uppercase tracking-wider block">
                Batch Sensor CSV Upload
              </span>
              <p className="text-xs text-slate-500">
                Upload a CSV containing Apple Watch sensor records (required columns: steps, calories, distance, resting_heart, heart_rate).
              </p>

              <div className="border-2 border-dashed border-slate-300 hover:border-blue-400 rounded-xl p-6 text-center bg-slate-50/50 cursor-pointer transition">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleCsvUpload}
                  className="hidden"
                  id="csv-file-input"
                />
                <label htmlFor="csv-file-input" className="cursor-pointer block">
                  <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <span className="text-xs font-bold text-blue-600 block">
                    {csvFile ? csvFile.name : 'Click to select CSV file'}
                  </span>
                  <span className="text-[11px] text-slate-400 block mt-1">
                    Accepts .csv with sensor columns
                  </span>
                </label>
              </div>

              {isCsvLoading && (
                <div className="text-xs text-center text-blue-600 py-4 font-medium animate-pulse">
                  Validating CSV and calculating batch predictions...
                </div>
              )}

              {csvResult && (
                <div className="space-y-4 pt-3 border-t border-slate-100">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-slate-900">
                      Evaluated {csvResult.valid_records} of {csvResult.total_records} rows
                    </span>
                    <span className="text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded">
                      Validation Passed
                    </span>
                  </div>

                  {/* Summary Distribution Table */}
                  <div className="border border-slate-200 rounded-lg overflow-hidden text-xs">
                    <table className="w-full text-left">
                      <thead className="bg-slate-50 border-b border-slate-200 text-slate-500">
                        <tr>
                          <th className="p-2 font-medium">Activity Class</th>
                          <th className="p-2 font-medium">Predicted Count</th>
                          <th className="p-2 font-medium">Share</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {Object.entries(csvResult.summary_distribution || {}).map(([cName, info]: any) => (
                          <tr key={cName}>
                            <td className="p-2 font-semibold text-slate-800">{cName}</td>
                            <td className="p-2 font-mono text-slate-700">{info.count}</td>
                            <td className="p-2 text-slate-600">{info.percentage}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Right Column (Prediction Output): 5 Cols */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Prediction Results
              </span>
              <span className="text-[11px] font-mono text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                {predictionResult?.model_version || 'Global Model'}
              </span>
            </div>

            {predictionResult ? (
              <div className="space-y-4">
                {/* Predicted Class Card */}
                <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/50 flex items-center justify-between">
                  <div>
                    <span className="text-[11px] font-bold text-blue-700 uppercase tracking-wider block">
                      Predicted Activity Class
                    </span>
                    <h3 className="text-xl font-extrabold text-slate-900 mt-0.5">
                      {predictionResult.predicted_activity}
                    </h3>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-slate-500 uppercase block">Confidence</span>
                    <span className="text-lg font-bold text-blue-700">
                      {predictionResult.confidence_percent}%
                    </span>
                  </div>
                </div>

                {/* Probability Distribution Bar Chart */}
                <div>
                  <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">
                    Class Probability Distribution
                  </span>
                  <div className="h-52 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                        <XAxis type="number" domain={[0, 100]} unit="%" tick={{ fontSize: 10, fill: '#64748b' }} />
                        <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: '#334155' }} width={90} />
                        <Tooltip
                          formatter={(val: any) => [`${val}%`, 'Probability']}
                          contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', fontSize: '11px' }}
                        />
                        <Bar dataKey="probability" radius={[0, 4, 4, 0]}>
                          {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={getActivityColor(entry.name)} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Derived physiological features applied */}
                {predictionResult.features_used && (
                  <div className="pt-3 border-t border-slate-100 text-[11px] space-y-1.5 text-slate-600">
                    <span className="font-bold text-slate-800 block">Derived Interaction Features:</span>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-slate-50 p-2 rounded">
                        <span className="text-slate-400 block">Heart Elevation:</span>
                        <strong className="text-slate-900">{predictionResult.features_used.heart_elevation} bpm</strong>
                      </div>
                      <div className="bg-slate-50 p-2 rounded">
                        <span className="text-slate-400 block">Metabolic Intensity:</span>
                        <strong className="text-slate-900">{predictionResult.features_used.metabolic_intensity}</strong>
                      </div>
                      <div className="bg-slate-50 p-2 rounded">
                        <span className="text-slate-400 block">Step Cadence:</span>
                        <strong className="text-slate-900">{predictionResult.features_used.step_cadence}</strong>
                      </div>
                      <div className="bg-slate-50 p-2 rounded">
                        <span className="text-slate-400 block">Validation Status:</span>
                        <strong className="text-emerald-700">Verified Input</strong>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center border border-dashed border-slate-200 rounded-xl bg-slate-50/50 text-center px-4">
                <Activity className="w-8 h-8 text-slate-400 mb-2" />
                <p className="text-xs font-semibold text-slate-700">Awaiting Input Data</p>
                <p className="text-[11px] text-slate-500 max-w-xs mt-1">
                  Select a test patient preset or enter biometric values, then click 'Classify Physical Activity'.
                </p>
              </div>
            )}

            {/* Research Disclaimer */}
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-[11px] text-slate-500 leading-relaxed">
              <strong>Research Disclaimer:</strong> This activity classification demonstration is based on retrospective sensor recordings from the Harvard Apple Watch dataset and is designed strictly for machine learning research, not clinical patient diagnosis.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientActivityTestingPage;
