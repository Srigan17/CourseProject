import os
import typst
import pypdf

typst_content = r'''
#set page(
  paper: "us-letter",
  margin: (x: 18mm, top: 19mm, bottom: 20mm)
)

#set text(
  font: "Times New Roman",
  size: 9.35pt,
  lang: "en"
)

#set par(
  justify: true,
  leading: 0.49em,
  first-line-indent: 1.2em
)

// Header / Title Block
#align(center)[
  #v(-3mm)
  #text(size: 17pt, weight: "bold")[
    Secure FHIR-Based Federated Learning Framework for Wearable Healthcare Data Using Differential Privacy and Secure Aggregation
  ]
  #v(3mm)
  #text(size: 9.8pt)[
    #super[1]K.Srigan, #super[2]K.Bala Venkat, #super[3]K.Sasank, #super[4]Sangeetha S#super[\*]
  ]
  #v(1.2mm)
  #text(size: 9.0pt)[
    School of Computer Science and Engineering    Vellore Institute of Technology, Vellore 632014, India
  ]
  #v(0.8mm)
  #text(size: 8.3pt, font: "Courier New")[
    #super[1]kakaraparthi.srigan2023\@vitstudent.ac.in #h(3mm)
    #super[2]kancharla.naga2023\@vitstudent.ac.in #h(3mm)
    #super[3]kandepalli.bala2023\@vitstudent.ac.in #h(3mm)
    #super[4]s.sangeetha\@vit.ac.in#super[\*]
  ]
  #v(2.5mm)
]

#show: columns.with(2, gutter: 5mm)

#text(weight: "bold", style: "italic")[Abstract]---The promise of consumer health wearables with continuous physiological and physical activity measurements holds great prospects for proactive health care, however the centralized collection of biometric data raises significant issues related to privacy, legislation and liability. While Federated Learning (FL) enables distributed model training using shared models while not revealing underlying data, traditional federated learning systems are vulnerable to attacks such as reconstruction, gradient inversion and membership inference attacks. Furthermore, data from wearable devices collected in clinical environments suffers from semantic fragmentation due to different proprietary data formats used by various vendors. In this paper, we introduce a defense-in-depth federated learning approach that is based on combination of data normalization with Fast Healthcare Interoperability Resources (HL7 FHIR Release 4) with client side Differential Privacy and multi-party Secure Aggregation (SecAgg+). We apply our proposed framework to benchmark dataset Harvard Apple Watch and Fitbit (3,656 records, 6 physical activities) in 4 architectures and 5 seed experiments, $N = 732$. Practically speaking, we demonstrate that the fixedpoint Flower-based SecAgg+ framework introduces essentially no utility loss ($67.92\% plus.minus 1.16\%$ accuracy compared to plaintext baseline of $67.60\% plus.minus 0.66\%$; improvement of $+0.32$ percentage points). By combining our technique with client-side DPSGD with PRV accounting, our technique allows us to maintain $(epsilon=4.29, delta=10^(-5))$ differential privacy guarantees at noise multiplier $sigma=2.0$ with $38.44\% plus.minus 0.93\%$ test accuracy on a six-class classification problem ($+21.77$ percentage points above random guess). We verify that SecAgg+ does not result in any utility loss for DP models ($|Delta| <= 0.086$ percentage points), thus demonstrating empirical feasibility of defense-in-depth for distributed digital health applications.

#v(1mm)
#text(weight: "bold", style: "italic")[Index Terms]---Federated Learning; Wearable Healthcare; Fast Healthcare Interoperability Resources (FHIR); Differential Privacy; DPSGD; Secure Aggregation; Shamir Secret Sharing; Digital Biomarkers.

#footnote[#super[\*]Corresponding author (Project Guide): s.sangeetha\@vit.ac.in]

= I. INTRODUCTION
The extensive use of consumer-grade smartwatches and biometric wristbands has brought about the continuous collection of high-resolution digital biomarkers including heart-rate kinetics, step frequency, and accelerometric energy expenditure @akhmetov2025auto. The physiological markers aid in automated physical activity recognition (HAR), cardiac condition detection, and longitudinal metabolic profiling. However, continuous transmission of fine-grained personal time-series data to centralized cloud databases violates the right of the patient, poses serious privacy concerns, and goes against stringent regulations such as HIPAA and GDPR @rieke2020future, @kaissis2020secure.

Federated Learning (FL) @mcmahan2017communication has been proposed as an appealing distributed solution where clinical edge nodes or patient devices develop local models collectively without transmitting raw sensor telemetry to the cloud. With the exchange of only temporary model parameter updates with the server, FL theoretically avoids direct data exposure. Nonetheless, adversarial machine learning has shown that raw FL model updates are inherently unprivate. Semihonest or malicious servers can execute deep gradient inversion, attribute reconstruction, and membership inference attacks to reverse engineer the sensor patterns of patients or identify participation of clients @abadi2016deep, @kairouz2021advances.

Two different privacy-preserving approaches to counteract such limitations have been proposed:
- *Differential Privacy (DP):* Adding noise to the gradients of the parameters on the training dataset in order to limit the statistical impact of each single training datum @abadi2016deep, @dwork2014algorithmic.
- *Secure Aggregation (SecAgg+):* Using cryptographic masking, Diffie-Hellman key exchange and Shamir's secret sharing protocol guarantees that the aggregating server will have access only to the sum of the clients' updates, being cryptographically blind to all individual clients' trajectories @bonawitz2017practical, @bell2020secaggplus.

Notably, however, neither one of such solutions in isolation is sufficient for healthcare data environments. Without SecAgg, DP would expose the perturbed individual updates to an untrusted server, while without DP, SecAgg would expose the aggregated global model to the post-aggregation inference attacks on the aggregated output. Besides, distributed wearable telemetry in the real-world healthcare environment suffers from a syntax and semantic fragmentation due to the device schemas being proprietary.

To address these interrelated problems, the current research work introduces an end-to-end federated learning defence in depth architecture that facilitates clinical data interoperability along with dual layer protection using cryptography and differential privacy techniques.

The primary contributions made in this research paper are:
1. *Interoperable Clinical Data Schema Mapping:* We propose an interoperable HL7 FHIR (Release 4) normalisation pipeline where we map multimodal accelerometer and cardiograph telemetry data to patient, device and observation FHIR bundles.
2. *Defence In Depth Architecture with Dual Layer Protection:* We introduce a client side DPSGD along with PRV accounting along with a fixed-point SecAgg+ scheme using flower library, addressing problems related to communication and trust in the server.
3. *Experimental Verification Audit Benchmark:* We conduct an experimental audit verification benchmark using 25 runs with 5 canonical seeds ($N = 732$ test records) for four configurations---Plaintext FedAvg (A), DPonly FedAvg (B), SecAggonly FedAvg (C) and DP + SecAgg (D).

The structure of the rest of the paper is as follows: In Section II, we survey the existing literature on the topic. Section III presents the problem statement and threat model. Section IV details the FHIR interoperability architecture. Section V describes our federated DP-SGD and SecAgg+ framework. Section VI discusses our experiments and setup. Section VII shows our results. Section VIII outlines the limitations of the work, and Section IX concludes.

= II. RELATED WORK
== A. Federated Learning in Wearable Digital Health
Distributed federated optimization was first introduced by McMahan et al. @mcmahan2017communication and reviewed later on by Li et al. @li2020federated. Federated learning in ubiquitous healthcare informatics is discussed in papers by Xu et al. @xu2021federated, Sarma et al. @sarma2021federated, and Vepakomma et al. @vepakomma2018split wherein split learning was used to split layers of a model without combining raw data. Chen et al. @chen2020fedhealth developed FedHealth for federated learning in transfer learning scenarios with edge wearables. Most recently, Akhmetov et al. (2025) @akhmetov2025auto proposed auto-fl-fit, an automated FL approach for activity classification using gradient-boosted trees and MLP neural networks trained using wearable sensor records. While the viability of decentralized activity classification was shown using auto-fl-fit, all communication in it occurred in plaintext and not encrypted, which makes our decentralized approach vulnerable to model reconstruction at the server side.

== B. Interoperability of Health Data and HL7 FHIR
Fast Healthcare Interoperability Resources (FHIR) has been suggested by Health Level Seven International @hl7fhir2019 for overcoming the issue of fragmentation in clinical data using resource modelling based on modern RESTful JSON API. The feasibility of the FHIR approach for standardised electronic health records in federated systems has been established by Benaissa et al. @benaissa2021flfhir. However, earlier studies have hardly ever considered the streaming of high-frequency biometric telemetry originating from smartwatches.

== C. Differential Privacy and Privacy Accounting
The notion of Differential Privacy was introduced by Dwork and Roth @dwork2014algorithmic for the definition of information-theoretic bound on the information leakage between neighboring data sets. The DP-SGD (Differential Private Stochastic Gradient Descent) algorithm was developed by Abadi et al. @abadi2016deep using per-sample gradient clipping and adding of the Gaussian noise. Geyer et al. @geyer2017differentially developed federated optimization under the paradigm of differential privacy. Whereas the initial approaches to privacy accounting included Moments Accountant @abadi2016deep or Rényi Differential Privacy (RDP) @mironov2017renyi, the latest research from Gopi et al. @gopi2021numerical relies on introducing Privacy Loss Distributions via Privacy Random Variables (PRV).

== D. Cryptographic Secure Aggregation
Practical implementations of secure aggregation (SecAgg) on mobile devices through additive masking and Shamir secret sharing scheme @shamir1979share were proposed by Bonawitz et al. @bonawitz2017practical. Bell et al. @bell2020secaggplus further refined SecAgg to SecAgg+ with improvements in terms of communication overhead per client via sparse random graphs and threshold secret sharing scheme. Truex et al. @truex2019hybrid have focused on hybrid privacy issues in federated learning for industry applications but their framework uses threshold Paillier homomorphic encryption, causing high computation latency which cannot be implemented efficiently in wearable devices with limited processing power. Recent works including Turbo-Aggregate @so2021turbo and FastSecAgg @kadhe2020fastsecagg utilized multi-group circular topology and fast Fourier transforms to simplify secure aggregation. Our work leverages Flower 1.42 primitives @beaufays2020flower.

== E. Hybrid Privacy Architectures in Healthcare
In recent times, healthcare surveys @truxzkowski2021review, @agrawal2022privacy emphasized that successful deployment of digital health applications requires hybrid privacy architectures that incorporate cryptographic techniques for securing data transmission and statistical perturbation. In case of genomic association studies, Nasirigerdeh et al. @nasirigerdeh2021splink have applied additive secret sharing along with the locally differentially private approach. Similarly, in the case of medical image analysis, Kaissis et al. @kaissis2020secure observed that neither DP nor homomorphic encryption can be effective against reconstruction attacks in multi-site federated settings. However, the current hybrids have been applied only in static images or EHRs and have neglected wearable telemetry. The proposed framework resolves this challenge through integration of FHIR normalization with DP-SecAgg.

#v(1mm)
#align(center)[
  #image("figures/fig1_system_architecture.png", width: 95%)
  #v(-1.5mm)
  #text(size: 7.8pt)[
    *Fig. 1.* Comprehensive end-to-end architecture of the proposed secure FHIR-based federated learning framework: (1) Wearable sensor ingestion and HL7 FHIR resource bundle mapping; (2) Local client optimization with DP-SGD per-sample gradient clipping, Gaussian perturbation, and persistent PRV accountant; (3) Multi-party SecAgg+ fixed-point quantization, Diffie-Hellman pairwise masking, and Shamir secret sharing; and (4) Global server-side masked aggregation and model distribution.
  ]
]
#v(1mm)

= III. PROBLEM FORMULATION AND THREAT MODEL
== A. Decentralized Network Model
Federated Network of Cross-Silos consists of an untrusted aggregating authority $S$, and $K = 4$ distinct clinical clients ${C_1, C_2, C_3, C_4}$. Each distinct client $c in {1, ..., K}$ owns its own private dataset $cal(D)_c = {(x_(c,i), y_(c,i))}_(i=1)^(N_c)$ that contains wearable health data, where $x_(c,i) in RR^d$ are normalized wearable biometric predictors ($d=16$), while $y_(c,i) in {1, ..., 6}$ are physical activity classes. The task is to fit a global neural network parameterized by $w in RR^D$ to minimize global empirical risk:

$ min_(w in RR^D) F(w) = sum_(c=1)^K p_c F_c(w), quad "where" quad F_c(w) = 1/N_c sum_(i=1)^(N_c) cal(L)(w; x_(c,i), y_(c,i)) $

where $cal(L)(dot)$ denotes cross-entropy loss, and $p_c$ represents aggregation weights.

== B. Threat Model and Assumptions about Adversaries
In this paper we construct a rigorous threat model of two adversary types:
1. *Malicious Server:* The aggregation server $S$ follows the protocol rules (aggregate all vectors) of the federated learning but tries to infer private information about the patients (training data or patient history) from the parameters of individual clients $Delta w$ or gradients. Up to $K - t$ clients may be absent or collude with the server, where $t = 3$ is a threshold to restore the data cryptographically.
2. *Adversarial Global Output Observer:* An external entity (or an end-user of the global model $w_T$) makes membership inference or attribute inference on the output parameters.

== C. Reason for Defense-in-Depth
None of these defenses alone can protect against all the potential attacks:
- SecAgg+ ensures confidentiality during the data transfer process to $S$, but the unmasked global sum $sum_c Delta w_c$ is vulnerable to global inference.
- DP-SGD alone ensures privacy by perturbing gradients in order to bound global inference, but it suffers from the gradient inversion attack by $S$ using cleartext noisy vectors.

The proposed dual-defense approach ensures that $S$ gets to see only the masked modular sums (confidentiality), whereas the aggregate update computed from these sums ensures record level differential privacy.

= IV. FHIR DATA INTEROPERABILITY PIPELINE
For standardized representation of heterogeneous digital health infrastructure, the raw streams coming out from the wearable sensors are translated into FHIR R4 resources before local training.

== A. Resource Architecture
The normalization pipeline generates three independent but related primitive FHIR resources:
- *Patient:* This resource consists of standardized data about the patient including administrative information.
- *Device:* Consists of specifications for the wearable device such as model, firmware version, and sampling rate.
- *Observation:* Each entry in the physiological data is stored as an observation resource. It consists of a measured value of the biometric with time stamp coded using LOINC codes (for instance, LOINC 8867-4 for heart rate and 55423-8 for number of steps) along with a numeric quantity coded using UCUM units.

== B. Batch Extraction and Feature Validity Testing
The FHIR resources in standardized format are tested for validity with the use of fhir.resources while they are combined into bundle transactions. The feature extraction layer uses the validated bundle data to produce a 16-dimensional predictor vector:

$ x = [v_1, v_2, ..., v_16]^T in RR^16 $

and which include the number of steps, heart rate, calories per minute burn rate, metabolic equivalent, and directional acceleration. The predictor vector is normalized using a global StandardScaler with only training subsets to ensure that the predictors have zero mean and unit variance. The mapping of predictors to LOINC codes can be seen in Table III below.

#v(1mm)
#align(center)[
  #text(size: 8pt, weight: "bold")[TABLE III\ STANDARDIZED WEARABLE PREDICTOR FEATURES AND CLINICAL LOINC MAPPINGS]
  #v(0.5mm)
  #table(
    columns: (12%, 46%, 22%, 20%),
    align: (center, left, center, center),
    stroke: 0.4pt + luma(120),
    fill: (x, y) => if y == 0 { luma(235) } else { none },
    table.header([*Idx*], [*Biometric Feature*], [*LOINC*], [*Unit*]),
    [1], [Heart Rate (Instantaneous)], [8867-4], [beats/min],
    [2], [Resting Heart Rate], [40443-4], [beats/min],
    [3], [Cumulative Step Count], [55423-8], [count],
    [4], [Active Caloric Burn], [41981-2], [kcal],
    [5], [Basal Metabolic Energy], [41979-6], [kcal],
    [6], [Metabolic Equivalent (MET)], [82260-1], [MET],
    [7], [Mean Triaxial Accel X], [93808-4], [m/s#super[2]],
    [8], [Mean Triaxial Accel Y], [93809-2], [m/s#super[2]],
    [9], [Mean Triaxial Accel Z], [93810-0], [m/s#super[2]],
    [10], [Accel Variance (Vector Mag)], [93811-8], [m#super[2]/s#super[4]],
    [11], [Cadence Frequency], [55424-6], [steps/min],
    [12], [Normalized Heart Rate Reserve], [8868-2], [percentage],
    [13], [Velocity Trend Estimator], [93812-6], [m/s],
    [14], [Energy Expenditure Rate], [41982-0], [kcal/min],
    [15], [Elevation Gain Counter], [93813-4], [meters],
    [16], [Ambient Temperature Proxy], [8310-5], [Cel]
  )
  #v(-1.5mm)
  #text(size: 7.0pt, style: "italic")[
    Notes: Features standardized from raw Apple Watch telemetry and validated through HL7 FHIR Observation transactional bundles.
  ]
]
#v(1mm)

= V. METHODOLOGY
== A. Model Architecture
The local optimization of the model is performed using a fine-tuned PyTorch Multi-layer Perceptron (TunedActivityMLP), which is especially created for kinematic classification on wearables. The network consists of four linear layers one after another:

$ RR^16 arrow.r "Linear"(128) arrow.r "ReLU" arrow.r "Linear"(64) arrow.r "ReLU" arrow.r "Linear"(32) arrow.r "ReLU" arrow.r "Linear"(6) $

forming a concise network with exactly $D = 12,710$ parameters. The model is optimized with AdamW optimizer, learning rate $eta = 0.003$ and weight decay $lambda = 10^(-3)$. The update rule for the parameter in the local iteration $t$ is:

$ m_t = beta_1 m_(t-1) + (1 - beta_1) tilde(g)_t, quad v_t = beta_2 v_(t-1) + (1 - beta_2) tilde(g)_t^2 $
$ w_t = w_(t-1) - eta (hat(m)_t / (sqrt(hat(v)_t) + epsilon_("opt")) + lambda w_(t-1)) $

where $beta_1 = 0.9, beta_2 = 0.999$, and $epsilon_("opt") = 10^(-8)$.

== B. Client-side Differential Privacy (DP-SGD)
To satisfy the definition of differential privacy formally, each client $c$ uses local stochastic gradient descent with Opacus 1.6.0 @yousefpour2021opacus. Each round of training is composed of $E = 3$ local epochs and $R = 25$ global rounds of communication.

*1) Poisson Batch Subsampling:* The sampling of the batch $B_(c,t)$ of the dataset $cal(D)_c$, which consists of $N_c = 731$ instances, is done independently with probability $q$:

$ Pr[i in B_(c,t)] = q = 1 / (|cal(D)_c|) / B_("nom") = 1 / 23 approx 0.043478 $

Here, $B_("nom") = 32$ is a nominal batch size. Then, the expected batch size for Poisson sample equals to $EE[B] = 731 times (1/23) approx 31.78$ instances.

*2) Per-Sample Gradient Clipping:* Each per-sample gradient $g_i (w) = nabla_w cal(L)(w; x_i, y_i)$ is clipped to ensure its $L_2$ norm to be less than or equal to $C = 1.0$:

$ bar(g)_i (w) = g_i (w) / (max(1, (||g_i (w)||_2) / C)) $

*3) Gaussian Noise Addition:* The calibrated spherical Gaussian noise is added to the sum of the clipped batch gradients:

$ tilde(g)(w) = 1 / (|B_(c,t)|) ( sum_(i in B_(c,t)) bar(g)_i (w) + cal(N)(0, sigma^2 C^2 I_D) ) $

where $sigma in {0.5, 1.0, 1.5, 2.0}$ is a configurable noise multiplier.

*4) Privacy Composition and PRV Accounting:* By definition, a randomized algorithm $cal(M)$ meets $(epsilon, delta)$-DP if for all neighboring datasets $D, D'$ that differ by exactly one record:

$ Pr[cal(M)(D) in cal(S)] <= e^epsilon Pr[cal(M)(D') in cal(S)] + delta $

Over $R = 25$ iterations and $E = 3$ local epochs, each client accountant executes precisely:
$ T = R times E times 23 = 25 times 3 times 23 = 1,725 "accountant actions." $

The privacy composition analysis is done based on Privacy Loss Distributions, utilizing Privacy Random Variables (PRV) @gopi2021numerical, avoiding conservative loose bounds. We cross-verify bounds with Rényi Differential Privacy (RDP) @mironov2017renyi.

#v(1mm)
#align(center)[
  #image("figures/fig2_secagg_workflow.png", width: 95%)
  #v(-1.5mm)
  #text(size: 7.8pt)[
    *Fig. 2.* Sequence flow of the four-round Secure Aggregation (SecAgg+) protocol showing peer Diffie-Hellman key exchange, $(t, n)$ Shamir secret sharing $(t = 3, n = 4)$, masked integer vector aggregation, survivor self-mask unmasking, and dropout recovery.
  ]
]
#v(1mm)

== C. Fixed Public Aggregation Weights
In the classical FedAvg setting, the aggregation weights depend upon the record count: $p_c = N_c / (sum N_j)$. In case of standard record-level adjacency, if there is a change in one record, $p_c$ changes, leading to differential privacy issues for proving post-processing theorems. Since all partitions in clinical methodology are equal in terms of record count ($N_c = 731$), fixed public aggregation weights are used:

$ p_c = 1 / K = 0.25 quad forall c in {1, ..., 4} $

By using such aggregation weights, it is ensured that they are data-independent public constants, rigorously preserving post-processing differential privacy.

== D. Secure Aggregation (SecAgg+) Protocol
To prevent disclosure of cleartext parameter vectors to the server $S$, the client model weights are masked by four rounds of the SecAgg+ protocol with the aid of verified Flower 1.42 primitives @beaufays2020flower, @bell2020secaggplus.

*1) Fixed-Point Quantization:* Floating-point model parameters $x in [-R, R]$ (clipping range $R = 8.0$) are converted into discrete integer domain $[0, Q]$ with $b = 22$ bits quantization in the way:

$ |x| = "round" ( (x + R) / (2 R) times (2^b - 1) ) $

As $Q = 2^22 - 1 = 4,194,303$, summing of integer values in case of aggregation $K = 4$ clients will not be more than $4 times 2^22 = 2^24 < 2^32$ to ensure no modular integer overflow in 32-bit unsigned integers space ($ZZ_M$ where $M = 2^32$).

*2) Dual Additive Masking:* For each client $u$, a self-random seed $b_u$ is generated and the pairwise secret $s_(u,v) = "DH"(s_u^("priv"), s_v^("pub"))$ is computed for all other $v eq.not u$ clients using Diffie-Hellman key agreement protocol @diffie1976new. The vector for sending to the server $S$ is as follows:

$ y_u = ( |x|_u + "PRG"(b_u) + sum_(v > u) "PRG"(s_(u,v)) - sum_(v < u) "PRG"(s_(u,v)) ) mod M $

*3) Robustness to Dropouts:* Using $(t = 3, n = 4)$ Shamir secret sharing @shamir1979share, client $u$ breaks up $b_u$ and $s_u^("priv")$ into 4 shares and delivers the shares to his peer clients in an encrypted manner. Upon getting the masked vectors from the surviving clients $U_2$, server $S$ asks the surviving clients for their shares:
- Surviving clients $u in U_2$ give out shares of self mask $b_u$.
- Drop-out clients $d in.not U_2$ give out shares of seed $s_d^("priv")$.

As $sum_u sum_(v eq.not u) Delta_(u,v) equiv 0 mod M$, the pairwise masks get cancelled off. Server $S$ then eliminates self-masks $"PRG"(b_u)$, and computes the precise sum:

$ sum_(u in U_2) |x|_u mod M $

This dequantization process yields the exact global floating-point average with no mathematical distortion at all.

= VI. EXPERIMENTAL SETUP AND EVALUATION
== A. Wearable Dataset Specifications
We use the benchmarked Apple Watch telemetry partition from Harvard Dataverse physical activity data set @fuller2020applewatch. The dataset contains $N = 3,656$ structured instances with 16 continuous sensor predictor features such as cardiovascular response, calorie flow and 3-axis tri-axial acceleration. The target feature includes six classes of validated physical activities:
1. Walking (Class 0: 610 instances)
2. Running (Class 1: 610 instances)
3. Cycling (Class 2: 610 instances)
4. Elliptical Trainer (Class 3: 610 instances)
5. Resting/Sedentary (Class 4: 610 instances)
6. Sports/Exercise (Class 5: 606 instances)

== B. Stratified Partitioning and Strict Test Isolation
Stratified global data set ($N = 3,656$) is partitioned in an 80/20 sample fashion as follows:
- *Central Training Partition:* 2,924 instances (80%).
- *Held-Out Test Partition:* 732 instances (20%).

2,924 training instances are further partitioned into $K = 4$ disjoint client partitions (`client_0.csv` to `client_3.csv`), each containing exactly 731 client partition instances.

*Isolation of Tests:* In all 25 rounds of communication, the 732-sample test set is completely isolated from any kind of influence of the training procedure. Evaluation gradients and metrics are not computed in rounds 1 to 24, and the test set is not involved in any stopping conditions, learning rate schedules or model selection. The test set is evaluated only once at the end of the last round of communication (round 25).

== C. Four Architectural Configurations under Canonical Experiments
Four particular architectural configurations are benchmarked against five canonical experiments [42, 123, 456, 789, 2026]:
- *Configuration A (Plaintext FedAvg Baseline):* Standard federated averaging without differential privacy and secure aggregation of parameters. The cleartext vectors are exchanged between the devices.
- *Configuration B (DP-FedAvg Baseline):* Decentralized training with differential privacy used on clients' side via DP-SGD for noise multipliers $sigma in {0.5, 1.0, 1.5, 2.0}$ with clipping factor $C = 1.0$ and $delta = 10^(-5)$. Cleartext vectors of updates with noise are exchanged.
- *Configuration C (SecAgg-FedAvg Baseline):* Training using plaintext along with SecAgg+ protocol (no DP noise). Validates quantization fidelity.
- *Configuration D (Full Defense-in-Depth Framework):* Client-side DP-SGD hybridized with multi-party SecAgg+ across identical noise multipliers and seeds.

#v(1mm)
#align(center)[
  #text(size: 8pt, weight: "bold")[TABLE I\ MASTER FOUR-CONFIGURATION PERFORMANCE MATRIX (HELD-OUT TEST SET $N = 732$)]
  #v(0.5mm)
  #table(
    columns: (15%, 31%, 20%, 20%, 14%),
    align: (center, left, center, center, center),
    stroke: 0.4pt + luma(120),
    fill: (x, y) => if y == 0 { luma(235) } else { none },
    table.header([*Config*], [*Architecture & Protocol*], [*Test Acc (%)* \ ($mu plus.minus sigma_("sample")$)], [*Macro $F_1$ (%)* \ ($mu plus.minus sigma_("sample")$)], [*PRV $epsilon$* \ ($delta=10^(-5)$)]),
    [Config A], [Plaintext FedAvg (Ref)], [67.60 $plus.minus$ 0.66], [67.89 $plus.minus$ 0.62], [$infinity$],
    [Config C], [SecAgg-FedAvg (No DP)], [67.92 $plus.minus$ 1.16], [68.21 $plus.minus$ 1.17], [$infinity$],
    [Config B-1], [DP-FedAvg ($sigma = 0.5$)], [45.98 $plus.minus$ 1.75], [44.90 $plus.minus$ 2.05], [72.55],
    [Config D-1], [DP + SecAgg ($sigma = 0.5$)], [46.07 $plus.minus$ 1.82], [44.96 $plus.minus$ 2.09], [72.55],
    [Config B-2], [DP-FedAvg ($sigma = 1.0$)], [41.56 $plus.minus$ 1.52], [40.14 $plus.minus$ 1.41], [12.77],
    [Config D-2], [DP + SecAgg ($sigma = 1.0$)], [41.56 $plus.minus$ 1.56], [40.13 $plus.minus$ 1.46], [12.77],
    [Config B-3], [DP-FedAvg ($sigma = 1.5$)], [39.54 $plus.minus$ 1.68], [37.75 $plus.minus$ 1.68], [6.42],
    [Config D-3], [DP + SecAgg ($sigma = 1.5$)], [39.54 $plus.minus$ 1.62], [37.74 $plus.minus$ 1.61], [6.42],
    [Config B-4], [DP-FedAvg ($sigma = 2.0$)], [38.47 $plus.minus$ 0.99], [35.89 $plus.minus$ 1.22], [4.29],
    [Config D-4], [DP + SecAgg ($sigma = 2.0$)], [38.44 $plus.minus$ 0.93], [35.86 $plus.minus$ 1.17], [4.29]
  )
  #v(-1.5mm)
  #text(size: 6.8pt, style: "italic")[
    Notes: Values are reported as mean $plus.minus$ sample standard deviation ($"ddof" = 1$) across five canonical seeds [42, 123, 456, 789, 2026]. Corresponding population standard deviations ($"ddof" = 0$) used in raw JSON summaries are: Config A acc 0.59%, Config C acc 1.04%, Config B accs [1.57%, 1.36%, 1.50%, 0.88%], and Config D accs [1.63%, 1.40%, 1.45%, 0.83%]. All models evaluated strictly once post-training on $N = 732$ test samples.
  ]
]
#v(1mm)

= VII. RESULTS AND DISCUSSION
== A. Convergence of the Algorithm and Quantization Invariance
The empirical performance values are shown in Table I for all four considered configurations. The centralized algorithm reaches $75.98\% plus.minus 0.66\%$ accuracy, thus providing an empirical upper bound for this specific feature space. As for distributed training, Plaintext FedAvg (Configuration A) demonstrates $67.60\% plus.minus 0.66\%$ accuracy and $67.89\% plus.minus 0.62\%$ Macro $F_1$. Crucially, Configuration C, which corresponds to SecAgg-FedAvg without DP, reaches $67.92\% plus.minus 1.16\%$ accuracy and $68.21\% plus.minus 1.17\%$ Macro $F_1$, which demonstrates improved performance in comparison with Config A by $+0.328$ percentage points ($+0.485\%$ relative change). Because this variance is rather small taking into account seed variations empirically ($sigma_("sample") = 1.16$ pp), we can conclude that 22-bit fixed-point quantization, modular addition in $ZZ_(2^32)$, and Shamir mask cancelation do not cause any quantization distortion to federated convergence.

== B. Privacy Utility Trade-Off for DP-SGD
As seen from Table I and shown in Fig. 3, adding Gaussian noise during the training of local models leads to the following privacy utility trade-off:
- With $sigma = 0.5$ (poor privacy: $epsilon_("PRV") = 72.55$), there is a decrease in accuracy to $45.98\% plus.minus 1.75\%$ ($-21.62$ pp penalty).
- With $sigma = 1.0$ (medium privacy: $epsilon_("PRV") = 12.77$), there is an accuracy of $41.56\% plus.minus 1.52\%$ ($-26.04$ pp penalty).
- With $sigma = 1.5$ (good privacy: $epsilon_("PRV") = 6.42$), there is an accuracy of $39.54\% plus.minus 1.68\%$ ($-28.06$ pp penalty).
- With $sigma = 2.0$ (very good privacy: $epsilon_("PRV") = 4.29$), there is an accuracy of $38.47\% plus.minus 0.99\%$ ($-29.13$ pp penalty).

Despite the sacrifice in utility, our most private model ($epsilon_("PRV") = 4.29$) achieves $38.44\%$ accuracy in classification on 6-class dataset. This gives $+21.77$ percentage points of improvement compared to random guess ($16.67\%$).

#v(1mm)
#align(center)[
  #image("figures/fig3_privacy_utility_tradeoff.png", width: 95%)
  #v(-1.5mm)
  #text(size: 7.8pt)[
    *Fig. 3.* Empirical privacy-utility trade-off curve on the held-out test set ($N = 732$) showing test accuracy vs. PRV privacy parameter $epsilon$ ($delta = 10^(-5)$) across noise multipliers $sigma in {0.5, 1.0, 1.5, 2.0}$. Config D (DP + SecAgg) tracks Config B (DP-only) with near-perfect congruence.
  ]
]
#v(1mm)

== C. Defense-in-Depth Validation: Config D and Config B
In order to verify if there is any distortion created by the integration of multi-party SecAgg+ onto DP-SGD, we look at the paired seed-wise differences:

$ Delta_i = ("Acc"_(D,i) - "Acc"_(B,i)) times 100 quad ["pp"] $

The paired differences in the accuracy level per seed are provided in Table II for the 732 test partition samples, over 20 paired comparisons.

#v(1mm)
#align(center)[
  #text(size: 8pt, weight: "bold")[TABLE II\ PER-SEED PAIRED ACCURACY DIFFERENCES ($N = 732$ TEST SET)]
  #v(0.5mm)
  #table(
    columns: (16%, 14%, 14%, 14%, 14%, 14%, 14%),
    align: center,
    stroke: 0.4pt + luma(120),
    fill: (x, y) => if y == 0 { luma(235) } else { none },
    table.header([*Noise $sigma$*], [*Seed 42*], [*Seed 123*], [*Seed 456*], [*Seed 789*], [*Seed 2026*], [*Mean $Delta$*]),
    [$sigma = 0.5$], [+0.14 pp], [+0.28 pp], [$-0.27$ pp], [+0.14 pp], [+0.14 pp], [*+0.086 pp*],
    [$sigma = 1.0$], [$-0.14$ pp], [0.00 pp], [+0.13 pp], [0.00 pp], [0.00 pp], [*-0.002 pp*],
    [$sigma = 1.5$], [$-0.14$ pp], [0.00 pp], [0.00 pp], [0.00 pp], [+0.14 pp], [*0.000 pp*],
    [$sigma = 2.0$], [0.00 pp], [0.00 pp], [0.00 pp], [$-0.14$ pp], [0.00 pp], [*-0.028 pp*]
  )
  #v(-1.5mm)
  #text(size: 6.8pt, style: "italic")[
    Notes: $Delta = "Acc"_D - "Acc"_B$ in percentage points. In 13 of 20 runs, accuracy is identical (0.00 pp, 0 record shift); in 7 runs, divergence is bounded by $plus.minus 1$ or $plus.minus 2$ records.
  ]
]
#v(1mm)

The key empirical findings based on Table II are the following:
- In 20 comparisons, in 13 cases the classification decisions taken by the classifier trained using DP + SecAgg algorithm coincide with the decisions taken by the baseline classifier trained using only DP (0.00 pp difference, 0 records difference).
- In 20 comparisons, in 7 cases the record difference lies in the interval of $[-1; 1]$ ($-/+$ 0.14 pp) or $[-2; +2]$ ($-/+$ 0.28/$-0.27$ pp) records.
- Average difference of paired accuracy $|Delta_("mean")| <= 0.086$ percentage points for all noise levels.

Therefore, SecAgg+ provides guarantee of confidentiality of the server side communication without any distortion of differentially private models.

#v(1mm)
#align(center)[
  #text(size: 8pt, weight: "bold")[TABLE IV\ COMPREHENSIVE MULTI-METRIC PERFORMANCE EVALUATION ON HELD-OUT TEST DATA ($N = 732$)]
  #v(0.5mm)
  #table(
    columns: (24%, 19%, 19%, 19%, 19%),
    align: (left, center, center, center, center),
    stroke: 0.4pt + luma(120),
    fill: (x, y) => if y == 0 { luma(235) } else { none },
    table.header([*Configuration*], [*Precision (%)* \ ($mu plus.minus sigma$)], [*Recall (%)* \ ($mu plus.minus sigma$)], [*Cohen's $kappa$* \ ($mu plus.minus sigma$)], [*Test Loss* \ ($mu plus.minus sigma$)]),
    [Config A (Plain)], [67.93 $plus.minus$ 0.54], [68.29 $plus.minus$ 0.95], [0.6104 $plus.minus$ 0.0084], [0.9189 $plus.minus$ 0.0205],
    [Config C (SecAgg)], [68.31 $plus.minus$ 0.75], [68.56 $plus.minus$ 1.49], [0.6141 $plus.minus$ 0.0147], [0.9133 $plus.minus$ 0.0278],
    [Config B ($sigma = 0.5$)], [45.86 $plus.minus$ 2.18], [45.31 $plus.minus$ 1.88], [0.3477 $plus.minus$ 0.0217], [1.5577 $plus.minus$ 0.0330],
    [Config D ($sigma = 0.5$)], [45.93 $plus.minus$ 2.21], [45.40 $plus.minus$ 1.94], [0.3487 $plus.minus$ 0.0225], [1.5579 $plus.minus$ 0.0331],
    [Config B ($sigma = 1.0$)], [41.29 $plus.minus$ 1.92], [40.53 $plus.minus$ 1.53], [0.2932 $plus.minus$ 0.0184], [1.5381 $plus.minus$ 0.0135],
    [Config D ($sigma = 1.0$)], [41.26 $plus.minus$ 1.96], [40.53 $plus.minus$ 1.58], [0.2932 $plus.minus$ 0.0190], [1.5381 $plus.minus$ 0.0135],
    [Config B ($sigma = 1.5$)], [39.67 $plus.minus$ 1.82], [38.33 $plus.minus$ 1.77], [0.2672 $plus.minus$ 0.0204], [1.5430 $plus.minus$ 0.0124],
    [Config D ($sigma = 1.5$)], [39.65 $plus.minus$ 1.82], [38.33 $plus.minus$ 1.70], [0.2672 $plus.minus$ 0.0197], [1.5430 $plus.minus$ 0.0125],
    [Config B ($sigma = 2.0$)], [39.34 $plus.minus$ 2.19], [36.97 $plus.minus$ 1.01], [0.2524 $plus.minus$ 0.0120], [1.5437 $plus.minus$ 0.0131],
    [Config D ($sigma = 2.0$)], [39.30 $plus.minus$ 2.17], [36.94 $plus.minus$ 0.96], [0.2520 $plus.minus$ 0.0114], [1.5436 $plus.minus$ 0.0131]
  )
  #v(-1.5mm)
  #text(size: 6.8pt, style: "italic")[
    Notes: Multi-metric breakdown evaluated across 5 seeds showing strong concordance between Config B and Config D.
  ]
]
#v(1mm)

== D. Standard Deviation Conventions and Statistical Observations
In all of our experiments, the sample standard deviation ($sigma_("sample")$, ddof = 1) is clearly stated to be the standard convention for scientific reporting, with five stochastic independent experiments ($N = 5$). It can be seen in Tables I and IV that the sample standard deviation is directly proportional to the population standard deviation ($"ddof" = 0$) used by NumPy as follows:

$ sigma_("sample") = sigma_("pop") times sqrt(5/4) approx 1.1180 times sigma_("pop") $

Reporting sample standard deviations allows for an unbiased estimation of variance from finite samples of experimental observations.

= VIII. LIMITATIONS AND THREAT MODEL BOUNDARIES
In order to preserve scientific rigor, we set up the limitations and assumptions of this empirical study:
1. *Record-Level Privacy vs. Patient-Level Privacy:* Because the Harvard wearable data lacks the validated longitudinal identity of each individual associated with each record, the differential privacy property in our case is guaranteed only at record-level adjacency ($plus.minus 1$ observation difference between datasets). We explicitly do not claim the patient-level differential privacy guarantee.
2. *Regulatory Limitations:* The mathematical guarantees, as well as cryptographic secret sharing solutions guarantee technical mitigations but not automatic HIPAA or GDPR legal compliance.
3. *Sample-Level Generalization:* Experiments were conducted using 3,656 standardized Apple Watch records from four clients and five canonical seeds. Although this sample size is enough to validate the protocol and noise sensitivity, clinical trials on diverse hardware of wearables are still needed.
4. *Cryptographic Hardness vs. Inference:* SecAgg+ guarantees confidential communication against the untrusted server, but no immunity to inference attack on the global unmasked model; in that case, the differential privacy solution is needed.
5. *Communication Overhead:* Although SecAgg+ is able to reduce public key cryptography in message updates, the 4-round communication protocol involves $cal(O)(K^2)$ secret sharing ($K=4 arrow.r.double 16$ messages) for each round. This is very scalable in the organizational hospital silos but needs sparse graph optimization for millions of edge smartwatches.

= IX. CONCLUSION
In this work, we have created a solid and multilayered architecture of security protocols for wearable devices digital health analysis via federated learning. Applying the principles of HL7 FHIR resource standardization and DP-SGD along with multi-party SecAgg+ protocol, we managed to solve at the same time the issues of semantic heterogeneity, parameter interception, and global model inversion. In 25 benchmark cases, we proved that fixed point SecAgg+ is connected to a low utility loss ($+0.32$ pp to plaintext) and no change in the differentially private gradients ($|Delta| <= 0.086$ pp), as well as participant privacy guarantee ($epsilon = 4.29, delta = 10^(-5)$) and high level of prediction utility ($38.44\%$ vs. $16.67\%$). In further research, we will investigate the participation grouping in longitudinal multi-modal clinical registries.

#v(1mm)
#text(weight: "bold")[ACKNOWLEDGMENTS] This work is done as part of B.Tech. Project-I within the School of Computer Science and Engineering, Vellore Institute of Technology, Vellore, India. The authors would like to extend their heartfelt thanks to Project Guide Sangeetha S for her technical guidance and supervision through the entire conceptualization, empirical process, and auditing of this experiment. The authors do not have any competing interests.

#colbreak()
#set text(size: 8.0pt)
#set par(leading: 0.42em)
#bibliography("references.bib", title: [REFERENCES], style: "ieee")
'''

with open("course_project_paper.typ", "w", encoding="utf-8") as f:
    f.write(typst_content)

print("Compiling course_project_paper.typ...")
typst.compile("course_project_paper.typ", output="course_project_paper.pdf")
print("Compiled course_project_paper.pdf successfully!")

# Also update journal_paper.pdf to match
typst.compile("course_project_paper.typ", output="journal_paper.pdf")
print("Updated journal_paper.pdf successfully!")

reader = pypdf.PdfReader("course_project_paper.pdf")
print(f"Total pages: {len(reader.pages)}")
for i, p in enumerate(reader.pages):
    print(f"Page {i+1}: {len(p.extract_text().split())} words, {len(p.extract_text())} chars")
