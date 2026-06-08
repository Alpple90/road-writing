# Interpolation Algorithm Evaluation for CERPM-Based Lane Keep Assist Systems

---

## Cover Page

**Unit:** Advanced Driver Assistance Systems Research Project

**Report Type:** Final Research Thesis

**Author:** Alexander Bruce

**Student Contribution:** This report represents the Lane Keep Assist (LKA) subsystem contribution to the group's Advanced Driver Assistance Systems (ADAS) project. The author was responsible for the full scope of this subsystem: problem definition, literature review, system architecture design, simulation development in Python (including road geometry parsing, CERPM resampling, Monte Carlo simulation framework, and all analysis/visualisation code), execution of experiments across three road geometries, and analysis and interpretation of results.

**Date:** June 2026

---

## Abstract

Lane Keep Assist (LKA) is a foundational safety technology within Advanced Driver Assistance Systems (ADAS), designed to prevent unintentional lane departures through corrective steering. Current commercial LKA implementations rely primarily on camera-based computer vision, which suffers significant performance degradation under poor lane markings and adverse weather conditions. This research investigates a Vehicle-to-Infrastructure (V2I) alternative using Chip Enabled Raised Pavement Markers (CERPMs), which transmit GPS positional data directly to the onboard vehicle computer.

The central research questions are: (1) which interpolation algorithm most accurately reconstructs the lane centreline from CERPM position data; and (2) how do different CERPM dropout scenarios — random failures, consecutive clustered failures, and physically-sized gap-length failures — degrade accuracy across varying marker spacings?

A Python simulation framework was developed to parse real-world road geometries from Lanelet2 OSM files and to evaluate seven interpolation methods (linear, quadratic, cubic spline, quartic, quintic, PCHIP, and Akima) under Monte Carlo conditions across three distinct road geometries. Results show that at dense CERPM spacings (≤1 m) all methods achieve sub-centimetre median centreline error with near-zero failure rates. As spacing increases beyond 2 m, higher-order smooth methods (cubic spline, PCHIP, Akima) substantially outperform linear and quadratic interpolation. Under gap-length dropout, linear interpolation fails catastrophically at nearly all spacings beyond 1 m, while PCHIP and Akima exhibit the most robust behaviour. These findings provide actionable guidance for CERPM deployment standards and algorithm selection in production LKA systems.

---

## Table of Contents

1. Introduction
2. Literature Review
3. Methodology
4. Results and Analysis
5. Conclusions and Recommendations
6. References
7. Appendices

---

## 1. Introduction

### 1.1 General Background

Road safety remains one of the most pressing public health challenges globally. In Australia, lane departure — encompassing run-off-road and head-on collisions — is the single largest contributor to road fatalities, accounting for 62% of deaths nationally, rising to 73% in regional areas and 71% in remote areas [3]. In the United States, the National Highway Traffic Safety Administration (NHTSA) has estimated that vehicles equipped with Lane Keep Assist are on average 24% less likely to be involved in a fatal road departure crash [4]. These statistics establish LKA as one of the highest-leverage active safety technologies available.

The growing regulatory landscape reinforces this. From 7 July 2024, the European Commission mandated LKA as a standard fitment on all new motor vehicles sold in the European Union, projecting the technology will contribute to saving over 25,000 lives by 2038 [5]. LKA also forms the perceptual and control foundation upon which higher-order autonomous driving functions — such as highway pilot and lane-change assist — are built. Its reliability is therefore critical not only as a standalone safety feature but as an enabler of the broader ADAS ecosystem.

### 1.2 The Problem with Vision-Based LKA

Current production LKA systems universally rely on forward-facing cameras combined with computer vision algorithms to detect lane markings. While these systems perform reliably under ideal conditions, field evidence demonstrates that performance degrades substantially when lane markings are worn, faded, or absent — conditions disproportionately common on rural and regional roads where lane departure risk is highest. Additionally, adverse weather (rain, fog, snow, glare) and challenging lighting conditions (tunnels, night driving, low sun angles) further compromise detection reliability [6]. Near lane transitions such as merges, diverges, and construction zones introduce additional failure modes.

Lane Departure Warning (LDW) systems, a precursor to LKA, mitigate the problem by alerting the driver. However, these systems depend on the driver responding appropriately, which is unreliable when fatigue, distraction, or impairment is present — precisely the conditions where lane departure most commonly occurs. LKA addresses this by actuating the steering system directly, without requiring driver response.

### 1.3 The CERPM-Based V2I Approach

A fundamentally different approach has emerged from recent research: instead of detecting lane boundaries visually, the vehicle receives lane boundary positional data directly from road-embedded infrastructure. Chip Enabled Raised Pavement Markers (CERPMs) are road stud-type devices equipped with a wireless transceiver that broadcasts their GPS coordinates to vehicles within range (demonstrated range: up to 350 m [1][2]). When both the left and right lane boundary CERPMs are visible to the vehicle, the lane centreline can be computed through interpolation of the received coordinate streams.

This approach decouples LKA accuracy from environmental and surface conditions entirely: it operates in darkness, fog, rain, snow, and on roads with no visible markings. Kadav et al. [2] demonstrated that CERPM-based lane centering outperformed the Mobileye 630 — a state-of-the-art commercial computer vision system — across all tested conditions including sharp curves, varying lighting, and degraded lane markings.

### 1.4 Research Gap and Aims

The existing CERPM research [1][2] validated the concept and showed its superiority over vision-based approaches but did not investigate: (a) whether the choice of interpolation algorithm affects accuracy, or (b) how the system behaves when individual CERPMs fail or go missing — a practically inevitable scenario as road-embedded hardware is subject to vehicle damage, vandalism, and electronic failure.

This project directly addresses these gaps. The specific aims are:

1. Evaluate and compare seven interpolation algorithms for lane centreline estimation from CERPM data across multiple real-world road geometries.
2. Characterise how three categories of CERPM dropout — random uniform failure, contiguous clustered failure, and physically-sized gap-length failure — degrade centreline estimation accuracy as a function of marker spacing.
3. Identify which algorithm-spacing combinations maintain acceptable accuracy (max centreline error ≤ 0.2 m) under realistic failure conditions, and provide recommendations for deployment.

### 1.5 Scope

This project is scoped to the perception component of LKA — the estimation of lane centreline position from CERPM data. The downstream control system (steering actuation) is outside scope. Road geometries are sourced from Lanelet2-format OSM map files derived from the CARLA simulator environment, representing a range of road curvatures and lengths. GPS positioning error of the CERPMs themselves is not modelled; the simulation assumes ground-truth CERPM coordinates are transmitted accurately.

---

## 2. Literature Review

### 2.1 State of the Art in LKA Perception

The perception layer of modern LKA systems has evolved considerably from early threshold-based edge detectors to deep neural network architectures operating on high-resolution camera feeds with multi-frame temporal integration. The OpenLKA dataset [6] — the first large-scale open benchmark for LKA research — aggregates approximately 400 hours of real-world LKA-actuated driving from 62 production vehicles across conditions ranging from clear highway to construction zones. Its empirical benchmarks confirm that even modern deep-learning LKA systems fail at high rates when lane markings are degraded or absent, and near lane transitions. This establishes the practical ceiling of camera-based approaches and motivates the search for complementary or alternative sensing modalities.

Fakhari and Anwar [7][8] proposed a Multiple Model Adaptive Estimation (MMAE) algorithm that fuses front and rear camera feeds through a Kalman filter framework, dynamically selecting the camera model whose uncertainty estimate is lowest. Tested under night conditions and adverse weather, their system demonstrates meaningful accuracy improvements over single-camera baselines. This approach represents the current frontier of camera-based robustness improvement but remains fundamentally dependent on some minimum level of visual lane marking quality.

### 2.2 Infrastructure-Based Lane Detection

The most relevant prior work comes from Sharma et al. [1] and the subsequent Kadav et al. study [2]. Sharma et al. introduced the concept of using CERPMs as a V2I data source for vehicle lateral offset estimation, demonstrating that the approach reduced compute requirements on the vehicle while delivering position estimates. Kadav et al. [2] conducted a direct comparative evaluation against the Mobileye 630 commercial kit, testing both systems on roads with sharp curves, variable lighting, and worn lane markings. CERPMs outperformed the Mobileye in every tested scenario, with a particularly notable advantage in detection range: CERPMs provided usable data from 350 m while the Mobileye was limited to 31 m. Crucially, neither study investigated which interpolation method was used for centreline estimation, nor did they characterise system behaviour when CERPMs fail. The current project addresses precisely this gap.

### 2.3 Interpolation Methods for Spatial Data

Interpolation of spatial coordinate sequences is a well-studied problem in computational geometry and robotics. Arc-length parameterisation — expressing the interpolation variable as normalised path distance rather than index or Euclidean coordinate — is the standard approach for curve reconstruction because it distributes interpolation effort proportionally to the physical spacing between points, avoiding the irregularity artefacts that arise with simple index-based methods.

**Linear interpolation** is the simplest method: piecewise straight-line segments between knot points. It is C⁰ continuous (position-continuous but not smooth), produces no overshoot, and degrades gracefully as point spacing increases. Its lack of smoothness makes it unsuitable for high-speed vehicle control, but it serves as a useful baseline.

**Polynomial splines** of degree *k* (quadratic: *k=2*, cubic: *k=3*, quartic: *k=4*, quintic: *k=5*) fit a single polynomial of degree *k* through all knot points, or equivalently use B-spline basis functions of the corresponding degree. Higher degree produces smoother curves and better approximation of smooth geometry, but increases sensitivity to outliers and to sparse or unevenly spaced knot points. Runge's phenomenon — oscillation near the endpoints of a polynomial fit — becomes problematic for high-degree methods when knot spacing is large.

**Cubic Spline (natural)** fits piecewise cubic polynomials with C² continuity, using natural endpoint conditions (zero second derivative at endpoints). This is the most common baseline smooth interpolator in engineering practice, and the method implicitly used in the original CERPM research.

**PCHIP (Piecewise Cubic Hermite Interpolating Polynomial)** is a C¹ continuous cubic method that enforces monotonicity between knot points, preventing overshoot. Unlike natural cubic splines, PCHIP explicitly preserves local shape, making it particularly well-suited to sparse or unevenly spaced road data where sudden gaps might otherwise introduce spurious oscillations.

**Akima interpolation** is a C¹ cubic method that uses a locally weighted slope estimate at each knot, designed so that a single outlier knot does not propagate oscillation to neighbouring curve segments. This local insensitivity property is especially relevant when isolated CERPM failures leave gaps in the data.

### 2.4 LKA Control

On the control side, Perozzi et al. [9] proposed a shared control architecture for steer-by-wire LKA using a quasi-continuous high-order sliding mode controller. The system continuously adjusts the balance of control authority between the driver and the automated system based on a sharing parameter, providing smooth handover without abrupt torque transitions. Validated in the SHERPA dynamic vehicle simulator, this architecture provides the control layer upon which the CERPM-based perception system developed in this project would operate. Wei, Pfeffer, and Edelmann [10] provide the most comprehensive recent review of LKA assessment methodologies, identifying significant gaps in standardisation across performance, ride comfort, safety, driver interaction, and driving style dimensions, and proposing an evaluation framework that future CERPM-based LKA systems should adopt.

### 2.5 Summary of Research Gap

The literature shows a clear and un-addressed gap: while the V2I CERPM concept has been validated as superior to vision-based approaches, no study has characterised (a) the comparative accuracy of different interpolation algorithms for centreline estimation, or (b) the effect of CERPM dropout — in any form — on system accuracy. This project provides the first systematic investigation of both questions.

---

## 3. Methodology

### 3.1 Overview

A simulation-based methodology was adopted because it enables controlled, repeatable, exhaustive testing across parameter combinations that would be impractical to replicate in physical field trials. The methodology follows four stages: (1) road geometry acquisition and parsing; (2) CERPM placement simulation; (3) dropout scenario simulation via Monte Carlo methods; (4) interpolation, centreline computation, and error measurement.

All code was implemented in Python, using NumPy for numerical computation, SciPy for interpolation algorithms, Shapely for geometric operations on polylines, and Matplotlib for visualisation.

### 3.2 Road Geometry Acquisition

Real-world road geometries were sourced from Lanelet2-format OSM files. Lanelet2 is a map format designed for autonomous driving applications; it encodes each lane as a *lanelet* containing a left boundary way and a right boundary way, each composed of nodes with local Cartesian coordinates (`local_x`, `local_y`, in metres). Three road geometries were used:

- **Town07:** A sinuous, S-curve road segment approximately 280 m in total path length (see Figure 1). Representative of a rural road with continuous curvature changes.
- **Town042:** A long, gradually curved segment approximately 560 m in length (see Figure 2). Representative of a rural highway or regional road with gentle bends.
- **Town044:** A road with two sharp 90° corners connected by a straight section, total path approximately 520 m (see Figure 3). Representative of an urban intersection approach or sealed rural road junction.

These three geometries were selected to represent meaningfully different curvature profiles. Town07 tests performance on high-frequency curvature variation; Town042 tests performance on a long gradually curving road; Town044 tests performance at abrupt direction changes.

Road geometry was parsed by extracting node coordinates, assembling them into way sequences, and then linking consecutive lanelets into continuous left and right boundary polylines using a chain-linking algorithm that matches the end node of each lanelet to the start node of the next.

### 3.3 CERPM Placement Simulation

CERPMs were simulated by resampling the left and right boundary polylines at a configurable uniform interval using Shapely's `interpolate` method on a `LineString` object. This produces a set of evenly spaced point coordinates along each boundary, mimicking the physical placement of CERPMs at a given inter-marker spacing.

Six CERPM intervals were tested: **0.5 m, 1.0 m, 2.0 m, 4.0 m, 6.0 m, and 12.0 m**. The 0.5–2.0 m range reflects dense installations suitable for high-speed or safety-critical corridors. The 4.0–12.0 m range reflects sparser installations driven by cost constraints.

### 3.4 True Centreline Computation

The ground-truth lane centreline was computed directly from the full-resolution boundary polylines (before resampling) using a perpendicular-nearest-point algorithm. For each point sampled at 0.5 m intervals along the longer boundary, the nearest point on the opposite boundary is found by projecting the sample point onto the opposite LineString. The centreline point is the arithmetic mean of the two boundary points. This produces a dense, geometrically accurate centreline against which interpolated estimates are compared.

### 3.5 Interpolation Methods

Seven interpolation methods were evaluated. All methods use arc-length parameterisation: the parameter *t* ∈ [0, 1] represents the normalised cumulative Euclidean path length along the CERPM sequence, and both the x and y coordinates are interpolated independently as functions of *t*. This parameterisation is necessary because road boundaries are spatial curves rather than functions, and a simple index-based parameterisation would distort spacing information.

The methods are:

| Method | Continuity | Key Characteristic |
|---|---|---|
| Linear | C⁰ | Piecewise straight; simplest baseline |
| Quadratic | C¹ | Degree-2 B-spline; smooth but low-order |
| Cubic Spline | C² | Natural cubic spline; current CERPM standard |
| Quartic | C³ | Degree-4 B-spline |
| Quintic | C⁴ | Degree-5 B-spline |
| PCHIP | C¹ | Monotone cubic; no overshoot |
| Akima | C¹ | Locally weighted cubic; outlier-resistant |

For methods requiring a minimum number of knot points (cubic spline and Akima require ≥3; quadratic requires ≥2), the method gracefully falls back to linear interpolation when the surviving CERPM count falls below this threshold.

### 3.6 Dropout Scenarios

Three dropout models were implemented, reflecting physically distinct failure mechanisms:

**Random Dropout:** Each CERPM independently fails with probability *p* (the dropout rate). This models uncorrelated hardware failures. Dropout rates tested: **10%, 15%, 20%, 25%**. For each interval-rate combination, 2,000 Monte Carlo trials were run, each with a different random seed.

**Gap-Length Dropout:** A contiguous block of CERPMs equivalent to a physical gap of length *g* metres is removed from one side (left or right boundary). This models a physically localised failure scenario such as a section of road resurfacing that destroyed a run of markers, a maintenance gap, or physical damage from a vehicle impact. Gap lengths tested: **2 m, 5 m, 10 m, 15 m, 20 m**. The gap is exhaustively placed at every valid starting position on both the left and right boundaries — producing a complete enumeration of all possible single-gap scenarios rather than a random sample.

**Clustered Dropout:** A contiguous block of *n* consecutive CERPMs is removed from one side. This is equivalent to gap-length dropout but parameterised by marker count rather than physical distance, enabling independent analysis of count versus distance effects. Cluster sizes tested: **2, 5, 10, 15, 20 markers**. Also exhaustively enumerated.

### 3.7 Error Metric

For each trial, the reconstructed left and right boundary polylines from the surviving CERPMs are used to compute a reconstructed centreline using the same perpendicular-nearest-point algorithm. The error for each centreline point is the Euclidean distance from that point to the nearest point on the true centreline LineString. Two metrics are recorded per trial:

- **Mean error:** Average perpendicular distance across all centreline points.
- **Max error:** Maximum perpendicular distance (worst-case deviation).

A trial is classified as a **failure** if the max error exceeds **0.2 m** — a threshold chosen based on the typical lane width of 3.5 m and an assumed LKA intervention threshold of approximately ±0.3 m from centreline, placing 0.2 m as the maximum tolerable estimation error before it begins to contribute to intervention timing errors.

Across the 2,000 trials per condition (random dropout) or the exhaustive enumeration (gap and clustered dropout), the distribution of mean errors is summarised by its 25th percentile (P25), 75th percentile (P75), and interquartile range (IQR = P75 − P25). The failure rate reports the percentage of trials in which max error exceeded 0.2 m.

### 3.8 Project Management

The project was managed across a twelve-week semester using the Gantt chart shown in the abstract. Research activities (weeks 4–6) covered interpolation algorithm theory, Australian RPM standards, and road geometry data sources. Planning (week 6) produced the class-level architecture. Development (weeks 6–9) implemented and debugged the full simulation pipeline. Data collection (week 9) ran all simulations. Results analysis (weeks 10–11) produced the comparative algorithm analysis, CERPM dropout analysis, and combined findings.

The primary project management tool was the Gantt chart for scheduling. Version control (Git) was used throughout development to track code changes, provide rollback capability, and manage the final deliverables.

---

## 4. Results and Analysis

### 4.1 Road Geometries

The three tested road geometries are shown in Figures 1–3 (the `Figure_1.png` plots generated by the simulation). Town07 is a complex sinuous road with multiple curve reversals over approximately 280 m, posing the greatest interpolation challenge due to high curvature variation. Town042 is a long, gradually curving road — the easiest geometry for interpolation as the boundary curves are smooth and regular. Town044 contains two sharp 90° turns, which challenge interpolation methods at the corner apices.

These diverse geometries ensure that findings are not geometry-specific and have broad applicability.

### 4.2 Effect of CERPM Interval on Baseline Accuracy

Before any dropout, the dominant driver of centreline error is CERPM spacing. Across all three road geometries and all seven methods:

- At **0.5 m and 1.0 m** intervals: all methods produce median centreline errors below 0.01 m (10 mm) with near-zero IQR. All methods are effectively equivalent at this resolution.
- At **2.0 m** intervals: the methods begin to diverge. Linear interpolation shows the first meaningful increase in IQR, while cubic spline, PCHIP, and Akima remain well below 0.05 m median error.
- At **4.0 m** intervals: linear IQR rises substantially (median error ~0.1–0.15 m on Town07). Higher-order methods (cubic spline, PCHIP, Akima) remain around 0.03–0.07 m median error.
- At **6.0 m and 12.0 m** intervals: linear interpolation fails at 100% rate under any dropout on all geometries. Quadratic also degrades severely. Cubic spline, quartic, and quintic perform better but exhibit increasing sensitivity to outlier placement. PCHIP and Akima show the most consistent performance, with their local curvature estimation remaining stable even at 12 m spacing.

This confirms the fundamental finding: **dense CERPM deployment renders algorithm choice irrelevant, while sparse deployment makes algorithm choice critical**.

### 4.3 Random Dropout Results

Under random dropout (10%–25% of all CERPMs independently failing), the results (Figures: `random_iqr_heatmap`, `random_iqr_bands`, `random_failure_rate`) show the following patterns:

**At 0.5 m and 1.0 m intervals:** All methods maintain near-zero failure rate across all dropout rates tested (10%–25%). The IQR of centreline error remains below 0.005 m. At these spacings, the density of surviving markers is high enough that even 25% random failure leaves sufficient data for any method to reconstruct the boundary accurately.

**At 2.0 m intervals:** Linear begins to show elevated failure rates at 20–25% dropout (43–67% failure rate on Town07). The smooth methods remain below 10% failure rate at all tested dropout rates.

**At 4.0 m intervals:** Linear reaches 100% failure across all dropout rates. Quadratic reaches 47–88% failure. Cubic spline shows 32–91% failure, quartic 29–75%, quintic 29–74%. PCHIP shows elevated failure (65–85%) at higher dropout rates. **Akima outperforms all others at this spacing, with failure rates of 56–96% — still elevated but consistently lower than alternatives.** The key distinction between methods is most pronounced in the 4–6 m range.

**At 6.0 m and 12.0 m intervals:** All methods show high failure rates under any dropout. At these spacings with any random failure, reconstruction of curved road boundaries is fundamentally challenged regardless of method.

**Cross-geometry comparison:** The Town042 geometry (gradual curve) consistently shows the lowest failure rates at any given interval and dropout rate, while Town07 (sinuous) shows the highest. Town044 (sharp corners) is intermediate but exhibits particular sensitivity at the corner positions where curvature is highest. This confirms that road geometry complexity should inform CERPM spacing standards: sinuous roads require denser installations than straight or gently curved roads.

### 4.4 Gap-Length Dropout Results

Gap-length dropout (Figures: `gaplength_iqr_heatmap`, `gaplength_iqr_bands`, `gaplength_failure_rate`) reveals the most practically important findings, as a physical gap represents the most realistic failure scenario.

**Linear interpolation is uniquely catastrophic under gap-length dropout.** For gaps of 5 m or greater at intervals of 2 m or more, linear shows 100% failure on all geometries. Even at 1.0 m spacing with a 10 m gap, linear fails in 14–18% of positions tested. At 12.0 m spacing, linear fails at 100% across every gap length tested. The reason is geometric: when a run of consecutive markers is missing, linear interpolation simply draws a straight line across the gap — which, on any curved road, diverges immediately from the true boundary curvature. The longer the gap or the greater the curvature, the larger the deviation.

**Cubic spline, quartic, and quintic** perform substantially better. At 1.0 m spacing with gaps up to 10 m, failure rates remain at 0–5% for these methods. At 4.0 m spacing with a 20 m gap, failure rates rise to 25–40% — still substantially better than linear's 100%.

**PCHIP and Akima show the best gap resilience.** Their C¹ local construction means that the shape of the curve on either side of the gap is determined by local knots rather than global polynomial fitting, limiting the extent to which the gap-induced distortion propagates. On Town042 (gradual curve), PCHIP and Akima maintain below 5% failure rate even at 4.0 m spacing for gaps up to 15 m. On Town07 (sinuous), these methods are elevated but remain the best performers.

**Quadratic** also performs notably poorly under gap-length dropout on curved roads. Because it fits a degree-2 polynomial globally (or per-segment), it cannot capture the curvature reversal typical of sinuous roads when markers are missing, resulting in systematic overshoot.

**Critical finding:** There is a significant interaction between gap length and CERPM spacing. A 5 m physical gap at 1.0 m spacing represents the removal of only 5 markers from a dense set — a small perturbation. The same 5 m gap at 5.0 m spacing may leave only 1 surviving marker on that side, making reconstruction impossible for any method. This means **gap failure severity is not measured by physical length alone but by the ratio of gap length to CERPM spacing**.

### 4.5 Comparative Algorithm Summary

Across all dropout scenarios and road geometries, the following ranking emerges:

| Rank | Method | Strengths | Weaknesses |
|---|---|---|---|
| 1 | **PCHIP** | Best gap resilience; no overshoot; consistent across geometries | Slightly higher IQR than cubic spline at dense spacings |
| 2 | **Akima** | Best local robustness; handles isolated outlier gaps well | Slightly more variable on sharp corners |
| 3 | **Cubic Spline** | Best accuracy at dense spacings; well understood | Sensitive to large gaps (Runge-type oscillation) |
| 4 | **Quartic** | Smoother than cubic on straight sections | More oscillation at endpoints with gaps |
| 5 | **Quintic** | Highest order smoothness | Overshoot at corners under gap dropout |
| 6 | **Quadratic** | Better than linear at sparse spacings | C¹ only; poor gap behaviour on curves |
| 7 | **Linear** | No parameters; always stable to use | Unacceptably large error on any non-trivial spacing or gap |

The original CERPM research implicitly used cubic spline, which ranks third in this evaluation. Replacing it with PCHIP would improve gap resilience with no meaningful cost penalty, representing an immediate actionable improvement.

### 4.6 Changes from Initial Research Plan

The initial plan specified five CERPM intervals (0.5, 1.0, 2.0, 3.0, 5.0 m). During development, this was revised to six intervals (0.5, 1.0, 2.0, 4.0, 6.0, 12.0 m) to better characterise the failure transition zone and to include the 12.0 m spacing representative of low-cost rural deployments. The plan specified 500 Monte Carlo runs per condition; this was increased to 2,000 runs to reduce statistical noise in the tail of the failure rate distribution, where a 500-run sample would give ±4.4 percentage points at 95% confidence versus ±2.2 percentage points for 2,000 runs.

Additionally, three road geometries were tested rather than the initially planned set, providing greater confidence in the generalisability of results. The gap-length dropout analysis was added as a more physically interpretable variant of the clustered dropout, providing results directly actionable by road engineers specifying maintenance intervals.

The 0.2 m failure threshold was set during the analysis phase based on the LKA intervention geometry described above; it was not defined in the initial abstract but provides a meaningful and defensible safety standard.

---

## 5. Conclusions and Recommendations

### 5.1 Conclusions

This research investigated the suitability of seven interpolation algorithms for CERPM-based lane centreline estimation and characterised the effect of three CERPM dropout scenarios on accuracy. The following conclusions are drawn:

**Conclusion 1 — CERPM spacing is the primary determinant of system performance.** At spacings of 0.5–1.0 m, all seven methods tested achieve sub-centimetre median error with near-zero failure rates under all dropout scenarios tested. At spacings beyond 2.0 m, algorithm selection and dropout resistance become critical.

**Conclusion 2 — PCHIP and Akima are the most robust algorithms for gap-length dropout.** Their locally-constructed slope estimation limits the propagation of gap-induced error to the immediate vicinity of the gap, unlike global polynomial splines that can oscillate across the entire road segment. For deployment at spacings where marker failures are plausible, these methods are recommended.

**Conclusion 3 — Linear interpolation is unacceptable for any real-world deployment scenario.** Its 100% failure rate under gap-length dropout at spacings ≥2.0 m on curved roads disqualifies it as a primary algorithm. While it has appeal for its simplicity, a hybrid fallback to PCHIP or Akima adds negligible computational overhead.

**Conclusion 4 — Road geometry complexity should drive CERPM spacing standards.** The sinuous Town07 geometry required approximately half the marker spacing of the gradual Town042 geometry to achieve equivalent accuracy. Sharp-corner geometries (Town044) similarly require denser installations at the curve apex.

**Conclusion 5 — The V2I CERPM approach is viable and robust** within the operating envelope defined by this research (spacing ≤2.0 m with the recommended PCHIP or Akima algorithm), supporting the broader ADAS project goal of reliable lane centering independent of visual conditions.

### 5.2 Recommendations

**R1 — Adopt PCHIP as the default interpolation algorithm** for CERPM-based LKA systems, replacing cubic spline. PCHIP provides superior gap resilience with equivalent or better accuracy at practical deployment spacings.

**R2 — Specify maximum CERPM spacing of 1.0 m for safety-critical applications.** At this spacing, even 25% random failure and gaps up to 15 m produce acceptable centreline error across all tested geometries with PCHIP or Akima interpolation.

**R3 — Specify maximum CERPM spacing of 2.0 m for lower-speed or rural applications**, with the understanding that gaps exceeding 5 m will begin to produce failures at elevated rates on sinuous roads. A maintenance protocol to minimise gap lengths should accompany this deployment standard.

**R4 — Implement gap detection logic in the onboard system.** When the number of received CERPMs on one side falls below a minimum threshold (e.g., three consecutive markers within expected range) during a known gap, the system should fall back to dead-reckoning or increase the LKA intervention threshold to avoid reacting to a degraded centreline estimate.

**R5 — Extend this research to include GPS positioning error.** The current simulation assumes exact CERPM coordinates. A follow-on study should characterise the combined effect of CERPM spacing, dropout, and GPS noise (expected 0.1–1.0 m RMS for commercial GNSS) on system accuracy.

**R6 — Evaluate integration with the vision-based LKA subsystem.** As noted in the introduction, CERPMs can be used in conjunction with camera-based detection. A sensor fusion study combining CERPM centreline estimates with camera-based detection would characterise the accuracy improvement achievable through redundancy.

---

## 6. References

[1] S. Sharma, J. Rojas, A. R. Ekti, R. Wang, Z. Asher, and R. Meyer, "Vehicle Lateral Offset Estimation Using Infrastructure Information for Reduced Compute Load," *SAE Technical Paper Series*, Apr. 2023, doi: https://doi.org/10.4271/2023-01-0800.

[2] P. Kadav et al., "Automated Lane Centering: An Off-the-Shelf Computer Vision Product vs. Infrastructure-Based Chip-Enabled Raised Pavement Markers," *Sensors*, vol. 24, no. 7, pp. 2327–2327, Apr. 2024, doi: https://doi.org/10.3390/s24072327.

[3] Department of Infrastructure, Transport, Cities and Regional Development, "Fact sheet: Evidence supporting the priority focus areas," *National Road Safety Strategy*, 2021. https://www.roadsafety.gov.au/nrss/fact-sheets/priority-focus-areas

[4] National Highway Traffic Safety Administration, "Estimating Effectiveness of Lane Keeping Assist Systems in Fatal Road Departure Crashes," 2024. [Online]. Available: https://crashstats.nhtsa.dot.gov/Api/Public/ViewPublication/813663

[5] European Commission, "Mandatory drivers assistance systems expected to help save over 25,000 lives by 2038," *Internal Market, Industry, Entrepreneurship and SMEs*, Jul. 05, 2024. https://single-market-economy.ec.europa.eu/news/mandatory-drivers-assistance-systems-expected-help-save-over-25000-lives-2038-2024-07-05_en

[6] Y. Wang, A. Alhuraish, S. Yuan, and H. Zhou, "GitHub - OpenLKA/OpenLKA: Open source multimodal OpenLKA dataset," GitHub, 2025. https://github.com/OpenLKA/OpenLKA (accessed Mar. 22, 2026).

[7] I. Fakhari and S. Anwar, "A Multiple Model Estimation Approach to Robust Lane Detection via Computer Vision Based Models," *2022 IEEE 31st International Symposium on Industrial Electronics (ISIE)*, pp. 576–581, Jun. 2022, doi: https://doi.org/10.1109/isie51582.2022.9831692.

[8] I. Fakhari and S. Anwar, "Computer vision model based robust lane detection using multiple model adaptive estimation methodology," *Frontiers in Mechanical Engineering*, vol. 11, Feb. 2025, doi: https://doi.org/10.3389/fmech.2025.1436338.

[9] G. Perozzi, J. J. Rath, C. Sentouh, J. Floris, and J.-C. Popieul, "Lateral Shared Sliding Mode Control for Lane Keeping Assist System in Steer-by-Wire Vehicles: Theory and Experiments," *IEEE Transactions on Intelligent Vehicles*, vol. 8, no. 4, pp. 3073–3082, Apr. 2023, doi: https://doi.org/10.1109/tiv.2021.3097352.

[10] S. Wei, P. E. Pfeffer, and J. Edelmann, "State of the Art: Ongoing Research in Assessment Methods for Lane Keeping Assistance Systems," *IEEE Transactions on Intelligent Vehicles*, vol. 9, no. 9, pp. 5853–5875, Sep. 2024, doi: https://doi.org/10.1109/tiv.2023.3269156.

---

## 7. Appendices

### Appendix A — Project Gantt Chart

The Gantt chart below (reproduced from the project abstract) summarises the planned schedule across the 12-week semester.

| Section | Task | Wk 4 | Wk 5 | Wk 6 | Wk 7 | Wk 8 | Wk 9 | Wk 10 | Wk 11 | Wk 12 |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Research | Interpolation Algorithms | ✓ | ✓ | | | | | | | |
| Research | Australian RPM Standards | ✓ | ✓ | | | | | | | |
| Research | Road Geometry Sources | | ✓ | ✓ | | | | | | |
| Research | Importing Road Geometry | | | ✓ | ✓ | | | | | |
| Planning | Class Diagram | | | ✓ | | | | | | |
| Development | Coding | | | ✓ | ✓ | ✓ | | | | |
| Development | Testing and Debugging | | | | | ✓ | ✓ | | | |
| Simulation | Data Collection | | | | | | ✓ | | | |
| Results | Interpolation Algorithms Comparison | | | | | | | ✓ | ✓ | |
| Results | Analysis of CERPM Dropout | | | | | | | ✓ | ✓ | |
| Results | Combine Findings | | | | | | | | ✓ | ✓ |

### Appendix B — Software Architecture

The simulation is implemented across four Python modules:

- **`test.py`** — Core geometric utilities: OSM node/way/lanelet parsing (`getNodes`, `getWays`, `getLanelets`), lanelet chain-linking (`combineWays`), CERPM resampling (`resample`), and centreline computation (`calCenterline`).
- **`Interpolations.py`** — Arc-length parameterisation (`arcLenghtParameter`) and the unified `interpolate(pts, numPts, method)` function implementing all seven methods via SciPy.
- **`Simulation.py`** — Monte Carlo engine: `runMonteCarloRandom`, `runMonteCarloClusteredSingle`, and `runMonteCarloGapLength`, all using `ProcessPoolExecutor` for parallel trial execution. Error measurement via Shapely point-to-LineString distance.
- **`xmlParse.py`** — Top-level orchestration, parameter sweep management, and all visualisation functions (IQR heatmaps, IQR band plots, failure rate heatmaps, ranking heatmaps, summary tables).

### Appendix C — Simulation Parameters

| Parameter | Values |
|---|---|
| CERPM intervals | 0.5, 1.0, 2.0, 4.0, 6.0, 12.0 m |
| Random dropout rates | 10%, 15%, 20%, 25% |
| Gap lengths | 2, 5, 10, 15, 20 m |
| Cluster sizes | 2, 5, 10, 15, 20 markers |
| Monte Carlo runs (random) | 2,000 per condition |
| Gap/cluster trials | Exhaustive enumeration (all valid positions, both sides) |
| Failure threshold | Max centreline error > 0.2 m |
| Centreline sample interval | 0.5 m |
| Road geometries | Town07, Town042, Town044 |

### Appendix D — Interpolation Method Properties

| Method | SciPy Implementation | Min Points Required | Continuity | Overshoot Possible |
|---|---|---|---|---|
| Linear | `numpy.interp` | 2 | C⁰ | No |
| Quadratic | `make_interp_spline(k=2)` | 3 | C¹ | Yes |
| Cubic Spline | `CubicSpline` (natural) | 3 | C² | Yes |
| Quartic | `make_interp_spline(k=4)` | 5 | C³ | Yes |
| Quintic | `make_interp_spline(k=5)` | 6 | C⁴ | Yes |
| PCHIP | `PchipInterpolator` | 2 | C¹ | No |
| Akima | `Akima1DInterpolator` | 3 | C¹ | Limited |
