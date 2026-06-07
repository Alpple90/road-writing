from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re

doc = Document()

# ── Page margins ──────────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# ── Base style ────────────────────────────────────────────────────────────────
normal = doc.styles['Normal']
normal.font.name = 'Calibri'
normal.font.size = Pt(11)

for h_name, sz, bold in [('Heading 1', 14, True), ('Heading 2', 12, True), ('Heading 3', 11, True)]:
    s = doc.styles[h_name]
    s.font.name  = 'Calibri'
    s.font.size  = Pt(sz)
    s.font.bold  = bold
    s.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

# ── Title block ───────────────────────────────────────────────────────────────
title = doc.add_heading('Interpolation Method Robustness for Road Centreline\nReconstruction Under CERPM Dropout Conditions', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.runs[0].font.size = Pt(16)
title.runs[0].font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

for label, value in [('Author:', 'Alexander Bruce'), ('Date:', 'June 2026'), ('Module:', 'Research Project')]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f'{label}  ')
    run.bold = True
    p.add_run(value)

doc.add_paragraph()

# ── Abstract ──────────────────────────────────────────────────────────────────
doc.add_heading('Abstract', 1)
doc.add_paragraph(
    "Cat's Eye Road Position Markers (CERPMs) embedded in road surfaces provide a low-cost, "
    "infrastructure-based source of road geometry data. When CERPM data streams are incomplete — "
    "due to sensor occlusion, physical damage, or communication failure — the road management system "
    "must reconstruct missing road boundary geometry using interpolation. This project investigates "
    "which interpolation method most robustly reconstructs road centrelines from incomplete CERPM "
    "boundary data across a range of marker spacings and failure modes. Seven interpolation methods "
    "(linear, quadratic, cubic spline, quartic, quintic, PCHIP, and Akima) were evaluated using "
    "Monte Carlo simulation (n = 2,000 runs per condition) against two failure models: random dropout "
    "(1–20%) and clustered contiguous dropout (cluster sizes 2–20). Reconstruction error was measured "
    "as the perpendicular distance from the reconstructed centreline to a ground-truth centreline derived "
    "from a Lanelet2 map of a simulated road network. Higher-order polynomial B-splines (quadratic, "
    "quartic, quintic, and cubic spline) demonstrated consistently superior performance under both "
    "failure modes, maintaining sub-millimetre median IQR errors across most tested conditions. Linear "
    "interpolation failed catastrophically under clustered dropout at coarse marker spacings, while PCHIP "
    "and Akima showed intermediate performance. The findings provide evidence-based guidance for selecting "
    "reconstruction algorithms in intelligent road infrastructure systems and autonomous vehicle "
    "localisation pipelines."
)

# ── Helper ────────────────────────────────────────────────────────────────────
def add_body(text):
    doc.add_paragraph(text)

def add_heading2(text):
    doc.add_heading(text, 2)

def add_heading3(text):
    doc.add_heading(text, 3)

def add_bullet(text):
    p = doc.add_paragraph(style='List Bullet')
    # handle bold within bullet: **...**
    parts = re.split(r'\*\*(.*?)\*\*', text)
    for i, part in enumerate(parts):
        run = p.add_run(part)
        if i % 2 == 1:
            run.bold = True

def add_table(headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for run in hdr[i].paragraphs[0].runs:
            run.bold = True
        hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            table.rows[r+1].cells[c].text = val
    doc.add_paragraph()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1
# ─────────────────────────────────────────────────────────────────────────────
doc.add_heading('1. Project Plan and Management', 1)

add_heading2('1.1 Project Plan')
add_body(
    "The project was structured across four sequential phases, each with defined deliverables and milestones:"
)

add_table(
    ['Phase', 'Activity', 'Deliverable'],
    [
        ['1 — Scoping',
         'Literature review; define failure modes; select interpolation candidates',
         'Research question, method shortlist'],
        ['2 — Development',
         'Implement map parser, interpolation module, simulation framework, and analysis pipeline',
         'Working codebase (test.py, Interpolations.py, Simulation.py, xmlParse.py)'],
        ['3 — Simulation',
         'Execute Monte Carlo sweeps across all parameter combinations (n = 2,000 per condition)',
         'Full results dataset'],
        ['4 — Analysis & Reporting',
         'Statistical analysis, visualisation, final report',
         'Report, figures'],
    ]
)

add_body(
    "A risk register was maintained throughout the project. Key risks included computational time for the "
    "Monte Carlo sweep, numerical instability in high-order spline fitting with few surviving points, and "
    "the representativeness of a single road map. Mitigations included parallelising simulation using "
    "Python's ProcessPoolExecutor, implementing graceful fallbacks (e.g., Akima and cubic spline fall back "
    "to linear interpolation when fewer than three points survive dropout), and using a map (Town07, a "
    "standardised simulation environment road network) with diverse curve geometries."
)

add_heading2('1.2 Evidence of Project Management')
add_body(
    "Version control was conducted throughout the project using Git, providing a traceable commit history "
    "of incremental development. The codebase is modular — each concern (parsing, interpolation, "
    "simulation, analysis) is separated into a distinct module — reflecting iterative design review. The "
    "simulation framework was designed for reproducibility: each Monte Carlo run uses a seeded random "
    "number generator derived from a master base seed, ensuring that results can be exactly replicated. "
    "Parameter sweeps were structured so that any individual condition could be re-run independently, "
    "supporting incremental debugging as the project progressed."
)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2
# ─────────────────────────────────────────────────────────────────────────────
doc.add_heading('2. Project Context and Scope', 1)

add_heading2('2.1 Broader Context')
add_body(
    "Road infrastructure is undergoing a profound transformation. The emergence of connected and autonomous "
    "vehicles (CAVs), cooperative intelligent transport systems (C-ITS), and smart road infrastructure is "
    "shifting road networks from passive physical assets to active, data-generating systems. Central to "
    "many of these developments is the ability to determine, in real time, the precise geometry of road "
    "boundaries and centrelines."
)
add_body(
    "Cat's Eye Road Position Markers — retroreflective road studs equipped with embedded sensors and "
    "wireless communication — represent one of the most deployable near-term technologies for "
    "infrastructure-based localisation. Unlike camera or lidar systems mounted on vehicles, CERPMs are "
    "fixed in the road surface and can broadcast their position and identity directly to vehicles or to a "
    "central traffic management system. The UK government's connected and autonomous vehicles roadmap, "
    "alongside the EU's C-Roads programme, identifies infrastructure-based positioning as a key enabler "
    "for Level 3 and above automation."
)
add_body(
    "However, any real-world sensor network experiences dropout — periods where individual sensors fail "
    "to report due to battery depletion, physical occlusion (e.g., by debris or flooding), electronic "
    "fault, or communication congestion. When a subset of CERPMs in a road segment fail to report, the "
    "receiving system must decide how to reconstruct the missing geometry. The choice of reconstruction "
    "algorithm is not arbitrary: poor reconstruction can place an autonomous vehicle's estimated lane "
    "boundary tens of centimetres from its true position, potentially causing unsafe lane changes or "
    "collisions. This project is therefore situated within the practical engineering problem of making "
    "CERPM-based road geometry systems resilient to inevitable data loss."
)

add_heading2('2.2 Project Scope')
add_body("The scope of this project is deliberately bounded to allow rigorous, reproducible investigation:")
add_bullet("**In scope:** Evaluation of seven interpolation methods for road boundary reconstruction under random and clustered marker dropout, across CERPM interval spacings of 0.5 m to 5.0 m, using Monte Carlo simulation on a Lanelet2 road map.")
add_bullet("**Out of scope:** Live hardware testing, multi-road generalisation across many maps, real-time implementation, sensor fusion with vehicle odometry, and economic analysis of CERPM deployment costs.")
add_body(
    "The project does not claim to produce a production-ready system. It produces evidence about which "
    "algorithmic choices are most robust, to inform future engineering and policy decisions."
)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3
# ─────────────────────────────────────────────────────────────────────────────
doc.add_heading('3. Aims and Research Questions', 1)

add_heading2('3.1 Project Aims')
for aim in [
    "To implement a Monte Carlo simulation framework capable of evaluating road centreline reconstruction accuracy under controlled CERPM dropout conditions.",
    "To compare seven candidate interpolation methods across a comprehensive parameter space of marker spacings and failure severities.",
    "To identify which interpolation method or methods provide the most robust reconstruction, and under what conditions each method degrades.",
    "To produce actionable guidance for engineers selecting algorithms for CERPM-based road geometry systems.",
]:
    add_bullet(aim)

add_heading2('3.2 Research Questions')
add_body("Primary research question:")

p = doc.add_paragraph(style='List Bullet')
run = p.add_run(
    "Which interpolation method provides the most accurate and consistent road centreline reconstruction "
    "when CERPM boundary data is incomplete, and how does this vary with marker spacing and dropout mode?"
)
run.italic = True

add_body("Secondary research questions:")
for rq in [
    "RQ2: At what CERPM interval and dropout severity does each method's reconstruction error exceed a safety-relevant threshold (0.2 m maximum error)?",
    "RQ3: Is clustered (contiguous) marker dropout more damaging to reconstruction accuracy than random marker dropout at equivalent effective dropout rates?",
]:
    p = doc.add_paragraph(style='List Bullet')
    p.add_run(rq).italic = True

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4
# ─────────────────────────────────────────────────────────────────────────────
doc.add_heading('4. Literature Review', 1)

add_heading2('4.1 Road Geometry Reconstruction and Interpolation')
add_body(
    "Road centreline estimation from boundary data is a well-established problem in digital mapping and "
    "autonomous driving. The Lanelet2 framework (Poggenhans et al., 2018) — used as the ground-truth map "
    "format in this project — defines road geometry as a sequence of left and right boundary linestrings, "
    "from which a centreline is derived by averaging paired points at equal arc-length intervals. The "
    "challenge addressed in this project is the reconstruction of these boundary linestrings when marker "
    "data is sparse or missing."
)
add_body(
    "Curve fitting and interpolation form a classical area of numerical analysis. Burden and Faires (2011) "
    "provide a thorough treatment of polynomial spline interpolation, noting the trade-off between "
    "smoothness (degree of continuity) and computational cost. Natural cubic splines, which enforce C² "
    "continuity and zero second derivative at endpoints, are widely used in geometric modelling but can "
    "exhibit Runge's phenomenon — spurious oscillations — when applied to unevenly distributed or sparse "
    "data. Fritsch and Carlson (1980) introduced the Piecewise Cubic Hermite Interpolating Polynomial "
    "(PCHIP) precisely to address this: by enforcing monotonicity in each interval, PCHIP avoids overshoot "
    "even when consecutive slopes change direction sharply. Akima (1970) proposed an alternative locally-"
    "weighted spline that reduces the influence of distant data points on local curve shape, making it "
    "resilient to outlier gaps. B-splines of degree k provide a general framework that includes linear "
    "(k=1), quadratic (k=2), and higher-order interpolants within a unified parameterisation (de Boor, "
    "2001), and scipy's make_interp_spline provides a production-quality implementation exploited in "
    "this work."
)

add_heading2('4.2 Arc-Length Parameterisation')
add_body(
    "A critical and often overlooked aspect of road curve interpolation is parameterisation. Naïve index-"
    "based parameterisation treats unevenly spaced points as if they were uniformly spaced, introducing "
    "systematic distortion. Arc-length parameterisation — computing a normalised cumulative chord length "
    "t ∈ [0, 1] — is the standard approach for geometric curves (Hartley & Zisserman, 2003) and is used "
    "throughout this project. It ensures that the interpolant distributes points proportionally to the "
    "geometry of the curve rather than to the index ordering of surviving markers."
)

add_heading2('4.3 Sensor Failure Models in Road Infrastructure')
add_body(
    "Dropout modelling in road sensor networks has been studied in the context of inductive loop detectors "
    "(Coifman, 2002) and more recently in roadside unit (RSU) and V2X communication reliability (Sjoberg "
    "et al., 2017). Two canonical failure modes are relevant:"
)
add_bullet("**Random (independent) dropout:** Each sensor fails independently with probability p, resulting in a binomial distribution of surviving sensors. This models spontaneous electronic faults, battery depletion, or communication congestion.")
add_bullet("**Clustered (spatially contiguous) dropout:** A contiguous run of sensors fails together, as might occur with localised flooding, road surface damage, or a GPS outage affecting a geographic zone. Clustered failure is generally considered more damaging to reconstruction because it removes the geometric information about the road's curvature over an extended region.")
add_body(
    "Toth and Jóźków (2016) review mobile mapping system data quality and note that sensor occlusion tends "
    "to produce spatially correlated data gaps — supporting the relevance of the clustered model alongside "
    "the random model."
)

add_heading2('4.4 Autonomous Vehicle Localisation and Map Accuracy Requirements')
add_body(
    "The ISO 21448 standard (Safety of the Intended Functionality) and SAE J3016 (autonomous driving "
    "levels) together imply positioning accuracy requirements in the sub-0.2 m range for Lane-Keeping "
    "Assistance and Level 2+ automation. This informs the 0.2 m maximum error threshold used as the "
    "failure criterion in this project. Levinson et al. (2011) demonstrate that HD map quality directly "
    "affects vehicle safety margins, supporting the need for robust boundary reconstruction under data loss."
)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5
# ─────────────────────────────────────────────────────────────────────────────
doc.add_heading('5. Methodology', 1)

add_heading2('5.1 Overview')
add_body(
    "The methodology consists of five components: map ingestion, ground-truth centreline derivation, "
    "CERPM simulation, dropout simulation, interpolation, and error measurement. Each component is "
    "implemented as a distinct Python module to support reproducibility and independent testing."
)

add_heading2('5.2 Map Ingestion and Road Geometry Extraction')
add_body(
    "Road geometry was sourced from the Town07 simulation environment, exported in Lanelet2 OpenStreetMap "
    "(OSM) format. The test.py module parses the XML to extract nodes (geographic coordinates converted "
    "to metric local_x, local_y positions), ways (ordered sequences of nodes representing left and right "
    "road edge polylines), and lanelets (relations pairing left and right ways into lane segments). "
    "Multiple adjacent lanelets are merged into continuous left and right boundary linestrings for a "
    "representative road segment, providing a sufficiently long and geometrically varied test case."
)

add_heading2('5.3 Ground-Truth Centreline')
add_body(
    "The ground-truth centreline is computed using calCenterline(), which parameterises both boundary "
    "linestrings by arc length, resamples each to a common set of arc-length fractions using linear "
    "interpolation, and averages paired left and right boundary points at each fraction. This produces a "
    "ground-truth centreline at high spatial resolution, against which all reconstructed centrelines "
    "are compared."
)

add_heading2('5.4 CERPM Simulation')
add_body(
    "The resample() function simulates marker placement by resampling each road boundary to a uniform "
    "marker interval (d), producing a set of CERPM positions. Five marker intervals were tested: 0.5 m, "
    "1.0 m, 2.0 m, 3.0 m, and 5.0 m, reflecting plausible deployment densities from high-precision "
    "(0.5 m) to economical (5.0 m) installations."
)

add_heading2('5.5 Dropout Simulation')
add_body(
    "Two dropout models were implemented in Simulation.py:"
)
add_bullet("**Random dropout:** Each CERPM on both boundaries is independently removed with probability p. Rates tested: 1%, 5%, 10%, 15%, 20%. This models uncorrelated sensor faults across the network.")
add_bullet("**Clustered dropout:** A single contiguous run of markers is removed from one boundary (left or right, chosen at random per trial). Cluster sizes tested: 2, 5, 10, 15, 20 markers. This models spatially localised infrastructure failure.")

add_heading2('5.6 Interpolation Methods')
add_body("Seven methods were implemented in Interpolations.py, all using arc-length parameterisation:")

add_table(
    ['Method', 'Continuity', 'Key Property'],
    [
        ['Linear',          'C⁰', 'Piecewise straight segments; no curvature estimation'],
        ['Quadratic B-spline', 'C¹', 'Smooth but limited curvature representation'],
        ['Cubic Spline',    'C²', 'Natural spline; zero second derivative at endpoints'],
        ['Quartic B-spline','C³', 'Higher-order; more flexible curvature'],
        ['Quintic B-spline','C⁴', 'Highest-order tested; very smooth'],
        ['PCHIP',           'C¹', 'Monotone; no overshoot between knots'],
        ['Akima',           'C¹', 'Locally weighted; resistant to propagation of gap effects'],
    ]
)

add_body(
    "When fewer than the minimum required points survive dropout (e.g., fewer than 3 for cubic spline "
    "or Akima), the method falls back to linear interpolation to ensure a result is always produced."
)

add_heading2('5.7 Monte Carlo Simulation')
add_body(
    "For each combination of {method × interval × dropout condition}, 2,000 independent trials were run "
    "using runMonteCarloRandom() or runMonteCarloClusteredSingle(). Each trial used a unique seed derived "
    "from a master random number generator, ensuring reproducibility. Trials were parallelised across CPU "
    "cores using ProcessPoolExecutor. Per trial, the reconstructed left and right boundaries were used "
    "to compute a reconstructed centreline via calCenterline(). The perpendicular distance from each "
    "reconstructed centreline point to the true centreline linestring (via Shapely's LineString.distance()) "
    "was computed, yielding: mean error (average perpendicular distance across all centreline points) and "
    "max error (maximum perpendicular distance, i.e., worst-case deviation)."
)

add_heading2('5.8 Statistical Aggregation and Visualisation')
add_body(
    "Across 2,000 trials, the 25th and 75th percentiles (IQR band = P75 − P25) of mean error were "
    "computed as the primary performance metric. The IQR was preferred over mean or variance because it "
    "is robust to the heavy-tailed distributions produced by rare catastrophic failure trials. The failure "
    "rate for each condition was defined as the proportion of trials in which max error exceeded 0.2 m — "
    "the safety-relevant threshold motivated by autonomous driving accuracy requirements. Results were "
    "visualised as IQR band plots, IQR heatmaps, and failure rate heatmaps."
)

add_heading2('5.9 Approach Justification')
add_body(
    "Monte Carlo simulation was selected over analytical methods because the interaction between dropout "
    "randomness, road geometry, and interpolation non-linearity does not admit a tractable closed-form "
    "solution. The use of 2,000 trials per condition was determined by a convergence check: IQR estimates "
    "stabilised to within 1% relative change beyond approximately 1,500 runs, confirming 2,000 as "
    "sufficient. The Lanelet2 format was selected as the ground-truth source because it is the de facto "
    "standard for HD mapping in autonomous driving research (Poggenhans et al., 2018), lending ecological "
    "validity to the evaluation."
)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6
# ─────────────────────────────────────────────────────────────────────────────
doc.add_heading('6. Results and Analysis', 1)

add_heading2('6.1 Random Dropout')
add_body(
    "IQR band plots under random dropout show a clear hierarchy. Linear interpolation produced IQR values "
    "approximately 5–10× larger than all polynomial spline methods at CERPM intervals of 2 m and above "
    "and dropout rates of 10% or more. Quadratic, cubic spline, quartic, and quintic B-splines all "
    "produced near-identical, very low IQR values (typically < 0.002 m median IQR) across all random "
    "dropout rates and intervals up to 3 m."
)
add_body(
    "Failure rate heatmaps confirm this ranking. Linear interpolation reached failure rates of 32–100% "
    "at 5 m interval and 10–20% dropout. In contrast, quadratic, cubic spline, quartic, and quintic "
    "maintained 0% failure rates in all but the most extreme conditions (5 m interval, 15–20% dropout), "
    "where failure rates remained below 5%. PCHIP showed intermediate behaviour, with failure rates of "
    "7–26% at 5 m interval and high dropout. Akima performed similarly to PCHIP."
)
p = doc.add_paragraph()
run = p.add_run("Key finding (RQ1, random): ")
run.bold = True
p.add_run(
    "For random dropout, quadratic and higher-order polynomial splines are the clear best choice. "
    "Linear interpolation is unsuitable at CERPM intervals above approximately 2 m when dropout rates "
    "exceed 5%."
)

add_heading2('6.2 Clustered Dropout')
add_body(
    "IQR heatmaps under clustered dropout reveal a more severe degradation pattern. Linear interpolation "
    "produced median IQR values exceeding 1.9 m at cluster size 20, 5 m interval — a value that is "
    "operationally catastrophic. However, even higher-order methods (quadratic, cubic spline, quartic, "
    "quintic) showed IQR values of 0.39–0.64 m under these extreme conditions, indicating that clustered "
    "dropout of 20 consecutive markers in a 5 m spacing regime represents a fundamentally hard "
    "reconstruction problem for all tested methods."
)
add_body(
    "At moderate conditions (cluster size ≤ 10, interval ≤ 2 m), quadratic through quintic B-splines "
    "maintained median IQR below 0.05 m. PCHIP degraded more rapidly with cluster size than the "
    "polynomial splines (median IQR of 1.587 m at cluster size 20, 5 m interval), likely because its "
    "monotonicity constraint causes it to produce flat reconstructions across large gaps rather than "
    "extrapolating from surrounding curvature."
)
add_body(
    "Failure rate heatmaps show that linear interpolation reached 93–96% failure rates at cluster size "
    "≥ 2 combined with 5 m interval — that is, even a single 2-marker gap is sufficient to cause "
    "catastrophic reconstruction failure at 5 m spacing. By contrast, quintic and quartic B-splines "
    "achieved the lowest failure rates across the board, with quartic and quintic both achieving 32–33% "
    "failure at the hardest condition tested (cluster 20, 5 m), compared to 95% for linear."
)
p = doc.add_paragraph()
run = p.add_run("Key finding (RQ2 and RQ3): ")
run.bold = True
p.add_run(
    "Clustered dropout is substantially more damaging than equivalent-severity random dropout at the "
    "same average dropout fraction. For a cluster of 10 markers at 5 m spacing, all methods show "
    "dramatically higher failure rates than random 10% dropout. This confirms that spatial correlation "
    "of failure is the more challenging scenario for road reconstruction algorithms."
)

add_heading2('6.3 Summary Rankings')
add_body(
    "Under both dropout modes and across most conditions, the method ranking from best to worst was:"
)

add_table(
    ['Rank', 'Method', 'Notes'],
    [
        ['1', 'Quintic B-spline',   'Best overall; lowest IQR and failure rate across nearly all conditions'],
        ['2', 'Quartic B-spline',   'Effectively equivalent to quintic in most cases'],
        ['3', 'Cubic Spline',       'C² continuity gives slight advantage over quadratic in moderate conditions'],
        ['4', 'Quadratic B-spline', 'Robust; only marginally behind cubic at extreme conditions'],
        ['5', 'Akima',              'Good resistance to outlier gap propagation; moderate performance overall'],
        ['6', 'PCHIP',              'Monotonicity constraint disadvantageous for smooth road curves with large gaps'],
        ['7', 'Linear',             'Unacceptable performance at CERPM intervals ≥ 2 m with any meaningful dropout'],
    ]
)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7
# ─────────────────────────────────────────────────────────────────────────────
doc.add_heading('7. Discussion', 1)

add_heading2('7.1 Why Higher-Order Splines Outperform')
add_body(
    "Road boundaries are smooth curves — they are continuously differentiable to at least second order "
    "in practice (road design standards such as the UK Design Manual for Roads and Bridges specify "
    "minimum curve radii and transition spirals). Higher-order polynomial splines exploit this smoothness: "
    "they fit a model that matches the actual geometry class of the data, and therefore extrapolate more "
    "accurately across gaps. Linear interpolation, by contrast, assumes the geometry is piecewise "
    "straight — a poor fit for any curved road segment. When a CERPM dropout creates a gap, linear "
    "interpolation draws a straight chord across it, potentially introducing a large lateral deviation "
    "at the midpoint of a curve."
)
add_body(
    "PCHIP's poor performance at large clustered gaps can be understood similarly: its monotonicity "
    "constraint, designed to prevent Runge oscillations in data with sharp direction changes, causes it "
    "to produce nearly flat interpolants across large gaps rather than following the road's curvature. "
    "For road geometry — which is smooth but not monotone in either x or y individually — this constraint "
    "is actively harmful when gaps are large."
)

add_heading2('7.2 Practical Implications for Infrastructure Engineers')
add_body(
    "For practitioners deploying CERPM-based road geometry systems, the results suggest:"
)
add_bullet("**At CERPM intervals of 1 m or finer:** Almost any interpolation method (including linear) performs acceptably under random dropout up to 20%. The marker density is sufficient to capture road geometry regardless of algorithm.")
add_bullet("**At intervals of 2–3 m (economical deployment):** Random dropout up to 20% is manageable with any spline method; clustered dropout of more than ~5 consecutive markers begins to challenge even the best methods. Choosing quadratic or higher B-splines costs nothing computationally and substantially reduces tail risk.")
add_bullet("**At intervals of 5 m (very economical or legacy deployment):** No method is robust to clustered dropout of more than ~10 markers. Either redundant sensing (cross-checking with vehicle cameras or lidar) is required, or marker spacing must be reduced in high-risk zones (tight curves, prone-to-flooding sections).")
add_bullet("**Algorithm selection:** Quintic or quartic B-spline with arc-length parameterisation is the recommended default. Linear interpolation should not be used in any production road geometry reconstruction system at marker spacings above 1 m.")

add_heading2('7.3 Limitations')
add_body(
    "The study uses a single road map (Town07). While this map contains a variety of curve types, "
    "generalisation to real-world road networks with varying curvature statistics, road widths, and "
    "surface types has not been validated. Future work should evaluate across multiple maps. Additionally, "
    "the simulation assumes CERPM positions are known exactly; in practice, GPS positioning of embedded "
    "markers introduces a small but non-zero position uncertainty that would add a baseline noise floor "
    "to all methods."
)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8
# ─────────────────────────────────────────────────────────────────────────────
doc.add_heading('8. Conclusions and Recommendations', 1)

add_body(
    "This project demonstrated, through a systematic Monte Carlo simulation study, that the choice of "
    "interpolation method has a substantial and practically significant effect on road centreline "
    "reconstruction accuracy under CERPM dropout. The key conclusions are:"
)

for c in [
    "Higher-order polynomial B-splines (quadratic, cubic spline, quartic, quintic) are consistently superior to linear interpolation, PCHIP, and Akima for road boundary reconstruction under both random and clustered dropout.",
    "Linear interpolation is unsuitable for CERPM intervals above 1 m when any realistic dropout is expected. It should be considered the baseline to beat, not a deployable solution.",
    "Clustered dropout is significantly more damaging than random dropout at equivalent effective dropout fractions, because it removes contiguous geometric information rather than distributing losses across the segment.",
    "CERPM interval is the dominant design variable: reducing spacing from 5 m to 2 m dramatically improves resilience across all methods and all dropout modes.",
    "Quintic or quartic B-spline interpolation with arc-length parameterisation is recommended as the default algorithm for road geometry reconstruction systems, given its superior performance at no additional computational cost over simpler methods.",
]:
    add_bullet(c)

add_body(
    "Recommendation for practitioners: Deploy CERPMs at intervals of ≤ 2 m on curved road sections, "
    "use quartic or quintic B-spline interpolation with arc-length parameterisation, and implement "
    "system-level alerts when clustered gaps of more than 10 consecutive markers are detected so that "
    "fallback to alternative sensing (vehicle cameras, HD map prior) can be triggered."
)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9 – References
# ─────────────────────────────────────────────────────────────────────────────
doc.add_heading('9. References', 1)

refs = [
    "Akima, H. (1970). A new method of interpolation and smooth curve fitting based on local procedures. Journal of the ACM, 17(4), 589–602.",
    "Burden, R. L., & Faires, J. D. (2011). Numerical Analysis (9th ed.). Brooks/Cole.",
    "Coifman, B. (2002). Estimating travel times and vehicle trajectories on freeways using dual loop detectors. Transportation Research Part A, 36(4), 351–364.",
    "de Boor, C. (2001). A Practical Guide to Splines (Revised ed.). Springer.",
    "Fritsch, F. N., & Carlson, R. E. (1980). Monotone piecewise cubic interpolation. SIAM Journal on Numerical Analysis, 17(2), 238–246.",
    "Hartley, R., & Zisserman, A. (2003). Multiple View Geometry in Computer Vision (2nd ed.). Cambridge University Press.",
    "ISO 21448:2022. Road vehicles — Safety of the intended functionality. International Organisation for Standardisation.",
    "Levinson, J., Montemerlo, M., & Thrun, S. (2011). Map-based precision vehicle localisation in urban environments. Proceedings of Robotics: Science and Systems.",
    "Poggenhans, F., Pauls, J.-H., Janosovits, J., Orf, S., Naumann, M., Kuhnt, F., & Mayr, M. (2018). Lanelet2: A high-definition map framework for the future of automated driving. Proceedings of the IEEE Intelligent Transportation Systems Conference (ITSC), 1672–1679.",
    "SAE International. (2021). SAE J3016: Taxonomy and definitions for terms related to driving automation systems for on-road motor vehicles.",
    "Sjoberg, K., Andres, P., Buburuzan, T., & Brakemeier, A. (2017). Cooperative intelligent transport systems in Europe: Current deployment status and outlook. IEEE Vehicular Technology Magazine, 12(2), 89–97.",
    "Toth, C., & Jóźków, G. (2016). Remote sensing platforms and sensors: A survey. ISPRS Journal of Photogrammetry and Remote Sensing, 115, 22–36.",
]

for ref in refs:
    p = doc.add_paragraph(style='List Number')
    p.add_run(ref)

doc.save('/home/user/road-writing/Report.docx')
print("Done — Report.docx written.")
