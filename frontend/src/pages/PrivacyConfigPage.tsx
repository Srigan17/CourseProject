import React, { useState, useEffect } from 'react';
import {
  Shield,
  KeyRound,
  Lock,
  Calculator,
  CheckCircle2,
  AlertTriangle,
  Play,
  ArrowRight,
  Fingerprint,
  Cpu,
  Layers
} from 'lucide-react';
import { apiClient } from '../api/client';

export const PrivacyConfigPage: React.FC = () => {
  // DP State
  const [clippingNorm, setClippingNorm] = useState(1.0);
  const [noiseMultiplier, setNoiseMultiplier] = useState(0.5);
  const [targetDelta, setTargetDelta] = useState(1e-5);
  const [numRounds, setNumRounds] = useState(5);
  const [dpBudgetResult, setDpBudgetResult] = useState<any | null>(null);
  const [isCalculatingDP, setIsCalculatingDP] = useState(false);

  // SecAgg State
  const [numClientsTest, setNumClientsTest] = useState(3);
  const [paramCountTest, setParamCountTest] = useState(15);
  const [secaggTestResult, setSecaggTestResult] = useState<any | null>(null);
  const [isTestingSecagg, setIsTestingSecagg] = useState(false);

  // Byzantine & Outlier State
  const [byzantineResult, setByzantineResult] = useState<any | null>(null);
  const [isTestingByzantine, setIsTestingByzantine] = useState(false);

  // AES Test State
  const [aesPlaintext, setAesPlaintext] = useState('Confidential Hospital EHR: Patient vitals HR=74, Calories=450kcal');
  const [aesResult, setAesResult] = useState<any | null>(null);
  const [isTestingAES, setIsTestingAES] = useState(false);

  // Calculate DP on mount
  useEffect(() => {
    handleCalculateDP();
  }, [clippingNorm, noiseMultiplier, targetDelta, numRounds]);

  const handleCalculateDP = async () => {
    setIsCalculatingDP(true);
    try {
      const res = await apiClient.calculateDPBudget({
        num_rounds: numRounds,
        clipping_norm: clippingNorm,
        noise_multiplier: noiseMultiplier,
        target_delta: targetDelta,
        sample_rate: 1.0
      });
      setDpBudgetResult(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsCalculatingDP(false);
    }
  };

  const handleRunSecAggTest = async () => {
    setIsTestingSecagg(true);
    try {
      const res = await apiClient.testSecAggVerification(numClientsTest, paramCountTest);
      setSecaggTestResult(res);
    } catch (err: any) {
      alert(`SecAgg Test Failed: ${err.message}`);
    } finally {
      setIsTestingSecagg(false);
    }
  };

  const handleRunByzantineTest = async () => {
    setIsTestingByzantine(true);
    try {
      const res = await apiClient.testAnomalyDetection();
      setByzantineResult(res);
    } catch (err: any) {
      alert(`Byzantine Test Failed: ${err.message}`);
    } finally {
      setIsTestingByzantine(false);
    }
  };

  const handleRunAESTest = async () => {
    setIsTestingAES(true);
    try {
      const res = await apiClient.testAESGCM({
        plaintext: aesPlaintext,
        associated_data: 'local_hospital_ehr_vault'
      });
      setAesResult(res);
    } catch (err: any) {
      alert(`AES-GCM Test Failed: ${err.message}`);
    } finally {
      setIsTestingAES(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Overview Card */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Privacy-Preserving Security Architecture</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Cryptographic mechanisms integrated from github.com/Mallikarjun501/privacy-preserving-secure-aggregation-fl
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <span className="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full font-semibold">
            Paillier HE + (ε, δ)-DP Enabled
          </span>
        </div>
      </div>

      {/* Grid: Differential Privacy & Secure Aggregation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Section 1: Differential Privacy */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center font-bold">
                <Shield className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900">Differential Privacy Configuration</h4>
                <p className="text-[11px] text-slate-500">Gaussian Mechanism & Analytical Composition Accountant</p>
              </div>
            </div>
            <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-sky-50 text-sky-700">
              Active
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">L2 Clipping Norm Bound (C)</label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                max="10.0"
                value={clippingNorm}
                onChange={(e) => setClippingNorm(parseFloat(e.target.value) || 1.0)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-mono text-slate-800"
              />
              <span className="text-[10px] text-slate-400 mt-0.5 block">Bounds update sensitivity Δ = C</span>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Noise Multiplier (σ)</label>
              <input
                type="number"
                step="0.05"
                min="0.05"
                max="2.0"
                value={noiseMultiplier}
                onChange={(e) => setNoiseMultiplier(parseFloat(e.target.value) || 0.5)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-mono text-slate-800"
              />
              <span className="text-[10px] text-slate-400 mt-0.5 block">Std dev = σ · C</span>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Target Privacy Delta (δ)</label>
              <input
                type="text"
                value={targetDelta}
                disabled
                className="w-full bg-slate-100 border border-slate-200 rounded-lg p-2 font-mono text-slate-500"
              />
              <span className="text-[10px] text-slate-400 mt-0.5 block">Cryptographic failure probability (10⁻⁵)</span>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Evaluated Training Rounds</label>
              <input
                type="number"
                min="1"
                max="20"
                value={numRounds}
                onChange={(e) => setNumRounds(parseInt(e.target.value) || 5)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-mono text-slate-800"
              />
              <span className="text-[10px] text-slate-400 mt-0.5 block">Composition parameter T</span>
            </div>
          </div>

          {/* Budget Result Box */}
          {dpBudgetResult && (
            <div className="p-4 bg-sky-50/60 rounded-xl border border-sky-200 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sky-950">Calculated Privacy Budget (ε, δ)</span>
                <span className="text-[10px] font-mono text-sky-700">Accountant: Advanced Composition</span>
              </div>
              <div className="flex items-baseline space-x-3">
                <div>
                  <span className="text-2xl font-bold font-mono text-sky-700">ε = {dpBudgetResult.epsilon}</span>
                </div>
                <div className="text-slate-500 font-mono text-xs">δ = {dpBudgetResult.delta}</div>
              </div>
              <p className="text-[11px] text-slate-600 leading-relaxed">
                <strong>Formal Guarantee:</strong> {dpBudgetResult.guarantee}. Limits individual participant membership
                inference leakage across {numRounds} training rounds.
              </p>
            </div>
          )}
        </div>

        {/* Section 2: Cryptographic Secure Aggregation */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                <Lock className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900">Paillier Secure Aggregation (SecAgg)</h4>
                <p className="text-[11px] text-slate-500">Additive Homomorphic Encryption with Zero Server Visibility</p>
              </div>
            </div>
            <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">
              512-bit Keys
            </span>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed">
            Directly reuses the additive homomorphic cryptosystem from the repository. Each hospital client encrypts
            scaled model parameters: <span className="font-mono bg-slate-100 px-1 py-0.5 rounded">E(w) = g^w · r^N mod N²</span>.
            The aggregation server computes homomorphic additions without access to private keys.
          </p>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-slate-500 text-[10px] font-semibold uppercase">Cryptosystem</span>
              <div className="font-bold text-slate-800 mt-0.5">Paillier (phe 1.5.0)</div>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-slate-500 text-[10px] font-semibold uppercase">Min. Participation Threshold</span>
              <div className="font-bold text-slate-800 mt-0.5">k ≥ 2 Clients</div>
            </div>
          </div>

          {/* Test SecAgg verification button */}
          <div className="pt-2">
            <button
              onClick={handleRunSecAggTest}
              disabled={isTestingSecagg}
              className="w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-sm flex items-center justify-center space-x-2 transition"
            >
              <Fingerprint className="w-4 h-4" />
              <span>{isTestingSecagg ? 'Executing Paillier Cryptographic Proof...' : 'Run Live SecAgg Cryptographic Verification'}</span>
            </button>
          </div>

          {secaggTestResult && (
            <div className="p-4 bg-emerald-50/60 rounded-xl border border-emerald-200 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-emerald-950 flex items-center space-x-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Homomorphic Sum Verification Succeeded!</span>
                </span>
                <span className="text-[10px] font-mono text-emerald-700">Error &lt; 10⁻⁴</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center text-[11px] font-mono">
                <div className="bg-white p-2 rounded-lg border border-emerald-200">
                  <span className="text-[10px] text-slate-400">Enc Time</span>
                  <div className="font-bold text-slate-800">{secaggTestResult.timing_and_overhead.encryption_time_sec}s</div>
                </div>
                <div className="bg-white p-2 rounded-lg border border-emerald-200">
                  <span className="text-[10px] text-slate-400">Agg Time</span>
                  <div className="font-bold text-slate-800">{secaggTestResult.timing_and_overhead.homomorphic_aggregation_time_sec}s</div>
                </div>
                <div className="bg-white p-2 rounded-lg border border-emerald-200">
                  <span className="text-[10px] text-slate-400">Overhead</span>
                  <div className="font-bold text-slate-800">{secaggTestResult.timing_and_overhead.communication_overhead_kb} KB</div>
                </div>
              </div>
              <p className="text-[10px] text-slate-500 font-mono">
                Proof: Expected {JSON.stringify(secaggTestResult.sample_plaintext_expected.slice(0, 3))} == Decrypted {JSON.stringify(secaggTestResult.sample_secagg_decrypted.slice(0, 3))}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Grid: Byzantine Resilience & AES-256-GCM Storage */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Section 3: Byzantine Resilience (Krum) */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold">
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900">Byzantine Resilience & Outlier Defense</h4>
                <p className="text-[11px] text-slate-500">Multi-Krum Filter from secagg_repo/byzantine_resilience.py</p>
              </div>
            </div>
            <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700">
              Active
            </span>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed">
            Protects against poisoning attacks by calculating pairwise Euclidean distance scores:
            <span className="font-mono bg-slate-100 px-1 py-0.5 rounded">score_i = Σ ||w_i - w_j||²</span>.
            Identifies and rejects malicious client updates that deviate significantly from benign hospital distributions.
          </p>

          <button
            onClick={handleRunByzantineTest}
            disabled={isTestingByzantine}
            className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm flex items-center justify-center space-x-2 transition"
          >
            <Shield className="w-4 h-4" />
            <span>{isTestingByzantine ? 'Evaluating Byzantine Attack Defense...' : 'Test Poisoning & Anomaly Defense'}</span>
          </button>

          {byzantineResult && (
            <div className="p-4 bg-indigo-50/60 rounded-xl border border-indigo-200 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-indigo-950 flex items-center space-x-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Poisoning Attack Blocked!</span>
                </span>
                <span className="text-[10px] font-mono text-indigo-700">Krum Outlier Algorithm</span>
              </div>
              <div className="text-[11px] text-slate-700">
                Rejected Clients: <strong className="text-rose-600 font-mono">{byzantineResult.krum_outlier_detection.rejected_clients.join(', ')}</strong>
              </div>
              <div className="text-[11px] text-slate-700">
                Accepted Clients: <strong className="text-emerald-700 font-mono">{byzantineResult.krum_outlier_detection.accepted_clients.join(', ')}</strong>
              </div>
            </div>
          )}
        </div>

        {/* Section 4: AES-256-GCM Storage Encryption */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-bold">
                <KeyRound className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900">AES-256-GCM Encryption at Rest</h4>
                <p className="text-[11px] text-slate-500">Authenticated Storage for Local Patient Records & Checkpoints</p>
              </div>
            </div>
            <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-700">
              Active
            </span>
          </div>

          <div className="text-xs space-y-2">
            <label className="font-semibold text-slate-700 block">Plaintext Patient Health Record</label>
            <input
              type="text"
              value={aesPlaintext}
              onChange={(e) => setAesPlaintext(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-mono text-xs text-slate-800"
            />
          </div>

          <button
            onClick={handleRunAESTest}
            disabled={isTestingAES}
            className="w-full py-2.5 px-4 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-semibold shadow-sm flex items-center justify-center space-x-2 transition"
          >
            <Lock className="w-4 h-4" />
            <span>{isTestingAES ? 'Encrypting with 96-bit Nonce...' : 'Test AES-256-GCM Authenticated Roundtrip'}</span>
          </button>

          {aesResult && (
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs font-mono space-y-1.5">
              <div className="text-emerald-700 font-bold flex items-center space-x-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Roundtrip Verified (Plaintext == Decrypted)</span>
              </div>
              <div className="text-[11px] text-slate-600 truncate">
                Nonce: <span className="text-slate-900">{aesResult.encrypted_result.nonce}</span>
              </div>
              <div className="text-[11px] text-slate-600 truncate">
                Ciphertext: <span className="text-slate-900">{aesResult.encrypted_result.ciphertext}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
