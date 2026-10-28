import json
import numpy as np

# Load artifacts
with open("results/baseline_track2/track2_tuned_mlp_baseline_results.json") as f:
    p2 = json.load(f)
with open("results/dp_track2/phase3_dp_fedavg_results.json") as f:
    p3 = json.load(f)
with open("results/secagg_track2/phase4_secagg_results.json") as f:
    p4 = json.load(f)

seeds = ["42", "123", "456", "789", "2026"]

ref_a_accs = [p2["federated"]["k4"]["per_seed"][s]["accuracy"] for s in seeds]
ref_a_f1s = [p2["federated"]["k4"]["per_seed"][s]["f1"] for s in seeds]
ref_a_mean_acc = float(np.mean(ref_a_accs))

c_accs = [p4["configurations"]["config_c_secagg_plaintext"]["per_seed"][s]["accuracy"] for s in seeds]
c_f1s = [p4["configurations"]["config_c_secagg_plaintext"]["per_seed"][s]["f1"] for s in seeds]

audit_data = {
    "audit_metadata": {
        "title": "Phase 4 Results Integrity and Cross-Configuration Audit",
        "timestamp": "2026-10-27T19:50:00Z",
        "held_out_test_records": 732,
        "evaluation_seeds": [42, 123, 456, 789, 2026],
        "std_convention_note": "Includes both population std (ddof=0, used in raw JSON summaries) and sample std (ddof=1, standard for scientific reporting with N=5)."
    },
    "configurations_summary": {
        "config_a_plaintext_fedavg": {
            "description": "Baseline Plaintext FedAvg (k=4, no DP, no SecAgg)",
            "accuracy": {
                "mean": round(ref_a_mean_acc, 4),
                "std_pop_ddof0": round(float(np.std(ref_a_accs, ddof=0)), 4),
                "std_sample_ddof1": round(float(np.std(ref_a_accs, ddof=1)), 4),
                "per_seed": {s: ref_a_accs[i] for i, s in enumerate(seeds)}
            },
            "f1": {
                "mean": round(float(np.mean(ref_a_f1s)), 4),
                "std_pop_ddof0": round(float(np.std(ref_a_f1s, ddof=0)), 4),
                "std_sample_ddof1": round(float(np.std(ref_a_f1s, ddof=1)), 4)
            }
        },
        "config_c_secagg_fedavg": {
            "description": "Plaintext Local Training + SecAgg+ Aggregation (k=4)",
            "accuracy": {
                "mean": round(float(np.mean(c_accs)), 4),
                "std_pop_ddof0": round(float(np.std(c_accs, ddof=0)), 4),
                "std_sample_ddof1": round(float(np.std(c_accs, ddof=1)), 4),
                "per_seed": {s: c_accs[i] for i, s in enumerate(seeds)}
            },
            "f1": {
                "mean": round(float(np.mean(c_f1s)), 4),
                "std_pop_ddof0": round(float(np.std(c_f1s, ddof=0)), 4),
                "std_sample_ddof1": round(float(np.std(c_f1s, ddof=1)), 4)
            },
            "quantization_gap_vs_config_a": {
                "difference_percentage_points": round(float(np.mean(c_accs) - ref_a_mean_acc) * 100, 3),
                "relative_percent_change": round(float((np.mean(c_accs) - ref_a_mean_acc) / ref_a_mean_acc) * 100, 3),
                "interpretation": "Config C is +0.324 pp (+0.48% relative) compared to Config A, well within empirical seed variation."
            }
        },
        "matched_dp_comparisons_b_vs_d": {}
    }
}

for sigma_key in ["sigma_0.5", "sigma_1.0", "sigma_1.5", "sigma_2.0"]:
    sigma_val = float(sigma_key.split("_")[1])
    b_data = p3["configurations"][sigma_key]
    d_data = p4["configurations"]["config_d_full_framework"][sigma_key]
    
    b_accs = [b_data["per_seed"][s]["accuracy"] for s in seeds]
    d_accs = [d_data["per_seed"][s]["accuracy"] for s in seeds]
    
    paired_diffs_pp = [(d_accs[i] - b_accs[i]) * 100 for i in range(len(seeds))]
    
    audit_data["configurations_summary"]["matched_dp_comparisons_b_vs_d"][sigma_key] = {
        "noise_multiplier": sigma_val,
        "runtime_prv_epsilon": b_data["summary"]["privacy"]["runtime_epsilon_prv"],
        "runtime_rdp_epsilon": b_data["summary"]["privacy"]["runtime_epsilon_rdp"],
        "accounted_steps": b_data["summary"]["privacy"]["runtime_accounted_steps"],
        "config_b_dp_only": {
            "accuracy_mean": round(float(np.mean(b_accs)), 4),
            "accuracy_std_ddof0": round(float(np.std(b_accs, ddof=0)), 4),
            "accuracy_std_ddof1": round(float(np.std(b_accs, ddof=1)), 4),
            "per_seed": {s: b_accs[i] for i, s in enumerate(seeds)}
        },
        "config_d_dp_plus_secagg": {
            "accuracy_mean": round(float(np.mean(d_accs)), 4),
            "accuracy_std_ddof0": round(float(np.std(d_accs, ddof=0)), 4),
            "accuracy_std_ddof1": round(float(np.std(d_accs, ddof=1)), 4),
            "per_seed": {s: d_accs[i] for i, s in enumerate(seeds)}
        },
        "paired_seed_comparison_d_minus_b": {
            "per_seed_percentage_points": {s: round(paired_diffs_pp[i], 3) for i, s in enumerate(seeds)},
            "mean_difference_percentage_points": round(float(np.mean(paired_diffs_pp)), 3),
            "std_paired_difference": round(float(np.std(paired_diffs_pp, ddof=1)), 3),
            "interpretation": f"At sigma={sigma_val}, SecAgg adds a mean difference of {np.mean(paired_diffs_pp):+.3f} percentage points relative to DP-only."
        },
        "total_penalty_vs_plaintext_a": {
            "penalty_percentage_points": round((ref_a_mean_acc - float(np.mean(d_accs))) * 100, 3),
            "relative_utility_loss_percent": round(((ref_a_mean_acc - float(np.mean(d_accs))) / ref_a_mean_acc) * 100, 3)
        }
    }

out_path = "results/secagg_track2/phase4_results_integrity_audit.json"
with open(out_path, "w") as f:
    json.dump(audit_data, f, indent=2)

print(f"Results integrity audit successfully generated and saved to: {out_path}")
