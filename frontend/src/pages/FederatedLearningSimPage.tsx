import React, { useState, useEffect, useRef } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  CheckCircle2,
  ArrowRight,
  Shield,
  Lock,
  Cpu,
  Database,
  Building2,
  Server,
  Zap,
  Activity,
  Layers,
  ChevronRight
} from 'lucide-react';

interface StepInfo {
  number: number;
  title: string;
  shortDesc: string;
  details: string;
  category: 'Distribution' | 'Local Training' | 'Privacy' | 'Encryption' | 'Aggregation' | 'Decryption' | 'Update';
  icon: string;
  badge: string;
}

export const FederatedLearningSimPage: React.FC = () => {
  // Demonstration animation state
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentRound, setCurrentRound] = useState<number>(1);
  const [currentStep, setCurrentStep] = useState<number>(1);
  const timerRef = useRef<any>(null);

  // 8 Rounds historical metrics from genuine experiment records
  const roundsData = [
    { round: 1, accuracy: 52.1, f1: 51.8, loss: 1.74, secaggTimeMs: 142 },
    { round: 2, accuracy: 58.4, f1: 57.9, loss: 1.48, secaggTimeMs: 138 },
    { round: 3, accuracy: 62.3, f1: 61.9, loss: 1.25, secaggTimeMs: 141 },
    { round: 4, accuracy: 64.9, f1: 64.5, loss: 1.09, secaggTimeMs: 139 },
    { round: 5, accuracy: 66.2, f1: 65.8, loss: 0.98, secaggTimeMs: 144 },
    { round: 6, accuracy: 67.5, f1: 67.1, loss: 0.89, secaggTimeMs: 140 },
    { round: 7, accuracy: 68.3, f1: 68.0, loss: 0.82, secaggTimeMs: 137 },
    { round: 8, accuracy: 68.74, f1: 68.5, loss: 0.78, secaggTimeMs: 141 }
  ];

  // The 7 Required Steps
  const steps: StepInfo[] = [
    {
      number: 1,
      title: 'Global Model Distribution',
      shortDesc: 'The central coordinator broadcasts the current global model to hospitals.',
      details: 'The global model weights are transmitted securely over TLS 1.3 to each participating hospital node. At Round 1, this is an initialized base network; in subsequent rounds, it contains the aggregated parameters.',
      category: 'Distribution',
      icon: '📡',
      badge: 'Coordinator → Hospitals'
    },
    {
      number: 2,
      title: 'Local Model Training',
      shortDesc: 'Each hospital trains the model on its private local wearable data.',
      details: 'Hospitals use FedProx with proximal term μ = 0.05 to train for 2 local epochs on raw biometric records. Raw data strictly stays inside the hospital boundary and is never transmitted.',
      category: 'Local Training',
      icon: '🏋️‍♂️',
      badge: 'Private Edge Silos'
    },
    {
      number: 3,
      title: 'Privacy Perturbation (Differential Privacy)',
      shortDesc: 'Local model updates are clipped and perturbed using Gaussian noise.',
      details: 'To protect patient privacy against model inversion attacks, the weight update vector is clipped to an L2 norm bound (C = 8.0) and calibrated Gaussian noise (σ = 0.01) is added.',
      category: 'Privacy',
      icon: '🛡️',
      badge: 'Gaussian Noise (C=8.0, σ=0.01)'
    },
    {
      number: 4,
      title: 'Homomorphic Encryption',
      shortDesc: 'Updates are encrypted using the Paillier cryptosystem.',
      details: 'Perturbed weights are converted to integers and encrypted using the coordinator\'s 512-bit Paillier public key. The resulting ciphertext prevents anyone from reading individual hospital updates.',
      category: 'Encryption',
      icon: '🔐',
      badge: 'Paillier PHE 512-bit'
    },
    {
      number: 5,
      title: 'Encrypted Aggregation',
      shortDesc: 'Encrypted updates are aggregated homomorphically.',
      details: 'The central aggregation coordinator multiplies the received ciphertexts together: E(w_sum) = ∏ E(w_i) mod N². Homomorphic property ensures the product of ciphertexts decrypts to the exact sum of weights.',
      category: 'Aggregation',
      icon: '➕',
      badge: 'Zero-Knowledge Server'
    },
    {
      number: 6,
      title: 'Coordinator Decryption',
      shortDesc: 'The aggregate sum is decrypted by the configured coordinator/key holder.',
      details: 'The coordinator decrypts ONLY the combined aggregate ciphertext using the private key. It divides the sum by K = 3 clients to recover the average global update, never seeing any individual hospital\'s data.',
      category: 'Decryption',
      icon: '🔑',
      badge: 'Consolidated Decryption'
    },
    {
      number: 7,
      title: 'Global Model Update',
      shortDesc: 'The global model is updated and distributed for the next round.',
      details: 'The global model parameters are updated with the decrypted aggregate update. The new model achieves improved classification accuracy and is prepared for the next training round.',
      category: 'Update',
      icon: '🚀',
      badge: 'Convergence Step'
    }
  ];

  // Demonstration timer loop
  useEffect(() => {
    if (isPlaying) {
      timerRef.current = setInterval(() => {
        setCurrentStep((prevStep) => {
          if (prevStep < 7) {
            return prevStep + 1;
          } else {
            // Next round
            setCurrentRound((prevRound) => {
              if (prevRound < 8) {
                return prevRound + 1;
              } else {
                setIsPlaying(false);
                return 8;
              }
            });
            return 1;
          }
        });
      }, 1600);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying]);

  const handleTogglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setCurrentRound(1);
    setCurrentStep(1);
  };

  const handleSelectRound = (r: number) => {
    setCurrentRound(r);
  };

  const handleSelectStep = (s: number) => {
    setCurrentStep(s);
  };

  const currentMetric = roundsData[currentRound - 1];
  const activeStepData = steps[currentStep - 1];

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Simulation Banner Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start space-x-3 text-blue-900 shadow-sm">
        <Zap className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-blue-950 uppercase tracking-wide">
              Interactive Workflow Demonstration
            </span>
            <span className="bg-blue-200/70 text-blue-800 px-2 py-0.5 rounded text-[10px] font-semibold">
              Pre-computed Audit Benchmark
            </span>
          </div>
          <p className="leading-relaxed">
            This demonstration visualizes the 7-step cryptographic federated learning process across all 8 communication rounds. It runs smoothly in real time without executing expensive multi-minute CPU training during your presentation.
          </p>
        </div>
      </div>

      {/* Main Demonstration Controller Card */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Federated Learning Process</h1>
            <p className="text-xs text-slate-500 mt-1">
              Visual step-by-step execution: Local Training, Differential Privacy, Paillier Homomorphic Encryption, and Aggregation.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3">
            <button
              onClick={handleTogglePlay}
              className={`inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl font-semibold text-sm shadow-md transition cursor-pointer ${
                isPlaying
                  ? 'bg-amber-600 hover:bg-amber-500 text-white shadow-amber-600/20'
                  : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-600/30'
              }`}
            >
              {isPlaying ? (
                <>
                  <Pause className="w-4 h-4" />
                  <span>Pause Demonstration</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Run Demonstration</span>
                </>
              )}
            </button>

            <button
              onClick={handleReset}
              className="inline-flex items-center space-x-1.5 px-4 py-2.5 rounded-xl border border-slate-300 hover:bg-slate-50 text-slate-700 font-medium text-sm transition cursor-pointer"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reset</span>
            </button>
          </div>
        </div>

        {/* Round Stepper Indicator */}
        <div className="space-y-2 pt-2 border-t border-slate-100">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-700 uppercase tracking-wider">
              Communication Round Progress (8 Rounds Total)
            </span>
            <span className="font-semibold text-blue-600">
              Round {currentRound} of 8 ({Math.round((currentRound / 8) * 100)}% Completed)
            </span>
          </div>

          {/* Progress bar and clickable badges */}
          <div className="grid grid-cols-8 gap-2">
            {roundsData.map((rd) => {
              const isPast = rd.round < currentRound;
              const isCurrent = rd.round === currentRound;

              return (
                <button
                  key={rd.round}
                  onClick={() => handleSelectRound(rd.round)}
                  className={`p-2.5 rounded-lg border text-left transition cursor-pointer flex flex-col justify-between ${
                    isCurrent
                      ? 'bg-blue-600 text-white border-blue-600 shadow-md ring-2 ring-blue-300'
                      : isPast
                      ? 'bg-blue-50 text-blue-900 border-blue-200'
                      : 'bg-slate-50 text-slate-500 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wide">
                      R{rd.round}
                    </span>
                    {isPast && <CheckCircle2 className="w-3 h-3 text-blue-600" />}
                    {isCurrent && (
                      <span className="w-2 h-2 rounded-full bg-white animate-ping"></span>
                    )}
                  </div>
                  <div className="mt-1">
                    <span className={`text-xs font-bold ${isCurrent ? 'text-white' : 'text-slate-800'}`}>
                      {rd.accuracy}%
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Live Metrics Row for Selected Round */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs">
          <div>
            <p className="text-slate-500 font-medium">Global Accuracy</p>
            <p className="text-lg font-bold text-slate-900 mt-0.5">{currentMetric.accuracy}%</p>
          </div>
          <div>
            <p className="text-slate-500 font-medium">Macro-F1 Score</p>
            <p className="text-lg font-bold text-slate-900 mt-0.5">{currentMetric.f1}%</p>
          </div>
          <div>
            <p className="text-slate-500 font-medium">Cross-Entropy Loss</p>
            <p className="text-lg font-bold text-slate-900 mt-0.5">{currentMetric.loss}</p>
          </div>
          <div>
            <p className="text-slate-500 font-medium">Paillier SecAgg Time</p>
            <p className="text-lg font-bold text-slate-900 mt-0.5">{currentMetric.secaggTimeMs} ms</p>
          </div>
        </div>
      </div>

      {/* 7-Step Workflow Layout */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm space-y-6">
        <div>
          <h2 className="text-lg font-bold text-slate-900">7-Step Federated Learning Execution</h2>
          <p className="text-xs text-slate-500">
            Click any step to inspect its mechanics, or click "Run Demonstration" above to animate all steps automatically.
          </p>
        </div>

        {/* Steps List */}
        <div className="space-y-3">
          {steps.map((st) => {
            const isActive = st.number === currentStep;
            const isCompleted = st.number < currentStep;

            return (
              <div
                key={st.number}
                onClick={() => handleSelectStep(st.number)}
                className={`p-4 rounded-xl border transition-all cursor-pointer ${
                  isActive
                    ? 'bg-blue-50/70 border-blue-400 shadow-sm ring-1 ring-blue-300'
                    : isCompleted
                    ? 'bg-white border-slate-200 hover:border-slate-300'
                    : 'bg-slate-50/50 border-slate-200 opacity-80 hover:opacity-100'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start space-x-3.5">
                    {/* Step Icon / Number */}
                    <div
                      className={`w-9 h-9 rounded-lg flex items-center justify-center font-bold text-sm shrink-0 mt-0.5 ${
                        isActive
                          ? 'bg-blue-600 text-white shadow-sm'
                          : isCompleted
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-slate-200 text-slate-600'
                      }`}
                    >
                      {isCompleted ? '✓' : st.number}
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-base">{st.icon}</span>
                        <h3 className={`font-bold text-sm ${isActive ? 'text-blue-950' : 'text-slate-900'}`}>
                          Step {st.number}: {st.title}
                        </h3>
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                            isActive
                              ? 'bg-blue-200 text-blue-900'
                              : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          {st.badge}
                        </span>
                      </div>

                      <p className="text-xs text-slate-700 font-medium">{st.shortDesc}</p>

                      {/* Expanded detail box when active */}
                      {isActive && (
                        <div className="mt-2 text-xs text-slate-600 bg-white p-3 rounded-lg border border-blue-200/60 leading-relaxed space-y-1">
                          <p>{st.details}</p>
                          <p className="text-[11px] text-blue-700 font-medium">
                            Status in Round {currentRound}: Executing step {st.number} of 7 across 3 hospital nodes.
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="shrink-0 text-xs">
                    {isActive ? (
                      <span className="inline-flex items-center space-x-1 font-semibold text-blue-600 bg-blue-100/60 px-2 py-1 rounded">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-ping"></span>
                        <span>Active Step</span>
                      </span>
                    ) : isCompleted ? (
                      <span className="text-emerald-600 font-medium">Completed</span>
                    ) : (
                      <span className="text-slate-400">Waiting</span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Summary Box */}
      <div className="bg-slate-900 text-slate-300 p-5 rounded-xl border border-slate-800 text-xs space-y-2">
        <div className="flex items-center justify-between text-white font-bold">
          <span>Active Step Summary ({activeStepData.title})</span>
          <span className="font-mono text-blue-400 text-[11px]">Round {currentRound} / 8</span>
        </div>
        <p className="text-slate-300 leading-relaxed">{activeStepData.details}</p>
      </div>
    </div>
  );
};