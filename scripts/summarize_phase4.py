import json

with open("results/secagg_track2/phase4_secagg_results.json") as f:
    d = json.load(f)

print("=" * 115)
print("             PHASE 4 BENCHMARK: COMPLETE 4-WAY CONFIGURATION COMPARISON TABLE")
print("=" * 115)
print(f"{'Configuration':<28} | {'Accuracy (mean+/-std)':<20} | {'Macro F1':<10} | {'PRV eps':<8} | {'Delta vs Matched':<16} | {'Total Penalty'}")
print("-" * 115)

# Config A: Plaintext FedAvg
ref_a = d["metadata"]["reference_benchmarks"]["config_a_plaintext_fedavg"]
print(f"{'Config A: Plaintext FedAvg':<28} | {ref_a['accuracy']*100:.2f}% +/- 0.59%        | {ref_a['f1']*100:.2f}%     | {'N/A':<8} | {'Reference':<16} | {'0.00%'}")

# Config C: SecAgg-FedAvg (No DP)
c_sum = d["configurations"]["config_c_secagg_plaintext"]["summary"]
c_gap = c_sum["quantization_impact"]["delta_accuracy_quantization"]
print(f"{'Config C: SecAgg-FedAvg':<28} | {c_sum['accuracy']['mean']*100:.2f}% +/- {c_sum['accuracy']['std']*100:.2f}%        | {c_sum['f1']['mean']*100:.2f}%     | {'N/A':<8} | {f'{c_gap*100:+.2f}% (vs A)':<16} | {f'{c_gap*100:+.2f}%'}")

print("-" * 115)

# Config B and D for each sigma
with open("results/dp_track2/phase3_dp_fedavg_results.json") as f:
    dp_data = json.load(f)

for sigma_key in ["sigma_0.5", "sigma_1.0", "sigma_1.5", "sigma_2.0"]:
    sigma_val = sigma_key.split("_")[1]
    b_sum = dp_data["configurations"][sigma_key]["summary"]
    d_sum = d["configurations"]["config_d_full_framework"][sigma_key]["summary"]
    comp = d_sum["comparative_impact"]
    
    label_b = f"Config B: DP-FedAvg (s={sigma_val})"
    label_d = f"Config D: Full (DP+SecAgg s={sigma_val})"
    
    b_pen = ref_a['accuracy'] - b_sum['accuracy']['mean']
    delta_b_str = f"{comp['delta_secagg_on_dp']*100:+.2f}% (vs B)"
    tot_pen_str = f"+{comp['total_utility_penalty_vs_plaintext']*100:.2f}%"
    print(f"{label_b:<28} | {b_sum['accuracy']['mean']*100:.2f}% +/- {b_sum['accuracy']['std']*100:.2f}%        | {b_sum['f1']['mean']*100:.2f}%     | {b_sum['privacy']['runtime_epsilon_prv']:<8.2f} | {'Phase 3 DP Ref':<16} | +{b_pen*100:.2f}%")
    print(f"{label_d:<28} | {d_sum['accuracy']['mean']*100:.2f}% +/- {d_sum['accuracy']['std']*100:.2f}%        | {d_sum['f1']['mean']*100:.2f}%     | {d_sum['privacy']['runtime_epsilon_prv']:<8.2f} | {delta_b_str:<16} | {tot_pen_str}")
    print("." * 115)

print("\nPer-Seed Breakdown for Config C (SecAgg-FedAvg):")
for s_id in ["42", "123", "456", "789", "2026"]:
    r = d["configurations"]["config_c_secagg_plaintext"]["per_seed"][s_id]
    print(f"  Seed {s_id:<4}: Acc = {r['accuracy']*100:.2f}%, F1 = {r['f1']*100:.2f}%, Kappa = {r['kappa']:.4f}, Loss = {r['loss']:.4f}")

print("\nPer-Seed Breakdown for Config D (DP + SecAgg):")
for sigma_key in ["sigma_0.5", "sigma_1.0", "sigma_1.5", "sigma_2.0"]:
    print(f"\n--- {sigma_key} ---")
    for s_id in ["42", "123", "456", "789", "2026"]:
        r = d["configurations"]["config_d_full_framework"][sigma_key]["per_seed"][s_id]
        print(f"  Seed {s_id:<4}: Acc = {r['accuracy']*100:.2f}%, F1 = {r['f1']*100:.2f}%, Kappa = {r['kappa']:.4f}, Loss = {r['loss']:.4f}")
