import json

with open("results/dp_track2/phase3_dp_fedavg_results.json") as f:
    d = json.load(f)

print("Configuration | Test Accuracy | Test Macro F1 | Cohen Kappa | Test Loss | PRV eps | RDP eps | Steps | Acc Utility Gap")
print("-" * 115)

# Reference plaintext baseline:
print(f"Plaintext (Ref)| 67.60% +/- 0.59% | 67.89% +/- 0.55% | 0.6104 +/- 0.0076 | 0.9189 +/- 0.0183 |    N/A  |    N/A  |  1725 |   0.00%")

for k, v in d["configurations"].items():
    s = v["summary"]
    acc = s["accuracy"]
    f1 = s["f1"]
    kappa = s["kappa"]
    loss = s["loss"]
    p = s["privacy"]
    u = s["utility_degradation"]
    label = k.replace("_", "=")
    print(f"DP {label:<11} | {acc['mean']*100:.2f}% +/- {acc['std']*100:.2f}% | {f1['mean']*100:.2f}% +/- {f1['std']*100:.2f}% | {kappa['mean']:.4f} +/- {kappa['std']:.4f} | {loss['mean']:.4f} +/- {loss['std']:.4f} | {p['runtime_epsilon_prv']:7.4f} | {p['runtime_epsilon_rdp']:7.4f} | {p['runtime_accounted_steps']} | {u['delta_accuracy']*100:+.2f}%")

print("\nPer-Seed Breakdown:")
for k, v in d["configurations"].items():
    print(f"\n--- {k} ---")
    for s_id in ["42", "123", "456", "789", "2026"]:
        r = v["per_seed"][s_id]
        print(f"  Seed {s_id:<4}: Acc = {r['accuracy']*100:.2f}%, F1 = {r['f1']*100:.2f}%, Kappa = {r['kappa']:.4f}, Loss = {r['loss']:.4f}, Time = {r['training_time_seconds']}s")
