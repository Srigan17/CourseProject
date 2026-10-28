import json

with open("results/baseline_track2/track2_mlp_baseline_results.json") as f:
    orig = json.load(f)

with open("results/baseline_track2/track2_tuned_mlp_baseline_results.json") as f:
    tuned = json.load(f)

print("Configuration | Orig Accuracy | Orig Macro F1 | Tuned Accuracy | Tuned Macro F1 | Tuned Kappa | Tuned Loss")
print("-" * 105)

c_o = orig["centralized"]["summary"]
c_t = tuned["centralized"]["summary"]
print(f"Centralized   | {c_o['accuracy']['mean']*100:.2f}% +/- {c_o['accuracy']['std']*100:.2f}% | {c_o['f1']['mean']*100:.2f}% +/- {c_o['f1']['std']*100:.2f}% | {c_t['accuracy']['mean']*100:.2f}% +/- {c_t['accuracy']['std']*100:.2f}% | {c_t['f1']['mean']*100:.2f}% +/- {c_t['f1']['std']*100:.2f}% | {c_t['kappa']['mean']:.4f} +/- {c_t['kappa']['std']:.4f} | {c_t['loss']['mean']:.4f} +/- {c_t['loss']['std']:.4f}")

for k in ["k2", "k4", "k8"]:
    s_o = orig["federated"][k]["summary"]
    s_t = tuned["federated"][k]["summary"]
    label = f"FedAvg ({k.upper()})"
    print(f"{label:<13} | {s_o['accuracy']['mean']*100:.2f}% +/- {s_o['accuracy']['std']*100:.2f}% | {s_o['f1']['mean']*100:.2f}% +/- {s_o['f1']['std']*100:.2f}% | {s_t['accuracy']['mean']*100:.2f}% +/- {s_t['accuracy']['std']*100:.2f}% | {s_t['f1']['mean']*100:.2f}% +/- {s_t['f1']['std']*100:.2f}% | {s_t['kappa']['mean']:.4f} +/- {s_t['kappa']['std']:.4f} | {s_t['loss']['mean']:.4f} +/- {s_t['loss']['std']:.4f}")

print("\nDelta Increases (Accuracy):")
print(f"Centralized: +{(c_t['accuracy']['mean'] - c_o['accuracy']['mean'])*100:.2f}%")
for k in ["k2", "k4", "k8"]:
    diff = (tuned['federated'][k]['summary']['accuracy']['mean'] - orig['federated'][k]['summary']['accuracy']['mean']) * 100
    print(f"FedAvg ({k.upper()}): +{diff:.2f}%")

print("\nDelta Increases (Macro F1):")
print(f"Centralized: +{(c_t['f1']['mean'] - c_o['f1']['mean'])*100:.2f}%")
for k in ["k2", "k4", "k8"]:
    diff = (tuned['federated'][k]['summary']['f1']['mean'] - orig['federated'][k]['summary']['f1']['mean']) * 100
    print(f"FedAvg ({k.upper()}): +{diff:.2f}%")
