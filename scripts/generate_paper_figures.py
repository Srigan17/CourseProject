import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs('figures', exist_ok=True)

# Set global styles
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Times']
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 9
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 8
plt.rcParams['figure.titlesize'] = 11

# ==========================================
# FIGURE 1: SYSTEM ARCHITECTURE
# ==========================================
fig, ax = plt.subplots(figsize=(7.16, 3.2), dpi=300)
ax.axis('off')

from matplotlib.patches import FancyBboxPatch

# Bounding boxes for main components
# 1. Healthcare Data & FHIR Ingestion (Left)
rect_fhir = FancyBboxPatch((0.02, 0.1), 0.22, 0.8, facecolor='#EBF5FB', edgecolor='#2980B9', lw=1.5, boxstyle="round,pad=0.01")
ax.add_patch(rect_fhir)
ax.text(0.13, 0.85, "Phase 1: Interoperability", ha='center', va='center', weight='bold', color='#1B4F72', fontsize=9)
ax.text(0.13, 0.77, "Wearable Raw Data\n(Apple Watch/Fitbit)", ha='center', va='center', fontsize=8)
ax.text(0.13, 0.63, "HL7 FHIR Mapping\n• Patient Resource\n• Device Resource\n• Observation Bundles\n• Standardized Vocab", ha='center', va='center', fontsize=7.5, bbox=dict(boxstyle="square,pad=0.3", fc='white', ec='#AED6F1'))
ax.text(0.13, 0.40, "Stratified Partitioning\n(k = 4 Clinical Clients)\nExact 731 records/client", ha='center', va='center', fontsize=7.5, bbox=dict(boxstyle="square,pad=0.3", fc='white', ec='#AED6F1'))
ax.text(0.13, 0.18, "Held-Out Test Partition\n(N = 732 records, 20%)\nStrictly Isolated", ha='center', va='center', fontsize=7.5, weight='bold', color='#78281F', bbox=dict(boxstyle="square,pad=0.3", fc='#FADBD8', ec='#E74C3C'))

# Arrow FHIR to Clients
ax.annotate("", xy=(0.27, 0.55), xytext=(0.24, 0.55), arrowprops=dict(arrowstyle="->", lw=1.5, color='#1B4F72'))

# 2. Decentralized Clients & DP-SGD (Center-Left)
rect_clients = FancyBboxPatch((0.27, 0.1), 0.30, 0.8, facecolor='#FEF9E7', edgecolor='#D4AC0D', lw=1.5, boxstyle="round,pad=0.01")
ax.add_patch(rect_clients)
ax.text(0.42, 0.85, "Phase 2: Local DP-SGD", ha='center', va='center', weight='bold', color='#7D6608', fontsize=9)
ax.text(0.42, 0.73, "Tuned MLP (16->128->64->32->6)\n12,710 Parameters | AdamW", ha='center', va='center', fontsize=7.5, bbox=dict(boxstyle="square,pad=0.3", fc='white', ec='#F9E79F'))
ax.text(0.42, 0.53, "Per-Sample Gradient Clipping\n||g_i||_2 <= C (C = 1.0)", ha='center', va='center', fontsize=7.5, bbox=dict(boxstyle="square,pad=0.3", fc='white', ec='#F9E79F'))
ax.text(0.42, 0.36, "Calibrated Gaussian Noise\ng_t + N(0, sigma^2 C^2 I)\nsigma in {0.5, 1.0, 1.5, 2.0}", ha='center', va='center', fontsize=7.5, bbox=dict(boxstyle="square,pad=0.3", fc='white', ec='#F9E79F'))
ax.text(0.42, 0.18, "Persistent PRV/RDP Accountant\nq = 1/23, 1725 Accounted Steps\nRecord-Level (epsilon, delta)-DP", ha='center', va='center', fontsize=7.5, weight='bold', color='#145A32', bbox=dict(boxstyle="square,pad=0.3", fc='#D5F5E3', ec='#2ECC71'))

# Arrow Clients to SecAgg
ax.annotate("", xy=(0.60, 0.55), xytext=(0.57, 0.55), arrowprops=dict(arrowstyle="->", lw=1.5, color='#7D6608'))

# 3. Secure Aggregation Engine (Center-Right)
rect_secagg = FancyBboxPatch((0.60, 0.1), 0.22, 0.8, facecolor='#E8F8F5', edgecolor='#16A085', lw=1.5, boxstyle="round,pad=0.01")
ax.add_patch(rect_secagg)
ax.text(0.71, 0.85, "Phase 3: SecAgg+ Layer", ha='center', va='center', weight='bold', color='#0E6251', fontsize=9)
ax.text(0.71, 0.71, "Fixed-Point Quantization\nFloat -> Int32\nRange [-8.0, 8.0], 22-bit", ha='center', va='center', fontsize=7.5, bbox=dict(boxstyle="square,pad=0.3", fc='white', ec='#A3E4D7'))
ax.text(0.71, 0.51, "Dual Mask Generation\n• Pairwise Diffie-Hellman s_u,v\n• Individual Self-Mask b_u", ha='center', va='center', fontsize=7.5, bbox=dict(boxstyle="square,pad=0.3", fc='white', ec='#A3E4D7'))
ax.text(0.71, 0.31, "(t, n) Shamir Secret Sharing\nThreshold t=3, n=4 Clients\nDropout-Resilient Recovery", ha='center', va='center', fontsize=7.5, bbox=dict(boxstyle="square,pad=0.3", fc='white', ec='#A3E4D7'))
ax.text(0.71, 0.16, "Masked Vector Transmission\ny_u = x_u + p_u + sum s_u,v mod M", ha='center', va='center', fontsize=7, color='#78281F')

# Arrow SecAgg to Server
ax.annotate("", xy=(0.85, 0.55), xytext=(0.82, 0.55), arrowprops=dict(arrowstyle="->", lw=1.5, color='#16A085'))

# 4. Global Server Aggregation (Right)
rect_server = FancyBboxPatch((0.85, 0.1), 0.13, 0.8, facecolor='#F4ECF7', edgecolor='#8E44AD', lw=1.5, boxstyle="round,pad=0.01")
ax.add_patch(rect_server)
ax.text(0.915, 0.85, "Federated Server", ha='center', va='center', weight='bold', color='#512E5F', fontsize=9)
ax.text(0.915, 0.68, "Sum Masked Vectors\nsum y_u mod M\nPairwise Masks Cancel", ha='center', va='center', fontsize=7.5, bbox=dict(boxstyle="square,pad=0.2", fc='white', ec='#D2B4DE'))
ax.text(0.915, 0.48, "Reconstruct Self-Masks\nvia t=3 Shamir Shares\nUnmask Exact Sum", ha='center', va='center', fontsize=7.5, bbox=dict(boxstyle="square,pad=0.2", fc='white', ec='#D2B4DE'))
ax.text(0.915, 0.30, "Equal Weight p_c=0.25\nDequantize to Float\nGlobal Model Update", ha='center', va='center', fontsize=7.5, bbox=dict(boxstyle="square,pad=0.2", fc='white', ec='#D2B4DE'))
ax.text(0.915, 0.15, "Broadcast Global W_t\n(25 Rounds Complete)", ha='center', va='center', fontsize=7, weight='bold', color='#1B4F72')

# Feedback loop arrow from Server back to Clients
ax.annotate("", xy=(0.42, 0.92), xytext=(0.915, 0.92), arrowprops=dict(arrowstyle="->", lw=1.2, color='#8E44AD', linestyle='dashed'))
ax.text(0.67, 0.94, "Global Parameter Distribution (Rounds 1 .. 25)", ha='center', va='bottom', fontsize=7.5, style='italic', color='#512E5F')

plt.tight_layout()
fig.savefig('figures/fig1_system_architecture.pdf', format='pdf', bbox_inches='tight')
fig.savefig('figures/fig1_system_architecture.png', format='png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Fig 1 generated successfully.")

# ==========================================
# FIGURE 2: SECAGG+ PROTOCOL INTERACTION FLOW
# ==========================================
fig, ax = plt.subplots(figsize=(7.16, 3.0), dpi=300)
ax.axis('off')

# Timeline columns: Client u, Client v, Federated Server
ax.text(0.15, 0.92, "Client u (Active)", ha='center', va='center', weight='bold', fontsize=8.5, bbox=dict(boxstyle="round,pad=0.3", fc='#EBF5FB', ec='#2980B9'))
ax.text(0.50, 0.92, "Client v (Peer Client)", ha='center', va='center', weight='bold', fontsize=8.5, bbox=dict(boxstyle="round,pad=0.3", fc='#EBF5FB', ec='#2980B9'))
ax.text(0.85, 0.92, "Untrusted Server", ha='center', va='center', weight='bold', fontsize=8.5, bbox=dict(boxstyle="round,pad=0.3", fc='#FADBD8', ec='#E74C3C'))

# Vertical lifelines
ax.plot([0.15, 0.15], [0.85, 0.05], color='#BDC3C7', lw=1.2, linestyle=':')
ax.plot([0.50, 0.50], [0.85, 0.05], color='#BDC3C7', lw=1.2, linestyle=':')
ax.plot([0.85, 0.85], [0.85, 0.05], color='#BDC3C7', lw=1.2, linestyle=':')

# Round 0: Key Exchange
ax.text(0.02, 0.77, "Round 0\nKey Setup", ha='left', va='center', weight='bold', fontsize=7.5, color='#2C3E50')
ax.annotate("", xy=(0.84, 0.77), xytext=(0.16, 0.77), arrowprops=dict(arrowstyle="->", lw=1.0, color='#2980B9'))
ax.text(0.50, 0.79, "Advertise public keys (c_u, s_u)", ha='center', va='bottom', fontsize=7.2, color='#1B4F72')
ax.annotate("", xy=(0.16, 0.72), xytext=(0.84, 0.72), arrowprops=dict(arrowstyle="->", lw=1.0, color='#8E44AD'))
ax.text(0.50, 0.70, "Broadcast peer key dictionary to all clients", ha='center', va='top', fontsize=7.2, color='#512E5F')

# Round 1: Share Distribution
ax.text(0.02, 0.58, "Round 1\nSecret Share", ha='left', va='center', weight='bold', fontsize=7.5, color='#2C3E50')
ax.text(0.15, 0.58, "Generate b_u\nCompute s_u,v = DH(s_u, s_v)\nCreate Shamir shares (t=3, n=4)", ha='center', va='center', fontsize=6.8, bbox=dict(boxstyle="square,pad=0.2", fc='white', ec='#BDC3C7'))
ax.annotate("", xy=(0.84, 0.54), xytext=(0.16, 0.54), arrowprops=dict(arrowstyle="->", lw=1.0, color='#2980B9'))
ax.text(0.50, 0.55, "Encrypted shares Enc_c_v(share_b_u,v || share_s_u,v)", ha='center', va='bottom', fontsize=7, color='#1B4F72')
ax.annotate("", xy=(0.16, 0.49), xytext=(0.84, 0.49), arrowprops=dict(arrowstyle="->", lw=1.0, color='#8E44AD'))
ax.text(0.50, 0.47, "Forward encrypted share bundles to intended recipients", ha='center', va='top', fontsize=7, color='#512E5F')

# Round 2: Masked Update Collection
ax.text(0.02, 0.35, "Round 2\nMasked Input", ha='left', va='center', weight='bold', fontsize=7.5, color='#2C3E50')
ax.text(0.15, 0.35, "Local DP-SGD update x_u\nQuantize x_u -> x_bar_u\ny_u = x_bar_u + PRG(b_u) + sum Delta_u,v mod M", ha='center', va='center', fontsize=6.8, bbox=dict(boxstyle="square,pad=0.2", fc='white', ec='#BDC3C7'))
ax.annotate("", xy=(0.84, 0.33), xytext=(0.16, 0.33), arrowprops=dict(arrowstyle="->", lw=1.0, color='#2980B9'))
ax.text(0.50, 0.34, "Send masked integer vector y_u", ha='center', va='bottom', fontsize=7.2, color='#1B4F72')

# Round 3: Unmasking & Recovery
ax.text(0.02, 0.17, "Round 3\nUnmasking", ha='left', va='center', weight='bold', fontsize=7.5, color='#2C3E50')
ax.annotate("", xy=(0.16, 0.20), xytext=(0.84, 0.20), arrowprops=dict(arrowstyle="->", lw=1.0, color='#8E44AD'))
ax.text(0.50, 0.21, "Request self-mask shares (survivors) / DH shares (dropouts)", ha='center', va='bottom', fontsize=7, color='#512E5F')
ax.annotate("", xy=(0.84, 0.13), xytext=(0.16, 0.13), arrowprops=dict(arrowstyle="->", lw=1.0, color='#2980B9'))
ax.text(0.50, 0.14, "Submit requested shares (>= t = 3 required)", ha='center', va='bottom', fontsize=7.2, color='#1B4F72')

# Server completion box
ax.text(0.85, 0.07, "Server cancels pairwise masks sum Delta_u,v = 0;\nReconstructs PRG(b_u) to recover sum x_bar_u;\nDequantizes to exact average global weights W_t+1", ha='center', va='center', fontsize=6.8, weight='bold', color='#145A32', bbox=dict(boxstyle="square,pad=0.2", fc='#D5F5E3', ec='#27AE60'))

plt.tight_layout()
fig.savefig('figures/fig2_secagg_workflow.pdf', format='pdf', bbox_inches='tight')
fig.savefig('figures/fig2_secagg_workflow.png', format='png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Fig 2 generated successfully.")

# ==========================================
# FIGURE 3: PRIVACY-UTILITY TRADEOFF CURVE
# ==========================================
fig, ax1 = plt.subplots(figsize=(3.45, 2.7), dpi=300)

sigmas = [0.5, 1.0, 1.5, 2.0]
prv_eps = [72.55, 12.77, 6.42, 4.29]

# Verified sample standard deviation metrics
acc_b_means = [45.98, 41.56, 39.54, 38.47]
acc_b_stds = [1.75, 1.52, 1.68, 0.99]

acc_d_means = [46.07, 41.56, 39.54, 38.44]
acc_d_stds = [1.82, 1.56, 1.62, 0.93]

# Reference baselines
ref_a_mean = 67.60
ref_a_std = 0.66
ref_c_mean = 67.92
ref_c_std = 1.16

# Plotting Accuracy vs Epsilon
ax1.errorbar(prv_eps, acc_b_means, yerr=acc_b_stds, fmt='o-', color='#2980B9', lw=1.5, capsize=3, label='Config B: DP-FedAvg', markersize=5)
ax1.errorbar(prv_eps, acc_d_means, yerr=acc_d_stds, fmt='s--', color='#E74C3C', lw=1.5, capsize=3, label='Config D: DP + SecAgg', markersize=5)

# Reference baseline horizontal lines
ax1.axhline(ref_a_mean, color='#27AE60', linestyle=':', lw=1.2, label='Config A: Plaintext (67.60%)')
ax1.axhline(ref_c_mean, color='#8E44AD', linestyle='-.', lw=1.0, label='Config C: SecAgg (67.92%)')
ax1.axhline(16.67, color='#7F8C8D', linestyle='--', lw=0.8, label='Random Chance (16.67%)')

ax1.set_xlabel(r'Privacy Parameter $\epsilon$ (PRV Accountant, $\delta=10^{-5}$)', fontsize=8.5)
ax1.set_ylabel(r'Test Accuracy (%) $\pm$ 1 $\sigma_{\rm sample}$', fontsize=8.5)
ax1.set_xscale('log')
ax1.set_xticks([4.29, 6.42, 12.77, 72.55])
ax1.get_xaxis().set_major_formatter(plt.ScalarFormatter())
ax1.set_ylim(10, 75)
ax1.grid(True, linestyle=':', alpha=0.6)

# Annotate noise multipliers
for i, txt in enumerate([r'$\sigma=2.0$', r'$\sigma=1.5$', r'$\sigma=1.0$', r'$\sigma=0.5$']):
    ax1.annotate(txt, (prv_eps[i], acc_d_means[i]), textcoords="offset points", xytext=(0, -12 if i % 2 == 0 else 8), ha='center', fontsize=7, color='#78281F')

ax1.legend(loc='lower right', frameon=True, fontsize=6.8, facecolor='white', framealpha=0.9)

plt.tight_layout()
fig.savefig('figures/fig3_privacy_utility_tradeoff.pdf', format='pdf', bbox_inches='tight')
fig.savefig('figures/fig3_privacy_utility_tradeoff.png', format='png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Fig 3 generated successfully.")
