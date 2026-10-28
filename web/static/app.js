// HealthFL SecAgg Clinical Analytics Platform Frontend Logic

let convergenceChart = null;
let probabilitiesChart = null;
let cryptoBenchmarkChart = null;
let configurationsChart = null;
let bandwidthChart = null;

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    loadOverviewData();
    loadTopologyData();
    loadConvergenceData(8);
    loadConfigurationsData();
    loadBandwidthData();
    setupPatientTesting();
    setupCryptoBenchmark();
});

// 1. Navigation Active State
function initNavigation() {
    const navLinks = document.querySelectorAll(".nav-link");
    window.addEventListener("scroll", () => {
        let current = "";
        const sections = document.querySelectorAll("section");
        sections.forEach(sec => {
            const top = sec.offsetTop - 120;
            if (window.pageYOffset >= top) {
                current = sec.getAttribute("id");
            }
        });
        navLinks.forEach(link => {
            link.classList.remove("text-cyan-400", "border-cyan-400", "font-semibold");
            if (link.getAttribute("href") === `#${current}`) {
                link.classList.add("text-cyan-400", "border-cyan-400", "font-semibold");
            }
        });
    });
}

// 1. Load Overview KPIs
async function loadOverviewData() {
    try {
        const res = await fetch("/api/overview");
        const data = await res.json();
        
        document.getElementById("kpi-clients").innerText = data.hospital_network_nodes;
        document.getElementById("kpi-accuracy").innerText = `${data.performance_kpis.secagg_fedavg_accuracy}%`;
        document.getElementById("kpi-accuracy-sub").innerText = `vs Plaintext ${data.performance_kpis.plaintext_fedavg_accuracy}% (+0.32 pp)`;
        document.getElementById("kpi-epsilon").innerText = `ε = ${data.privacy_parameters.runtime_epsilon_prv}`;
        document.getElementById("kpi-epsilon-sub").innerText = `δ = ${data.privacy_parameters.target_delta} (PRV Accountant)`;
        document.getElementById("kpi-bandwidth").innerText = `${data.performance_kpis.bandwidth_per_client_round_kb} KB`;
        document.getElementById("kpi-overhead").innerText = `+${data.performance_kpis.cryptographic_latency_overhead_ms} ms`;
        document.getElementById("kpi-modulus").innerText = "2³¹ - 1";
    } catch (err) {
        console.error("Failed to load overview data:", err);
    }
}

// 2. Load Topology and mTLS Certificates
async function loadTopologyData() {
    try {
        const res = await fetch("/api/topology");
        const data = await res.json();
        
        const container = document.getElementById("hospital-nodes-grid");
        container.innerHTML = "";
        
        data.client_nodes.forEach(node => {
            const card = document.createElement("div");
            card.className = "glass-card p-5 relative overflow-hidden border border-slate-700/60 hover:border-cyan-500/50";
            card.innerHTML = `
                <div class="flex items-start justify-between mb-3">
                    <div class="flex items-center gap-3">
                        <span class="w-3 h-3 rounded-full bg-emerald-400 pulse-emerald"></span>
                        <div>
                            <h4 class="font-bold text-white text-base leading-snug">${node.hospital_name}</h4>
                            <p class="text-xs text-slate-400 font-mono">${node.location} • ${node.ip_address}:${node.port}</p>
                        </div>
                    </div>
                    <span class="badge-tech badge-emerald text-xs">Round ${node.current_round} Synced</span>
                </div>
                
                <div class="grid grid-cols-2 gap-2 text-xs py-2 my-2 border-y border-slate-800">
                    <div>
                        <span class="text-slate-400">Dataset Records:</span>
                        <span class="font-semibold text-slate-200 block">${node.dataset_records} (FHIR Bundled)</span>
                    </div>
                    <div>
                        <span class="text-slate-400">gRPC Ping Latency:</span>
                        <span class="font-semibold text-cyan-400 block">${node.latency_ping_ms} ms</span>
                    </div>
                    <div>
                        <span class="text-slate-400">Participation Rate:</span>
                        <span class="font-semibold text-emerald-400 block">${node.round_participation_rate}</span>
                    </div>
                    <div>
                        <span class="text-slate-400">mTLS Handshake:</span>
                        <span class="font-semibold text-emerald-400 block">Strict Verified</span>
                    </div>
                </div>

                <div class="mt-3">
                    <button onclick="viewCertificate('${node.id}')" class="w-full py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg text-xs font-mono flex items-center justify-center gap-2 transition">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                        Inspect mTLS Certificate
                    </button>
                </div>
            `;
            container.appendChild(card);
        });

        // Store globally for modal access
        window.topologyNodes = data.client_nodes;
    } catch (err) {
        console.error("Failed to load topology:", err);
    }
}

function viewCertificate(nodeId) {
    if (!window.topologyNodes) return;
    const node = window.topologyNodes.find(n => n.id === nodeId);
    if (!node) return;
    
    const cert = node.certificate;
    const modalContent = document.getElementById("cert-modal-content");
    modalContent.innerHTML = `
        <div class="space-y-3 font-mono text-xs">
            <div class="p-3 bg-slate-900/90 rounded border border-cyan-500/30">
                <p class="text-cyan-400 font-bold text-sm mb-1">${node.hospital_name}</p>
                <p class="text-slate-300">Common Name: <span class="text-emerald-400 font-bold">${cert.subject_cn}</span></p>
                <p class="text-slate-400 break-all text-[11px] mt-1">${cert.subject_dn}</p>
            </div>
            
            <div class="grid grid-cols-2 gap-2">
                <div class="p-2.5 bg-slate-900/60 rounded border border-slate-800">
                    <span class="text-slate-400 block text-[10px]">ISSUING AUTHORITY</span>
                    <span class="text-slate-200 font-bold">${cert.issuer_cn}</span>
                </div>
                <div class="p-2.5 bg-slate-900/60 rounded border border-slate-800">
                    <span class="text-slate-400 block text-[10px]">CIPHER SUITE</span>
                    <span class="text-emerald-400 font-bold text-[11px]">${cert.cipher_suite}</span>
                </div>
                <div class="p-2.5 bg-slate-900/60 rounded border border-slate-800">
                    <span class="text-slate-400 block text-[10px]">KEY EXCHANGE</span>
                    <span class="text-cyan-400 font-bold">${cert.key_exchange}</span>
                </div>
                <div class="p-2.5 bg-slate-900/60 rounded border border-slate-800">
                    <span class="text-slate-400 block text-[10px]">SERIAL NUMBER</span>
                    <span class="text-slate-200 font-bold">${cert.serial_number}</span>
                </div>
            </div>

            <div class="p-2.5 bg-slate-900/60 rounded border border-slate-800">
                <span class="text-slate-400 block text-[10px]">SHA-256 FINGERPRINT</span>
                <span class="text-amber-400 break-all text-[11px] font-bold">${cert.fingerprint_sha256}</span>
            </div>

            <div class="flex items-center justify-between p-2.5 bg-emerald-950/30 border border-emerald-500/40 rounded text-emerald-300 text-xs">
                <span>Validity: ${cert.valid_from} → ${cert.valid_until}</span>
                <span class="badge-tech badge-emerald">${cert.days_remaining} Days Remaining</span>
            </div>
        </div>
    `;
    
    document.getElementById("cert-modal").classList.remove("hidden");
}

function closeCertModal() {
    document.getElementById("cert-modal").classList.add("hidden");
}

// 3. Live Patient Activity Testing & Clinical Inference
const featureKeys = [
    "age", "gender", "height", "weight", "steps", "hear_rate", "calories", "distance",
    "entropy_heart", "entropy_setps", "resting_heart", "corr_heart_steps",
    "norm_heart", "intensity_karvonen", "sd_norm_heart", "steps_times_distance"
];

function setupPatientTesting() {
    const inputs = featureKeys.map(k => document.getElementById(`vital-${k}`));
    inputs.forEach(input => {
        if (!input) return;
        input.addEventListener("input", (e) => {
            const valDisplay = document.getElementById(`val-${e.target.name}`);
            if (valDisplay) valDisplay.innerText = Number(e.target.value).toFixed(2);
        });
    });

    // Default: load a brisk walking patient sample
    loadPatientPreset("Self Pace walk");
}

async function loadPatientPreset(activity) {
    try {
        const url = activity ? `/api/patient-sample?activity=${encodeURIComponent(activity)}` : "/api/patient-sample";
        const res = await fetch(url);
        const data = await res.json();
        
        featureKeys.forEach(k => {
            const input = document.getElementById(`vital-${k}`);
            const display = document.getElementById(`val-${k}`);
            if (input && data[k] !== undefined) {
                input.value = data[k];
                if (display) display.innerText = Number(data[k]).toFixed(2);
            }
        });
        
        document.getElementById("sample-ground-truth").innerText = data.ground_truth_activity;
        document.getElementById("sample-patient-id").innerText = `#${data.participant_id}`;
        
        // Auto-run inference upon loading sample
        runClinicalInference();
    } catch (err) {
        console.error("Failed to load preset:", err);
    }
}

async function runClinicalInference() {
    const payload = {};
    featureKeys.forEach(k => {
        const input = document.getElementById(`vital-${k}`);
        payload[k] = parseFloat(input.value) || 0.0;
    });

    const runBtn = document.getElementById("btn-run-inference");
    runBtn.disabled = true;
    runBtn.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        Evaluating PyTorch MLP...
    `;

    try {
        const res = await fetch("/api/predict", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        
        // Update inference cards
        document.getElementById("pred-activity-badge").innerText = result.predicted_activity;
        document.getElementById("pred-activity-badge").style.backgroundColor = `${result.status_color}25`;
        document.getElementById("pred-activity-badge").style.borderColor = result.status_color;
        document.getElementById("pred-activity-badge").style.color = result.status_color;

        document.getElementById("pred-confidence").innerText = `${result.confidence_percentage}%`;
        document.getElementById("pred-met-score").innerText = `${result.clinical_met_score} METs`;
        document.getElementById("pred-exertion-level").innerText = result.exertion_level;
        document.getElementById("pred-assessment").innerText = result.clinical_assessment;
        document.getElementById("pred-latency").innerText = `${result.inference_latency_ms} ms`;

        // Render Class Probabilities Chart
        renderProbabilitiesChart(result.probabilities);
    } catch (err) {
        console.error("Inference failed:", err);
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = `
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            Execute Real-Time Clinical Inference
        `;
    }
}

function renderProbabilitiesChart(probs) {
    const ctx = document.getElementById("probabilitiesChart").getContext("2d");
    const labels = probs.map(p => p.class);
    const data = probs.map(p => p.percentage);

    if (probabilitiesChart) probabilitiesChart.destroy();

    probabilitiesChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Posterior Probability (%)",
                data: data,
                backgroundColor: [
                    "#06b6d4", "#3b82f6", "#10b981", "#f59e0b", "#f97316", "#ec4899"
                ],
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` Confidence: ${ctx.raw}%`
                    }
                }
            },
            scales: {
                x: {
                    max: 100,
                    grid: { color: "rgba(255,255,255,0.05)" },
                    ticks: { color: "#94a3b8" }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: "#f1f5f9", font: { weight: "600" } }
                }
            }
        }
    });
}

// 4. Convergence Curves across FL Rounds
async function loadConvergenceData(rounds = 8) {
    try {
        const res = await fetch(`/api/convergence?rounds=${rounds}`);
        const data = await res.json();
        
        // Update active button state
        document.getElementById("btn-rounds-8").classList.toggle("bg-cyan-600", rounds === 8);
        document.getElementById("btn-rounds-8").classList.toggle("bg-slate-800", rounds !== 8);
        document.getElementById("btn-rounds-25").classList.toggle("bg-cyan-600", rounds === 25);
        document.getElementById("btn-rounds-25").classList.toggle("bg-slate-800", rounds !== 25);

        renderConvergenceChart(data);
    } catch (err) {
        console.error("Failed to load convergence curves:", err);
    }
}

function renderConvergenceChart(data) {
    const ctx = document.getElementById("convergenceChart").getContext("2d");
    const labels = data.rounds.map(r => `Round ${r}`);

    if (convergenceChart) convergenceChart.destroy();

    convergenceChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "SecAgg-FedAvg Test Accuracy (%)",
                    data: data.secagg_fedavg.accuracy,
                    borderColor: "#06b6d4",
                    backgroundColor: "rgba(6, 182, 212, 0.1)",
                    borderWidth: 2.5,
                    tension: 0.3,
                    yAxisID: "y"
                },
                {
                    label: "Plaintext FedAvg Accuracy (%)",
                    data: data.plaintext_fedavg.accuracy,
                    borderColor: "#3b82f6",
                    borderDash: [5, 5],
                    borderWidth: 2,
                    tension: 0.3,
                    yAxisID: "y"
                },
                {
                    label: "DP-FedAvg (σ=1.0) Accuracy (%)",
                    data: data.dp_fedavg_sigma_1.accuracy,
                    borderColor: "#f59e0b",
                    borderWidth: 2,
                    tension: 0.3,
                    yAxisID: "y"
                },
                {
                    label: "SecAgg Test Loss",
                    data: data.secagg_fedavg.loss,
                    borderColor: "#10b981",
                    borderDash: [3, 3],
                    borderWidth: 1.5,
                    tension: 0.3,
                    yAxisID: "y1"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: {
                    labels: { color: "#cbd5e1", font: { size: 11 } }
                }
            },
            scales: {
                x: {
                    grid: { color: "rgba(255,255,255,0.05)" },
                    ticks: { color: "#94a3b8" }
                },
                y: {
                    type: "linear",
                    display: true,
                    position: "left",
                    title: { display: true, text: "Accuracy (%)", color: "#38bdf8" },
                    grid: { color: "rgba(255,255,255,0.05)" },
                    ticks: { color: "#38bdf8" }
                },
                y1: {
                    type: "linear",
                    display: true,
                    position: "right",
                    title: { display: true, text: "Cross-Entropy Loss", color: "#34d399" },
                    grid: { drawOnChartArea: false },
                    ticks: { color: "#34d399" }
                }
            }
        }
    });
}

// 5. Comparative Configurations Table & Radar/Bar
async function loadConfigurationsData() {
    try {
        const res = await fetch("/api/configurations");
        const data = await res.json();
        
        const tbody = document.getElementById("configurations-table-body");
        tbody.innerHTML = "";
        
        data.configurations.forEach(cfg => {
            const tr = document.createElement("tr");
            tr.className = "border-b border-slate-800 hover:bg-slate-800/40 text-xs";
            
            let badgeClass = "badge-tech";
            if (cfg.config_id === "A") badgeClass += " badge-amber";
            else if (cfg.config_id === "C") badgeClass += " badge-emerald";
            
            tr.innerHTML = `
                <td class="py-3 px-3 font-semibold text-white">
                    <span class="${badgeClass} mr-1">${cfg.config_id}</span> ${cfg.name}
                </td>
                <td class="py-3 px-3 font-mono text-cyan-400 font-bold">${cfg.epsilon_display}</td>
                <td class="py-3 px-3 font-mono font-bold text-white">${cfg.accuracy_mean}% <span class="text-slate-400 font-normal">±${cfg.accuracy_std_sample}%</span></td>
                <td class="py-3 px-3 font-mono text-slate-300">${cfg.f1_mean}% <span class="text-slate-400 font-normal">±${cfg.f1_std_sample}%</span></td>
                <td class="py-3 px-3 font-mono text-slate-300">${cfg.kappa_mean}</td>
                <td class="py-3 px-3 font-mono text-slate-300">${cfg.mcc_mean}</td>
                <td class="py-3 px-3 font-mono text-slate-400">${cfg.loss_mean}</td>
                <td class="py-3 px-3 font-mono text-slate-400">${cfg.client_time_s}s</td>
            `;
            tbody.appendChild(tr);
        });

        renderConfigurationsChart(data.configurations);
    } catch (err) {
        console.error("Failed to load configurations:", err);
    }
}

function renderConfigurationsChart(configs) {
    const ctx = document.getElementById("configurationsChart").getContext("2d");
    
    // Pick key configurations to display
    const selected = configs.filter(c => ["A", "C", "B-1.0", "D-1.0", "B-0.5", "D-0.5"].includes(c.config_id));
    const labels = selected.map(c => c.name.split(":")[1].trim());
    const accs = selected.map(c => c.accuracy_mean);
    const f1s = selected.map(c => c.f1_mean);

    if (configurationsChart) configurationsChart.destroy();

    configurationsChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Mean Accuracy (%)",
                    data: accs,
                    backgroundColor: "#06b6d4",
                    borderRadius: 4
                },
                {
                    label: "Macro F1 Score (%)",
                    data: f1s,
                    backgroundColor: "#3b82f6",
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: "#cbd5e1" } }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: "#94a3b8", maxRotation: 25, minRotation: 25, font: { size: 10 } }
                },
                y: {
                    max: 80,
                    grid: { color: "rgba(255,255,255,0.05)" },
                    ticks: { color: "#cbd5e1" }
                }
            }
        }
    });
}

// 6. Communication Payload & Bandwidth
async function loadBandwidthData() {
    try {
        const res = await fetch("/api/bandwidth");
        const data = await res.json();
        
        document.getElementById("bw-round-kb").innerText = `${data.summary.secagg_round_kb_per_client} KB`;
        document.getElementById("bw-overhead-bytes").innerText = `${data.summary.cryptographic_overhead_bytes_per_client} B`;
        document.getElementById("bw-cum-8").innerText = `${data.summary.cumulative_8_rounds_kb_per_client} KB`;
        document.getElementById("bw-cum-25").innerText = `${data.summary.cumulative_25_rounds_kb_per_client} KB`;

        renderBandwidthChart(data);
    } catch (err) {
        console.error("Failed to load bandwidth data:", err);
    }
}

function renderBandwidthChart(data) {
    const ctx = document.getElementById("bandwidthChart").getContext("2d");
    const labels = data.payload_components.map(p => p.component);
    const bytes = data.payload_components.map(p => p.bytes);

    if (bandwidthChart) bandwidthChart.destroy();

    bandwidthChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data: bytes,
                backgroundColor: ["#06b6d4", "#3b82f6", "#10b981", "#f59e0b"],
                borderWidth: 2,
                borderColor: "#0f172a"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: "#cbd5e1", boxWidth: 12, font: { size: 11 } }
                },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` ${ctx.label}: ${ctx.raw} bytes (${((ctx.raw / 44796) * 100).toFixed(2)}%)`
                    }
                }
            }
        }
    });
}

// 7. Cryptographic Latency Benchmark
function setupCryptoBenchmark() {
    // Run initial benchmark
    triggerCryptoBenchmark();
}

async function triggerCryptoBenchmark() {
    const btn = document.getElementById("btn-run-benchmark");
    btn.disabled = true;
    btn.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        Benchmarking Flower Primitives...
    `;

    try {
        const res = await fetch("/api/crypto-benchmark", { method: "POST" });
        const result = await res.json();
        
        document.getElementById("lat-total").innerText = `${result.total_round_crypto_overhead_ms} ms`;
        document.getElementById("lat-client").innerText = `${result.total_client_crypto_overhead_ms} ms`;
        document.getElementById("lat-server").innerText = `${result.total_server_crypto_overhead_ms} ms`;
        document.getElementById("lat-timestamp").innerText = result.timestamp;

        renderCryptoChart(result);
    } catch (err) {
        console.error("Benchmark error:", err);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            Re-Run Live Cryptographic Benchmark
        `;
    }
}

function renderCryptoChart(data) {
    const ctx = document.getElementById("cryptoBenchmarkChart").getContext("2d");
    const labels = [
        "X25519 KeyGen",
        "Diffie-Hellman",
        "Shamir Create (t=3)",
        "Shamir Recon",
        "Quantization",
        "PRG Masking",
        "Server Unmasking",
        "Dequantization"
    ];
    const latencies = [
        data.client_keygen_ms,
        data.diffie_hellman_ms,
        data.shamir_create_ms,
        data.shamir_reconstruct_ms,
        data.quantization_ms,
        data.prg_expansion_ms,
        data.server_unmasking_ms,
        data.dequantization_ms
    ];

    if (cryptoBenchmarkChart) cryptoBenchmarkChart.destroy();

    cryptoBenchmarkChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Execution Latency (ms)",
                data: latencies,
                backgroundColor: [
                    "#38bdf8", "#818cf8", "#34d399", "#a78bfa", "#f59e0b", "#fb923c", "#f43f5e", "#2dd4bf"
                ],
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` Latency: ${ctx.raw} ms`
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: "#cbd5e1", maxRotation: 30, minRotation: 30, font: { size: 10 } }
                },
                y: {
                    title: { display: true, text: "Milliseconds (ms)", color: "#94a3b8" },
                    grid: { color: "rgba(255,255,255,0.05)" },
                    ticks: { color: "#94a3b8" }
                }
            }
        }
    });
}
